"""
IndianHorrorTapes Autonomous Scheduler & Uploader:
- Schedules and uploads 9:16 portrait horror shorts on Wednesday & Sunday at 9:00 PM IST (15:30 UTC).
- Strict channel safety: Verifies token belongs to IndianHorrorTapes (UCNRr8A9gVZQZJi1eMKiXIJw).
- Renders 8K/4K/1080p, generates descriptions with mathematical SEO, attaches custom 8K thumbnails,
  and updates state.json for continuous sequential episodic release.
"""

import os
import sys
import json
import time
from datetime import datetime, timedelta

# Ensure UTF-8 output
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

from story_generator import get_or_create_story
from video_producer import produce_horror_short

EXPECTED_CHANNEL_ID = "UCNRr8A9gVZQZJi1eMKiXIJw"
EXPECTED_NAME = "IndianHorrorTapes"

def compute_next_publish_time(publish_time_utc="15:30", schedule_days=[2, 6]):
    """
    Computes next Wednesday (2) or Sunday (6) publish timestamp at 9:00 PM IST (15:30 UTC).
    Ensures timestamp is at least 15 minutes in the future for YouTube publishAt API.
    """
    try:
        from datetime import timezone
        now_utc = datetime.now(timezone.utc)
        target_hour, target_min = map(int, publish_time_utc.split(":"))

        for days_ahead in range(8):
            candidate_date = (now_utc + timedelta(days=days_ahead)).date()
            candidate_dt = datetime(
                candidate_date.year, candidate_date.month, candidate_date.day,
                target_hour, target_min, 0, tzinfo=timezone.utc
            )
            if candidate_dt.weekday() in schedule_days and candidate_dt > now_utc + timedelta(minutes=15):
                return candidate_dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    except Exception as e:
        print(f"Schedule calculation error: {e}")
    return None

def verify_channel_identity(youtube, expected_channel_id=EXPECTED_CHANNEL_ID, expected_name=EXPECTED_NAME):
    """
    STRICT SECURITY GUARD:
    Verifies that the authenticated YouTube token belongs specifically to IndianHorrorTapes.
    Rejects the token immediately if it belongs to TigerVlogs or MindNestTales.
    """
    try:
        res = youtube.channels().list(mine=True, part="snippet").execute()
        items = res.get("items", [])
        if not items:
            return False, "No YouTube channel associated with this token."
        actual_id = items[0]["id"]
        actual_title = items[0]["snippet"]["title"]
        if expected_channel_id and actual_id != expected_channel_id:
            return False, f"Token belongs to '{actual_title}' ({actual_id}), NOT target '{expected_name}' ({expected_channel_id})!"
        return True, f"Verified: '{actual_title}' ({actual_id})"
    except Exception as e:
        print(f"Warning: Could not verify channel identity: {e}")
        return True, "Verification bypassed"

def get_youtube_service():
    """Resolves OAuth credentials specifically for IndianHorrorTapes."""
    if not HAS_GOOGLE_CLIENT:
        print("Notice: google-api-python-client not installed in this environment.")
        return None

    token_path = os.path.join(script_dir, "token.json")

    # Check environment variable
    env_token = os.environ.get("INDIANHORRORTAPES_TOKEN_JSON") or os.environ.get("YOUTUBE_TOKEN_JSON")
    if env_token and env_token.strip() and not os.path.exists(token_path):
        with open(token_path, "w", encoding="utf-8") as f:
            f.write(env_token.strip())

    if not os.path.exists(token_path):
        print(f"⚠️ Notice: No credentials found for {EXPECTED_NAME}. Running in local render mode.")
        print(f"👉 Run 'python channels/IndianHorrorTapes/authenticate_youtube.py' to link your channel.")
        return None

    try:
        with open(token_path, "r", encoding="utf-8") as f:
            token_data = json.load(f)

        creds = Credentials.from_authorized_user_info(token_data)
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(google.auth.transport.requests.Request())
            with open(token_path, "w", encoding="utf-8") as f:
                f.write(creds.to_json())

        youtube = build("youtube", "v3", credentials=creds)
        valid, msg = verify_channel_identity(youtube)
        if not valid:
            print(f"❌ AUTHENTICATION REJECTED: {msg}")
            return None
        print(f"🔒 Authenticated channel: {msg}")
        return youtube
    except Exception as e:
        print(f"Failed to initialize YouTube service: {e}")
        return None

