from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any


def _parse_sections(audit_text: str) -> dict[str, list[str]]:
    """Split Claude's audit output into named sections."""
    section_headings = [
        "PROFILE OVERVIEW",
        "WHAT THEY'RE DOING WELL",
        "CONTENT GAPS & IMPROVEMENT OPPORTUNITIES",
        "ENGAGEMENT ANALYSIS",
        "WHY A HIGH TICKET WEBINAR STRATEGY WOULD WORK FOR THEM",
        "PERSONALISED OUTREACH TALKING POINTS",
    ]
    sections: dict[str, list[str]] = {}
    current_heading = None
    current_lines: list[str] = []

    for line in audit_text.split("\n"):
        stripped = line.strip()
        matched_heading = next(
            (h for h in section_headings if stripped.upper() == h.upper()), None
        )
        if matched_heading:
            if current_heading:
                sections[current_heading] = current_lines
            current_heading = matched_heading
            current_lines = []
        elif current_heading and stripped:
            current_lines.append(stripped)

    if current_heading:
        sections[current_heading] = current_lines

    return sections


def _lines_to_html(lines: list[str]) -> str:
    html_parts = []
    for line in lines:
        if line.startswith("- ") or line.startswith("• "):
            html_parts.append(f"<li>{line[2:]}</li>")
        else:
            html_parts.append(f"<p>{line}</p>")

    # Wrap consecutive <li> in <ul>
    result = "\n".join(html_parts)
    result = re.sub(r"((?:<li>.*?</li>\n?)+)", r"<ul>\1</ul>", result)
    return result


SECTION_CONFIG = {
    "PROFILE OVERVIEW": {
        "icon": "👤",
        "label": "Profile Overview",
        "accent": "#6366f1",
        "bg": "#eef2ff",
    },
    "WHAT THEY'RE DOING WELL": {
        "icon": "✅",
        "label": "What They're Doing Well",
        "accent": "#16a34a",
        "bg": "#f0fdf4",
    },
    "CONTENT GAPS & IMPROVEMENT OPPORTUNITIES": {
        "icon": "⚡",
        "label": "Content Gaps & Improvement Opportunities",
        "accent": "#d97706",
        "bg": "#fffbeb",
    },
    "ENGAGEMENT ANALYSIS": {
        "icon": "📊",
        "label": "Engagement Analysis",
        "accent": "#0891b2",
        "bg": "#ecfeff",
    },
    "WHY A HIGH TICKET WEBINAR STRATEGY WOULD WORK FOR THEM": {
        "icon": "🎯",
        "label": "Why a High Ticket Webinar Strategy Would Work",
        "accent": "#7c3aed",
        "bg": "#f5f3ff",
    },
    "PERSONALISED OUTREACH TALKING POINTS": {
        "icon": "💬",
        "label": "Personalised Outreach Talking Points",
        "accent": "#be185d",
        "bg": "#fdf2f8",
    },
}


