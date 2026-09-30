"""
BuzzStormNow - Autonomous 3-Posts/Day Scheduler & Lead Editor Engine
====================================================================
Features:
- Monitors live feeds (Economic Times, NSE Announcements, Board Meetings, Circulars, Livemint)
- Ranks candidate stories by BuzzScore and relevance to current market session
- Rewrites candidates into viral, high-CTR articles with 16:9 8K visuals
- Publishes/Schedules posts on https://buzzstormnow.blogspot.com
- Archives posted items in 'blog/data/published_archive.json' to prevent duplicates
"""

import os
import sys
import json
import time
from datetime import datetime, timezone, timedelta

# Ensure UTF-8 output across Windows and Linux
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

from config import (
    BLOG_ID, BLOG_NAME, BLOG_URL, DAILY_POSTING_SLOTS,
    ARCHIVE_FILE, DRAFTS_DIR
)
from rss_parser import get_fresh_news_candidates, load_archive, save_archive
from viral_editor import transform_news_into_viral_article
from blogger_publisher import publish_article_to_blogger, get_blogger_service

def determine_current_slot():
    """
    Determines the best schedule slot based on current Indian Standard Time (IST = UTC+5:30).
    - Before 11:00 AM IST -> Slot 1: Morning Bell
    - 11:00 AM to 03:30 PM IST -> Slot 2: Mid-Day Movers
    - After 03:30 PM IST -> Slot 3: Closing Bell Wrap
    """
    now_utc = datetime.now(timezone.utc)
    now_ist = now_utc + timedelta(hours=5, minutes=30)
    hour = now_ist.hour

    if hour < 11:
        return DAILY_POSTING_SLOTS[0] # Morning Bell
    elif 11 <= hour < 15 or (hour == 15 and now_ist.minute <= 30):
        return DAILY_POSTING_SLOTS[1] # Mid-Day Movers
    else:
        return DAILY_POSTING_SLOTS[2] # Closing Bell Wrap

def run_single_post(slot=None, force_category=None, is_draft=False, dry_run=False):
    """
    Selects top candidate news item, transforms it into a viral article,
    publishes to Blogger, and updates the archive.
    """
    if not slot:
        slot = determine_current_slot()

    print("\n" + "=" * 65)
    print(f"⚡ BUZZSTORMNOW LEAD EDITOR EXECUTION")
    print(f"Target Blog: {BLOG_NAME} (ID: {BLOG_ID})")
    print(f"Current Slot: {slot['name']} ({slot['target_time_ist']} IST)")
    print(f"Focus: {slot['hook_focus']}")
    print("=" * 65)

    preferred_cat = force_category or (slot["primary_categories"][0] if slot["primary_categories"] else None)
    candidates = get_fresh_news_candidates(max_candidates=10, preferred_category=preferred_cat)

    if not candidates:
        print("ℹ️ No fresh candidates found right now. All current feed items are already in archive.")
        return None

    # Pick the top scoring fresh candidate
    chosen_item = candidates[0]
    print(f"\n🎯 Selected Candidate (BuzzScore: {chosen_item['buzz_score']}):")
    print(f"   Source: [{chosen_item['source_name']}] {chosen_item['category']}")
    print(f"   Original Title: {chosen_item['title']}")
    print(f"   Link: {chosen_item['link']}")

    # Transform into viral article
    print("\n✍️ Lead Editor: Rewriting into viral high-CTR format...")
    article = transform_news_into_viral_article(chosen_item)

    print(f"🔥 Viral Title: {article['viral_title']}")
    print(f"🏷️ Tags: {article['tags']}")
    print(f"🖼️ Featured Image: {article['image_url'][:70]}...")

    if dry_run:
        from blogger_publisher import save_local_draft
        html_path = save_local_draft(article)
        print(f"\n[DRY RUN] Preview saved to: file:///{html_path.replace(os.sep, '/')}")
        return {"status": "DRY_RUN", "title": article["viral_title"], "preview": html_path}

    # Publish to Blogger
    result = publish_article_to_blogger(article, is_draft=is_draft)

    # Record in persistent archive
    archive = load_archive()
    archive.setdefault("published_urls", []).append(chosen_item["link"])
    archive.setdefault("published_titles", []).append(chosen_item["title"])
    archive.setdefault("articles", []).append({
        "viral_title": article["viral_title"],
        "original_title": chosen_item["title"],
        "original_link": chosen_item["link"],
        "source": chosen_item["source_name"],
        "category": chosen_item["category"],
        "blogger_url": result.get("url"),
        "blogger_post_id": result.get("post_id"),
        "status": result.get("status"),
        "slot": slot["slot_id"],
        "published_at": datetime.now(timezone.utc).isoformat()
    })
    save_archive(archive)

    print("\n" + "=" * 65)
    print(f"🎉 EXECUTION COMPLETE: {result.get('status')}")
    print(f"🌐 Article URL: {result.get('url')}")
    print("=" * 65)

    return result

def run_daily_batch(count=3, is_draft=False):
    """
    Executes a complete 3-post daily campaign across all 3 slots.
    """
    print("\n" + "=" * 65)
    print(f"🚀 GENERATING DAILY 3-POST VIRAL CAMPAIGN FOR BUZZSTORMNOW")
    print(f"Target Blog: {BLOG_NAME} (ID: {BLOG_ID})")
    print("=" * 65)

    results = []
    slots = DAILY_POSTING_SLOTS[:count]

    for i, slot in enumerate(slots, 1):
        print(f"\n--- [Post {i}/{len(slots)}: {slot['name']}] ---")
        res = run_single_post(slot=slot, is_draft=is_draft)
        if res:
            results.append(res)
        time.sleep(2) # Graceful delay between feed parses

    print("\n" + "=" * 65)
    print(f"🏁 DAILY BATCH COMPLETED ({len(results)}/{len(slots)} posts processed)")
    for r in results:
        print(f" - [{r.get('status')}] {r.get('title')} -> {r.get('url')}")
    print("=" * 65)
    return results

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "auto"

    if mode == "batch":
        count = int(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[2].isdigit() else 3
        run_daily_batch(count=count)
    elif mode == "preview":
        run_single_post(dry_run=True)
    elif mode == "draft":
        run_single_post(is_draft=True)
    elif mode in ("post_now", "auto", "run"):
        run_single_post(is_draft=False)
    else:
        print(f"Unknown mode: {mode}. Use: auto, batch, preview, draft, or post_now")
