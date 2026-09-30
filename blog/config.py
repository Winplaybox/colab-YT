"""
BuzzStormNow - Blog Automation Configuration
===========================================
Target Blog: https://buzzstormnow.blogspot.com
Blog ID: 7128783356419391680
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

# 3 Optimal Daily Posting Windows for Indian Market & Global Finance
# Times in IST (Indian Standard Time, UTC+5:30)
DAILY_POSTING_SLOTS = [
    {
        "slot_id": "morning_bell",
        "name": "Morning Bell & Pre-Market Setup",
        "target_time_ist": "08:15",
        "target_time_utc": "02:45",
        "primary_categories": ["Market Analysis", "Breaking News", "Pre-Market Cues"],
        "tagline": "Morning Pulse: What You Need To Know Before The Market Opens 🔔",
        "hook_focus": "overnight developments, gift nifty cues, global market signals, key stocks in radar"
    },
    {
        "slot_id": "midday_movers",
        "name": "Mid-Day Movers & Board Actions",
        "target_time_ist": "13:00",
        "target_time_utc": "07:30",
        "primary_categories": ["Board Meetings", "Official Announcements", "Corporate Actions"],
        "tagline": "Mid-Day Surge: Breaking Deals, Boardroom Decisions & Movers 🔥",
        "hook_focus": "breaking earnings, board meeting resolutions, massive volume breakouts, corporate shakeups"
    },
    {
        "slot_id": "closing_wrap",
        "name": "Closing Bell Wrap & Tomorrow's Radar",
        "target_time_ist": "17:30",
        "target_time_utc": "12:00",
        "primary_categories": ["Circulars", "Market Analysis", "Corporate News"],
        "tagline": "Closing Bell: Market Scorecard, Big Secrets & Tomorrow's Playbook 📈",
        "hook_focus": "NSE circulars, daily closing sentiment, institutional buying/selling, tomorrow's strategy"
    }
]

# Curated High-Authority RSS Feeds
FEEDS = [
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
        "priority": 2
    },
    {
        "name": "Livemint Companies",
        "url": "https://www.livemint.com/rss/companies",
        "category": "Corporate News",
        "priority": 2
    },
    {
        "name": "Economic Times Top Stories",
        "url": "https://economictimes.indiatimes.com/rssfeedstopstories.cms",
        "category": "Breaking News",
        "priority": 2
    }
]

# Editorial Tone & Branding Settings
EDITORIAL_SETTINGS = {
    "author": "BuzzStormNow Editorial Team",
    "site_title": "BuzzStormNow",
    "brand_color": "#ff4500",
    "secondary_color": "#1e293b",
    "accent_gold": "#f59e0b",
    "default_tags": ["Stock Market", "BuzzStormNow", "Business", "Investing", "India"],
    "disclaimer": (
        "Disclaimer: This article is published for informational and educational purposes only. "
        "It does not constitute financial, investment, or legal advice. "
        "Stock market investments are subject to market risks. Please consult a SEBI-registered "
        "financial advisor before making any investment decisions."
    )
}
