from __future__ import annotations

import base64
import time

import httpx

from config import settings


def _api(method: str, path: str, **kwargs) -> dict:
    url = f"https://api.github.com{path}"
    headers = {
        "Authorization": f"token {settings.GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
    }
    for attempt in range(4):
        resp = httpx.request(method, url, headers=headers, timeout=20, **kwargs)
        if resp.status_code == 429:
            time.sleep(2 ** attempt)
            continue
        resp.raise_for_status()
        return resp.json() if resp.content else {}
    raise RuntimeError(f"GitHub API call failed after retries: {path}")


def deploy_html(handle: str, html: str) -> str:
    """
    Push an HTML file to the GitHub Pages repo and return the public URL.
    Repo must have GitHub Pages enabled on the main branch, root or /docs folder.
    """
    repo = settings.GITHUB_PAGES_REPO          # e.g. "your-org/audits"
    branch = settings.GITHUB_PAGES_BRANCH      # e.g. "main"
    path_prefix = settings.GITHUB_PAGES_PATH   # e.g. "" or "docs" (no trailing slash)

    file_path = f"{path_prefix}/{handle}.html".lstrip("/")
    api_path = f"/repos/{repo}/contents/{file_path}"

    encoded = base64.b64encode(html.encode()).decode()

    # Check if file already exists (need its SHA to update)
    sha = None
    try:
        existing = _api("GET", api_path, params={"ref": branch})
        sha = existing.get("sha")
    except httpx.HTTPStatusError as e:
        if e.response.status_code != 404:
            raise

    payload: dict = {
        "message": f"audit: {handle}",
        "content": encoded,
        "branch": branch,
    }
    if sha:
        payload["sha"] = sha

    _api("PUT", api_path, json=payload)

    # Build the public Pages URL
    org, repo_name = repo.split("/", 1)
    base_url = settings.GITHUB_PAGES_CUSTOM_DOMAIN or f"https://{org}.github.io/{repo_name}"
    return f"{base_url}/{file_path}"
