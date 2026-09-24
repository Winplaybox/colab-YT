"""
MindNest Tales Multi-Channel Scheduler:
- Produces and uploads 3D Pixar-style moral stories across 11 language channels
- Supports single-language, single-channel, or batch-network release
"""

import os
import sys
import json
import time
from datetime import datetime, timedelta

# Ensure UTF-8 output across Windows and Linux
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
from video_producer import produce_story_video, load_story, load_network_config
try:
    from sheets_tracker import record_story_status, init_tracking_sheet
except ImportError:
    def record_story_status(story_number, lang, status): pass
    def init_tracking_sheet(): pass


def get_channel_youtube_service(lang_code):
    """
    Resolves YouTube OAuth credentials for a specific language channel.
    """
    if not HAS_GOOGLE_CLIENT:
        print(f"Notice: Google API client libraries not installed in this environment. Video produced locally.")
        return None

    creds_dir = os.path.join(script_dir, "credentials")
    os.makedirs(creds_dir, exist_ok=True)
    
    token_path = os.path.join(creds_dir, f"token_{lang_code}.json")
    
    # Check fallback single-account token
    if not os.path.exists(token_path):
        general_token = os.path.join(script_dir, "token.json")
        if os.path.exists(general_token):
            token_path = general_token
        elif os.path.exists(os.path.join(script_dir, "..", "TigerVlogs-2026", "token.json")):
            token_path = os.path.join(script_dir, "..", "TigerVlogs-2026", "token.json")

    # Check Environment Variables (GitHub Secrets)
    env_keys = [f"MINDNEST_TOKEN_{lang_code.upper()}_JSON", "MINDNEST_TOKEN_JSON", "YOUTUBE_TOKEN_JSON"]
    for k in env_keys:
        if k in os.environ and os.environ[k].strip() and not os.path.exists(token_path):
            with open(token_path, "w", encoding="utf-8") as f:
                f.write(os.environ[k].strip())
            break

    if not os.path.exists(token_path):
        print(f"Warning: No credentials found for {lang_code.upper()}. Will skip upload step.")
        return None

    try:
        creds = Credentials.from_authorized_user_file(token_path)
        if creds.expired and creds.refresh_token:
            creds.refresh(google.auth.transport.requests.Request())
            with open(token_path, "w", encoding="utf-8") as f:
                f.write(creds.to_json())
        return build("youtube", "v3", credentials=creds)
    except Exception as e:
        print(f"Auth error for {lang_code.upper()}: {e}")
        return None

def upload_story_to_channel(youtube, video_file, title, description, tags, thumbnail_path=None, publish_at=None, category_id="1"):
    """Uploads story video to target channel (Category 1: Film & Animation) and attaches custom thumbnail."""
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
            "tags": tags[:25],
            "categoryId": category_id
        },
        "status": status
    }

    insert_request = youtube.videos().insert(
        part="snippet,status",
        body=body,
        media_body=MediaFileUpload(video_file, chunksize=-1, resumable=True)
    )

    print(f"Uploading to YouTube: {title}")
    response = insert_request.execute()
    vid = response.get("id")
    print(f"SUCCESS: Video published! ID: {vid} (https://youtu.be/{vid})")

    # Set custom thumbnail if available
    if thumbnail_path and os.path.exists(thumbnail_path):
        try:
            youtube.thumbnails().set(
                videoId=vid,
                media_body=MediaFileUpload(thumbnail_path)
            ).execute()
            print(f"Custom thumbnail attached: {thumbnail_path}")
        except Exception as te:
            print(f"Note: Could not set thumbnail (channel may need phone verification): {te}")

    return vid

def load_state():
    """Loads state.json to determine current story and run history."""
    state_file = os.path.join(script_dir, "state.json")
    if os.path.exists(state_file):
        with open(state_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"current_story": 1, "last_run_date": None, "total_stories": 51, "completed_stories": []}

def save_state(state):
    """Saves updated state back to state.json."""
    state_file = os.path.join(script_dir, "state.json")
    with open(state_file, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)

