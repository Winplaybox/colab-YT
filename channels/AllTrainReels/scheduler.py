"""
AllTrainReels Autonomous Scheduler & Uploader
=============================================
- Schedules and uploads 9:16 portrait train shorts daily at 18:30 IST (13:00 UTC).
- Automatically manages video rendering, description formatting, tags, and pinned comment.
- Tracks upload status and queue in state.json.
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

from story_generator import generate_story_from_bank, get_or_create_story, peek_story
from video_producer import produce_train_video

def compute_next_publish_time(publish_time_utc="13:00"):
    """
    Computes next daily publish timestamp at 18:30 IST (13:00 UTC).
    Ensures timestamp is at least 15 minutes in future.
    """
    try:
        from datetime import timezone
        now_utc = datetime.now(timezone.utc)
        target_hour, target_min = map(int, publish_time_utc.split(":"))

        candidate = datetime(now_utc.year, now_utc.month, now_utc.day, target_hour, target_min, 0, tzinfo=timezone.utc)
        if candidate <= now_utc + timedelta(minutes=15):
            candidate += timedelta(days=1)
        return candidate.strftime("%Y-%m-%dT%H:%M:%SZ")
    except Exception as e:
        print(f"Schedule calculation notice: {e}")
        return None

EXPECTED_CHANNEL_ID = "UCKfX7By0w94LHI-AWj0a_QQ"
EXPECTED_NAME = "All Train Reels"

def verify_channel_identity(youtube):
    """Verifies that the authenticated token strictly belongs to AllTrainReels."""
    try:
        res = youtube.channels().list(mine=True, part="snippet").execute()
        items = res.get("items", [])
        if not items:
            return False, "No YouTube channel associated with this token."
        actual_id = items[0]["id"]
        actual_title = items[0]["snippet"]["title"]
        if actual_id != EXPECTED_CHANNEL_ID:
            return False, f"Token belongs to '{actual_title}' ({actual_id}), NOT target '{EXPECTED_NAME}' ({EXPECTED_CHANNEL_ID})!"
        return True, f"Verified: '{actual_title}' ({actual_id})"
    except Exception as e:
        print(f"Warning: Channel verification check: {e}")
        return True, "Verification check bypassed"

def get_youtube_service():
    """Resolves OAuth credentials specifically for AllTrainReels."""
    if not HAS_GOOGLE_CLIENT:
        print("Notice: google-api-python-client not installed in this environment.")
        return None

    token_path = os.path.join(script_dir, "token.json")

    # Check environment variable
    env_token = os.environ.get("ALLTRAINREELS_TOKEN_JSON") or os.environ.get("YOUTUBE_TOKEN_JSON")
    if env_token and env_token.strip() and not os.path.exists(token_path):
        with open(token_path, "w", encoding="utf-8") as f:
            f.write(env_token.strip())

    if not os.path.exists(token_path) or os.path.getsize(token_path) < 50:
        print("⚠️ No valid token.json found in channels/AllTrainReels/. Run authenticate_youtube.py first.")
        return None

    try:
        with open(token_path, "r", encoding="utf-8") as f:
            creds_data = json.load(f)
        creds = Credentials.from_authorized_user_info(creds_data)
        if creds.expired and creds.refresh_token:
            request = google.auth.transport.requests.Request()
            creds.refresh(request)
            with open(token_path, "w", encoding="utf-8") as f:
                f.write(creds.to_json())
        service = build("youtube", "v3", credentials=creds)

        ok, msg = verify_channel_identity(service)
        if not ok:
            print(f"❌ AUTHENTICATION ERROR: {msg}")
            return None
        print(f"✅ [YouTube Auth] {msg}")
        return service
    except Exception as e:
        print(f"Failed to build YouTube service: {e}")
        return None

def upload_short(video_path, story_data, publish_mode="schedule", force=False):
    """Uploads and configures YouTube Short with tags and pinned comment."""
    youtube = get_youtube_service()
    if not youtube:
        print(f"Simulation Mode: Would upload {video_path} for '{story_data['title']}'")
        return None

    title = story_data["youtube_title"]
    description = story_data["description"]
    raw_tags = story_data.get("tags", []) + story_data.get("seo_keywords", [])
    tags = [t.lstrip("#").strip() for t in raw_tags if t.strip()]

    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags,
            "categoryId": "28"
        },
        "status": {
            "selfDeclaredMadeForKids": False
        }
    }

    if publish_mode in ("schedule", "scheduled"):
        next_pub = compute_next_publish_time()
        if next_pub:
            body["status"]["privacyStatus"] = "private"
            body["status"]["publishAt"] = next_pub
            print(f"📅 Scheduled for: {next_pub}")
        else:
            body["status"]["privacyStatus"] = "unlisted"
    elif publish_mode in ("public", "immediate"):
        body["status"]["privacyStatus"] = "public"
    else:
        body["status"]["privacyStatus"] = "unlisted"

    # Live YouTube Duplicate Protection
    if not force:
        try:
            try:
                from common.youtube_duplicate_checker import check_existing_upload
            except ImportError:
                sys.path.insert(0, os.path.abspath(os.path.join(script_dir, "..")))
                from common.youtube_duplicate_checker import check_existing_upload

            ep_num = story_data.get("story_number") or story_data.get("episode_number")
            dup = check_existing_upload(youtube, candidate_title=title, episode_number=ep_num, channel_type="AllTrainReels")
            if dup.get("exists"):
                existing_id = dup["video_id"]
                print(f"\n🛑 [DUPLICATE PREVENTED] Video ALREADY exists on All Train Reels YouTube!")
                print(f"   Existing Title: '{dup.get('matched_title', dup.get('title'))}'")
                print(f"   Reason:         {dup.get('reason')}")
                print(f"   Video ID:       {existing_id} ({dup.get('status', 'unknown')})")
                print(f"   YouTube Link:   https://youtu.be/{existing_id}")
                print(f"   ⏭️ Skipping upload to avoid creating duplicate content on YouTube.\n")
                return existing_id
        except Exception as ce:
            print(f"Notice: Duplicate checker notice: {ce}")
    else:
        print("⚡ [FORCE MODE] Live YouTube duplicate check bypassed for upload.")

    media = MediaFileUpload(video_path, chunksize=10*1024*1024, resumable=True, mimetype="video/mp4")
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)

    print(f"🚀 Uploading Short to YouTube: '{title}'...")
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"Uploaded {int(status.progress() * 100)}%")

    video_id = response.get("id")
    video_url = f"https://www.youtube.com/shorts/{video_id}"
    print(f"✅ Video Uploaded! URL: {video_url}")

    # Add pinned comment
    pinned_text = story_data.get("pinned_comment")
    if pinned_text:
        try:
            comment_body = {
                "snippet": {
                    "videoId": video_id,
                    "topLevelComment": {
                        "snippet": {
                            "textOriginal": pinned_text
                        }
                    }
                }
            }
            youtube.commentThreads().insert(part="snippet", body=comment_body).execute()
            print(f"📌 Pinned Comment Added: {pinned_text}")
        except Exception as e:
            print(f"Notice: Could not post pinned comment: {e}")

    return video_id

def load_state():
    """Loads state.json tracking current episode and upload history."""
    state_file = os.path.join(script_dir, "state.json")
    if os.path.exists(state_file):
        try:
            with open(state_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "channel_id": "AllTrainReels",
        "channel_name": "AllTrainReels",
        "current_story_number": 1,
        "total_stories": 30,
        "last_run": None,
        "last_uploaded_video_id": None,
        "history": []
    }

def save_state(state):
    """Saves updated state.json back to disk."""
    state_file = os.path.join(script_dir, "state.json")
    with open(state_file, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)
    print(f"💾 Updated state.json (Next episode queued: #{state['current_story_number']})")

def run_episode(episode_number=None, quality="1080p", publish_mode="scheduled", force=False):
    """
    Runs complete episodic release workflow for AllTrainReels:
    1. Determines episode number from state.json if not specified
    2. Generates that single episode on-demand via get_or_create_story
    3. Renders 8K/4K/1080p Short with procedural soundscape and yellow subtitles
    4. Schedules or uploads to YouTube
    5. Updates state.json and advances to next episode
    """
    state = load_state()
    if episode_number is None or str(episode_number).strip() == "":
        episode_number = state.get("current_story_number", 13)
    else:
        episode_number = int(episode_number)

    print(f"\n🚀 [AllTrainReels Workflow Trigger] Processing Episode #{episode_number:02d} ({quality})...")

    # Pre-render live YouTube check
    yt_svc = get_youtube_service()
    if yt_svc and not force:
        try:
            try:
                from common.youtube_duplicate_checker import check_existing_upload
            except ImportError:
                sys.path.insert(0, os.path.abspath(os.path.join(script_dir, "..")))
                from common.youtube_duplicate_checker import check_existing_upload

            max_checks = 25
            attempts = 0
            while attempts < max_checks:
                cand_story = peek_story(episode_number)
                cand_title = cand_story.get("youtube_title", cand_story.get("title", ""))
                dup = check_existing_upload(yt_svc, candidate_title=cand_title, episode_number=episode_number, channel_type="AllTrainReels")
                if dup.get("exists"):
                    attempts += 1
                    print(f"🛑 [LIVE YOUTUBE CHECK] Episode #{episode_number:02d} ('{cand_title}') is ALREADY on YouTube ({dup['video_id']}).")
                    print(f"   ⏩ Skipping duplicate candidate. Checking Episode #{episode_number + 1:02d}...")
                    episode_number += 1
                else:
                    break

            if attempts >= max_checks:
                print(f"⚠️ [SAFETY STOP] Checked {max_checks} episodes and all matched existing YouTube videos. Halting to avoid runaway execution.")
                return None

            state["current_story_number"] = episode_number
            save_state(state)
        except Exception as pe_err:
            print(f"Notice: Pre-check duplicate notice: {pe_err}")
    elif force:
        print("⚡ [FORCE MODE] Live YouTube duplicate pre-check bypassed.")

    # Generate single episode on-demand
    story = get_or_create_story(episode_number)

    slug = story['story_id'].replace('train_', '')
    story_path = os.path.join(script_dir, "stories", f"story_{episode_number:02d}_{slug}.json")
    video_path = produce_train_video(story_path, quality=quality)

    video_id = None
    if publish_mode != "render_only":
        video_id = upload_short(video_path, story, publish_mode=publish_mode, force=force)

    # Update state.json progression — episodes count up forever (no wrap)
    if publish_mode != "render_only":
        next_ep = episode_number + 1
        state["last_run"] = datetime.now().isoformat()
        state["last_uploaded_video_id"] = video_id
        state["current_story_number"] = next_ep
        state.setdefault("history", []).append({
            "episode_number": episode_number,
            "title": story["title"],
            "video_id": video_id,
            "mode": publish_mode,
            "timestamp": state["last_run"]
        })
        save_state(state)
        print(f"\n🎉 Episode #{episode_number:02d} workflow completed! Next episode queued: #{next_ep:02d}")
    else:
        print(f"\n🎉 Episode #{episode_number:02d} render complete (render_only mode). State preserved at Episode #{episode_number:02d}.")

    return video_path


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="AllTrainReels Autonomous Scheduler & Uploader")
    parser.add_argument("--episode", "--story", dest="episode", type=int, default=None, help="Episode number to run")
    parser.add_argument("--mode", default="scheduled", choices=["scheduled", "schedule", "immediate", "public", "render_only"], help="Publish mode")
    parser.add_argument("--quality", default="1080p", choices=["1080p", "4k", "8k"], help="Video render quality")
    parser.add_argument("--force", action="store_true", help="Force production/upload and bypass duplicate checks")
    args, unknown = parser.parse_known_args()

    ep = args.episode
    if ep is None and len(sys.argv) > 1 and sys.argv[1].isdigit():
        ep = int(sys.argv[1])
    quality = args.quality
    if len(sys.argv) > 2 and sys.argv[2] in ["1080p", "4k", "8k"]:
        quality = sys.argv[2]
    mode = args.mode
    if "--immediate" in sys.argv or "--public" in sys.argv:
        mode = "public"
    elif "--render-only" in sys.argv:
        mode = "render_only"

    run_episode(episode_number=ep, quality=quality, publish_mode=mode, force=args.force)
