from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from typing import Any

import anthropic
from google.oauth2 import service_account
from googleapiclient.discovery import build

from config import settings
from config.icp import HIGH_TICKET_WEBINAR_STRATEGY

_anthropic_client: anthropic.Anthropic | None = None
_docs_service = None
_drive_service = None

SCOPES = [
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/drive",
]


def _get_anthropic() -> anthropic.Anthropic:
    global _anthropic_client
    if _anthropic_client is None:
        _anthropic_client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
    return _anthropic_client


def _get_docs():
    global _docs_service
    if _docs_service is None:
        creds = service_account.Credentials.from_service_account_file(
            settings.GOOGLE_SERVICE_ACCOUNT_FILE, scopes=SCOPES
        )
        _docs_service = build("docs", "v1", credentials=creds)
    return _docs_service


def _get_drive():
    global _drive_service
    if _drive_service is None:
        creds = service_account.Credentials.from_service_account_file(
            settings.GOOGLE_SERVICE_ACCOUNT_FILE, scopes=SCOPES
        )
        _drive_service = build("drive", "v3", credentials=creds)
    return _drive_service


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
    """Call Claude to generate the audit copy."""
    client = _get_anthropic()
    prompt = _build_audit_prompt(research)
    message = client.messages.create(
        model=settings.CLAUDE_MODEL,
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text.strip()


def _audit_to_doc_requests(title: str, audit_text: str, research: dict) -> list[dict]:
    """Convert audit plain text into Google Docs API batchUpdate requests."""
    requests_list = []
    index = 1  # Docs API uses 1-based insertion index

    SECTION_HEADINGS = [
        "PROFILE OVERVIEW",
        "WHAT THEY'RE DOING WELL",
        "CONTENT GAPS & IMPROVEMENT OPPORTUNITIES",
        "ENGAGEMENT ANALYSIS",
        "WHY A HIGH TICKET WEBINAR STRATEGY WOULD WORK FOR THEM",
        "PERSONALISED OUTREACH TALKING POINTS",
    ]

    lines = audit_text.split("\n")
    elements: list[tuple[str, str]] = []  # (style, text)

    # Title block
    date_str = datetime.now(timezone.utc).strftime("%d %B %Y")
    elements.append(("title", f"{research.get('full_name', '')} — Content Audit\n"))
    elements.append(("subtitle", f"@{research.get('handle')} | {research.get('niche')} | Generated {date_str}\n"))
    elements.append(("normal", "\n"))

    for line in lines:
        stripped = line.strip()
        if not stripped:
            elements.append(("normal", "\n"))
        elif stripped.upper() in [h.upper() for h in SECTION_HEADINGS]:
            elements.append(("heading1", stripped + "\n"))
        elif stripped.startswith("- ") or stripped.startswith("• "):
            elements.append(("bullet", stripped[2:] + "\n"))
        else:
            elements.append(("normal", stripped + "\n"))

    # Build insert requests
    for style, text in elements:
        requests_list.append({
            "insertText": {"location": {"index": index}, "text": text}
        })
        text_len = len(text)

        if style == "title":
            requests_list.append({
                "updateParagraphStyle": {
                    "range": {"startIndex": index, "endIndex": index + text_len},
                    "paragraphStyle": {"namedStyleType": "TITLE"},
                    "fields": "namedStyleType",
                }
            })
        elif style == "subtitle":
            requests_list.append({
                "updateParagraphStyle": {
                    "range": {"startIndex": index, "endIndex": index + text_len},
                    "paragraphStyle": {"namedStyleType": "SUBTITLE"},
                    "fields": "namedStyleType",
                }
            })
        elif style == "heading1":
            requests_list.append({
                "updateParagraphStyle": {
                    "range": {"startIndex": index, "endIndex": index + text_len},
                    "paragraphStyle": {"namedStyleType": "HEADING_1"},
                    "fields": "namedStyleType",
                }
            })
        elif style == "bullet":
            requests_list.append({
                "createParagraphBullets": {
                    "range": {"startIndex": index, "endIndex": index + text_len},
                    "bulletPreset": "BULLET_DISC_CIRCLE_SQUARE",
                }
            })

        index += text_len

    return requests_list


def create_google_doc(research: dict[str, Any], audit_text: str) -> str:
    """Create a formatted Google Doc with the audit. Returns the doc URL."""
    docs = _get_docs()
    drive = _get_drive()

    name = research.get("full_name") or research.get("handle", "Lead")
    doc_title = f"{name} — Content Audit"

    # Create blank doc
    doc = docs.documents().create(body={"title": doc_title}).execute()
    doc_id = doc["documentId"]

    # Move to designated folder if configured
    if settings.GOOGLE_DRIVE_FOLDER_ID:
        file = drive.files().get(fileId=doc_id, fields="parents").execute()
        previous_parents = ",".join(file.get("parents", []))
        drive.files().update(
            fileId=doc_id,
            addParents=settings.GOOGLE_DRIVE_FOLDER_ID,
            removeParents=previous_parents,
            fields="id, parents",
        ).execute()

    # Write content
    batch_requests = _audit_to_doc_requests(doc_title, audit_text, research)
    if batch_requests:
        docs.documents().batchUpdate(
            documentId=doc_id,
            body={"requests": batch_requests},
        ).execute()

    return f"https://docs.google.com/document/d/{doc_id}/edit"


def generate_audit_doc(research: dict[str, Any]) -> str:
    """Full pipeline: generate audit text → create Google Doc → return URL."""
    print(f"  Generating audit for {research.get('full_name') or research.get('handle')}...")
    audit_text = generate_audit_text(research)
    print(f"  Creating Google Doc...")
    url = create_google_doc(research, audit_text)
    return url
