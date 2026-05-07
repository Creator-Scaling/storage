ICP = {
    "follower_min": 10_000,
    "follower_max": 200_000,
    "posts_per_month_min": 10,
    "reel_views_min": 500,
    "locations": ["US", "USA", "United States", "Canada", "UK", "United Kingdom", "GB", "England", "Scotland", "Wales"],
    "disqualify_email_prefixes": ["info", "support", "contact", "hello", "team", "admin", "mail", "sales", "noreply", "no-reply"],
    "niches": [
        "Make Money Online / Business Opportunity",
        "Real Estate",
        "Credit & Finances",
        "AI Solutions",
        "SaaS & Tech-Enabled Businesses",
        "High-Ticket Education & Online Programmes",
        "Coaching, Consulting & Mentorship Offers",
    ],
}

# Hashtags to discover leads per niche. Extend freely.
NICHE_HASHTAGS: dict[str, list[str]] = {
    "Make Money Online / Business Opportunity": [
        "makemoneyonline", "onlinebusiness", "digitalmarketing", "passiveincome",
        "entrepreneur", "onlinemarketing", "workfromhome", "sidehustle",
        "dropshipping", "affiliatemarketing",
    ],
    "Real Estate": [
        "realestateinvesting", "realestatecoach", "realestateeducation",
        "realestatementor", "realestateinvestor", "propertyinvesting",
        "realestatecourse", "wholesalerealestate",
    ],
    "Credit & Finances": [
        "creditrepair", "creditcoach", "financialfreedom", "moneymindset",
        "personalfinance", "debtfree", "creditbuilding", "creditrestoration",
        "buildcredit", "financialcoach",
    ],
    "AI Solutions": [
        "artificialintelligence", "aitools", "chatgpt", "aibusiness",
        "automationtools", "aimarketing", "aicoach", "promptengineering",
    ],
    "SaaS & Tech-Enabled Businesses": [
        "saas", "techstartup", "softwarebusiness", "techentrepreneur",
        "saasfounder", "b2bsaas",
    ],
    "High-Ticket Education & Online Programmes": [
        "highticket", "onlinecourse", "coursecreator", "onlineeducation",
        "digitalcourse", "elearning", "highticketsales", "highticketcoaching",
    ],
    "Coaching, Consulting & Mentorship Offers": [
        "businesscoach", "mindsetcoach", "businessmentor", "executivecoach",
        "coachingbusiness", "consultant", "lifecoach", "successcoach",
        "onlinecoach", "businessconsultant",
    ],
}

# Paste your High Ticket Webinar strategy description here.
# Claude uses this to personalise the audit's "Why This Works For You" section.
HIGH_TICKET_WEBINAR_STRATEGY = """
[PLACEHOLDER — add your High Ticket Webinar strategy description here]

Describe:
- What a High Ticket Webinar is and how it works
- Who it's designed for (coaches, educators, info-product creators)
- The core mechanism (webinar → high-ticket offer conversion)
- Why it outperforms cold DMs, low-ticket funnels, or organic-only approaches
- Results or proof points you can reference
"""

# Reference profiles will be loaded here once you supply them.
# Format: list of dicts with keys: handle, niche, why_they_qualify
REFERENCE_PROFILES: list[dict] = [
    # Example:
    # {
    #     "handle": "example_coach",
    #     "niche": "Coaching, Consulting & Mentorship Offers",
    #     "why_they_qualify": "Sells a $5k mentorship, 45k followers, consistent reels 2k+ views",
    # },
]
