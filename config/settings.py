import os
from dotenv import load_dotenv

load_dotenv()


def _require(key: str) -> str:
    val = os.environ.get(key)
    if not val:
        raise EnvironmentError(f"Missing required environment variable: {key}")
    return val


ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
APIFY_API_TOKEN = os.environ.get("APIFY_API_TOKEN", "")
APOLLO_API_KEY = os.environ.get("APOLLO_API_KEY", "")
GOOGLE_SERVICE_ACCOUNT_FILE = os.environ.get("GOOGLE_SERVICE_ACCOUNT_FILE", "service_account.json")
GOOGLE_SHEETS_ID = os.environ.get("GOOGLE_SHEETS_ID", "")

# GitHub Pages — for hosting audit HTML pages
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
GITHUB_PAGES_REPO = os.environ.get("GITHUB_PAGES_REPO", "")          # e.g. your-org/audits
GITHUB_PAGES_BRANCH = os.environ.get("GITHUB_PAGES_BRANCH", "main")
GITHUB_PAGES_PATH = os.environ.get("GITHUB_PAGES_PATH", "")          # subfolder, leave blank for root
GITHUB_PAGES_CUSTOM_DOMAIN = os.environ.get("GITHUB_PAGES_CUSTOM_DOMAIN", "")  # e.g. https://audits.yourdomain.com

CLAUDE_MODEL = "claude-sonnet-4-6"

# Apify actor IDs
APIFY_INSTAGRAM_HASHTAG_ACTOR = "apify/instagram-hashtag-scraper"
APIFY_INSTAGRAM_PROFILE_ACTOR = "apify/instagram-profile-scraper"
APIFY_YOUTUBE_ACTOR = "apify/youtube-scraper"

SHEETS_TAB_NAME = "Leads"
