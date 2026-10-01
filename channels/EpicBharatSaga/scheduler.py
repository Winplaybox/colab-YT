"""
EpicBharatSaga Autonomous Scheduler & Uploader
===============================================
Produces and uploads one mythology Short daily at 19:00 IST (13:30 UTC).
Seasons progress automatically: Shiva → Vishnu → Durga → Hanuman → Ganesha → ...
All stories are unique — tracked via state.json used_story_ids.
"""

import os
import sys
import json
import time
from datetime import datetime, timedelta

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

try:
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload
    from googleapiclient.errors import HttpError
    from google.oauth2.credentials import Credentials
    import google.auth.transport.requests
    HAS_GOOGLE_CLIENT = True
except ImportError:
    HAS_GOOGLE_CLIENT = False

script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

from story_generator import generate_story_from_bank
from video_producer import produce_train_video   # reuses same producer logic

EXPECTED_CHANNEL_ID = "UCakmjqTBA6KgCF2F30Tnpjg"
EXPECTED_NAME = "EpicBharatSaga"


def compute_next_publish_time(publish_time_utc="13:30"):
    """Computes next daily publish at 19:00 IST (13:30 UTC)."""
    try:
        from datetime import timezone
        now_utc = datetime.now(timezone.utc)
        h, m = map(int, publish_time_utc.split(":"))
        candidate = datetime(now_utc.year, now_utc.month, now_utc.day, h, m, 0, tzinfo=timezone.utc)
        if candidate <= now_utc + timedelta(minutes=15):
            candidate += timedelta(days=1)
        return candidate.strftime("%Y-%m-%dT%H:%M:%SZ")
    except Exception as e:
        print(f"Schedule calc error: {e}")
        return None


def verify_channel_identity(youtube):
    """Verifies token belongs to EpicBharatSaga."""
    try:
        res = youtube.channels().list(mine=True, part="snippet").execute()
        if res.get("items"):
            ch = res["items"][0]
            cid = ch["id"]
            name = ch["snippet"]["title"]
            if cid != EXPECTED_CHANNEL_ID:
                print(f"⛔ WRONG CHANNEL: token belongs to '{name}' ({cid}). Expected {EXPECTED_NAME}.")
                sys.exit(1)
            print(f"✅ Channel verified: {name} ({cid})")
            return True
    except Exception as e:
        print(f"Channel verify warning: {e}")
    return False


def load_credentials():
    """Loads YouTube credentials from token.json."""
    token_path = os.path.join(script_dir, "token.json")
    env_token = os.environ.get("EPICBHARATSAGA_TOKEN_JSON")

    if env_token:
        try:
            data = json.loads(env_token)
            creds = Credentials.from_authorized_user_info(data)
            if creds.expired and creds.refresh_token:
                creds.refresh(google.auth.transport.requests.Request())
            return creds
        except Exception as e:
            print(f"[WARN] Env token issue: {e}")

    if os.path.exists(token_path):
        try:
            with open(token_path, "r") as f:
                data = json.load(f)
            creds = Credentials.from_authorized_user_info(data)
            if creds.expired and creds.refresh_token:
                creds.refresh(google.auth.transport.requests.Request())
            return creds
        except Exception as e:
            print(f"[WARN] Token file issue: {e}")

    return None


def load_state():
    """Loads state.json."""
    state_file = os.path.join(script_dir, "state.json")
    try:
        with open(state_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"current_episode": 1, "used_story_ids": [], "history": []}


def save_state(state):
    """Saves state.json."""
    state_file = os.path.join(script_dir, "state.json")
    with open(state_file, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)


