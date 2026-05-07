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
GOOGLE_DRIVE_FOLDER_ID = os.environ.get("GOOGLE_DRIVE_FOLDER_ID", "")

CLAUDE_MODEL = "claude-sonnet-4-6"

# Apify actor IDs
APIFY_INSTAGRAM_HASHTAG_ACTOR = "apify/instagram-hashtag-scraper"
APIFY_INSTAGRAM_PROFILE_ACTOR = "apify/instagram-profile-scraper"
APIFY_YOUTUBE_ACTOR = "apify/youtube-scraper"

SHEETS_TAB_NAME = "Leads"