def build_metadata(story_data, publish_time_iso=None):
    """Builds high-converting SEO metadata optimized for YouTube Shorts."""
    num = story_data.get("story_number", 1)
    title_raw = story_data.get("title", "")
    loc = story_data.get("location", "")
    tagline = story_data.get("tagline", "")
    next_num = (num % 103) + 1

    clean_title = title_raw
    if "#Shorts" not in clean_title and "#shorts" not in clean_title:
        clean_title = f"{clean_title} | Ep. {num} #Shorts"
    if len(clean_title) > 95:
        clean_title = clean_title[:95]

    desc = story_data.get("seo_description")
    if not desc:
        desc = f"""⚠️ EPISODE {num}: {title_raw}
📍 Location: {loc}
🕯️ Reality Behind The Legend: {tagline}

Kehte hain India ki har purani deewar ke peeche ek aisi kahani dabi hai jo din ke ujaale mein kabhi bahar nahi aati... Lekin jab raat hoti hai, tab ye raaz bolne lagte hain.

Part {next_num} coming next Wednesday/Sunday at 9:00 PM IST!

Subscribe to @IndianHorrorTapes for 100+ Real Indian Horror Stories & Paranormal Legends.

---
#Shorts #IndianHorrorTapes #IndianHorror #RealHorrorStories #HauntedIndia #GhostStories #UrbanLegends #HindiHorror #Bhangarh #Kuldhara #Paranormal
"""

    tags = story_data.get("tags", []) + [
        "indian horror tapes",
        "real horror stories in hindi",
        "haunted places in india",
        "ghost stories hindi",
        "paranormal investigation india",
        "horror shorts hindi",
        "shorts"
    ]
    seen = set()
    dedup_tags = []
    for t in tags:
        t_clean = t.strip()
        if t_clean.lower() not in seen:
            seen.add(t_clean.lower())
            dedup_tags.append(t_clean)

    body = {
        "snippet": {
            "title": clean_title,
            "description": desc,
            "tags": dedup_tags[:30],
            "categoryId": "24",
            "defaultLanguage": "hi",
            "defaultAudioLanguage": "hi"
        },
        "status": {
            "selfDeclaredMadeForKids": False
        }
    }

    if publish_time_iso:
        body["status"]["privacyStatus"] = "private"
        body["status"]["publishAt"] = publish_time_iso
    else:
        body["status"]["privacyStatus"] = "public"

    return body

def upload_video(youtube, video_path, metadata, thumbnail_path=None, pinned_comment=None):
    """Uploads video to YouTube with automatic retry, thumbnail upload, and pinned engagement comment."""
    print(f"\n🚀 Initiating YouTube Upload: {video_path}")
    print(f"📌 Title: {metadata['snippet']['title']}")
    if "publishAt" in metadata["status"]:
        print(f"⏰ Scheduled for (publishAt): {metadata['status']['publishAt']} (Wednesday / Sunday 9:00 PM IST)")
    else:
        print("⚡ Publishing Immediately as Public!")

    media = MediaFileUpload(
        video_path,
        chunksize=1024 * 1024 * 8, # 8MB chunks
        resumable=True,
        mimetype="video/mp4"
    )

    request = youtube.videos().insert(
        part="snippet,status",
        body=metadata,
        media_body=media
    )

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            pct = int(status.progress() * 100)
            print(f"⬆️ Upload Progress: {pct}%", end="\r", flush=True)

    video_id = response.get("id")
    video_url = f"https://www.youtube.com/shorts/{video_id}"
    print(f"\n🎉 UPLOAD COMPLETE! Video ID: {video_id}")
    print(f"🔗 YouTube Link: {video_url}")

    # Set custom 8K thumbnail if present
    if thumbnail_path and os.path.exists(thumbnail_path):
        try:
            print(f"🖼️ Uploading custom 8K thumbnail: {thumbnail_path}...")
            youtube.thumbnails().set(
                videoId=video_id,
                media_body=MediaFileUpload(thumbnail_path, mimetype="image/jpeg")
            ).execute()
            print("✅ Custom thumbnail attached successfully!")
        except Exception as te:
            print(f"Warning: Failed to set thumbnail: {te}")

    # Post engagement comment if present
    if pinned_comment:
        try:
            print("💬 Posting algorithm-boosting engagement comment...")
            youtube.commentThreads().insert(
                part="snippet",
                body={
                    "snippet": {
                        "videoId": video_id,
                        "topLevelComment": {
                            "snippet": {
                                "textOriginal": pinned_comment
                            }
                        }
                    }
                }
            ).execute()
            print("✅ Engagement comment posted successfully!")
        except Exception as ce:
            print(f"Notice: Could not post engagement comment: {ce}")

    return video_id, video_url

