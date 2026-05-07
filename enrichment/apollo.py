from __future__ import annotations

import time

import httpx

from config import settings
from config.icp import ICP

APOLLO_BASE = "https://api.apollo.io/v1"


def _is_generic_email(email: str) -> bool:
    prefix = email.split("@")[0].lower()
    return prefix in ICP["disqualify_email_prefixes"]


def find_email(
    first_name: str,
    last_name: str,
    instagram_handle: str | None = None,
    full_name: str | None = None,
    retries: int = 3,
) -> tuple[str | None, str]:
    """
    Search Apollo.io for a verified personal email.
    Returns (email, source) where source describes how it was found.
    """
    if not settings.APOLLO_API_KEY:
        return None, "no_api_key"

    headers = {
        "Content-Type": "application/json",
        "Cache-Control": "no-cache",
        "X-Api-Key": settings.APOLLO_API_KEY,
    }

    # Try people/match first (most accurate)
    payload: dict = {"first_name": first_name, "last_name": last_name}
    if instagram_handle:
        payload["organization_name"] = instagram_handle  # loose signal

    for attempt in range(retries):
        try:
            resp = httpx.post(
                f"{APOLLO_BASE}/people/match",
                json=payload,
                headers=headers,
                timeout=20,
            )
            if resp.status_code == 429:
                time.sleep(2 ** attempt)
                continue
            resp.raise_for_status()
            data = resp.json()
            person = data.get("person") or {}
            email = person.get("email")
            if email and not _is_generic_email(email):
                return email, "apollo_match"
            break
        except Exception as exc:
            if attempt < retries - 1:
                time.sleep(2 ** attempt)
            else:
                print(f"  Apollo match failed for {first_name} {last_name}: {exc}")

    # Fall back to people/search
    search_name = full_name or f"{first_name} {last_name}"
    search_payload = {
        "q_keywords": search_name,
        "page": 1,
        "per_page": 5,
    }

    for attempt in range(retries):
        try:
            resp = httpx.post(
                f"{APOLLO_BASE}/people/search",
                json=search_payload,
                headers=headers,
                timeout=20,
            )
            if resp.status_code == 429:
                time.sleep(2 ** attempt)
                continue
            resp.raise_for_status()
            data = resp.json()
            people = data.get("people") or []
            for person in people:
                email = person.get("email")
                if email and not _is_generic_email(email):
                    return email, "apollo_search"
            break
        except Exception as exc:
            if attempt < retries - 1:
                time.sleep(2 ** attempt)
            else:
                print(f"  Apollo search failed for {search_name}: {exc}")

    return None, "not_found"


def extract_bio_email(profile: dict) -> str | None:
    """Pull email directly from Apify profile data if Apollo returned one, or bio."""
    business_email = profile.get("businessEmail")
    if business_email and not _is_generic_email(business_email):
        return business_email

    bio = profile.get("biography") or ""
    import re
    matches = re.findall(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}", bio)
    for email in matches:
        if not _is_generic_email(email):
            return email

    return None
