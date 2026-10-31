"""
BuzzStormNow - Google AdSense Quality & Compliance Auditor
==========================================================
Scans https://buzzstormnow.blogspot.com to detect:
1. Thin / Low Value Content risks (Word count per post).
2. Presence of mandatory legal trust pages (Privacy Policy, About Us, Contact Us, Terms, Disclaimer).
3. Google Search E-E-A-T compliance status.
4. Generates a clear approval roadmap to pass AdSense review.
"""

import os
import sys
import re
import requests

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

MANDATORY_LEGAL_PAGES = [
    {"slug": "content-policy", "name": "Content Policy", "file": "blog/legal_pages/content_policy.html"},
    {"slug": "privacy-policy", "name": "Privacy Policy", "file": "blog/legal_pages/privacy_policy.html"},
    {"slug": "terms-of-service", "name": "Terms of Service", "file": "blog/legal_pages/terms_of_service.html"},
    {"slug": "disclaimer", "name": "Disclaimer", "file": "blog/legal_pages/disclaimer.html"},
    {"slug": "about-us", "name": "About Us", "file": "blog/legal_pages/about_us.html"},
    {"slug": "contact-us", "name": "Contact Us", "file": "blog/legal_pages/contact_us.html"}
]

def run_adsense_audit():
    print("=" * 65)
    print("🔍 BUZZSTORMNOW GOOGLE ADSENSE COMPLIANCE AUDIT")
    print(f"Target Blog: {BLOG_NAME} ({BLOG_URL})")
    print("=" * 65)

    svc = get_blogger_service()
    if not svc:
        print("❌ Error: Could not connect to Blogger API. Run 'python blog/authenticate_blogger.py'.")
        return

    # 1. Audit Blog Overview
    try:
        blog = svc.blogs().get(blogId=BLOG_ID).execute()
        total_posts = blog.get("posts", {}).get("totalItems", 0)
        total_pages = blog.get("pages", {}).get("totalItems", 0)
        print(f"\n📊 Blog Health Overview:")
        print(f" - Blog Title: {blog.get('name')}")
        print(f" - Published Posts: {total_posts}")
        print(f" - Static Pages: {total_pages}")
    except Exception as e:
        print(f"Blog info error: {e}")
        return

    # 2. Audit Existing Static Pages (Check for mandatory trust pages)
    print(f"\n📑 Checking Mandatory AdSense Legal & Trust Pages:")
    existing_page_slugs = []
    try:
        pages_res = svc.pages().list(blogId=BLOG_ID).execute()
        pages = pages_res.get("items", [])
        for p in pages:
            existing_page_slugs.append(p.get("url", "").lower())
            print(f"   ✓ Found Existing Page: '{p.get('title')}' -> {p.get('url')}")
    except Exception as e:
        print(f"Notice querying pages: {e}")

    missing_pages = []
    for req in MANDATORY_LEGAL_PAGES:
        # Check if slug or name exists in any URL or title
        found = any(req["slug"] in u or req["name"].lower() in u for u in existing_page_slugs)
        if not found:
            # Test direct HTTP request to check if page exists
            test_url = f"{BLOG_URL.rstrip('/')}/p/{req['slug']}.html"
            try:
                r = requests.get(test_url, timeout=5)
                if r.status_code == 200 and "Page not found" not in r.text:
                    found = True
            except Exception:
                pass

        if found:
            print(f"   ✅ {req['name']}: LIVE & ACTIVE")
        else:
            print(f"   ❌ {req['name']}: MISSING (Required by AdSense!) -> Template ready in {req['file']}")
            missing_pages.append(req)

    # 3. Audit Recent Posts for Word Count (Low Value Content Check)
    print(f"\n📝 Auditing Content Depth (Thin Content / Word Count Check):")
    try:
        posts_res = svc.posts().list(blogId=BLOG_ID, maxResults=10).execute()
        posts = posts_res.get("items", [])
        thin_count = 0
        rich_count = 0

        for post in posts:
            title = post.get("title", "Untitled")
            content = post.get("content", "")
            plain_text = re.sub(r"<[^>]+>", " ", content)
            words = plain_text.split()
            w_count = len(words)

            if w_count < 400:
                print(f"   ⚠️ [THIN CONTENT] ({w_count} words): '{title[:50]}...'")
                thin_count += 1
            else:
                print(f"   ✅ [HIGH VALUE] ({w_count} words): '{title[:50]}...'")
                rich_count += 1

        print(f"\nRecent Posts Summary: {rich_count} High-Value (>=400 words) | {thin_count} Thin (<400 words)")
    except Exception as e:
        print(f"Notice querying posts: {e}")

    # 4. Actionable AdSense Approval Roadmap
    print("\n" + "=" * 65)
    print("🎯 ACTIONABLE ROADMAP TO GET ADSENSE APPROVED QUICKLY:")
    print("=" * 65)
    
    step = 1
    if missing_pages:
        print(f"{step}. CREATE THE 5 MANDATORY STATIC PAGES IN BLOGGER DASHBOARD:")
        print("   Go to Blogger.com -> Pages -> + New Page, and copy the HTML templates:")
        for mp in missing_pages:
            print(f"   - {mp['name']}: Copy from '{mp['file']}'")
        print("   *Make sure these 5 pages are linked in your blog's Header or Footer navigation!*")
        step += 1

    print(f"{step}. PUBLISH 10 TO 15 HIGH-VALUE IN-DEPTH ARTICLES (1,000+ words):")
    print("   Run: python blog/scheduler.py batch 5")
    print("   Our upgraded Lead Editor automatically produces 1,000+ words with tables, FAQs & Schemas.")
    step += 1

    print(f"{step}. CLEAN UP TEMPLATE PLACEHOLDER LINKS:")
    print("   Ensure your blog's main menu does not contain '#' links or empty categories.")
    print("   Check Blogger -> Layout -> Header Menu, and link to your actual post labels (e.g. /search/label/Stock%20Market).")
    step += 1

    print(f"{step}. RE-SUBMIT FOR ADSENSE REVIEW:")
    print("   Once the 5 pages are linked and 10+ new 1,000-word articles are published, go to:")
    print("   Google AdSense -> Sites -> buzzstormnow.blogspot.com -> Request Review.")
    print("=" * 65)

if __name__ == "__main__":
    run_adsense_audit()
