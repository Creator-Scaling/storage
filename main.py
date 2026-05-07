#!/usr/bin/env python3
"""
Lead Generation & Audit Pipeline
=================================
Commands:
  discover  — Scrape Instagram/YouTube leads, qualify with Claude, write to Sheets
  enrich    — Find emails for leads in Sheets that are missing one
  research  — Process "Approved" leads: deep research + Claude audit + Google Doc
  status    — Print a quick count of leads by status
"""
from __future__ import annotations

import click

from config.icp import NICHE_HASHTAGS


@click.group()
def cli():
    pass


@cli.command()
@click.option("--niches", "-n", multiple=True, help="Specific niche(s) to scrape. Defaults to all.")
@click.option("--posts-per-hashtag", default=50, show_default=True, help="Posts to pull per hashtag.")
@click.option("--limit", default=0, help="Cap total profiles before qualification (0 = no cap).")
@click.option("--dry-run", is_flag=True, help="Qualify and print results without writing to Sheets.")
def discover(niches, posts_per_hashtag, limit, dry_run):
    """Discover and qualify leads from Instagram, write qualified ones to Sheets."""
    from scrapers.instagram import discover_handles_by_niche, get_profile_data, extract_youtube_url_from_bio
    from qualification.qualifier import qualify_batch
    from enrichment.apollo import extract_bio_email, find_email
    from storage import sheets

    selected_niches = list(niches) if niches else list(NICHE_HASHTAGS.keys())
    click.echo(f"\n[1/4] Discovering handles for niches: {', '.join(selected_niches)}")
    handles = discover_handles_by_niche(selected_niches, posts_per_hashtag=posts_per_hashtag)

    if limit and len(handles) > limit:
        handles = handles[:limit]
        click.echo(f"  Capped to {limit} handles.")

    click.echo(f"\n[2/4] Fetching full profile data for {len(handles)} handles...")
    profiles = get_profile_data(handles)
    click.echo(f"  Retrieved {len(profiles)} profiles.")

    click.echo(f"\n[3/4] Qualifying {len(profiles)} profiles...")
    results = qualify_batch(profiles)

    qualified = [(p, r) for p, r in results if r.get("qualified")]
    click.echo(f"  Qualified: {len(qualified)} / {len(profiles)}")

    if not qualified:
        click.echo("No qualified leads found. Try different niches or hashtags.")
        return

    if dry_run:
        click.echo("\n[DRY RUN] Qualified leads:")
        for profile, result in qualified:
            click.echo(f"  @{profile.get('username')} | {result.get('niche')} | {result.get('confidence')}% | {result.get('reason')}")
        return

    click.echo(f"\n[4/4] Enriching and writing {len(qualified)} leads to Sheets...")
    sheets.ensure_header_row()

    lead_rows = []
    for profile, result in qualified:
        posts = profile.get("latestPosts") or []

        # Attempt bio-level email first
        email = extract_bio_email(profile)
        email_source = "bio" if email else ""

        if not email:
            fn = result.get("first_name") or ""
            ln = result.get("last_name") or ""
            if fn or ln:
                email, email_source = find_email(fn, ln, instagram_handle=profile.get("username"))

        from qualification.qualifier import _posts_per_month, _avg_reel_views
        ppm = round(_posts_per_month(posts), 1)
        avg_views = round(_avg_reel_views(posts))

        youtube_url = extract_youtube_url_from_bio(profile)

        lead_rows.append({
            "first_name": result.get("first_name") or "",
            "last_name": result.get("last_name") or "",
            "email": email or "",
            "email_source": email_source,
            "instagram_handle": profile.get("username", ""),
            "instagram_url": f"https://instagram.com/{profile.get('username', '')}",
            "followers": profile.get("followersCount"),
            "posts_per_month": ppm,
            "avg_reel_views": avg_views,
            "location": result.get("location", "Unknown"),
            "niche": result.get("niche", ""),
            "youtube_url": youtube_url or "",
            "selling_evidence": result.get("selling_evidence", ""),
            "confidence": result.get("confidence", 0),
            "qualification_notes": result.get("reason", ""),
        })

    added = sheets.append_leads(lead_rows)
    click.echo(f"  Written {added} leads to Google Sheets.")
    click.echo("\nDone. Open your Sheet, review leads, and mark approved ones as 'Approved' to trigger research.")


