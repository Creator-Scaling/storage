from __future__ import annotations

from typing import Any

import requests
from bs4 import BeautifulSoup

from scrapers.instagram import get_profile_data, get_recent_posts
from scrapers.youtube import get_channel_data


def _fetch_linkinbio(url: str) -> str:
    """Fetch text content from a link-in-bio page (Linktree, Beacons, etc.)."""
    if not url:
        return ""
    try:
        resp = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(resp.text, "html.parser")
        # Remove scripts and styles
        for tag in soup(["script", "style", "nav", "footer"]):
            tag.decompose()
        text = soup.get_text(separator=" ", strip=True)
        return text[:3000]
    except Exception:
        return ""


def research_lead(lead: dict[str, Any]) -> dict[str, Any]:
    """
    Gather all available content for a lead to inform the audit.
    lead dict uses Google Sheets column names.
    """
    handle = lead.get("Instagram Handle", "").lstrip("@")
    youtube_url = lead.get("YouTube URL", "")

    print(f"  Fetching Instagram data for @{handle}...")
    profiles = get_profile_data([handle]) if handle else []
    profile = profiles[0] if profiles else {}

    posts = get_recent_posts(handle, limit=30) if handle else []

    linkinbio_text = ""
    external_url = profile.get("externalUrl", "")
    if external_url:
        print(f"  Fetching link-in-bio: {external_url}")
        linkinbio_text = _fetch_linkinbio(external_url)

    youtube_data: dict | None = None
    if youtube_url:
        print(f"  Fetching YouTube channel: {youtube_url}")
        youtube_data = get_channel_data(youtube_url)

    post_summaries = []
    for p in posts[:25]:
        caption = (p.get("caption") or "")[:300]
        post_summaries.append({
            "type": p.get("type", "Post"),
            "caption": caption,
            "likes": p.get("likesCount"),
            "comments": p.get("commentsCount"),
            "views": p.get("videoViewCount"),
            "timestamp": p.get("timestamp"),
        })

    yt_video_summaries = []
    if youtube_data:
        for v in (youtube_data.get("videos") or [])[:15]:
            yt_video_summaries.append({
                "title": v.get("title"),
                "views": v.get("views"),
                "description_snippet": (v.get("description") or "")[:200],
            })

    return {
        "handle": handle,
        "full_name": f"{lead.get('First Name', '')} {lead.get('Last Name', '')}".strip(),
        "bio": profile.get("biography", ""),
        "external_url": external_url,
        "followers": profile.get("followersCount"),
        "niche": lead.get("Niche", ""),
        "selling_evidence": lead.get("Selling", ""),
        "linkinbio_text": linkinbio_text,
        "recent_posts": post_summaries,
        "youtube": {
            "channel_name": youtube_data.get("channel_name") if youtube_data else None,
            "subscribers": youtube_data.get("subscriber_count") if youtube_data else None,
            "description": youtube_data.get("description") if youtube_data else None,
            "videos": yt_video_summaries,
        } if youtube_data else None,
    }