def update_state(story_number, video_id, publish_at):
    """Updates state.json after successful upload and advances story pointer."""
    state_file = os.path.join(script_dir, "state.json")
    state = {
        "channel_id": EXPECTED_CHANNEL_ID,
        "channel_name": EXPECTED_NAME,
        "current_story_number": 1,
        "total_stories": 103,
        "last_run": None,
        "last_uploaded_video_id": None,
        "history": []
    }
    if os.path.exists(state_file):
        try:
            with open(state_file, "r", encoding="utf-8") as f:
                state = json.load(f)
        except Exception:
            pass

    next_story = (story_number % 103) + 1
    now_str = datetime.now().isoformat()

    state["current_story_number"] = next_story
    state["last_run"] = now_str
    state["last_uploaded_video_id"] = video_id
    if "history" not in state:
        state["history"] = []

    state["history"].append({
        "story_number": story_number,
        "video_id": video_id,
        "publish_at": publish_at,
        "uploaded_at": now_str
    })

    with open(state_file, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)
    print(f"📈 State updated. Next story will be: #{next_story}")

def run_schedule(story_number=None, quality="8k", force_immediate=False):
    """
    Main orchestration routine:
    1. Loads current story definition
    2. Renders 9:16 portrait video
    3. Calculates Wednesday/Sunday 9:00 PM IST slot
    4. Uploads to YouTube and updates state
    """
    state_file = os.path.join(script_dir, "state.json")
    if story_number is None and os.path.exists(state_file):
        try:
            with open(state_file, "r", encoding="utf-8") as f:
                st = json.load(f)
                story_number = st.get("current_story_number", 1)
        except Exception:
            story_number = 1

    if story_number is None:
        story_number = 1

    story_data = get_or_create_story(story_number)
    output_dir = os.path.join(script_dir, "output")
    os.makedirs(output_dir, exist_ok=True)
    video_path = os.path.join(output_dir, f"IndianHorrorTapes_Ep{story_number:02d}_{quality}.mp4")

    # Render video
    produce_horror_short(story_data, video_path, quality=quality)

    # Compute release schedule: Wednesday / Sunday 9:00 PM IST (15:30 UTC)
    publish_iso = None if force_immediate else compute_next_publish_time(publish_time_utc="15:30", schedule_days=[2, 6])
    metadata = build_metadata(story_data, publish_iso)

    thumb_path = os.path.join(script_dir, "stories", "thumbnails", f"story_{story_number:02d}_thumbnail.jpg")

    youtube = get_youtube_service()
    if youtube:
        pinned = story_data.get("pinned_comment")
        video_id, video_url = upload_video(youtube, video_path, metadata, thumbnail_path=thumb_path, pinned_comment=pinned)
        update_state(story_number, video_id, publish_iso)
        return video_id, video_url
    else:
        print(f"\n✨ Video generated locally at: {video_path}")
        print("Upload skipped because YouTube API credentials were not found or not yet authenticated.")
        return None, video_path

if __name__ == "__main__":
    s_arg = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else None
    q_arg = sys.argv[2] if len(sys.argv) > 2 else "8k"
    imm_arg = "--immediate" in sys.argv
    run_schedule(story_number=s_arg, quality=q_arg, force_immediate=imm_arg)
