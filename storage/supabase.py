from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import httpx

from config import settings

STATUS_PENDING = "Pending Review"
STATUS_APPROVED = "Approved"
STATUS_REJECTED = "Rejected"
STATUS_RESEARCHING = "Researching"
STATUS_AUDITED = "Audited"

TABLE = "leads"


def _headers() -> dict:
    return {
        "apikey": settings.SUPABASE_SERVICE_KEY,
        "Authorization": f"Bearer {settings.SUPABASE_SERVICE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation",
    }


def _url(path: str = "") -> str:
    return f"{settings.SUPABASE_URL}/rest/v1/{TABLE}{path}"


def append_leads(leads: list[dict[str, Any]]) -> int:
    if not leads:
        return 0
    now = datetime.now(timezone.utc).isoformat()
    rows = []
    for lead in leads:
        rows.append({
            "status": STATUS_PENDING,
            "first_name": lead.get("first_name") or "",
            "last_name": lead.get("last_name") or "",
            "email": lead.get("email") or "",
            "email_source": lead.get("email_source") or "",
            "instagram_handle": lead.get("instagram_handle") or "",
            "instagram_url": lead.get("instagram_url") or "",
            "followers": lead.get("followers"),
            "posts_per_month": lead.get("posts_per_month"),
            "avg_reel_views": lead.get("avg_reel_views"),
            "location": lead.get("location") or "",
            "niche": lead.get("niche") or "",
            "youtube_url": lead.get("youtube_url") or "",
            "selling_evidence": lead.get("selling_evidence") or "",
            "confidence": lead.get("confidence"),
            "qualification_notes": lead.get("qualification_notes") or "",
            "audit_url": "",
            "created_at": now,
            "audited_at": None,
        })

    resp = httpx.post(_url(), json=rows, headers=_headers(), timeout=20)
    resp.raise_for_status()
    return len(rows)


def get_leads_by_status(status: str) -> list[dict[str, Any]]:
    resp = httpx.get(
        _url(),
        params={"status": f"eq.{status}", "order": "created_at.asc"},
        headers=_headers(),
        timeout=20,
    )
    resp.raise_for_status()
    return resp.json()


def update_lead_status(
    lead_id: int,
    status: str,
    audit_url: str | None = None,
) -> None:
    payload: dict[str, Any] = {"status": status}
    if audit_url:
        payload["audit_url"] = audit_url
        payload["audited_at"] = datetime.now(timezone.utc).isoformat()

    resp = httpx.patch(
        _url(f"?id=eq.{lead_id}"),
        json=payload,
        headers=_headers(),
        timeout=20,
    )
    resp.raise_for_status()


def update_lead_email(lead_id: int, email: str, source: str) -> None:
    resp = httpx.patch(
        _url(f"?id=eq.{lead_id}"),
        json={"email": email, "email_source": source},
        headers=_headers(),
        timeout=20,
    )
    resp.raise_for_status()


def get_status_counts() -> dict[str, int]:
    resp = httpx.get(
        f"{settings.SUPABASE_URL}/rest/v1/{TABLE}?select=status",
        headers=_headers(),
        timeout=20,
    )
    resp.raise_for_status()
    counts: dict[str, int] = {}
    for row in resp.json():
        s = row.get("status", "Unknown")
        counts[s] = counts.get(s, 0) + 1
    return counts
