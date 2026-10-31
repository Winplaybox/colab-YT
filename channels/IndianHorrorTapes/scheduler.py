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

    secret_path = os.path.join(script_dir, "youtube_client_secret.json")
    env_secret = os.environ.get("INDIANHORRORTAPES_CLIENT_SECRET_JSON") or os.environ.get("YOUTUBE_CLIENT_SECRET_JSON")
    if env_secret and env_secret.strip() and not os.path.exists(secret_path):
        with open(secret_path, "w", encoding="utf-8") as f:
            f.write(env_secret.strip())

    if not os.path.exists(token_path):
        print(f"⚠️ Notice: No credentials found for {EXPECTED_NAME}. Running in local render mode.")
        print(f"👉 Run 'python channels/IndianHorrorTapes/authenticate_youtube.py' to link your channel.")
        return None

    try:
        with open(token_path, "r", encoding="utf-8") as f:
            token_data = json.load(f)

        # Validate and synchronize client_id & client_secret
        if os.path.exists(secret_path):
            try:
                with open(secret_path, "r", encoding="utf-8") as sf:
                    sec_json = json.load(sf)
                    c_info = sec_json.get("installed") or sec_json.get("web") or {}
                    sec_cid = c_info.get("client_id")
                    sec_sec = c_info.get("client_secret")

                    tok_cid = token_data.get("client_id")
                    if tok_cid and sec_cid and tok_cid != sec_cid:
                        print(f"⚠️ Mismatched Client ID detected:")
                        print(f"   token.json uses:          {tok_cid}")
                        print(f"   client_secret.json uses:  {sec_cid}")
                        print("👉 If refresh fails, re-authenticate using authenticate_youtube.py with this client secret.")

                    if sec_cid and "client_id" not in token_data:
                        token_data["client_id"] = sec_cid
                    if sec_sec and "client_secret" not in token_data:
                        token_data["client_secret"] = sec_sec
            except Exception as se:
                print(f"Notice: Could not parse client secret file: {se}")

        creds = Credentials.from_authorized_user_info(token_data)
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(google.auth.transport.requests.Request())
                with open(token_path, "w", encoding="utf-8") as f:
                    f.write(creds.to_json())
                print("🔒 Access token refreshed successfully.")
            except Exception as re:
                err_str = str(re)
                print(f"❌ Failed to refresh token: {err_str}")
                if "invalid_grant" in err_str:
                    print("\n" + "=" * 70)
                    print("⚠️ GOOGLE OAUTH 'invalid_grant: Bad Request' DETECTED:")
                    print("This happens for one of two reasons:")
                    print("1. In Google Cloud Console (APIs & Services -> OAuth consent screen),")
                    print("   the Publishing status is in 'Testing' mode (refresh tokens expire in 7 days).")
                    print("   👉 Click 'PUBLISH APP' to switch to Production (tokens will never expire).")
                    print("2. The refresh token expired, was revoked, or was created with a different OAuth Client ID.")
                    print(f"   Active Client ID in secret: {token_data.get('client_id', 'unknown')}")
                    print("   👉 Run locally: 'python channels/IndianHorrorTapes/authenticate_youtube.py'")
                    print("   and update INDIANHORRORTAPES_TOKEN_JSON in GitHub Repository Secrets.")
                    print("=" * 70 + "\n")
                return None

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
#Shorts #IndianHorrorTapes #BhootKiKahani #HindiHorrorStories #RealHorrorStories #HauntedIndia #Khauf #Darr #ParanormalInvestigation #ScaryShorts #TrendingHorror #UrbanLegendsHindi
"""

    viral_horror_tags = [
        "indian horror tapes",
        "bhoot ki kahani",
        "real horror stories in hindi",
        "haunted places in india",
        "ghost stories hindi",
        "paranormal investigation india",
        "horror shorts hindi",
        "chudail ki kahani",
        "sacchi ghatna horror",
        "khauf",
        "darr",
        "bhoot pret",
        "scary horror stories",
        "haunted fort india",
        "creepy hindi kahaniya",
        "khooni raaz",
        "unsolved mysteries hindi",
        "trending horror shorts",
        "viral horror shorts",
        "horror story in hindi",
        "indian paranormal",
        "shorts"
    ]
    tags = story_data.get("tags", []) + viral_horror_tags
    seen = set()
    dedup_tags = []
    running_str = ""

    for t in tags:
        # YouTube prohibits commas and angle brackets in tags
        t_clean = t.replace(",", "").replace("<", "").replace(">", "").strip()
        if not t_clean:
            continue
        if t_clean.lower() not in seen:
            quoted_repr = f'"{t_clean}"' if ' ' in t_clean else t_clean
            test_str = f"{running_str},{quoted_repr}" if running_str else quoted_repr
            # YouTube enforces max 500-char/byte internal comma-quoted limit
            if len(test_str) <= 380 and len(test_str.encode("utf-8")) <= 380:
                seen.add(t_clean.lower())
                dedup_tags.append(t_clean)
                running_str = test_str
            if len(dedup_tags) >= 20:
                break

    body = {
        "snippet": {
            "title": clean_title,
            "description": desc,
            "tags": dedup_tags,
            "categoryId": "24",
            "defaultLanguage": "hi",
            "defaultAudioLanguage": "hi"
        },
        "status": {
            "selfDeclaredMadeForKids": False,
            "containsSyntheticMedia": False
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

    # Live YouTube Duplicate Protection
    try:
        try:
            from common.youtube_duplicate_checker import check_existing_upload
        except ImportError:
            sys.path.insert(0, os.path.abspath(os.path.join(script_dir, "..")))
            from common.youtube_duplicate_checker import check_existing_upload

        cand_title = metadata.get("snippet", {}).get("title", "")
        dup = check_existing_upload(youtube, candidate_title=cand_title, channel_type="IndianHorrorTapes")
        if dup.get("exists"):
            existing_id = dup["video_id"]
            print(f"\n🛑 [DUPLICATE PREVENTED] Video ALREADY exists on Indian Horror Tapes YouTube!")
            print(f"   Existing Title: '{dup.get('matched_title', dup.get('title'))}'")
            print(f"   Reason:         {dup.get('reason')}")
            print(f"   Video ID:       {existing_id} ({dup.get('status', 'unknown')})")
            print(f"   YouTube Link:   https://youtu.be/{existing_id}")
            print(f"   ⏭️ Skipping upload to avoid creating duplicate content on YouTube.\n")
            return existing_id, f"https://www.youtube.com/shorts/{existing_id}"
    except Exception as ce:
        print(f"Notice: Duplicate checker notice: {ce}")

    media = MediaFileUpload(
        video_path,
        chunksize=1024 * 1024 * 8, # 8MB chunks
        resumable=True,
        mimetype="video/mp4"
    )

    _b = _yt_brain()
    if _b:
        metadata = _b.before_insert("IndianHorrorTapes", youtube, metadata, is_short=True)
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
    if _b:
        _b.after_insert("IndianHorrorTapes", youtube, video_id)
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

def upload_subtitles_to_youtube(youtube, video_id, output_dir, story_number, story_data):
    """Uploads multi-language SRT caption tracks to the uploaded YouTube video."""
    slug = story_data.get("slug") or story_data.get("name", "").lower().replace(" ", "_")
    
    caption_tracks = [
        {"file": f"story_{story_number:02d}_{slug}_hi.srt", "lang": "hi", "name": "Hindi (हिन्दी)", "default": True},
        {"file": f"story_{story_number:02d}_{slug}_en.srt", "lang": "en", "name": "English", "default": False},
        {"file": f"story_{story_number:02d}_{slug}_hinglish.srt", "lang": "hi-Latn", "name": "Hinglish", "default": False}
    ]
    
    for track in caption_tracks:
        srt_path = os.path.join(output_dir, track["file"])
        if os.path.exists(srt_path):
            try:
                print(f"📝 Uploading [{track['lang']}] subtitle track: {track['name']}...")
                media = MediaFileUpload(srt_path, mimetype="application/x-subrip")
                youtube.captions().insert(
                    part="snippet",
                    body={
                        "snippet": {
                            "videoId": video_id,
                            "language": track["lang"],
                            "name": track["name"],
                            "isDraft": False
                        }
                    },
                    media_body=media
                ).execute()
                print(f"✅ Caption track [{track['lang']}] attached successfully!")
            except Exception as ce:
                print(f"Notice: Could not upload caption track [{track['lang']}]: {ce}")

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
        "history": [],
        "playlists": {}
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

def run_schedule(story_number=None, quality="4k", force_immediate=False):
    """
    Main orchestration routine:
    1. Loads current story definition
    2. Renders 9:16 portrait video with dynamic visual theme & multi-language subtitles
    3. Generates matching Community Tab Polls & Updates
    4. Calculates Wednesday/Sunday 9:00 PM IST slot
    5. Uploads to YouTube, pins engagement comment, attaches captions, and syncs playlists
    """
    state_file = os.path.join(script_dir, "state.json")
    if story_number is None and os.path.exists(state_file):
        try:
            with open(state_file, "r", encoding="utf-8") as f:
                st = json.load(f)
                story_number = st.get("current_story_number", 1)
        except Exception:
            story_number = 1

    # Pre-render check: inspect live YouTube to skip already uploaded stories
    yt_svc = get_youtube_service()
    if yt_svc:
        try:
            try:
                from common.youtube_duplicate_checker import check_existing_upload
            except ImportError:
                sys.path.insert(0, os.path.abspath(os.path.join(script_dir, "..")))
                from common.youtube_duplicate_checker import check_existing_upload

            visited = set()
            bank_size = 103
            while True:
                if story_number in visited or len(visited) >= bank_size:
                    print(f"\n🎉 [STORY BANK COMPLETE] All {len(visited)} stories from stories_bank.json are already live on YouTube!")
                    print("   To upload more, expand stories_bank.json or add new investigation locations.")
                    return None, None
                visited.add(story_number)

                cand_data = get_or_create_story(story_number)
                cand_title = f"{cand_data['title']} 💀 #Shorts"
                dup = check_existing_upload(yt_svc, candidate_title=cand_title, story_number=story_number, channel_type="IndianHorrorTapes")
                if dup.get("exists"):
                    print(f"🛑 [LIVE YOUTUBE CHECK] Story #{story_number:02d} ({cand_data['title']}) is ALREADY on YouTube ({dup['video_id']}).")
                    next_story = (story_number % bank_size) + 1
                    print(f"   ⏩ Skipping render. Advancing to Story #{next_story:02d}...")
                    story_number = next_story
                    if os.path.exists(state_file):
                        try:
                            with open(state_file, "r", encoding="utf-8") as f:
                                st = json.load(f)
                            st["current_story_number"] = story_number
                            with open(state_file, "w", encoding="utf-8") as f:
                                json.dump(st, f, indent=2)
                        except Exception:
                            pass
                else:
                    break
        except Exception as pe_err:
            print(f"Notice: Pre-check duplicate notice: {pe_err}")

    story_data = get_or_create_story(story_number)
    output_dir = os.path.join(script_dir, "output")
    os.makedirs(output_dir, exist_ok=True)
    video_path = os.path.join(output_dir, f"IndianHorrorTapes_Ep{story_number:02d}_{quality}.mp4")

    # 1. Render video (which now applies dynamic visual theme and outputs multi-language subtitles)
    produce_horror_short(story_data, video_path, quality=quality)

    # 2. Generate YouTube Community Posts & Polls
    from community_post_generator import build_community_bundle
    community_bundle = build_community_bundle(story_data)

    # 3. Compute release schedule: Wednesday / Sunday 9:00 PM IST (15:30 UTC)
    publish_iso = None if force_immediate else compute_next_publish_time(publish_time_utc="15:30", schedule_days=[2, 6])
    metadata = build_metadata(story_data, publish_iso)

    thumb_path = os.path.join(script_dir, "stories", "thumbnails", f"story_{story_number:02d}_thumbnail.jpg")

    youtube = get_youtube_service()
    if youtube:
        pinned = story_data.get("pinned_comment")
        video_id, video_url = upload_video(youtube, video_path, metadata, thumbnail_path=thumb_path, pinned_comment=pinned)

        # 4. Upload Captions: Skipped (YouTube generates high-accuracy automatic native Hindi captions)
        print("ℹ️ Skipping custom SRT/VTT caption upload — YouTube native auto-captions enabled.")

        # 5. Sync to Thematic Playlists (Category Playlist + All Episodes Chronological)
        from playlist_manager import sync_video_to_playlists
        cat = story_data.get("category", "ALL_EPISODES")
        sync_video_to_playlists(youtube, video_id, cat)

        update_state(story_number, video_id, publish_iso)
        return video_id, video_url
    else:
        print(f"\n✨ Video generated locally at: {video_path}")
        print(f"📊 Community Poll generated: {community_bundle['poll']['question']}")
        print("Upload skipped because YouTube API credentials were not found or not yet authenticated.")
        return None, video_path

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="IndianHorrorTapes Autonomous Scheduler")
    parser.add_argument("story_number", nargs="?", default=None, help="Story number (int) or empty")
    parser.add_argument("quality_pos", nargs="?", default=None, help="Quality positional (1080p, 4k, 8k)")
    parser.add_argument("--quality", default=None, help="Output quality (1080p, 4k, 8k)")
    parser.add_argument("--immediate", action="store_true", help="Publish immediately as Public")

    args = parser.parse_args()

    s_num = None
    if args.story_number and args.story_number.strip().isdigit():
        s_num = int(args.story_number.strip())

    # Resolve quality from --quality or positional
    q_val = args.quality or args.quality_pos or "4k"
    if q_val.startswith("--"):
        q_val = "4k"

    run_schedule(story_number=s_num, quality=q_val, force_immediate=args.immediate)
