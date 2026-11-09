"""
Master Release Scheduler for @TigerVlogs-2026
Automated daily execution engine for GitHub Actions & Google Colab.
Schedules 2 original daily videos (16:9 + Short) up to Year 2030 with automated quota protection.
"""

import os
import sys
import json
import time
from datetime import datetime, timedelta
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials
import google.auth.transport.requests

# Import local engine
script_dir = os.path.dirname(os.path.abspath(__file__))


def _yt_brain():
    """Shared metadata brain (channels/common/yt_brain.py). Returns module or None."""
    try:
        root = os.path.abspath(os.path.join(script_dir, "..", ".."))
        if root not in sys.path:
            sys.path.insert(0, root)
        from channels.common import yt_brain
        return yt_brain
    except Exception as e:
        print(f"yt_brain unavailable: {e}")
        return None

sys.path.insert(0, script_dir)
from engine import (
    generate_original_longform_video,
    generate_original_short,
)

def load_config():
    config_path = os.path.join(script_dir, "config.json")
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)

def get_authenticated_youtube_service():
    """Resolves YouTube API credentials from file or environment variable."""
    token_path = os.path.join(script_dir, "token.json")
    if not os.path.exists(token_path) and os.path.exists("/content/token.json"):
        token_path = "/content/token.json"

    # Support GitHub Actions Secrets via environment variables
    for env_key in ["TIGERVLOGS_TOKEN_JSON", "YOUTUBE_TOKEN_JSON"]:
        if env_key in os.environ and os.environ[env_key].strip() and not os.path.exists(token_path):
            with open(token_path, "w", encoding="utf-8") as f:
                f.write(os.environ[env_key].strip())
            break

    if not os.path.exists(token_path):
        raise FileNotFoundError(
            f"token.json not found in {script_dir}. "
            "Please ensure TIGERVLOGS_TOKEN_JSON is added to GitHub Repository Secrets!"
        )

    try:
        creds = Credentials.from_authorized_user_file(token_path)
    except Exception as e:
        raise ValueError(
            f"Failed to parse credentials from {token_path}: {e}. "
            "Please verify that the full JSON content was pasted into GitHub Secrets."
        )

    if creds.expired and creds.refresh_token:
        try:
            creds.refresh(google.auth.transport.requests.Request())
            with open(token_path, "w", encoding="utf-8") as f:
                f.write(creds.to_json())
            print("Access token refreshed automatically.")
        except Exception as e:
            print(f"Token refresh warning: {e}")

    return build("youtube", "v3", credentials=creds)

def upload_video_to_youtube(
    youtube,
    file_path,
    title,
    description,
    tags,
    publish_at=None,
    category_id="22"
):
    """Uploads a video and schedules it for release with retries."""
    status = {
        "privacyStatus": "private",
        "selfDeclaredMadeForKids": False
    }
    if publish_at:
        status["publishAt"] = publish_at

    body = {
        "snippet": {
            "title": title[:100],
            "description": description,
            "tags": tags,
            "categoryId": category_id
        },
        "status": status
    }

    # Live YouTube Duplicate Protection
    try:
        try:
            from common.youtube_duplicate_checker import check_existing_upload
        except ImportError:
            sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
            from common.youtube_duplicate_checker import check_existing_upload

        dup = check_existing_upload(youtube, candidate_title=title, channel_type="TigerVlogs")
        if dup.get("exists"):
            existing_id = dup["video_id"]
            print(f"\n🛑 [DUPLICATE PREVENTED] Video ALREADY exists on Tiger Vlogs YouTube!")
            print(f"   Existing Title: '{dup.get('matched_title', dup.get('title'))}'")
            print(f"   Reason:         {dup.get('reason')}")
            print(f"   Video ID:       {existing_id} ({dup.get('status', 'unknown')})")
            print(f"   YouTube Link:   https://youtu.be/{existing_id}")
            print(f"   ⏭️ Skipping upload to avoid creating duplicate content on YouTube.\n")
            return existing_id
    except Exception as ce:
        print(f"Notice: Duplicate checker notice: {ce}")

    _b = _yt_brain()
    if _b:
        body = _b.before_insert("TigerVlogs", youtube, body, is_short=None)
    insert_request = youtube.videos().insert(
        part="snippet,status",
        body=body,
        media_body=MediaFileUpload(file_path, chunksize=-1, resumable=True)
    )

    print(f"Uploading: {title}")
    if publish_at:
        print(f" -> Scheduled Release: {publish_at}")

    for attempt in range(1, 4):
        try:
            response = insert_request.execute()
            vid = response.get("id")
            if _b:
                _b.after_insert("TigerVlogs", youtube, vid)
            print(f"SUCCESS: Video '{title}' uploaded! ID: {vid}")
            return vid
        except HttpError as e:
            print(f"HTTP error on attempt {attempt}: {e}")
            if attempt == 3: raise
            time.sleep(3)
        except Exception as e:
            print(f"Upload error on attempt {attempt}: {e}")
            if attempt == 3: raise
            time.sleep(3)
    return None

