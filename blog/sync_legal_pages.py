"""
BuzzStormNow - Blogger Legal & Policy Pages Synchronizer
========================================================
Synchronizes all compliance and legal trust pages to https://buzzstormnow.blogspot.com
including the newly mandated Content Policy & Editorial Guidelines page.
"""

import os
import sys

# Ensure UTF-8 output across Windows and Linux
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

from config import BLOG_ID, BLOG_NAME, BLOG_URL
from blogger_publisher import get_blogger_service

LEGAL_PAGES = [
    {
        "id": "7722775378283773456",
        "title": "Privacy Policy",
        "file": os.path.join(script_dir, "legal_pages", "privacy_policy.html")
    },
    {
        "id": "3190806325162354594",
        "title": "Terms of Service",
        "file": os.path.join(script_dir, "legal_pages", "terms_of_service.html")
    },
    {
        "id": "4434701382473373276",
        "title": "Disclaimer",
        "file": os.path.join(script_dir, "legal_pages", "disclaimer.html")
    },
    {
        "id": "1849787417000363971",
        "title": "About Us",
        "file": os.path.join(script_dir, "legal_pages", "about_us.html")
    },
    {
        "id": "43521638601925199",
        "title": "Contact Us",
        "file": os.path.join(script_dir, "legal_pages", "contact_us.html")
    },
    {
        "id": None, # Will find by title or create new
        "title": "Content Policy",
        "file": os.path.join(script_dir, "legal_pages", "content_policy.html")
    }
]

def sync_pages():
    print("=" * 65)
    print(f"🔄 SYNCHRONIZING LEGAL & POLICY PAGES FOR {BLOG_NAME}")
    print(f"Target Blog: {BLOG_URL} (ID: {BLOG_ID})")
    print("=" * 65)

    svc = get_blogger_service()
    if not svc:
        print("❌ Error: Could not connect to Blogger API. Check credentials.")
        return False

    # Get current live pages
    pages_res = svc.pages().list(blogId=BLOG_ID).execute()
    live_pages = pages_res.get("items", [])
    live_map_by_title = {p.get("title", "").strip().lower(): p for p in live_pages}
    live_map_by_id = {p.get("id"): p for p in live_pages}

    for item in LEGAL_PAGES:
        title = item["title"]
        file_path = item["file"]

        if not os.path.exists(file_path):
            print(f"⚠️ Template file missing: {file_path}")
            continue

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        target_id = item.get("id")
        existing = None

        if target_id and target_id in live_map_by_id:
            existing = live_map_by_id[target_id]
        elif title.lower() in live_map_by_title:
            existing = live_map_by_title[title.lower()]
        elif title == "Terms of Service" and "terms and conditions" in live_map_by_title:
            existing = live_map_by_title["terms and conditions"]

        if existing:
            page_id = existing["id"]
            body = {
                "title": title,
                "content": content
            }
            try:
                res = svc.pages().update(blogId=BLOG_ID, pageId=page_id, body=body).execute()
                print(f"✅ Updated '{title}' (ID: {page_id}) -> {res.get('url')}")
            except Exception as e:
                print(f"❌ Failed to update '{title}': {e}")
        else:
            # Create new page
            body = {
                "title": title,
                "content": content
            }
            try:
                res = svc.pages().insert(blogId=BLOG_ID, body=body, isDraft=False).execute()
                print(f"🎉 Created & Published '{title}' (ID: {res.get('id')}) -> {res.get('url')}")
            except Exception as e:
                print(f"❌ Failed to create '{title}': {e}")

    print("=" * 65)
    print("✨ All legal & policy pages synchronized successfully!")
    print("=" * 65)
    return True

if __name__ == "__main__":
    sync_pages()
