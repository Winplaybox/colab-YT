"""BuzzStormNow - Autonomous 3-Posts/Day Scheduler & Lead Editor Engine
====================================================================
Features:
- Monitors live feeds and ranks candidate stories
- Generates original articles and visuals
- Publishes to Blogger
- Archives only Blogger-accepted posts (never local drafts or failed attempts)
"""
import os
import sys
import json
import time
from datetime import datetime, timezone, timedelta

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

from config import BLOG_ID, BLOG_NAME, BLOG_URL, DAILY_POSTING_SLOTS
from rss_parser import get_fresh_news_candidates, load_archive, save_archive
from viral_editor import transform_news_into_viral_article
from blogger_publisher import publish_article_to_blogger


def determine_current_slot():
    now_ist = datetime.now(timezone.utc) + timedelta(hours=5, minutes=30)
    hour = now_ist.hour
    if hour < 11:
        return DAILY_POSTING_SLOTS[0]
    if 11 <= hour < 15 or (hour == 15 and now_ist.minute <= 30):
        return DAILY_POSTING_SLOTS[1]
    return DAILY_POSTING_SLOTS[2]


def run_single_post(slot=None, force_category=None, is_draft=False, dry_run=False):
    if not slot:
        slot = determine_current_slot()

    print("\n" + "=" * 65)
    print("⚡ BUZZSTORMNOW LEAD EDITOR EXECUTION")
    print(f"Target Blog: {BLOG_NAME} (ID: {BLOG_ID})")
    print(f"Current Slot: {slot['name']} ({slot['target_time_ist']} IST)")
    print(f"Focus: {slot['hook_focus']}")
    print("=" * 65)

    preferred_cat = force_category or (slot["primary_categories"][0] if slot["primary_categories"] else None)
    candidates = get_fresh_news_candidates(max_candidates=10, preferred_category=preferred_cat)
    if not candidates:
        print("ℹ️ No fresh candidates found; no new article was published.")
        return None

    chosen_item = candidates[0]
    article = transform_news_into_viral_article(chosen_item)
    print(f"🔥 Viral Title: {article['viral_title']}")

    if dry_run:
        from blogger_publisher import save_local_draft
        html_path = save_local_draft(article)
        print(f"[DRY RUN] Preview saved to: file:///{html_path.replace(os.sep, '/')}")
        return {"status": "DRY_RUN", "title": article["viral_title"], "preview": html_path}

    result = publish_article_to_blogger(article, is_draft=is_draft)
    status = (result or {}).get("status")
    post_id = (result or {}).get("post_id")

    # A local HTML fallback, API error, or Blogger draft is not a published post.
    # Fail the Actions job so monitoring catches the missed publication.
    accepted_statuses = {"PUBLISHED", "SCHEDULED"}
    if is_draft:
        accepted_statuses.add("DRAFT")
    if status not in accepted_statuses or not post_id:
        raise RuntimeError(
            f"Blogger did not confirm the requested post state "
            f"(status={status!r}, post_id={post_id!r}, draft_requested={is_draft}); "
            "archive was not advanced."
        )

    # Draft mode is a successful draft operation, but drafts must never enter
    # the published archive or be treated as live posts.
    if status == "DRAFT":
        print(f"📝 BLOGGER CONFIRMED DRAFT: {result.get('url')}")
        return result

    archive = load_archive()
    source_url = chosen_item["link"]
    archive.setdefault("published_urls", [])
    archive.setdefault("published_titles", [])
    archive.setdefault("articles", [])

    # Idempotency guard: never append the same source URL twice.
    if source_url not in archive["published_urls"]:
        archive["published_urls"].append(source_url)
        archive["published_titles"].append(chosen_item["title"])
        archive["articles"].append({
            "viral_title": article["viral_title"],
            "original_title": chosen_item["title"],
            "original_link": source_url,
            "source": chosen_item["source_name"],
            "category": chosen_item["category"],
            "blogger_url": result.get("url"),
            "blogger_post_id": post_id,
            "status": status,
            "slot": slot["slot_id"],
            "published_at": datetime.now(timezone.utc).isoformat()
        })
        save_archive(archive)

    print(f"🎉 BLOGGER CONFIRMED: {status} | {result.get('url')}")
    return result


def run_daily_batch(count=3, is_draft=False):
    results = []
    for slot in DAILY_POSTING_SLOTS[:count]:
        result = run_single_post(slot=slot, is_draft=is_draft)
        if result:
            results.append(result)
        time.sleep(2)
    print(f"Daily campaign completed: {len(results)}/{min(count, len(DAILY_POSTING_SLOTS))} Blogger posts confirmed.")
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
        raise SystemExit(f"Unknown mode: {mode}. Use: auto, batch, preview, draft, or post_now")