USED_TOPICS_FILE = os.path.join(script_dir, "used_topics.json")


def load_used_topics():
    if os.path.exists(USED_TOPICS_FILE):
        with open(USED_TOPICS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_used_topics(used):
    with open(USED_TOPICS_FILE, "w", encoding="utf-8") as f:
        json.dump(used, f, ensure_ascii=False, indent=1)


def _planned_today():
    try:
        b = _yt_brain()   # makes channels.common importable
        from channels.common.growth_weekly import todays_plan
        return json.dumps(todays_plan("TigerVlogs") or {}, ensure_ascii=False)
    except Exception:
        return "{}"


def topic_from_claude(used_titles):
    """Fresh topic each day via Claude (needs ANTHROPIC_API_KEY). Returns dict or None."""
    if not os.environ.get("ANTHROPIC_API_KEY"):
        return None
    try:
        import anthropic, re
        prompt = (
            "You write for TigerVlogs, a pure-vegetarian Indian street-food channel (Hinglish narration).\n"
            "Give ONE new topic: a famous vegetarian Indian dish or street food, its history, how it is made, "
            "or a regional variety. Only well-established facts. NO health/medical claims, NO adulteration or "
            "safety tests, NO numbers you are not sure of.\n"
            f"Already used titles (do not repeat): {used_titles[-120:]}\n"
            f"Weekly growth plan for today (prefer it if it fits the rules): {_planned_today()}\n"
            'Return ONLY JSON: {"hook": "max 6 words, caps ok", "title": "max 60 chars English", '
            '"script": "70-90 words Hinglish (Roman script), friendly, ends with a question for comments", '
            '"wiki": "exact English Wikipedia article title for the dish", "tags": ["8 tags"]}'
        )
        msg = anthropic.Anthropic().messages.create(
            model=os.environ.get("CLAUDE_MODEL", "claude-sonnet-5-5"), max_tokens=800,
            messages=[{"role": "user", "content": prompt}])
        text = "".join(b.text for b in msg.content if getattr(b, "type", "") == "text")
        data = json.loads(re.search(r"\{.*\}", text, re.S).group(0))
        if all(data.get(k) for k in ("hook", "title", "script", "wiki")):
            return data
    except Exception as e:
        print(f"Claude topic notice: {e}")
    return None


def run_daily_batch(target_date_str=None, batch_dir="/tmp/tiger_vlogs_batch"):
    """
    Daily release (2 videos, both 100% original):
    - Slot 1 (1:00 PM IST / 07:30 UTC): 16:9 food video
    - Slot 2 (6:00 PM IST / 12:30 UTC): 9:16 Short on the same topic

    Removed (Oct 2026 audit):
    - Re-upload of another creator's YouTube video via yt-dlp (copyright strike +
      "reused content" demonetization risk; also blocked on GitHub runner IPs).
    - Third daily slot and the fixed 4-script rotation (same videos every 4 days =
      YouTube "inauthentic/repetitive content", policy updated 16 Jul 2026).
    """
    config = load_config()
    os.makedirs(batch_dir, exist_ok=True)
    youtube = get_authenticated_youtube_service()

    if not target_date_str:
        target_date_str = (datetime.utcnow() + timedelta(days=1)).strftime("%Y-%m-%d")

    print(f"\n=======================================================")
    print(f"🚀 RUNNING TIGER VLOGS BATCH FOR: {target_date_str}")
    print(f"=======================================================")

    results = []
    used = load_used_topics()
    used_titles = [u.get("title", "") for u in used]

    # Fallback pool, each used ONCE only (no rotation)
    TOPIC_POOL = [
        {
            "hook": "THE TRUTH ABOUT RECYCLED SAMOSA OIL! 😱",
            "title": "The Dark Truth of Street Food Samosa Oil! 😱 #FoodScience",
            "script": "Kya aapne socha hai ki jis kadhai me aapka tasty samosa tal raha hai, wo tel kitni baar reuse kiya gaya hai? FSSAI ke rules ke mutabik tel sirf teen baar garam ho sakta hai, lekin local stalls ise hafte bhar boil karte hain, jisse dangerous Total Polar Compounds aur Trans Fats bante hain! Hamesha fresh golden oil wale stalls se hi khana khayein!",
            "wiki": "Samosa",
            "tags": ["samosa", "street food oil", "food science", "indian street food", "healthy tips", "pure veg", "epic bharat", "tiger vlogs"]
        },
        {
            "hook": "HOW TO SPOT FAKE PANEER IN 5 SECONDS! 🧀⚠️",
            "title": "How to Spot Fake Paneer in 5 Seconds! 🧀⚠️ #FoodSafety",
            "script": "Market me milne wala sasta paneer aksar skimmed milk aur harmful starch ka mix hota hai. Iska test bahut aasan hai: paneer par do boond tincture iodine daalein. Agar wo neela ho jaye, toh usme sasta starch milaya gaya hai! Asli dairy paneer iodine se kabhi blue nahi hota. Apne parivar ko nakli khane se bachayein!",
            "wiki": "Paneer",
            "tags": ["paneer", "fake paneer test", "food adulteration", "street food india", "food science", "pure veg", "epic bharat", "tiger vlogs"]
        },
        {
            "hook": "THE SECRET OF FIRE PANI PURI! 🔥",
            "title": "The Crazy Science of Fire Pani Puri! 🔥 #FoodScience",
            "script": "Fire Pani Puri me aag kaise lagti hai? Isme edible clove oil ya pure alcohol ka use hota hai. Aag upar ki taraf jalti hai, isliye puri ka shell thanda rehta hai aur muh nahi jalta! Intense heat spices ke volatile oils ko release karti hai jo instant kick deta hai. Follow Epic Bharat for daily street food science!",
            "wiki": "Pani_puri",
            "tags": ["fire pani puri", "pani puri", "food science", "indian street food", "street food india", "epic bharat", "tiger vlogs"]
        }
    ]

    topic = topic_from_claude(used_titles)
    if not topic:
        fresh = [t for t in TOPIC_POOL if t["title"] not in used_titles]
        if not fresh:
            print("⏭️ No new topic (add ANTHROPIC_API_KEY or new TOPIC_POOL items). Skipping today to avoid repeat uploads.")
            return results
        topic = fresh[0]
    topic.setdefault("tags", ["street food india", "pure veg", "tiger vlogs"])
    credit = f"\n\n📷 Image: Wikipedia / Wikimedia Commons ({topic['wiki'].replace('_', ' ')}), CC BY-SA."

    # --- SLOT 1: Original 16:9 video ---
    pub_at_1 = f"{target_date_str}T07:30:00.000Z"
    v1_file = os.path.join(batch_dir, f"v1_{target_date_str}.mp4")
    print(f"\n[Slot 1 - {pub_at_1}] {topic['title']}")
    generate_original_longform_video(
        hook_headline=topic["hook"],
        hinglish_script=topic["script"],
        wiki_title=topic["wiki"],
        output_file=v1_file,
        voice="hi-IN-MadhurNeural"
    )
    v1_desc = (f"{topic['title']}\n\n{topic['script']}\n\n🌿 100% Pure Vegetarian.\n"
               f"📩 Business: {config['brand_email']}\n👉 Subscribe to {config['brand_handle']}{credit}")
    vid_1 = upload_video_to_youtube(youtube, v1_file, topic["title"], v1_desc, topic["tags"], publish_at=pub_at_1)
    if not vid_1:
        raise RuntimeError("TigerVlogs long-form upload was not confirmed; refusing to report a completed batch.")
    results.append({"slot": 1, "id": vid_1, "url": f"https://youtu.be/{vid_1}", "time": pub_at_1})
    if os.path.exists(v1_file): os.remove(v1_file)

    # --- SLOT 2: Original 9:16 Short, same topic ---
    pub_at_2 = f"{target_date_str}T12:30:00.000Z"
    v2_file = os.path.join(batch_dir, f"v2_short_{target_date_str}.mp4")
    print(f"\n[Slot 2 - {pub_at_2}] Short: {topic['title']}")
    generate_original_short(
        hook_headline=topic["hook"],
        hinglish_script=topic["script"],
        wiki_title=topic["wiki"],
        output_file=v2_file,
        voice="hi-IN-MadhurNeural"
    )
    v2_title = (topic["title"][:88] + " #Shorts")
    v2_desc = f"{topic['script']}\n\n🌿 100% Pure Vegetarian.\n👉 Subscribe to {config['brand_handle']}{credit}"
    vid_2 = upload_video_to_youtube(youtube, v2_file, v2_title, v2_desc, topic["tags"] + ["shorts"], publish_at=pub_at_2)
    if not vid_2:
        raise RuntimeError("TigerVlogs Short upload was not confirmed; batch is incomplete.")
    results.append({"slot": 2, "id": vid_2, "url": f"https://youtu.be/{vid_2}", "time": pub_at_2})
    if os.path.exists(v2_file): os.remove(v2_file)

    if results:
        used.append({"date": target_date_str, "title": topic["title"], "ids": [r["id"] for r in results]})
        save_used_topics(used)

    print("\n" + "="*60)
    print(f"🎉 COMPLETED BATCH FOR {target_date_str}:")
    for r in results:
        print(f" - Slot {r['slot']}: {r['url']} (Scheduled: {r['time']})")
    print("="*60)
    return results

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1].strip() else None
    run_daily_batch(target)