@cli.command()
def enrich():
    """Find and fill in missing emails for leads in Sheets."""
    from storage import sheets
    from enrichment.apollo import find_email

    click.echo("\nFetching leads missing emails...")
    leads = sheets.get_leads_by_status(sheets.STATUS_PENDING)
    missing = [l for l in leads if not l.get("Email")]
    click.echo(f"  {len(missing)} leads need email enrichment.")

    for i, lead in enumerate(missing):
        fn = lead.get("First Name", "")
        ln = lead.get("Last Name", "")
        handle = lead.get("Instagram Handle", "")
        click.echo(f"  [{i+1}/{len(missing)}] {fn} {ln} (@{handle})...")

        if not fn and not ln:
            click.echo("    Skipped — no name data.")
            continue

        email, source = find_email(fn, ln, instagram_handle=handle)
        if email:
            sheets.update_lead_email(lead["_row"], email, source)
            click.echo(f"    Found: {email} ({source})")
        else:
            click.echo("    Not found.")

    click.echo("\nEnrichment complete.")


@cli.command()
@click.option("--limit", default=0, help="Max number of approved leads to process (0 = all).")
def research(limit):
    """Run deep research + generate audit Google Docs for Approved leads."""
    from storage import sheets
    from research.researcher import research_lead
    from audit.generator import generate_audit_doc

    approved = sheets.get_leads_by_status(sheets.STATUS_APPROVED)
    if not approved:
        click.echo("No leads with status 'Approved' found.")
        return

    if limit:
        approved = approved[:limit]

    click.echo(f"\nProcessing {len(approved)} approved lead(s)...\n")

    for i, lead in enumerate(approved):
        name = f"{lead.get('First Name', '')} {lead.get('Last Name', '')}".strip() or lead.get("Instagram Handle", "?")
        click.echo(f"[{i+1}/{len(approved)}] {name} (@{lead.get('Instagram Handle')})")

        # Mark as researching so it won't be double-processed
        sheets.update_lead_status(lead["_row"], sheets.STATUS_RESEARCHING)

        try:
            research_data = research_lead(lead)
            doc_url = generate_audit_doc(research_data)
            sheets.update_lead_status(lead["_row"], sheets.STATUS_AUDITED, audit_doc_url=doc_url)
            click.echo(f"  Audit doc: {doc_url}\n")
        except Exception as exc:
            click.echo(f"  ERROR: {exc}")
            # Revert to Approved so it can be retried
            sheets.update_lead_status(lead["_row"], sheets.STATUS_APPROVED)

    click.echo("Research phase complete.")


@cli.command()
def status():
    """Print a summary of lead counts by status in Sheets."""
    from storage import sheets
    from googleapiclient.discovery import build
    from google.oauth2 import service_account
    from config import settings

    svc_creds = service_account.Credentials.from_service_account_file(
        settings.GOOGLE_SERVICE_ACCOUNT_FILE,
        scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"],
    )
    svc = build("sheets", "v4", credentials=svc_creds)
    result = svc.spreadsheets().values().get(
        spreadsheetId=settings.GOOGLE_SHEETS_ID,
        range=f"'{settings.SHEETS_TAB_NAME}'!A:A",
    ).execute()

    rows = result.get("values", [])
    counts: dict[str, int] = {}
    for row in rows[1:]:
        val = row[0] if row else "Unknown"
        counts[val] = counts.get(val, 0) + 1

    total = sum(counts.values())
    click.echo(f"\nLead pipeline — {total} total\n")
    for status_name, count in sorted(counts.items()):
        click.echo(f"  {status_name:<20} {count}")
    click.echo()


if __name__ == "__main__":
    cli()