def render(research: dict[str, Any], audit_text: str) -> str:
    sections = _parse_sections(audit_text)
    handle = research.get("handle", "")
    full_name = research.get("full_name") or f"@{handle}"
    niche = research.get("niche", "")
    followers = research.get("followers")
    followers_str = f"{int(followers):,}" if followers else "—"
    profile_pic = research.get("profile_pic_url", "")
    instagram_url = f"https://instagram.com/{handle}"
    youtube_url = (research.get("youtube") or {}).get("channel_url", "")
    date_str = datetime.now(timezone.utc).strftime("%d %B %Y")

    avatar_html = (
        f'<img src="{profile_pic}" alt="{full_name}" class="avatar">'
        if profile_pic
        else f'<div class="avatar avatar-fallback">{(full_name[0] or "?").upper()}</div>'
    )

    yt_badge = (
        f'<a href="{youtube_url}" target="_blank" class="badge badge-yt">▶ YouTube</a>'
        if youtube_url
        else ""
    )

    sections_html = ""
    for key in SECTION_CONFIG:
        cfg = SECTION_CONFIG[key]
        content = sections.get(key)
        if not content:
            continue
        body = _lines_to_html(content)
        sections_html += f"""
        <section class="card" style="--accent:{cfg['accent']};--bg:{cfg['bg']};">
            <h2><span class="icon">{cfg['icon']}</span>{cfg['label']}</h2>
            <div class="card-body">{body}</div>
        </section>"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{full_name} — Audit</title>
<style>
  :root {{
    --radius: 14px;
    --shadow: 0 2px 16px rgba(0,0,0,.07);
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ background: #f8f9fb; color: #1a1a2e; }}

  header {{
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
    color: #fff;
    padding: 48px 24px 40px;
    text-align: center;
  }}
  .avatar {{
    width: 96px; height: 96px;
    border-radius: 50%;
    border: 3px solid rgba(255,255,255,.3);
    object-fit: cover;
    margin-bottom: 16px;
    display: block;
    margin-left: auto;
    margin-right: auto;
  }}
  .avatar-fallback {{
    width: 96px; height: 96px;
    border-radius: 50%;
    background: #6366f1;
    display: flex; align-items: center; justify-content: center;
    font-size: 40px; font-weight: 700; color: #fff;
    margin: 0 auto 16px;
  }}
  header h1 {{ font-size: 1.6rem; font-weight: 700; }}
  .handle {{ opacity: .65; font-size: .95rem; margin-top: 4px; }}
  .meta {{
    display: flex; gap: 10px; justify-content: center;
    flex-wrap: wrap; margin-top: 18px;
  }}
  .badge {{
    display: inline-block; padding: 5px 14px;
    border-radius: 999px; font-size: .8rem; font-weight: 600;
    text-decoration: none;
    background: rgba(255,255,255,.15); color: #fff;
  }}
  .badge-yt {{ background: rgba(255,70,70,.25); }}
  .badge:hover {{ opacity: .85; }}

  .generated {{
    text-align: center; font-size: .75rem;
    color: #9ca3af; padding: 10px 0 0;
  }}

  main {{
    max-width: 780px; margin: 32px auto; padding: 0 16px 64px;
    display: flex; flex-direction: column; gap: 20px;
  }}

  .card {{
    background: var(--bg, #fff);
    border-radius: var(--radius);
    border-left: 4px solid var(--accent, #6366f1);
    box-shadow: var(--shadow);
    overflow: hidden;
  }}
  .card h2 {{
    display: flex; align-items: center; gap: 10px;
    font-size: 1rem; font-weight: 700;
    color: var(--accent);
    padding: 16px 20px;
    border-bottom: 1px solid rgba(0,0,0,.06);
  }}
  .icon {{ font-size: 1.1rem; }}
  .card-body {{
    padding: 16px 20px;
    line-height: 1.65;
    font-size: .93rem;
  }}
  .card-body p {{ margin-bottom: 10px; }}
  .card-body p:last-child {{ margin-bottom: 0; }}
  .card-body ul {{ padding-left: 20px; }}
  .card-body li {{ margin-bottom: 8px; }}

  @media (max-width: 600px) {{
    header {{ padding: 36px 16px 28px; }}
    header h1 {{ font-size: 1.3rem; }}
    main {{ margin: 20px auto; }}
  }}
</style>
</head>
<body>

<header>
  {avatar_html}
  <h1>{full_name}</h1>
  <div class="handle">@{handle}</div>
  <div class="meta">
    <span class="badge">{niche}</span>
    <span class="badge">👥 {followers_str} followers</span>
    <a href="{instagram_url}" target="_blank" class="badge">📸 Instagram</a>
    {yt_badge}
  </div>
  <p class="generated">Audit generated {date_str}</p>
</header>

<main>
{sections_html}
</main>

</body>
</html>"""
