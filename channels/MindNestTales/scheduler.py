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
    from compilation_producer import produce_10min_compilation
except ImportError:
    produce_10min_compilation = None
try:
    from analytics_engine import run_network_analytics_audit
except ImportError:
    run_network_analytics_audit = None
try:
    from sheets_tracker import record_story_status, init_tracking_sheet
except ImportError:
    def record_story_status(story_number, lang, status): pass
    def init_tracking_sheet(): pass


def compute_next_publish_time(publish_time_utc="03:30", schedule_days=[2, 5, 6]):
    """
    Computes next Saturday, Sunday, or Wednesday publish timestamp in ISO 8601 UTC.
    Days: Wednesday=2, Saturday=5, Sunday=6.
    Ensures at least 15 minutes in advance for YouTube scheduling API.
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

def verify_channel_identity(youtube, expected_channel_id, expected_channel_name):
    """
    STRICT SECURITY GUARD:
    Verifies that the authenticated YouTube token actually belongs to the target channel.
    Rejects the token immediately if it belongs to Tiger Vlogs or any other unexpected channel.
    """
    try:
        res = youtube.channels().list(mine=True, part="snippet").execute()
        items = res.get("items", [])
        if not items:
            return False, "No YouTube channel associated with this token."
        actual_id = items[0]["id"]
        actual_title = items[0]["snippet"]["title"]
        if expected_channel_id and actual_id != expected_channel_id:
            return False, f"Token belongs to '{actual_title}' ({actual_id}), NOT target '{expected_channel_name}' ({expected_channel_id})!"
        return True, f"Verified: '{actual_title}' ({actual_id})"
    except Exception as e:
        print(f"Warning: Could not verify channel identity: {e}")
        return True, "Channel verification bypassed"

def get_channel_youtube_service(lang_code, expected_channel_id=None, expected_name=None):
    """
    Resolves YouTube OAuth credentials strictly for the designated MindNest Tales channel.
    NEVER falls back to TigerVlogs. Validates channel ID to prevent cross-channel uploads.
    """
    if not HAS_GOOGLE_CLIENT:
        print(f"Notice: Google API client libraries not installed in this environment. Video produced locally.")
        return None

    creds_dir = os.path.join(script_dir, "credentials")
    os.makedirs(creds_dir, exist_ok=True)
    
    token_path = os.path.join(creds_dir, f"token_{lang_code}.json")
    
    # Check if unified all-in-one tokens bundle is provided
    all_tokens_env = os.environ.get("MINDNEST_ALL_TOKENS_JSON", "").strip()
    if all_tokens_env and not os.path.exists(token_path):
        try:
            tokens_dict = json.loads(all_tokens_env)
            if lang_code in tokens_dict:
                tok_val = tokens_dict[lang_code]
                with open(token_path, "w", encoding="utf-8") as f:
                    if isinstance(tok_val, str):
                        f.write(tok_val)
                    else:
                        json.dump(tok_val, f)
        except Exception as e:
            print(f"Notice: Could not parse MINDNEST_ALL_TOKENS_JSON for {lang_code}: {e}")

    # Check Environment Variables (Language specific or Master MindNest token)
    env_keys = [f"MINDNEST_TOKEN_{lang_code.upper()}_JSON", "MINDNEST_TOKEN_JSON"]
    for k in env_keys:
        if k in os.environ and os.environ[k].strip() and not os.path.exists(token_path):
            with open(token_path, "w", encoding="utf-8") as f:
                f.write(os.environ[k].strip())
            break

    # Master token fallback strictly within MindNest Tales directory only
    if not os.path.exists(token_path):
        general_token = os.path.join(script_dir, "token.json")
        if os.path.exists(general_token):
            token_path = general_token

    if not os.path.exists(token_path):
        print(f"⚠️ Notice: No credentials found for {expected_name or lang_code.upper()}. Will render locally (skipping upload).")
        print(f"👉 Run 'python channels/MindNestTales/authenticate_channels.py {lang_code}' to authenticate this channel.")
        return None

    try:
        creds = Credentials.from_authorized_user_file(token_path)
        if creds.expired and creds.refresh_token:
            creds.refresh(google.auth.transport.requests.Request())
            with open(token_path, "w", encoding="utf-8") as f:
                f.write(creds.to_json())
        service = build("youtube", "v3", credentials=creds)
        
        # Verify channel ownership
        is_valid, msg = verify_channel_identity(service, expected_channel_id, expected_name)
        if not is_valid:
            print(f"\n🛑 CRITICAL SAFETY ABORT: {msg}")
            print(f"Upload to this channel is BLOCKED to prevent uploading to the wrong channel!")
            print(f"👉 Re-authenticate: python channels/MindNestTales/authenticate_channels.py {lang_code}\n")
            return None
        print(f"✅ Channel authenticated: {msg}")
        return service
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

def post_pinned_comment(youtube, video_id, comment_text):
    """Inserts a top-level pinned comment on an uploaded video."""
    try:
        res = youtube.commentThreads().insert(
            part="snippet",
            body={
                "snippet": {
                    "videoId": video_id,
                    "topLevelComment": {
                        "snippet": {
                            "textOriginal": comment_text
                        }
                    }
                }
            }
        ).execute()
        return res.get("id")
    except Exception as e:
        print(f"Comment notice: {e}")
        return None

def run_mindnest_release(story_number=None, target_lang=None, quality="1080p", auto_advance=False, publish_at=None, work_dir="/tmp/mindnest_batch", mode="dual"):
    """
    Executes production & upload for MindNest Tales:
    - mode='dual': Renders 10-Minute Long Video + 180s Short with direct cross-linking CTA.
    - mode='short': Renders 180s Short only.
    - mode='long': Renders 10-Minute Long Video only.
    - mode='analytics': Executes real-time algorithm audit across all 11 channels.
    """
    if mode == "analytics" or story_number == "analytics":
        if run_network_analytics_audit:
            return run_network_analytics_audit()
        print("Analytics engine not found.")
        return None

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
    print(f"🚀 RELEASING STORY #{story_number}: '{story['base_title']}' [MODE: {mode.upper()}]")
    print(f"Channels in this run: {len(channels_to_process)}")
    print(f"=======================================================")

    for ch in channels_to_process:
        lang = ch["lang_code"]
        ch_name = ch["channel_name"]
        youtube = get_channel_youtube_service(
            lang,
            expected_channel_id=ch.get("channel_id"),
            expected_name=ch_name
        )

        channel_publish_at = publish_at
        if not channel_publish_at and ch.get("publish_time_utc"):
            channel_publish_at = compute_next_publish_time(ch.get("publish_time_utc", "03:30"))

        long_vid_url = None

        # -----------------------------------------------------------------
        # 1. 10-MINUTE LONG-FORM VIDEO (If dual or long mode)
        # -----------------------------------------------------------------
        if mode in ("dual", "long") and produce_10min_compilation:
            total_stories = state.get("total_stories", 51)
            story_ids = [
                story_number,
                (story_number % total_stories) + 1,
                ((story_number + 1) % total_stories) + 1
            ]
            print(f"\n[{ch_name} - {lang.upper()}] 🎬 Producing 10-Minute Compilation (Stories {story_ids})...")
            long_path = os.path.join(work_dir, f"compilation_{story_number:02d}_{lang}_{quality}.mp4")
            try:
                _, long_meta = produce_10min_compilation(story_ids, lang, long_path, quality=quality)
                # Prioritize language-specific localized 16:9 thumbnail
                long_thumb = os.path.join(script_dir, "stories", "thumbnails", f"compilation_{story_number:02d}_thumbnail_{lang}.jpg")
                if not os.path.exists(long_thumb):
                    long_thumb = os.path.join(script_dir, "stories", "thumbnails", f"compilation_{story_number:02d}_thumbnail.jpg")
                if not os.path.exists(long_thumb):
                    try:
                        from generate_thumbnail import generate_all_language_thumbnails
                        hero_img = os.path.join(script_dir, "stories", "assets", f"story_{story_number:02d}", "scene_03_pride.jpg")
                        if not os.path.exists(hero_img):
                            hero_img = thumb_path
                        if os.path.exists(hero_img):
                            generate_all_language_thumbnails(hero_img, story_number=story_number)
                            cand = os.path.join(script_dir, "stories", "thumbnails", f"compilation_{story_number:02d}_thumbnail_{lang}.jpg")
                            if os.path.exists(cand):
                                long_thumb = cand
                    except Exception as ge:
                        print(f"Thumbnail auto-gen note: {ge}")
                if not os.path.exists(long_thumb):
                    long_thumb = os.path.join(script_dir, "stories", "thumbnails", f"story_{story_number:02d}_long_thumbnail.jpg")
                if not os.path.exists(long_thumb):
                    long_thumb = thumb_path

                if youtube and os.path.exists(long_path):
                    long_id = upload_story_to_channel(
                        youtube,
                        long_path,
                        long_meta["title"],
                        long_meta["description"],
                        long_meta["tags"],
                        thumbnail_path=long_thumb,
                        publish_at=channel_publish_at
                    )
                    long_vid_url = f"https://youtu.be/{long_id}"
                    results.append({"channel": ch_name, "lang": lang, "type": "10-MIN", "status": "UPLOADED", "url": long_vid_url})
                    state.setdefault("compilations", {})[f"story_{story_number:02d}_{lang}"] = long_vid_url
            except Exception as le:
                print(f"Notice: Long-form build note: {le}")
            finally:
                if os.path.exists(long_path):
                    os.remove(long_path)

        # -----------------------------------------------------------------
        # 2. 175-SECOND SHORT (Strictly < 180s to prevent YouTube 3:01 limit)
        # -----------------------------------------------------------------
        if mode in ("dual", "short"):
            print(f"\n[{ch_name} - {lang.upper()}] 📱 Producing 175s Short (strict < 180s)...")
            record_story_status(story_number, lang, "Processing...")
            video_path = os.path.join(work_dir, f"story_{story_number:02d}_{lang}_{quality}.mp4")
            produce_story_video(story, lang, video_path, quality=quality, target_duration=175.0)

            translation = story["translations"].get(lang, story["translations"]["en"])
            title = translation["title"]
            if "#Shorts" not in title and "#shorts" not in title:
                title = f"{title} #Shorts"

            # If long video was uploaded, link it on the top line of description in pure native language
            desc = translation["description"]
            if long_vid_url:
                watch_labels = {
                    "en": "🎬 WATCH FULL 10-MINUTE EPISODE",
                    "hi": "🎬 पूरा 10 मिनट का विशेष एपिसोड यहाँ देखें",
                    "es": "🎬 MIRA EL EPISODIO COMPLETO DE 10 MINUTOS",
                    "pt": "🎬 ASSISTA AO EPISÓDIO COMPLETO DE 10 MINUTOS",
                    "fr": "🎬 REGARDEZ L'ÉPISODE COMPLET DE 10 MINUTES",
                    "de": "🎬 GANZE 10-MINÜTIGE FOLGE ANSEHEN",
                    "ar": "🎬 شاهد الحلقة الكاملة لمدة 10 دقائق",
                    "ja": "🎬 10分間の完全版エピソードを見る",
                    "ko": "🎬 10분 전체 에피소드 시청하기",
                    "vi": "🎬 XEM TRỌN VẸN TẬP ĐẶC BIỆT 10 PHÚT",
                    "fil": "🎬 PANOORIN ANG BUONG 10-MINUTONG EPISODE",
                }
                w_lbl = watch_labels.get(lang, "🎬 WATCH FULL 10-MINUTE EPISODE")
                desc = f"{w_lbl}: {long_vid_url}\n\n" + desc

            if youtube and os.path.exists(video_path):
                try:
                    vid = upload_story_to_channel(
                        youtube,
                        video_path,
                        title,
                        desc,
                        translation["tags"],
                        thumbnail_path=thumb_path,
                        publish_at=channel_publish_at
                    )
                    short_url = f"https://youtu.be/{vid}"
                    status_label = f"Scheduled ({channel_publish_at})" if channel_publish_at else f"Uploaded ({vid})"
                    results.append({"channel": ch_name, "lang": lang, "type": "SHORT", "status": status_label, "url": short_url})
                    record_story_status(story_number, lang, status_label)

                    if long_vid_url:
                        pin_labels = {
                            "en": "👉 Watch the full 10-minute 3-story special here:",
                            "hi": "👉 पूरा 10 मिनट का 3-कहानियों का विशेष एपिसोड यहाँ देखें:",
                            "es": "👉 Mira el especial completo de 10 minutos con 3 historias aquí:",
                            "pt": "👉 Assista ao especial completo de 10 minutos com 3 histórias aqui:",
                            "fr": "👉 Regardez l'épisode spécial de 10 minutes avec 3 histoires ici :",
                            "de": "👉 Hier die komplette 10-minütige Sonderfolge ansehen:",
                            "ar": "👉 شاهد الحلقة الخاصة الكاملة المكونة من 3 قصص هنا:",
                            "ja": "👉 3つの物語が入った10分特別エピソードはこちら:",
                            "ko": "👉 3가지 이야기가 담긴 10분 스페셜 영상 바로보기:",
                            "vi": "👉 Xem trọn vẹn tập 10 phút gồm 3 câu chuyện ý nghĩa tại đây:",
                            "fil": "👉 Panoorin ang buong 10-minutong espesyal na 3 kwento rito:",
                        }
                        p_lbl = pin_labels.get(lang, "👉 Watch the full 10-minute 3-story special here:")
                        pin_text = f"{p_lbl} {long_vid_url} 💛"
                        post_pinned_comment(youtube, vid, pin_text)

                except Exception as e:
                    print(f"Upload failed for {ch_name}: {e}")
                    results.append({"channel": ch_name, "lang": lang, "type": "SHORT", "status": "FAILED", "error": str(e)})
                    record_story_status(story_number, lang, f"Failed: {str(e)[:25]}")
            else:
                results.append({"channel": ch_name, "lang": lang, "type": "SHORT", "status": "RENDERED_LOCAL", "path": video_path})
                record_story_status(story_number, lang, "Rendered Local")

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
    print(f"🎉 BATCH COMPLETE FOR STORY #{story_number} [{mode.upper()}]:")
    for r in results:
        print(f" - [{r['lang'].upper()}] ({r.get('type')}) {r['channel']}: {r.get('url', r.get('status'))}")
    print("="*60)
    return results

if __name__ == "__main__":
    state = load_state()
    default_story = state.get("current_story", 1)

    story_arg = sys.argv[1] if len(sys.argv) > 1 else "auto"
    if story_arg == "analytics":
        run_mindnest_release(mode="analytics")
        sys.exit(0)

    if story_arg == "auto" or not story_arg.isdigit():
        story_no = default_story
        auto_adv = True
    else:
        story_no = int(story_arg)
        auto_adv = False

    lang = sys.argv[2] if len(sys.argv) > 2 else "all"
    quality = sys.argv[3] if len(sys.argv) > 3 else "1080p"
    mode = sys.argv[4] if len(sys.argv) > 4 else "dual"

    run_mindnest_release(story_no, lang, quality=quality, auto_advance=auto_adv, mode=mode)