def upload_short(video_path, story, publish_mode="scheduled"):
    """Uploads the mythology Short to EpicBharatSaga YouTube channel."""
    if not HAS_GOOGLE_CLIENT:
        print("[WARN] google-api-python-client not available. Skipping upload.")
        return None

    creds = load_credentials()
    if not creds:
        print("[ERROR] No valid credentials found for EpicBharatSaga.")
        return None

    youtube = build("youtube", "v3", credentials=creds)
    verify_channel_identity(youtube)

    publish_at = compute_next_publish_time("13:30") if publish_mode == "scheduled" else None

    status_body = {"privacyStatus": "public" if publish_mode == "immediate" else "private"}
    if publish_at:
        status_body = {"privacyStatus": "private", "publishAt": publish_at}

    ep_num = story.get("episode_number", 1)
    deity = story.get("deity", "Hindu Mythology")
    season = story.get("season", 1)

    request_body = {
        "snippet": {
            "title": story["youtube_title"],
            "description": story["description"],
            "tags": story.get("tags", []) + ["EpicBharatSaga", "HinduMythology", "SanatanDharma"],
            "categoryId": "22",
            "defaultLanguage": "hi",
        },
        "status": status_body
    }

    print(f"\n🔱 Uploading EpicBharatSaga Ep #{ep_num:03d} | Season {season} — {deity}")
    print(f"   Title: {story['youtube_title']}")

    media = MediaFileUpload(video_path, mimetype="video/mp4", resumable=True, chunksize=256 * 1024)
    insert = youtube.videos().insert(part="snippet,status", body=request_body, media_body=media)

    video_id = None
    response = None
    while response is None:
        try:
            status, response = insert.next_chunk()
            if status:
                pct = int(status.resumable_progress / status.total_size * 100)
                print(f"   Upload progress: {pct}%")
        except HttpError as e:
            print(f"[ERROR] Upload failed: {e}")
            return None

    video_id = response.get("id")
    video_url = f"https://www.youtube.com/watch?v={video_id}"
    print(f"✅ Uploaded! Video ID: {video_id}")
    print(f"   URL: {video_url}")
    if publish_at:
        print(f"   Scheduled for: {publish_at} UTC (19:00 IST)")

    # Post pinned comment
    try:
        pinned = story.get("pinned_comment", "🔱 Jai Mata Di! Jai Shri Ram! Om Namah Shivaya!")
        youtube.commentThreads().insert(
            part="snippet",
            body={"snippet": {"videoId": video_id, "topLevelComment": {"snippet": {"textOriginal": pinned}}}}
        ).execute()
        print(f"✅ Pinned comment posted")
    except Exception as e:
        print(f"[WARN] Pinned comment: {e}")

    return video_id


def run_episode(episode_number=None, publish_mode="scheduled", quality="1080p"):
    """Full pipeline: story → images → TTS → video → upload."""
    state = load_state()
    episode_number = episode_number or state.get("current_episode", 1)

    print(f"\n{'='*70}")
    print(f"🔱 EpicBharatSaga — Episode #{episode_number:03d}")
    print(f"{'='*70}\n")

    # 1. Generate story
    story = generate_story_from_bank(episode_number)
    print(f"\n📖 Story: [{story.get('deity', '')} S{story.get('season', 1)}] {story['youtube_title']}")

    # 2. Generate images
    from image_generator import generate_story_assets
    story_files = [f for f in os.listdir(os.path.join(script_dir, "stories"))
                   if f.startswith(f"story_{episode_number:03d}_") and f.endswith(".json")]
    if story_files:
        story_json_path = os.path.join(script_dir, "stories", story_files[0])
        asset_dir = generate_story_assets(story_json_path)
    else:
        asset_dir = None

    # 3. Produce video
    video_path = produce_train_video(story, quality=quality)
    if not video_path:
        print("[ERROR] Video production failed.")
        return None

    # 4. Upload
    video_id = None
    if publish_mode != "render_only":
        video_id = upload_short(video_path, story, publish_mode=publish_mode)

    # 5. Update state
    next_ep = episode_number + 1
    state["last_run"] = datetime.now().isoformat()
    state["last_uploaded_video_id"] = video_id
    state["current_episode"] = next_ep
    state["current_deity"] = story.get("deity", "Lord Shiva")
    state["current_season"] = story.get("season", 1)
    state["history"].append({
        "episode_number": episode_number,
        "deity": story.get("deity"),
        "season": story.get("season"),
        "title": story["title"],
        "video_id": video_id,
        "mode": publish_mode,
        "timestamp": state["last_run"]
    })
    save_state(state)
    print(f"\n🎉 Episode #{episode_number:03d} done! Next: #{next_ep:03d} [{story.get('deity', '')}]")
    return video_path


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--episode", type=int, default=None)
    parser.add_argument("--mode", default="scheduled", choices=["scheduled", "immediate", "render_only"])
    parser.add_argument("--quality", default="4k", choices=["1080p", "4k", "8k"])
    args = parser.parse_args()
    run_episode(episode_number=args.episode, publish_mode=args.mode, quality=args.quality)
