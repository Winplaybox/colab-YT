"""
Master Release Scheduler for @TigerVlogs-2026
Automated daily execution engine for GitHub Actions & Google Colab.
Schedules 3 daily videos/shorts up to Year 2030 with automated quota protection.
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
sys.path.insert(0, script_dir)
from engine import (
    generate_original_longform_video,
    generate_original_short,
    remix_street_food_short,
    download_youtube_video
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

def run_daily_batch(target_date_str=None, batch_dir="/tmp/tiger_vlogs_batch"):
    """
    Executes the 3 daily release slots:
    - Slot 1 (1:00 PM IST / 07:30 UTC): 100% Original 16:9 4K Food Investigation Video
    - Slot 2 (6:00 PM IST / 12:30 UTC): 4K Ultra-Vertical Street Food Short (from queue or generated)
    - Slot 3 (8:45 PM IST / 15:15 UTC): 100% Original 16:9 4K Food Science Video
    """
    config = load_config()
    os.makedirs(batch_dir, exist_ok=True)
    youtube = get_authenticated_youtube_service()

    if not target_date_str:
        # Default to tomorrow's date
        target_date_str = (datetime.utcnow() + timedelta(days=1)).strftime("%Y-%m-%d")

    print(f"\n=======================================================")
    print(f"🚀 RUNNING TIGER VLOGS BATCH FOR: {target_date_str}")
    print(f"=======================================================")

    results = []

    # --- TOPICAL ARCHIVE FOR ORIGINAL INVESTIGATIONS ---
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
            "hook": "IS STREET FOOD LASSI SAFE IN SUMMER? 🥛❄️",
            "title": "Is Street Food Lassi Actually Pure? 🥛❄️ #FoodSecrets",
            "script": "Garmiyo me roadside lassi peene se pehle ye jaan lijiye! Kai vendors thick consistency dene ke liye dahi me blotting paper ya industrial thickeners use karte hain. Real dahi lassi natural sweetness aur mild sour taste deti hai, jabki fake lassi me unnatural chemical smell hoti hai. Hamesha trusted dairy se hi fresh lassi lein!",
            "wiki": "Lassi",
            "tags": ["lassi", "summer drink", "street food india", "pure veg", "food science", "epic bharat", "tiger vlogs"]
        },
        {
            "hook": "THE SECRET OF FIRE PANI PURI! 🔥",
            "title": "The Crazy Science of Fire Pani Puri! 🔥 #FoodScience",
            "script": "Fire Pani Puri me aag kaise lagti hai? Isme edible clove oil ya pure alcohol ka use hota hai. Aag upar ki taraf jalti hai, isliye puri ka shell thanda rehta hai aur muh nahi jalta! Intense heat spices ke volatile oils ko release karti hai jo instant kick deta hai. Follow Epic Bharat for daily street food science!",
            "wiki": "Pani_puri",
            "tags": ["fire pani puri", "pani puri", "food science", "indian street food", "street food india", "epic bharat", "tiger vlogs"]
        }
    ]

    day_num = int(target_date_str.replace("-", "")) % len(TOPIC_POOL)
    day_topic_1 = TOPIC_POOL[day_num]
    day_topic_2 = TOPIC_POOL[(day_num + 1) % len(TOPIC_POOL)]

    # --- SLOT 1: Original 16:9 Food Investigation ---
    pub_at_1 = f"{target_date_str}T07:30:00.000Z"
    v1_file = os.path.join(batch_dir, f"v1_investigation_{target_date_str}.mp4")
    print(f"\n[Slot 1 - {pub_at_1}] Generating 16:9 Original Investigation...")
    generate_original_longform_video(
        hook_headline=day_topic_1["hook"],
        hinglish_script=day_topic_1["script"],
        wiki_title=day_topic_1["wiki"],
        output_file=v1_file,
        voice="hi-IN-MadhurNeural"
    )

    v1_desc = f"{day_topic_1['title']}\n\n{day_topic_1['script']}\n\n🌿 100% Pure Vegetarian & Food Science Content.\n📩 Business: {config['brand_email']}\n👉 Subscribe to {config['brand_handle']} for daily truths!"
    vid_1 = upload_video_to_youtube(youtube, v1_file, day_topic_1["title"], v1_desc, day_topic_1["tags"], publish_at=pub_at_1)
    if vid_1:
        results.append({"slot": 1, "id": vid_1, "url": f"https://youtu.be/{vid_1}", "time": pub_at_1})
    if os.path.exists(v1_file): os.remove(v1_file)

    # --- SLOT 2: 4K Ultra-Vertical Street Food Short (From queue or generated fallback) ---
    pub_at_2 = f"{target_date_str}T12:30:00.000Z"
    v2_file = os.path.join(batch_dir, f"v2_streetfood_short_{target_date_str}.mp4")
    print(f"\n[Slot 2 - {pub_at_2}] Preparing 4K Ultra-Vertical Short...")

    raw_video_url = "https://www.youtube.com/watch?v=ZF58UKMciVc" # Sheermal Wala
    dl_info = download_youtube_video(raw_video_url, output_path=batch_dir)

    if dl_info and dl_info.get("filepath") and os.path.exists(dl_info["filepath"]):
        remix_street_food_short(dl_info["filepath"], "AJMER'S CRAZIEST DRY FRUIT SHEERMAL! 👑🔥", v2_file, duration=28)
        if os.path.exists(dl_info["filepath"]): os.remove(dl_info["filepath"])
        v2_title = "Ajmer's Craziest Dry Fruit Sheermal! 🤤🔥 #Shorts"
        v2_desc = f"👑 World-Famous Dry Fruit Sheermal in Ajmer!\n\nLocation: Dargah Bazar, Ajmer, Rajasthan.\n🌿 100% Pure Vegetarian Street Food.\n👉 Subscribe to {config['brand_handle']} for daily street food shorts!"
        v2_tags = ["sheermal", "ajmer street food", "street food india", "dry fruits", "pure veg", "epic bharat", "shorts"]
    else:
        print("Using 100% original 4K Short generator fallback...")
        generate_original_short(
            hook_headline="CRAZIEST DRY FRUIT SHEERMAL! 👑🤤",
            hinglish_script="Ajmer ka ye world famous Dry Fruit Sheermal dekh kar aapke hosh udd jayenge! Isme daale jaate hain dhero kaju, badam, pista aur asli desi ghee! Pure vegetarian royal Indian street food. Subscribe to Epic Bharat for daily street food discoveries!",
            wiki_title="Sheermal",
            output_file=v2_file,
            voice="hi-IN-MadhurNeural"
        )
        v2_title = "Ajmer's Royal Dry Fruit Sheermal! 🤤🔥 #Shorts"
        v2_desc = f"👑 World-Famous Dry Fruit Sheermal in Ajmer!\n\n🌿 100% Pure Vegetarian Street Food.\n👉 Subscribe to {config['brand_handle']} for daily street food shorts!"
        v2_tags = ["sheermal", "ajmer street food", "street food india", "dry fruits", "pure veg", "epic bharat", "shorts"]

    vid_2 = upload_video_to_youtube(youtube, v2_file, v2_title, v2_desc, v2_tags, publish_at=pub_at_2)
    if vid_2:
        results.append({"slot": 2, "id": vid_2, "url": f"https://youtu.be/{vid_2}", "time": pub_at_2})
    if os.path.exists(v2_file): os.remove(v2_file)

    # --- SLOT 3: Original 16:9 Food Science Video ---
    pub_at_3 = f"{target_date_str}T15:15:00.000Z"
    v3_file = os.path.join(batch_dir, f"v3_science_{target_date_str}.mp4")
    print(f"\n[Slot 3 - {pub_at_3}] Generating 16:9 Original Science Discovery...")
    generate_original_longform_video(
        hook_headline=day_topic_2["hook"],
        hinglish_script=day_topic_2["script"],
        wiki_title=day_topic_2["wiki"],
        output_file=v3_file,
        voice="hi-IN-MadhurNeural"
    )

    v3_desc = f"{day_topic_2['title']}\n\n{day_topic_2['script']}\n\n🌿 100% Pure Vegetarian & Food Science Content.\n📩 Business: {config['brand_email']}\n👉 Subscribe to {config['brand_handle']} for daily food science!"
    vid_3 = upload_video_to_youtube(youtube, v3_file, day_topic_2["title"], v3_desc, day_topic_2["tags"], publish_at=pub_at_3)
    if vid_3:
        results.append({"slot": 3, "id": vid_3, "url": f"https://youtu.be/{vid_3}", "time": pub_at_3})
    if os.path.exists(v3_file): os.remove(v3_file)

    print("\n" + "="*60)
    print(f"🎉 COMPLETED BATCH FOR {target_date_str}:")
    for r in results:
        print(f" - Slot {r['slot']}: {r['url']} (Scheduled: {r['time']})")
    print("="*60)
    return results

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1].strip() else None
    run_daily_batch(target)
