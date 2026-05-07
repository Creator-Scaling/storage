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

# Platform/tool accounts whose followers are overwhelmingly coaches & course creators
PLATFORM_HANDLES = [
    "skool",
    "kajabi",
    "stanstore",
    "gohighlevel",
    "clickfunnels",
    "teachable",
    "thinkific",
    "podia",
    "mightynetworks",
]

# Bio/username keywords for direct Instagram account search
BIO_KEYWORDS = [
    "business coach",
    "online course creator",
    "life coach",
    "marketing coach",
    "financial coach",
    "real estate coach",
    "forex coach",
    "trading coach",
    "mindset coach",
    "high ticket coach",
    "online educator",
    "course creator",
    "I help entrepreneurs",
    "I help coaches",
    "join my programme",
    "join my program",
    "enroll now",
    "apply for coaching",
    "free training",
    "DM me to join",
]

# YouTube search terms for channel discovery
YOUTUBE_SEARCH_TERMS = [
    "business coaching programme",
    "online course creator",
    "make money online course",
    "real estate investing course",
    "forex trading course",
    "credit repair course",
    "AI tools for business",
    "high ticket coaching",
    "online mentorship programme",
    "dropshipping course 2025",
]

# ManyChat/funnel CTA signals in post captions
MANYCHAT_SIGNALS = [
    r"comment\s+['\"]?\w+['\"]?\s+(below|for|to get|and i'll)",
    r"type\s+['\"]?\w+['\"]?\s+(below|in the comments|for)",
    r"dm\s+me\s+(the word|['\"]?\w+['\"]?)\s+for",
    r"comment\s+(yes|['\"]yes['\"])\s+",
    r"m\.me/",
]

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

# Confirmed ideal prospects — used to calibrate Claude's qualification judgement.
REFERENCE_PROFILES: list[dict] = [
    # --- Make Money Online / Business Opportunity ---
    {
        "handle": "meganhealeey",
        "niche": "Make Money Online / Business Opportunity",
        "why_they_qualify": "Sells Vending Mastery Course via Skool, active programme with funnel, English-speaking US audience",
    },
    {
        "handle": "thejuanjeronimo",
        "niche": "Make Money Online / Business Opportunity",
        "why_they_qualify": "Sells Wealth Streams Academy ATM/passive income programme, active community funnel",
    },
    {
        "handle": "therubenlozoya",
        "niche": "Make Money Online / Business Opportunity",
        "why_they_qualify": "Sells push2win.biz programme, active website funnel, consistent output",
    },
    {
        "handle": "dnald14",
        "niche": "Make Money Online / Business Opportunity",
        "why_they_qualify": "Sells via Stan Store, active on Instagram and YouTube, Make Money Online niche",
    },
    {
        "handle": "rico_rixo",
        "niche": "Make Money Online / Business Opportunity",
        "why_they_qualify": "Beacons link-in-bio, active on YouTube and Instagram, online business content",
    },
    {
        "handle": "dsanglay",
        "niche": "Make Money Online / Business Opportunity",
        "why_they_qualify": "Active Linktree funnel, consistent Instagram and YouTube presence",
    },
    {
        "handle": "iamsebastianbetancur",
        "niche": "Make Money Online / Business Opportunity",
        "why_they_qualify": "Sells 6-figure affiliate marketing programme via Whop, active on both platforms",
    },
    {
        "handle": "sourcingwithazu",
        "niche": "Make Money Online / Business Opportunity",
        "why_they_qualify": "Sells Virtual Sourcing Masterclass, active Instagram presence in e-commerce/sourcing niche",
    },
    {
        "handle": "snipernick32",
        "niche": "Make Money Online / Business Opportunity",
        "why_they_qualify": "Sells via free-webinar funnel (sniperkicks.info), active Instagram and YouTube",
    },
    # --- Real Estate ---
    {
        "handle": "matthew.bnb",
        "niche": "Real Estate",
        "why_they_qualify": "Sells Passive Profits Coaching (Airbnb/STR), dedicated website, active on both platforms",
    },
    {
        "handle": "airbnbautomated",
        "niche": "Real Estate",
        "why_they_qualify": "Sean Rakidzich — sells Cracking Superhost programme, large YouTube audience, active funnel",
    },
    {
        "handle": "stefaniekebede",
        "niche": "Real Estate",
        "why_they_qualify": "Sells Real Estate Collective via Whop, active on Instagram and YouTube",
    },
    {
        "handle": "james_the_property_coach",
        "niche": "Real Estate",
        "why_they_qualify": "UK-based property coach, dedicated website jamesbennett.uk, active on both platforms",
    },
    {
        "handle": "landprofits",
        "niche": "Real Estate",
        "why_they_qualify": "Ella — UK-based, sells land investing masterclass, active Instagram",
    },
    {
        "handle": "flippingmastery",
        "niche": "Real Estate",
        "why_they_qualify": "Jerry — house flipping education, large YouTube presence, active Instagram",
    },
    {
        "handle": "bnbleaders",
        "niche": "Real Estate",
        "why_they_qualify": "BnB/STR coaching, active Instagram and YouTube content",
    },
    # --- Credit & Finances ---
    {
        "handle": "trader.jeafx_",
        "niche": "Credit & Finances",
        "why_they_qualify": "Sells forex trading programme at jeafx.com/go, active on Instagram and YouTube",
    },
    {
        "handle": "kellyohgee",
        "niche": "Credit & Finances",
        "why_they_qualify": "Sells trading education via tradeitsolutions.com, active on both platforms",
    },
    {
        "handle": "traderdivergent",
        "niche": "Credit & Finances",
        "why_they_qualify": "The Divergent Trader — active YouTube and Instagram, trading education",
    },
    {
        "handle": "mamba_trades",
        "niche": "Credit & Finances",
        "why_they_qualify": "Active on Instagram and YouTube, trading education content",
    },
    # --- AI Solutions ---
    {
        "handle": "edwinavoiceofai",
        "niche": "AI Solutions",
        "why_they_qualify": "Sells AIM Academy via Skool, active on Instagram and YouTube in AI education niche",
    },
    # --- Coaching, Consulting & Mentorship Offers ---
    {
        "handle": "autocleanacademy",
        "niche": "Coaching, Consulting & Mentorship Offers",
        "why_they_qualify": "Sells auto detailing training via free workshop funnel, active Instagram and YouTube",
    },
    {
        "handle": "austincookofficial",
        "niche": "Coaching, Consulting & Mentorship Offers",
        "why_they_qualify": "Sells Window Film Academy (tint training), dedicated programme website, active on both platforms",
    },
    {
        "handle": "withmarko",
        "niche": "Coaching, Consulting & Mentorship Offers",
        "why_they_qualify": "Marko — active on Instagram and YouTube, business/coaching content",
    },
    {
        "handle": "imlisatran",
        "niche": "Coaching, Consulting & Mentorship Offers",
        "why_they_qualify": "Lisa Tran — sells tutoring business programme via TutorBoss, active on both platforms",
    },
    {
        "handle": "jimmy_on_relationships",
        "niche": "Coaching, Consulting & Mentorship Offers",
        "why_they_qualify": "Relationship coaching, active Instagram and YouTube audience",
    },
    {
        "handle": "jacobgodar",
        "niche": "High-Ticket Education & Online Programmes",
        "why_they_qualify": "Jacob Godar — active on Instagram and YouTube, online education/creator niche",
    },
    {
        "handle": "thatnateblack",
        "niche": "High-Ticket Education & Online Programmes",
        "why_they_qualify": "Nate Black — sells RadicalYT programme, active YouTube and Instagram, creator education",
    },
]
