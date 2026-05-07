from __future__ import annotations

import time
from typing import Any

from apify_client import ApifyClient

from config import settings
from config.icp import NICHE_HASHTAGS

_client: ApifyClient | None = None


def _get_client() -> ApifyClient:
    global _client
    if _client is None:
        _client = ApifyClient(settings.APIFY_API_TOKEN)
    return _client


def discover_handles_by_niche(
    niches: list[str] | None = None,
    posts_per_hashtag: int = 50,
) -> list[str]:
    """Scrape hashtags for each niche and return unique Instagram handles."""
    niches = niches or list(NICHE_HASHTAGS.keys())
    hashtags: list[str] = []
    for niche in niches:
        hashtags.extend(NICHE_HASHTAGS.get(niche, []))

    print(f"  Scraping {len(hashtags)} hashtags across {len(niches)} niches...")

    run_input = {
        "hashtags": hashtags,
        "resultsLimit": posts_per_hashtag,
        "addParentData": False,
    }

    client = _get_client()
    run = client.actor(settings.APIFY_INSTAGRAM_HASHTAG_ACTOR).call(run_input=run_input)
    items = list(client.dataset(run["defaultDatasetId"]).iterate_items())

    handles: set[str] = set()
    for item in items:
        owner = item.get("ownerUsername") or item.get("owner", {}).get("username")
        if owner:
            handles.add(owner.lower())

    print(f"  Found {len(handles)} unique handles from hashtag scrape.")
    return list(handles)


def get_profile_data(handles: list[str], batch_size: int = 50) -> list[dict[str, Any]]:
    """Fetch full profile data for a list of handles using Apify profile scraper."""
    client = _get_client()
    profiles: list[dict[str, Any]] = []

    for i in range(0, len(handles), batch_size):
        batch = handles[i : i + batch_size]
        print(f"  Fetching profiles {i + 1}–{min(i + batch_size, len(handles))} of {len(handles)}...")

        run_input = {"usernames": batch}
        run = client.actor(settings.APIFY_INSTAGRAM_PROFILE_ACTOR).call(run_input=run_input)
        items = list(client.dataset(run["defaultDatasetId"]).iterate_items())
        profiles.extend(items)

        if i + batch_size < len(handles):
            time.sleep(2)

    return profiles


def get_recent_posts(handle: str, limit: int = 30) -> list[dict[str, Any]]:
    """Fetch recent posts for a single handle — used during research phase."""
    profiles = get_profile_data([handle])
    if not profiles:
        return []
    profile = profiles[0]
    return (profile.get("latestPosts") or [])[:limit]


def extract_youtube_url_from_bio(profile: dict[str, Any]) -> str | None:
    """Pull a YouTube URL from a profile's bio or external link if present."""
    fields = [
        profile.get("externalUrl", ""),
        profile.get("biography", ""),
        profile.get("bioLinks", []),
    ]
    for field in fields:
        text = field if isinstance(field, str) else " ".join(str(f) for f in field)
        if "youtube.com" in text or "youtu.be" in text:
            for token in text.split():
                if "youtube.com/channel" in token or "youtube.com/c/" in token or "youtube.com/@" in token:
                    return token.strip(".,;)")
    return None
