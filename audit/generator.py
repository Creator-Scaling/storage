from __future__ import annotations

import re
from typing import Any

import anthropic

from audit.html_template import render
from audit.github_pages import deploy_html
from config import settings
from config.icp import HIGH_TICKET_WEBINAR_STRATEGY

_anthropic_client: anthropic.Anthropic | None = None


def _get_anthropic() -> anthropic.Anthropic:
    global _anthropic_client
    if _anthropic_client is None:
        _anthropic_client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
    return _anthropic_client


def _build_audit_prompt(research: dict[str, Any]) -> str:
    posts_text = "\n".join(
        f"  [{p['type']}] Views: {p.get('views') or 'N/A'} | Likes: {p.get('likes')} | "
        f"Comments: {p.get('comments')} | Caption: {p.get('caption', '')[:150]}"
        for p in research.get("recent_posts", [])[:20]
    )

    yt_section = ""
    yt = research.get("youtube")
    if yt:
        yt_videos = "\n".join(
            f"  - {v.get('title')} ({v.get('views', 'N/A')} views)"
            for v in (yt.get("videos") or [])[:10]
        )
        yt_section = f"""
YOUTUBE CHANNEL:
Name: {yt.get('channel_name')}
Subscribers: {yt.get('subscribers')}
Description: {yt.get('description', '')[:500]}
Recent Videos:
{yt_videos}
"""

    return f"""You are a senior content strategist and webinar funnel consultant.
Write a detailed, personalised prospect audit for the following creator.
Your audit will be used internally — be direct, specific, and commercially sharp.

HIGH TICKET WEBINAR STRATEGY CONTEXT:
{HIGH_TICKET_WEBINAR_STRATEGY}

PROSPECT:
Name: {research.get('full_name')}
Instagram: @{research.get('handle')}
Followers: {research.get('followers')}
Niche: {research.get('niche')}
Bio: {research.get('bio')}
Offer (known): {research.get('selling_evidence')}
Link-in-bio page content: {research.get('linkinbio_text', '')[:800]}
{yt_section}
RECENT INSTAGRAM POSTS (most recent first):
{posts_text}

Write the audit using EXACTLY this structure (use these exact section headings):

PROFILE OVERVIEW
2-3 sentences summarising who they are, their audience, and their current offer.

WHAT THEY'RE DOING WELL
5 specific bullet points about their content strategy, engagement, or positioning that are working.

CONTENT GAPS & IMPROVEMENT OPPORTUNITIES
5 specific bullet points on what's missing, inconsistent, or underperforming.

ENGAGEMENT ANALYSIS
Analyse their engagement quality — are followers responding? What content performs best and why?

WHY A HIGH TICKET WEBINAR STRATEGY WOULD WORK FOR THEM
3-5 paragraphs tying their specific situation to the webinar strategy. Be concrete — reference their niche, audience size, current offer type, and content style.

PERSONALISED OUTREACH TALKING POINTS
5 punchy bullet points that can be used as talking points in a short personalised video message to this prospect. Each should feel like you've actually looked at their account.

Keep the tone professional but conversational. No generic filler. Every point should be specific to this prospect."""


def generate_audit_text(research: dict[str, Any]) -> str:
    client = _get_anthropic()
    message = client.messages.create(
        model=settings.CLAUDE_MODEL,
        max_tokens=4096,
        messages=[{"role": "user", "content": _build_audit_prompt(research)}],
    )
    return message.content[0].text.strip()


def generate_audit_page(research: dict[str, Any]) -> str:
    """Generate audit text → render HTML → push to GitHub Pages → return URL."""
    handle = research.get("handle", "lead")
    print(f"  Generating audit copy for @{handle}...")
    audit_text = generate_audit_text(research)

    print(f"  Rendering HTML page...")
    html = render(research, audit_text)

    print(f"  Deploying to GitHub Pages...")
    url = deploy_html(handle, html)

    return url
