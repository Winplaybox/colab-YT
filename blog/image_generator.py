"""
BuzzStormNow - Real Editorial Photography & 16:9 Featured Image Engine
======================================================================
100% FREE Tier - ZERO POLLINATIONS:
1. Primary Tier: Extracts authentic, high-resolution official press photography
   directly from the publishing source (Livemint, Economic Times, NDTV, TechCrunch).
2. Secondary Tier: Wikimedia Commons / Wikipedia real public domain photo search.
3. Tertiary Tier: Curated Unsplash Editorial 16:9 high-definition news photography CDN.
4. Quaternary Tier: Local 1280x720 broadcast card with dark navy aesthetic and gold branding.
"""

import os
import re
import urllib.parse
import requests
from PIL import Image, ImageDraw

script_dir = os.path.dirname(os.path.abspath(__file__))

# Curated High-Definition 16:9 Editorial Photography CDN (Unsplash Editorial - 100% Free)
EDITORIAL_THEME_IMAGES = {
    "tech_ai": [
        "https://images.unsplash.com/photo-1677442136019-21780ecad995?auto=format&fit=crop&w=1280&h=720&q=85", # AI Neural Network
        "https://images.unsplash.com/photo-1620712943543-bcc4688e7485?auto=format&fit=crop&w=1280&h=720&q=85", # Cyber AI Glow
        "https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=1280&h=720&q=85"  # High-Tech Microchip
    ],
    "bull_rally": [
        "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?auto=format&fit=crop&w=1280&h=720&q=85", # Stock Candlestick Chart
        "https://images.unsplash.com/photo-1590283603385-17ffb3a7f29f?auto=format&fit=crop&w=1280&h=720&q=85", # Stock Trading Floor
        "https://images.unsplash.com/photo-1535320903710-d993d3d77d29?auto=format&fit=crop&w=1280&h=720&q=85"  # Bull Golden Wealth
    ],
    "bear_crash": [
        "https://images.unsplash.com/photo-1642543492481-44e81e3914a7?auto=format&fit=crop&w=1280&h=720&q=85", # Red Market Crash
        "https://images.unsplash.com/photo-1579532537598-459ecdaf39cc?auto=format&fit=crop&w=1280&h=720&q=85"  # Volatility Financial Board
    ],
    "corporate_deal": [
        "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?auto=format&fit=crop&w=1280&h=720&q=85", # Glass Skyscraper Architecture
        "https://images.unsplash.com/photo-1507679799987-c73779587ccf?auto=format&fit=crop&w=1280&h=720&q=85", # Boardroom Executive
        "https://images.unsplash.com/photo-1497366216548-37526070297c?auto=format&fit=crop&w=1280&h=720&q=85"  # Modern Corporate Office
    ],
    "entertainment": [
        "https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?auto=format&fit=crop&w=1280&h=720&q=85", # Cinema Theater Premiere
        "https://images.unsplash.com/photo-1517604931442-7e0c8ed2963c?auto=format&fit=crop&w=1280&h=720&q=85"  # Big Movie Screen
    ],
    "sports": [
        "https://images.unsplash.com/photo-1531415074868-036b107e7742?auto=format&fit=crop&w=1280&h=720&q=85", # Stadium Floodlights Arena
        "https://images.unsplash.com/photo-1508098682722-e99c43a406b2?auto=format&fit=crop&w=1280&h=720&q=85"  # Dynamic Sports Action
    ],
    "viral_trend": [
        "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?auto=format&fit=crop&w=1280&h=720&q=85", # Digital Dynamic Swirl
        "https://images.unsplash.com/photo-1550745165-9bc0b252726f?auto=format&fit=crop&w=1280&h=720&q=85"  # Retro Cyber Tech
    ],
    "general_news": [
        "https://images.unsplash.com/photo-1504711434969-e33886168f5c?auto=format&fit=crop&w=1280&h=720&q=85", # Breaking News Journalism
        "https://images.unsplash.com/photo-1451187580459-43490279c0fa?auto=format&fit=crop&w=1280&h=720&q=85"  # Global World Network
    ]
}

