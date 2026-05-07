from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from google.oauth2 import service_account
from googleapiclient.discovery import build

from config import settings

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

HEADERS = [
    "Status",           # A
    "First Name",       # B
    "Last Name",        # C
    "Email",            # D
    "Email Source",     # E
    "Instagram Handle", # F
    "Instagram URL",    # G
    "Followers",        # H
    "Posts/Month",      # I
    "Avg Reel Views",   # J
    "Location",         # K
    "Niche",            # L
    "YouTube URL",      # M
    "Selling",          # N
    "Confidence",       # O
    "Qualification Notes", # P
    "Audit Doc URL",    # Q
    "Date Added",       # R
    "Date Audited",     # S
]

STATUS_PENDING = "Pending Review"
STATUS_APPROVED = "Approved"
STATUS_REJECTED = "Rejected"
STATUS_RESEARCHING = "Researching"
STATUS_AUDITED = "Audited"

_service = None


def _get_service():
    global _service
    if _service is None:
        creds = service_account.Credentials.from_service_account_file(
            settings.GOOGLE_SERVICE_ACCOUNT_FILE,
            scopes=SCOPES,
        )
        _service = build("sheets", "v4", credentials=creds)
    return _service


def _sheet_range(tab: str, start: str = "A", end: str | None = None) -> str:
    if end:
        return f"'{tab}'!{start}:{end}"
    return f"'{tab}'!{start}"


def ensure_header_row(tab: str = settings.SHEETS_TAB_NAME) -> None:
    svc = _get_service()
    result = svc.spreadsheets().values().get(
        spreadsheetId=settings.GOOGLE_SHEETS_ID,
        range=_sheet_range(tab, "A1", "S1"),
    ).execute()
    existing = result.get("values", [[]])[0] if result.get("values") else []
    if existing != HEADERS:
        svc.spreadsheets().values().update(
            spreadsheetId=settings.GOOGLE_SHEETS_ID,
            range=_sheet_range(tab, "A1", "S1"),
            valueInputOption="RAW",
            body={"values": [HEADERS]},
        ).execute()


def append_leads(leads: list[dict[str, Any]], tab: str = settings.SHEETS_TAB_NAME) -> int:
    """Append a list of lead dicts to the sheet. Returns number of rows added."""
    if not leads:
        return 0
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    rows = []
    for lead in leads:
        rows.append([
            STATUS_PENDING,
            lead.get("first_name") or "",
            lead.get("last_name") or "",
            lead.get("email") or "",
            lead.get("email_source") or "",
            lead.get("instagram_handle") or "",
            lead.get("instagram_url") or "",
            lead.get("followers") or "",
            lead.get("posts_per_month") or "",
            lead.get("avg_reel_views") or "",
            lead.get("location") or "",
            lead.get("niche") or "",
            lead.get("youtube_url") or "",
            lead.get("selling_evidence") or "",
            lead.get("confidence") or "",
            lead.get("qualification_notes") or "",
            "",  # Audit Doc URL (empty until research phase)
            now,
            "",  # Date Audited
        ])
    svc = _get_service()
    svc.spreadsheets().values().append(
        spreadsheetId=settings.GOOGLE_SHEETS_ID,
        range=_sheet_range(tab, "A", "S"),
        valueInputOption="RAW",
        insertDataOption="INSERT_ROWS",
        body={"values": rows},
    ).execute()
    return len(rows)


def get_leads_by_status(status: str, tab: str = settings.SHEETS_TAB_NAME) -> list[dict[str, Any]]:
    """Return all leads matching the given status, with their row index (1-based)."""
    svc = _get_service()
    result = svc.spreadsheets().values().get(
        spreadsheetId=settings.GOOGLE_SHEETS_ID,
        range=_sheet_range(tab, "A", "S"),
    ).execute()
    rows = result.get("values", [])
    if not rows:
        return []

    header = rows[0]
    leads = []
    for i, row in enumerate(rows[1:], start=2):  # row 2 onwards (1-indexed, header is row 1)
        padded = row + [""] * (len(HEADERS) - len(row))
        lead = dict(zip(HEADERS, padded))
        if lead.get("Status") == status:
            lead["_row"] = i
            leads.append(lead)
    return leads


def update_lead_status(
    row: int,
    status: str,
    audit_doc_url: str | None = None,
    tab: str = settings.SHEETS_TAB_NAME,
) -> None:
    svc = _get_service()
    updates = [{"range": f"'{tab}'!A{row}", "values": [[status]]}]
    if audit_doc_url:
        updates.append({"range": f"'{tab}'!Q{row}", "values": [[audit_doc_url]]})
        now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        updates.append({"range": f"'{tab}'!S{row}", "values": [[now]]})
    svc.spreadsheets().values().batchUpdate(
        spreadsheetId=settings.GOOGLE_SHEETS_ID,
        body={"valueInputOption": "RAW", "data": updates},
    ).execute()


def update_lead_email(row: int, email: str, source: str, tab: str = settings.SHEETS_TAB_NAME) -> None:
    svc = _get_service()
    svc.spreadsheets().values().batchUpdate(
        spreadsheetId=settings.GOOGLE_SHEETS_ID,
        body={
            "valueInputOption": "RAW",
            "data": [
                {"range": f"'{tab}'!D{row}", "values": [[email]]},
                {"range": f"'{tab}'!E{row}", "values": [[source]]},
            ],
        },
    ).execute()
