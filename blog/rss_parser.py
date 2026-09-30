"""
BuzzStormNow - RSS Feed Ingestion & Parsing Engine
==================================================
Fetches, cleans, and deduplicates news articles from NSE, Economic Times, and Livemint.
"""

import os
import sys
import re
import json
import html
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

# Ensure UTF-8 output across Windows and Linux
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

from config import FEEDS, ARCHIVE_FILE

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.google.com/"
}

VIRAL_KEYWORDS = [
    "surge", "soar", "jump", "skyrocket", "rally", "record", "massive",
    "crash", "plunge", "fall", "tumble", "slump", "alert", "warning",
    "dividend", "bonus", "split", "buyback", "acquisition", "merger",
    "earnings", "q1", "q2", "q3", "q4", "profit", "revenue", "loss",
    "rbi", "sebi", "order", "penalty", "approval", "contract", "deal",
    "ipo", "listing", "nifty", "sensex", "breakout", "target", "multibagger"
]

def load_archive():
    """Loads previously published and processed articles to avoid duplication."""
    if os.path.exists(ARCHIVE_FILE):
        try:
            with open(ARCHIVE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"published_urls": [], "published_titles": [], "articles": []}

def save_archive(archive):
    """Persists published archive to disk."""
    os.makedirs(os.path.dirname(ARCHIVE_FILE), exist_ok=True)
    with open(ARCHIVE_FILE, "w", encoding="utf-8") as f:
        json.dump(archive, f, indent=2, ensure_ascii=False)

def clean_text(raw_text):
    """Strips HTML tags, decodes entities, and normalizes whitespace."""
    if not raw_text:
        return ""
    # Strip HTML
    text = re.sub(r"<[^>]+>", " ", str(raw_text))
    # Decode HTML entities
    text = html.unescape(text)
    # Normalize spaces
    text = re.sub(r"\s+", " ", text).strip()
    return text

def parse_pubdate(date_str):
    """Attempts to parse pubDate into standard ISO format."""
    if not date_str:
        return datetime.now(timezone.utc).isoformat()
    try:
        dt = parsedate_to_datetime(date_str)
        return dt.isoformat()
    except Exception:
        pass
    try:
        dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        return dt.isoformat()
    except Exception:
        pass
    return datetime.now(timezone.utc).isoformat()

def calculate_buzz_score(title, description):
    """Calculates a viral potential score based on keywords and curiosity markers."""
    score = 10
    combined = f"{title} {description}".lower()
    for kw in VIRAL_KEYWORDS:
        if kw in combined:
            score += 8
    # Bonus for monetary/percentage metrics
    if re.search(r"(\d+%\s*|\$\d+|\₹\d+|crore|billion|lakh)", combined):
        score += 15
    # Bonus for question or curiosity words
    if any(q in combined for q in ["why", "how", "what", "reveals", "unveils", "secret", "future"]):
        score += 10
    return score

def find_node(elem, *tag_names):
    """Safely finds first matching XML tag without relying on Element truthiness."""
    for tag in tag_names:
        n = elem.find(tag)
        if n is not None:
            return n
    return None

def fetch_feed_items(feed_config):
    """Fetches and parses a single RSS feed."""
    items = []
    name = feed_config["name"]
    url = feed_config["url"]
    category = feed_config["category"]

    try:
        resp = requests.get(url, headers=HEADERS, timeout=12)
        if resp.status_code != 200:
            print(f"⚠️ [{name}] HTTP {resp.status_code}")
            return []

        # Parse XML
        root = ET.fromstring(resp.content)
        
        # Check standard RSS <item> or Atom <entry>
        raw_items = root.findall(".//item")
        if len(raw_items) == 0:
            # Check Atom format
            atom_ns = {"atom": "http://www.w3.org/2005/Atom"}
            raw_items = root.findall(".//atom:entry", atom_ns)
            if len(raw_items) == 0:
                raw_items = root.findall(".//entry")

        for elem in raw_items:
            # Title
            t_node = find_node(elem, "title", "{http://www.w3.org/2005/Atom}title")
            raw_title = t_node.text if t_node is not None else ""
            clean_title = clean_text(raw_title)

            if not clean_title or len(clean_title) < 5:
                continue

            # Link
            l_node = find_node(elem, "link", "{http://www.w3.org/2005/Atom}link")
            link = ""
            if l_node is not None:
                link = l_node.get("href") or l_node.text or ""
            link = link.strip()

            # Description / Content
            d_node = find_node(elem, "description", "summary", "{http://www.w3.org/2005/Atom}summary", "{http://www.w3.org/2005/Atom}content")
            raw_desc = d_node.text if d_node is not None else ""
            clean_desc = clean_text(raw_desc)

            # PubDate
            p_node = find_node(elem, "pubDate", "published", "updated", "{http://www.w3.org/2005/Atom}updated")
            raw_date = p_node.text if p_node is not None else ""
            pub_date = parse_pubdate(raw_date)

            # GUID / Identifier
            g_node = find_node(elem, "guid", "id", "{http://www.w3.org/2005/Atom}id")
            guid = g_node.text if g_node is not None and g_node.text else link

            buzz_score = calculate_buzz_score(clean_title, clean_desc)

            items.append({
                "source_name": name,
                "category": category,
                "title": clean_title,
                "link": link,
                "guid": guid,
                "description": clean_desc,
                "published_at": pub_date,
                "buzz_score": buzz_score
            })
    except Exception as e:
        print(f"Notice: Failed to parse feed '{name}': {e}")

    return items

def get_fresh_news_candidates(max_candidates=15, preferred_category=None):
    """
    Ingests all feeds, filters against already published items,
    and returns top candidates ranked by BuzzScore and recency.
    """
    archive = load_archive()
    published_links = set(archive.get("published_urls", []))
    published_titles = set(t.lower().strip() for t in archive.get("published_titles", []))

    all_items = []
    for f in FEEDS:
        items = fetch_feed_items(f)
        all_items.extend(items)

    fresh_items = []
    seen_links = set()

    for item in all_items:
        lnk = item["link"]
        tit = item["title"].lower().strip()

        # Deduplication checks
        if not lnk or lnk in published_links or lnk in seen_links:
            continue
        if tit in published_titles:
            continue

        # Soft title matching (ignore punctuation differences)
        norm_tit = re.sub(r"[^a-zA-Z0-9]", "", tit)
        if any(norm_tit == re.sub(r"[^a-zA-Z0-9]", "", pt) for pt in published_titles):
            continue

        seen_links.add(lnk)

        # Bonus score if category matches the target schedule slot
        if preferred_category and preferred_category.lower() in item["category"].lower():
            item["buzz_score"] += 20

        fresh_items.append(item)

    # Sort by BuzzScore descending, then by publication date
    fresh_items.sort(key=lambda x: (x["buzz_score"], x["published_at"]), reverse=True)
    return fresh_items[:max_candidates]


if __name__ == "__main__":
    print("Testing RSS feed ingestion...")
    candidates = get_fresh_news_candidates(5)
    print(f"Found {len(candidates)} fresh candidates:")
    for i, c in enumerate(candidates, 1):
        print(f"{i}. [{c['source_name']}] (Score: {c['buzz_score']}) {c['title']}")
        print(f"   Link: {c['link']}")
        print(f"   Snippet: {c['description'][:120]}...\n")
