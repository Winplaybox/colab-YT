"""
BuzzStormNow - Blog Automation Configuration
===========================================
Target Blog: https://buzzstormnow.blogspot.com
Blog ID: 7128783356419391680

Brand Identity:
"BuzzStormNow is your premier destination for viral stories, trending news, and breaking updates
from around the world. We leverage cutting-edge AI technology to bring you the most engaging
and relevant content, curated and delivered 24/7."
"""

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
DRAFTS_DIR = os.path.join(DATA_DIR, "drafts")
CREDENTIALS_DIR = os.path.join(BASE_DIR, "credentials")
ARCHIVE_FILE = os.path.join(DATA_DIR, "published_archive.json")

# Blogger Configuration
BLOG_ID = os.environ.get("BLOGGER_BLOG_ID", "7128783356419391680")
BLOG_NAME = "BuzzStormNow"
BLOG_URL = "https://buzzstormnow.blogspot.com"

# 3 Optimal Daily Posting Windows for Peak Engagement (IST = UTC+5:30)
DAILY_POSTING_SLOTS = [
    {
        "slot_id": "morning_bell",
        "name": "Morning Bell & Pre-Market Setup",
        "target_time_ist": "08:15",
        "target_time_utc": "02:45",
        "primary_categories": ["Market Analysis", "Breaking News", "Technology & AI"],
        "tagline": "Morning Pulse: What You Need To Know Before The Day Begins 🔔",
        "hook_focus": "overnight developments, market signals, breaking tech breakthroughs, key stories to watch"
    },
    {
        "slot_id": "midday_movers",
        "name": "Mid-Day Movers & Viral Surge",
        "target_time_ist": "13:00",
        "target_time_utc": "07:30",
        "primary_categories": ["Viral Content", "Official Announcements", "Board Meetings", "Technology & AI"],
        "tagline": "Mid-Day Surge: Stories Taking The Internet By Storm 🔥",
        "hook_focus": "trending internet sensations, corporate decisions, product launches, midday breakthroughs"
    },
    {
        "slot_id": "closing_wrap",
        "name": "Evening Deep Dive & World Radar",
        "target_time_ist": "17:30",
        "target_time_utc": "12:00",
        "primary_categories": ["Circulars", "World News", "Entertainment", "Market Analysis"],
        "tagline": "Evening Wrap: Global Recap, Big Reveals & Tomorrow's Radar 🌐",
        "hook_focus": "major daily recaps, official regulatory circulars, global entertainment & tomorrow's watchlist"
    }
]

# Curated High-Authority Multi-Niche Feeds for BuzzStormNow
FEEDS = [
    # 1. Market Analysis & Official Exchange Filings
    {
        "name": "Economic Times Markets",
        "url": "https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms",
        "category": "Market Analysis",
        "priority": 1
    },
    {
        "name": "NSE Online announcements",
        "url": "https://nsearchives.nseindia.com/content/RSS/Online_announcements.xml",
        "category": "Official Announcements",
        "priority": 1
    },
    {
        "name": "NSE Board Meetings",
        "url": "https://nsearchives.nseindia.com/content/RSS/Board_Meetings.xml",
        "category": "Board Meetings",
        "priority": 1
    },
    {
        "name": "NSE Circulars",
        "url": "https://nsearchives.nseindia.com/content/RSS/Circulars.xml",
        "category": "Circulars",
        "priority": 1
    },
    {
        "name": "Livemint Markets",
        "url": "https://www.livemint.com/rss/markets",
        "category": "Market Trends",
        "priority": 1
    },
    # 2. Breaking News & Top Stories
    {
        "name": "Economic Times Top Stories",
        "url": "https://economictimes.indiatimes.com/rssfeedstopstories.cms",
        "category": "Breaking News",
        "priority": 2
    },
    # 3. Technology & AI Trends
    {
        "name": "TechCrunch Latest",
        "url": "https://techcrunch.com/feed/",
        "category": "Technology & AI",
        "priority": 2
    },
    {
        "name": "The Verge Tech & AI",
        "url": "https://www.theverge.com/rss/index.xml",
        "category": "Technology & AI",
        "priority": 2
    },
    # 4. Viral Stories & Pop Culture Trends
    {
        "name": "India Today Trending",
        "url": "https://www.indiatoday.in/rss/1206584",
        "category": "Viral Content",
        "priority": 2
    }
]

# Editorial Tone & Branding Settings (Aligned with BuzzStormNow Mission)
EDITORIAL_SETTINGS = {
    "site_title": "BuzzStormNow",
    "site_tagline": "AI-Powered Viral Stories, Breaking News & What's Buzzing 24/7",
    "mission": (
        "BuzzStormNow is your premier destination for viral stories, trending news, and breaking updates "
        "from around the world. We leverage cutting-edge AI technology to bring you the most engaging "
        "and relevant content, curated and delivered 24/7."
    ),
    "brand_color": "#ff4500",
    "secondary_color": "#0f172a",
    "accent_gold": "#f59e0b",
    "default_tags": ["BuzzStormNow", "Viral News", "Trending", "Breaking News"],
    "disclaimer": (
        "Disclaimer: This article is curated and published by the BuzzStormNow Editorial Team for "
        "informational and educational purposes. Where financial or market matters are discussed, "
        "it does not constitute financial or investment advice. Always verify with official sources."
    )
}