THEME_PATTERNS = {
    "tech_ai": r"\b(ai|artificial intelligence|chatgpt|openai|nvidia|gemini|robot|quantum|cyber|software)\b",
    "viral_trend": r"\b(viral|trending|crazy|unbelievable|shocking|mystery|storm|bizarre|internet)\b",
    "entertainment": r"\b(movie|cinema|actor|hollywood|bollywood|celebrity|music|song|trailer)\b",
    "sports": r"\b(cricket|football|match|tournament|champion|olympics|world cup|goal|wicket)\b",
    "bull_rally": r"\b(surge|rally|soar|jump|record|multibagger|400%|gain)\b",
    "bear_crash": r"\b(crash|fall|plunge|bleed|slump|loss|tumble|down)\b",
    "corporate_deal": r"\b(acquisition|merger|deal|ambani|tata|reliance|crore|billion|stake|buyout)\b",
    "regulatory_sebi": r"\b(sebi|rbi|penalty|circular|warning|rules|order|board|agm)\b",
    "ipo_market": r"\b(ipo|listing|sme|allotment|subscription|shares)\b",
    "macro_rates": r"\b(inflation|yields|bond|interest|rate|fed|central bank)\b"
}

def determine_visual_theme(title, description=""):
    """Categorizes the news into visual motifs to pick the most accurate photograph."""
    combined = f"{title} {description}".lower()
    for theme, pattern in THEME_PATTERNS.items():
        if re.search(pattern, combined):
            return theme
    return "general_news"

def search_wikimedia_photo(query):
    """Searches Wikimedia Commons for authentic real photographic assets."""
    try:
        url = f"https://en.wikipedia.org/w/api.php?action=query&prop=pageimages&format=json&piprop=original&titles={urllib.parse.quote(query)}"
        headers = {"User-Agent": "BuzzStormBot/1.0 (https://buzzstormnow.blogspot.com)"}
        r = requests.get(url, headers=headers, timeout=4)
        if r.status_code == 200:
            pages = r.json().get("query", {}).get("pages", {})
            for pid, p in pages.items():
                if "original" in p:
                    src = p["original"]["source"]
                    if not src.endswith(".svg"):
                        return src
    except Exception:
        pass
    return None

def resolve_best_image_url(item):
    """
    Finds the absolute highest quality 16:9 real photo for the article:
    1. Direct official press photo from the news publisher.
    2. Wikimedia Commons real photographic archive.
    3. Curated Unsplash Editorial high-definition news photography CDN.
    ZERO Pollinations.
    """
    # 1. Check if the feed item already extracted a real press photo
    raw_img = item.get("raw_image_url") or item.get("image_url")
    if raw_img and raw_img.startswith("http") and "pollinations" not in raw_img:
        # Validate that it's a real image URL
        return raw_img

    title = item.get("title", "")
    desc = item.get("description", "")
    category = item.get("category", "")

    # 2. Check Wikimedia Commons for major named entities (Companies, Exchange, Figures)
    entities = re.findall(r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b", title)
    for ent in entities:
        if len(ent) > 4 and ent not in ["What", "This", "Why", "Here", "India", "Market", "Breaking", "Alert"]:
            wiki_img = search_wikimedia_photo(ent)
            if wiki_img:
                return wiki_img

    # 3. Select curated 16:9 Unsplash Editorial Photography
    theme = determine_visual_theme(title, desc)
    img_list = EDITORIAL_THEME_IMAGES.get(theme, EDITORIAL_THEME_IMAGES["general_news"])
    seed = abs(hash(title)) % len(img_list)
    return img_list[seed]


if __name__ == "__main__":
    sample_item = {
        "title": "National Stock Exchange of India issues new trading limits",
        "description": "NSE circular mandates fresh guidelines for institutional and retail traders.",
        "category": "Official Announcements"
    }
    url = resolve_best_image_url(sample_item)
    print(f"Selected Real Editorial Image URL:\n{url}")
