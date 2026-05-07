from __future__ import annotations

import time
from typing import Any

from apify_client import ApifyClient

from config import settings
from config.icp import NICHE_HASHTAGS, PLATFORM_HANDLES, BIO_KEYWORDS

_client: ApifyClient | None = None


def _get_client() -> ApifyClient:
    global _client
    if _client is None:
        _client = ApifyClient(settings.APIFY_API_TOKEN)
    return _client


def discover_handles_by_hashtag(
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


def discover_handles_by_keyword(
    keywords: list[str] | None = None,
    results_per_keyword: int = 30,
) -> list[str]:
    """Search Instagram by bio/username keywords and return unique handles."""
    keywords = keywords or BIO_KEYWORDS
    client = _get_client()
    handles: set[str] = set()

    print(f"  Searching Instagram for {len(keywords)} keywords...")

    for keyword in keywords:
        run_input = {
            "searchQueries": [keyword],
            "searchType": "user",
            "maxResults": results_per_keyword,
        }
        try:
            run = client.actor("apify/instagram-search-scraper").call(run_input=run_input)
            items = list(client.dataset(run["defaultDatasetId"]).iterate_items())
            for item in items:
                username = item.get("username") or item.get("ownerUsername")
                if username:
                    handles.add(username.lower())
            print(f"    '{keyword}' → {len(items)} accounts")
        except Exception as exc:
            print(f"    '{keyword}' failed: {exc}")
        time.sleep(1)

    print(f"  Found {len(handles)} unique handles from keyword search.")
    return list(handles)


def discover_handles_from_platform_followers(
    platform_handles: list[str] | None = None,
    limit_per_account: int = 300,
) -> list[str]:
    """Scrape followers of platform/tool accounts (Kajabi, Skool, etc.)."""
    platform_handles = platform_handles or PLATFORM_HANDLES
    client = _get_client()
    handles: set[str] = set()

    print(f"  Scraping followers of {len(platform_handles)} platform accounts...")

    for handle in platform_handles:
        print(f"    @{handle}...")
        run_input = {
            "username": [handle],
            "maxItems": limit_per_account,
        }
        try:
            run = client.actor("apify/instagram-follower-scraper").call(run_input=run_input)
            items = list(client.dataset(run["defaultDatasetId"]).iterate_items())
            count = 0
            for item in items:
                username = item.get("username")
                if username:
                    handles.add(username.lower())
                    count += 1
            print(f"      → {count} followers")
        except Exception as exc:
            print(f"      Failed: {exc}")
        time.sleep(2)

    print(f"  Found {len(handles)} unique handles from platform followers.")
    return list(handles)


def discover_handles_from_lookalikes(
    reference_handles: list[str],
    limit_per_handle: int = 20,
) -> list[str]:
    """Find suggested/similar accounts based on reference profiles."""
    client = _get_client()
    profiles = get_profile_data(reference_handles)
    handles: set[str] = set()

    for profile in profiles:
        related = profile.get("relatedProfiles") or profile.get("suggestedAccounts") or []
        for acc in related[:limit_per_handle]:
            username = acc.get("username")
            if username:
                handles.add(username.lower())

    print(f"  Found {len(handles)} lookalike handles from reference profiles.")
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