def run_mindnest_release(story_number=None, target_lang=None, quality="8k", auto_advance=False, publish_at=None, work_dir="/tmp/mindnest_batch"):
    """Executes production & upload for a specific language or all 11 channels at 8K/4K."""
    state = load_state()
    if story_number is None:
        story_number = state.get("current_story", 1)

    config = load_network_config()
    story = load_story(story_number)
    os.makedirs(work_dir, exist_ok=True)

    # Locate thumbnail if present
    thumb_path = os.path.join(script_dir, "stories", "thumbnails", f"story_{story_number:02d}_thumbnail.jpg")
    if not os.path.exists(thumb_path):
        thumb_path = os.path.join(script_dir, "stories", "thumbnails", f"story_{story_number:02d}_thumbnail.png")
    if not os.path.exists(thumb_path):
        thumb_path = None

    channels_to_process = config["channels"]
    if target_lang and target_lang != "all":
        channels_to_process = [c for c in config["channels"] if c["lang_code"] == target_lang]

    results = []
    print(f"\n=======================================================")
    print(f"🚀 RELEASING STORY #{story_number}: '{story['base_title']}' [{quality.upper()} SHORTS]")
    print(f"Channels in this run: {len(channels_to_process)}")
    print(f"=======================================================")

    for ch in channels_to_process:
        lang = ch["lang_code"]
        ch_name = ch["channel_name"]
        print(f"\n[{ch_name} - {lang.upper()}] Starting 8K Shorts production...")

        record_story_status(story_number, lang, "Processing...")
        video_path = os.path.join(work_dir, f"story_{story_number:02d}_{lang}_{quality}.mp4")
        produce_story_video(story, lang, video_path, quality=quality)

        # Upload
        translation = story["translations"].get(lang, story["translations"]["en"])
        title = translation["title"]
        if "#Shorts" not in title and "#shorts" not in title:
            title = f"{title} #Shorts"

        youtube = get_channel_youtube_service(lang)
        if youtube:
            try:
                vid = upload_story_to_channel(
                    youtube,
                    video_path,
                    title,
                    translation["description"],
                    translation["tags"],
                    thumbnail_path=thumb_path,
                    publish_at=publish_at
                )
                results.append({"channel": ch_name, "lang": lang, "status": "UPLOADED", "url": f"https://youtu.be/{vid}"})
                record_story_status(story_number, lang, f"Uploaded ({vid})")
            except Exception as e:
                print(f"Upload failed for {ch_name}: {e}")
                results.append({"channel": ch_name, "lang": lang, "status": "FAILED", "error": str(e)})
                record_story_status(story_number, lang, f"Failed: {str(e)[:25]}")
        else:
            results.append({"channel": ch_name, "lang": lang, "status": "RENDERED_LOCAL", "path": video_path})
            record_story_status(story_number, lang, "Rendered Local")

        # Automatically clean up rendered video to keep disk and repository light
        if os.path.exists(video_path):
            os.remove(video_path)


    # Update state tracker
    today_str = datetime.now().strftime("%Y-%m-%d")
    state["last_run_date"] = today_str
    if story_number not in state.get("completed_stories", []):
        state.setdefault("completed_stories", []).append(story_number)

    if auto_advance:
        total = state.get("total_stories", 51)
        next_story = (story_number % total) + 1
        state["current_story"] = next_story
        print(f"State updated: Next story in pipeline is Story #{next_story}")
    save_state(state)

    print("\n" + "="*60)
    print(f"🎉 BATCH COMPLETE FOR STORY #{story_number}:")
    for r in results:
        print(f" - [{r['lang'].upper()}] {r['channel']}: {r.get('url', r.get('status'))}")
    print("="*60)
    return results

if __name__ == "__main__":
    state = load_state()
    default_story = state.get("current_story", 1)

    story_arg = sys.argv[1] if len(sys.argv) > 1 else "auto"
    if story_arg == "auto" or not story_arg.isdigit():
        story_no = default_story
        auto_adv = True
    else:
        story_no = int(story_arg)
        auto_adv = False

    lang = sys.argv[2] if len(sys.argv) > 2 else "all"
    quality = sys.argv[3] if len(sys.argv) > 3 else "8k"

    run_mindnest_release(story_no, lang, quality=quality, auto_advance=auto_adv)


