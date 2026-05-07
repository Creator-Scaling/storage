from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from typing import Any

import anthropic

from config import settings
from config.icp import ICP, REFERENCE_PROFILES

_client: anthropic.Anthropic | None = None


def _get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        _client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
    return _client


def _posts_per_month(posts: list[dict]) -> float:
    """Estimate posts per month from a list of post objects with timestamps."""
    if len(posts) < 2:
        return 0.0
    timestamps = []
    for p in posts:
        ts = p.get("timestamp") or p.get("takenAt") or p.get("date")
        if ts:
            try:
                dt = datetime.fromisoformat(str(ts).replace("Z", "+00:00"))
                timestamps.append(dt)
            except ValueError:
                pass
    if len(timestamps) < 2:
        return float(len(posts))
    timestamps.sort()
    span_days = (timestamps[-1] - timestamps[0]).days or 1
    return len(timestamps) / span_days * 30


def _avg_reel_views(posts: list[dict]) -> float:
    views = [p.get("videoViewCount") or 0 for p in posts if p.get("type") == "Video"]
    return sum(views) / len(views) if views else 0.0


def _quantitative_check(profile: dict[str, Any]) -> tuple[bool, str]:
    """Fast pre-filter before calling Claude. Returns (passes, reason)."""
    followers = profile.get("followersCount") or 0
    if followers < ICP["follower_min"]:
        return False, f"Followers {followers} below minimum {ICP['follower_min']}"
    if followers > ICP["follower_max"]:
        return False, f"Followers {followers} above maximum {ICP['follower_max']}"

    posts = profile.get("latestPosts") or []
    ppm = _posts_per_month(posts)
    if ppm < ICP["posts_per_month_min"]:
        return False, f"Posts/month ~{ppm:.1f} below minimum {ICP['posts_per_month_min']}"

    avg_views = _avg_reel_views(posts)
    if posts and avg_views < ICP["reel_views_min"] and any(p.get("type") == "Video" for p in posts):
        return False, f"Avg reel views {avg_views:.0f} below minimum {ICP['reel_views_min']}"

    return True, "Passed quantitative checks"


def _build_qualification_prompt(profile: dict[str, Any]) -> str:
    posts = profile.get("latestPosts") or []
    post_captions = "\n".join(
        f"- [{p.get('type','Post')}] {(p.get('caption') or '')[:200]}"
        for p in posts[:15]
    )

    reference_examples = ""
    if REFERENCE_PROFILES:
        reference_examples = "\n\nREFERENCE PROFILES (confirmed good fits):\n" + "\n".join(
            f"- @{r['handle']} | Niche: {r['niche']} | Why: {r['why_they_qualify']}"
            for r in REFERENCE_PROFILES
        )

    return f"""You are a lead qualification specialist for a high-ticket webinar agency.
Assess whether this Instagram profile qualifies as an ideal prospect.{reference_examples}

TARGET NICHES: {', '.join(ICP['niches'])}

QUALIFICATION CRITERIA:
1. Actively selling a programme, course, or mentorship (evidence in bio, posts, or links)
2. Content is in English
3. Genuine engagement (real comments, not bot-like)
4. Based in US, Canada, or UK (if detectable)
5. Fits one of the target niches

PROFILE DATA:
Username: @{profile.get('username')}
Full Name: {profile.get('fullName')}
Bio: {profile.get('biography', '')}
External URL: {profile.get('externalUrl', 'None')}
Followers: {profile.get('followersCount')}
Following: {profile.get('followingCount')}
Total Posts: {profile.get('postsCount')}

RECENT POST CAPTIONS (sample):
{post_captions}

Respond with a JSON object only — no markdown, no explanation outside the JSON:
{{
  "qualified": true | false,
  "niche": "exact niche name from the list or null",
  "first_name": "extracted first name or null",
  "last_name": "extracted last name or null",
  "location": "US | Canada | UK | Unknown",
  "confidence": 0-100,
  "reason": "one sentence explanation",
  "selling_evidence": "what product/offer they appear to be selling, or null"
}}"""


def qualify_profile(profile: dict[str, Any]) -> dict[str, Any]:
    """Run full qualification (quantitative + Claude) on a single profile."""
    passes, reason = _quantitative_check(profile)
    if not passes:
        return {
            "qualified": False,
            "reason": reason,
            "niche": None,
            "first_name": None,
            "last_name": None,
            "location": "Unknown",
            "confidence": 0,
            "selling_evidence": None,
        }

    prompt = _build_qualification_prompt(profile)
    client = _get_client()

    try:
        message = client.messages.create(
            model=settings.CLAUDE_MODEL,
            max_tokens=512,
            messages=[{"role": "user", "content": prompt}],
        )
        text = message.content[0].text.strip()
        json_match = re.search(r"\{.*\}", text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
    except Exception as exc:
        print(f"  Claude qualification failed for @{profile.get('username')}: {exc}")

    return {
        "qualified": False,
        "reason": "Qualification API error",
        "niche": None,
        "first_name": None,
        "last_name": None,
        "location": "Unknown",
        "confidence": 0,
        "selling_evidence": None,
    }


def qualify_batch(profiles: list[dict[str, Any]]) -> list[tuple[dict, dict]]:
    """Qualify a list of profiles. Returns list of (profile, result) tuples."""
    results = []
    for i, profile in enumerate(profiles):
        handle = profile.get("username", "?")
        print(f"  [{i+1}/{len(profiles)}] Qualifying @{handle}...")
        result = qualify_profile(profile)
        results.append((profile, result))
    return results
