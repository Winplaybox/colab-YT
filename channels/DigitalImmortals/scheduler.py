"""
DigitalImmortals Autonomous YouTube Scheduler Engine
===================================================
1. Audits previous episode analytics (views, engagement, top questions).
2. Calculates optimal release time (Sunday 08:30 AM IST / Tuesday 18:30 IST).
3. Automates 8K cinematic rendering and YouTube upload.
4. Auto-syncs video to Kanda Playlist & Master Series Playlist.
"""

import os
import sys
import json
from datetime import datetime, timedelta

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

script_dir = os.path.dirname(os.path.abspath(__file__))
output_dir = os.path.join(script_dir, "output")
episodes_dir = os.path.join(script_dir, "episodes")
state_file = os.path.join(script_dir, "state.json")
config_file = os.path.join(script_dir, "config.json")
token_file = os.path.join(script_dir, "token.json")

import google.auth.transport.requests
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from playlist_manager import sync_episode_to_playlists
from analytics_tracker import audit_previous_episode

def get_youtube_client():
    if not os.path.exists(token_file):
        print(f"❌ token.json not found! Please run 'python authenticate_youtube.py' first.")
        return None
    with open(token_file, "r", encoding="utf-8") as f:
        tdata = json.load(f)
    creds = Credentials.from_authorized_user_info(tdata)
    req = google.auth.transport.requests.Request()
    creds.refresh(req)
    with open(token_file, "w", encoding="utf-8") as f:
        f.write(creds.to_json())
    return build("youtube", "v3", credentials=creds)

def get_next_optimal_publish_time():
    """
    Returns optimal ISO 8601 UTC publish time:
    - Sundays at 08:30 AM IST (03:00 UTC) -> Historic Ramayana Family Slot
    - Tuesdays at 18:30 PM IST (13:00 UTC) -> Auspicious Hanumanji / Evening Slot
    Ensures scheduling occurs strictly AFTER the most recently scheduled episode in state.json.
    """
    base_time = datetime.utcnow()
    try:
        if os.path.exists(state_file):
            with open(state_file, "r", encoding="utf-8") as f:
                sdata = json.load(f)
            history = sdata.get("history", [])
            scheduled_times = []
            for h in history:
                pat = h.get("publish_at")
                if pat and pat != "IMMEDIATE":
                    try:
                        scheduled_times.append(datetime.strptime(pat, "%Y-%m-%dT%H:%M:%SZ"))
                    except Exception:
                        pass
            if scheduled_times:
                latest = max(scheduled_times)
                if latest > base_time:
                    base_time = latest
    except Exception as e:
        print(f"[WARN] Error reading state history for scheduling: {e}")

    # Search for next Sunday or Tuesday after base_time
    for days_ahead in range(1, 14):
        candidate = base_time + timedelta(days=days_ahead)
        weekday = candidate.weekday() # 1 = Tuesday, 6 = Sunday
        if weekday == 6: # Sunday 08:30 AM IST (03:00 UTC)
            target_utc = candidate.replace(hour=3, minute=0, second=0, microsecond=0)
            if target_utc > base_time:
                return target_utc.strftime("%Y-%m-%dT%H:%M:%SZ")
        elif weekday == 1: # Tuesday 18:30 PM IST (13:00 UTC)
            target_utc = candidate.replace(hour=13, minute=0, second=0, microsecond=0)
            if target_utc > base_time:
                return target_utc.strftime("%Y-%m-%dT%H:%M:%SZ")

    return (base_time + timedelta(days=2)).replace(hour=13, minute=0, second=0, microsecond=0).strftime("%Y-%m-%dT%H:%M:%SZ")

from googleapiclient.http import MediaFileUpload

def _playlist_link_lines():
    """Only real (full-length) playlist IDs from state.json; old truncated IDs are skipped."""
    try:
        with open(state_file, "r", encoding="utf-8") as f:
            pl = json.load(f).get("playlists", {})
    except Exception:
        pl = {}
    lines = []
    master = pl.get("MASTER_SERIES", "")
    if len(master) >= 24:
        lines.append(f"🔗 Master Ramayana Series: https://www.youtube.com/playlist?list={master}")
    return lines or ["🔗 Channel: https://www.youtube.com/@DigitalImmortals/playlists"]

def build_episode_description(episode_num, scenes, scene_durations, ep_data=None):
    """Dynamically builds high-retention 22-minute description with exact chapter timestamps."""
    hook = ep_data.get("description_hook", "") if ep_data else ""
    kanda = ep_data.get("kanda", "बालकाण्ड (Bala Kanda)") if ep_data else "बालकाण्ड"
    title_hindi = ep_data.get("title_hindi", f"एपिसोड {episode_num:02d}") if ep_data else ""

    desc_lines = [
        hook,
        "",
        f"तिरुमाला तिरुपति देवस्थानम (TTD) द्वारा संरक्षित मूल वाल्मीकि रामायण के {kanda} पर आधारित यह 22-मिनट का भव्य चलचित्र सनातन धर्म के सबसे पावन इतिहास और रहस्यों को सजीव करता है।",
        "",
        "प्रकरण सूची (Timestamps):"
    ]

    current_sec = 0.0
    chapters = []
    for sc in scenes:
        sc_id = sc["scene_id"]
        dur = scene_durations.get(sc_id, 35.0)
        # Add timestamps for major milestones / key scenes
        if sc_id in [1, 2, 4, 6, 8, 11, 13, 15, 17, 21, 24, 26, 29, 30]:
            chapters.append((int(current_sec), sc["title"]))
        current_sec += dur
    # /yt-chapters rules: first at 00:00, 3+, each >= 10 s, ascending (otherwise YouTube shows none)
    try:
        sys.path.insert(0, os.path.abspath(os.path.join(script_dir, "..", "..")))
        from channels.common.skills import fix_chapters, validate_chapters, mmss
        chapters = fix_chapters(chapters, int(current_sec))
        ok, problems = validate_chapters(chapters, int(current_sec))
        if not ok:
            print(f"[chapters] still invalid after fix: {problems}")
    except Exception as ce:
        print(f"[chapters] validator notice: {ce}")
        mmss = lambda t: f"{int(t) // 60:02d}:{int(t) % 60:02d}"
    for t, title in chapters:
        desc_lines.append(f"{mmss(t)} - {title}")

    desc_lines.extend([
        "",
        "🎧 सर्वोत्तम अनुभव के लिए हेडफ़ोन (Headphones) का उपयोग करें।",
        "",
        "इस पावन शृंखला के सभी 54 प्रामाणिक एपिसोड्स देखने के लिए हमारे आधिकारिक प्लेलिस्ट को सेव करें:",
        *_playlist_link_lines(),
        "",
        "#ValmikiRamayan #Ramayana #DigitalImmortals #BalaKanda #ShriRam #Ayodhya #SanatanDharma #HinduMythology #EpicStories"
    ])
    return "\n".join(desc_lines)

def upload_episode_to_youtube(youtube, episode_num, video_path, thumbnail_path=None, publish_at=None, force_immediate=False):
    """Uploads the rendered 22-min episode to YouTube with metadata, thumbnail, and playlist sync."""
    json_path = os.path.join(episodes_dir, f"episode_{episode_num:02d}.json")
    with open(json_path, "r", encoding="utf-8") as f:
        ep_data = json.load(f)

    scenes = ep_data.get("scenes", [])

    # Calculate scene durations
    scene_durations = {}
    assets_dir = os.path.join(episodes_dir, f"episode_{episode_num:02d}", "assets")
    from video_producer import get_audio_duration
    for sc in scenes:
        sc_id = sc["scene_id"]
        v_file = os.path.join(assets_dir, f"scene_{sc_id:02d}_voice.mp3")
        scene_durations[sc_id] = get_audio_duration(v_file)

    title = ep_data.get("title_youtube", f"वाल्मीकि रामायण: रहस्यमयी गाथा (Ep {episode_num:02d})")
    desc = build_episode_description(episode_num, scenes, scene_durations, ep_data)

    tags = [
        "valmiki ramayan", "ramayan in hindi", f"ramayan episode {episode_num}",
        "digital immortals", "hindu mythology explained", "sanatan dharma",
        "putrakameshti yajna" if episode_num == 2 else "krauncha vadha",
        "king dasharatha", "ayodhya", "4k ramayan movie", "ancient indian history"
    ]

    body = {
        "snippet": {
            "title": title,
            "description": desc,
            "tags": tags,
            "categoryId": "27",
            "defaultLanguage": "hi",
            "defaultAudioLanguage": "hi"
        },
        "status": {
            "selfDeclaredMadeForKids": False
        }
    }

    if force_immediate:
        body["status"]["privacyStatus"] = "public"
        print(f"🚀 Publishing Immediately as PUBLIC on YouTube...")
    elif publish_at:
        body["status"]["privacyStatus"] = "private"
        body["status"]["publishAt"] = publish_at
        print(f"⏰ Scheduling release for: {publish_at}...")
    else:
        body["status"]["privacyStatus"] = "unlisted"
        print(f"🔒 Uploading as UNLISTED for pre-screening...")

    # Universal Live YouTube Duplicate Protection
    try:
        try:
            from channels.common.youtube_duplicate_checker import check_existing_upload
        except ImportError:
            sys.path.insert(0, os.path.abspath(os.path.join(script_dir, "..", "..")))
            from channels.common.youtube_duplicate_checker import check_existing_upload

        dup = check_existing_upload(youtube, candidate_title=title, episode_number=episode_num, channel_type="DigitalImmortals")
        if dup.get("exists"):
            existing_id = dup["video_id"]
            print(f"\n🛑 [DUPLICATE PREVENTED] Episode #{episode_num:02d} ALREADY exists on YouTube!")
            print(f"   Existing Title: '{dup.get('matched_title', dup.get('title'))}'")
            print(f"   Reason:         {dup.get('reason')}")
            print(f"   Video ID:       {existing_id} ({dup.get('status', 'unknown')})")
            print(f"   YouTube Link:   https://youtu.be/{existing_id}")
            print(f"   ⏭️ Skipping upload to avoid creating duplicate content on YouTube.\n")

            # Advance state.json pointer so pipeline never gets stuck in a loop
            try:
                with open(state_file, "r", encoding="utf-8") as f:
                    sdata = json.load(f)
                if sdata.get("current_episode", 1) <= episode_num:
                    sdata["current_episode"] = episode_num + 1
                    with open(state_file, "w", encoding="utf-8") as f:
                        json.dump(sdata, f, indent=2, ensure_ascii=False)
                    print(f"📈 Advanced state.json to next episode: Ep {episode_num + 1:02d}")
            except Exception as se:
                print(f"Notice: State update notice: {se}")

            return existing_id, f"https://www.youtube.com/watch?v={existing_id}"
    except Exception as d_err:
        print(f"Notice: Duplicate checker notice: {d_err}")

    print(f"⬆️ Uploading Master Video: {video_path} ({os.path.getsize(video_path):,} bytes)...")
    media = MediaFileUpload(video_path, chunksize=1024 * 1024 * 8, resumable=True, mimetype="video/mp4")
    req = youtube.videos().insert(part="snippet,status", body=body, media_body=media)

    response = None
    while response is None:
        status, response = req.next_chunk()
        if status:
            print(f"  Uploading: {int(status.progress() * 100)}%", end="\r", flush=True)

    video_id = response.get("id")
    video_url = f"https://www.youtube.com/watch?v={video_id}"
    print(f"\n🎉 UPLOAD SUCCESSFUL! Video ID: {video_id}")
    print(f"🔗 YouTube Link: {video_url}")

    # Set Custom 16:9 Thumbnail
    if thumbnail_path and os.path.exists(thumbnail_path):
        try:
            print(f"🖼️ Attaching Master Thumbnail: {thumbnail_path}...")
            youtube.thumbnails().set(
                videoId=video_id,
                media_body=MediaFileUpload(thumbnail_path, mimetype="image/jpeg")
            ).execute()
            print("✅ Custom Thumbnail attached successfully!")
        except Exception as te:
            print(f"Notice: Thumbnail upload error: {te}")

    # Sync to Kanda Playlist & Master Series Playlist
    try:
        print("📁 Synchronizing to Playlists...")
        sync_episode_to_playlists(youtube, video_id, episode_num)
    except Exception as pe:
        print(f"Notice: Playlist sync error: {pe}")

    # Post Pinned Community Engagement Comment
    if episode_num == 1:
        pinned_comment = "🏹 क्या आप जानते थे कि रामायण का पहला श्लोक वास्तव में एक शिकारी के लिए शाप था? कमेंट में 'जय श्री राम' लिखकर बताइए कि क्या आप इस 54-एपिसोड की पूरी अखंड यात्रा के लिए तैयार हैं? 👇 (हर सच्चे सनातनी का कमेंट पिन किया जाएगा!)"
    elif episode_num == 2:
        pinned_comment = "🔥 क्या आप जानते थे कि यज्ञ कुंड से निकले उस स्वर्ण पात्र में भरी खीर से ही प्रभु श्री राम का अवतार संभव हुआ? कमेंट में 'जय श्री राम' लिखकर बताइए कि क्या आप प्रभु श्री राम के जन्मोत्सव (Ep 03) के लिए तैयार हैं? 👇 (हर सच्चे सनातनी का कमेंट लाइक और पिन किया जाएगा!)"
    else:
        pinned_comment = f"🏹 वाल्मीकि रामायण के इस अलौकिक एपिसोड {episode_num:02d} से जुड़ने के लिए धन्यवाद! कमेंट में 'जय श्री राम' लिखकर प्रभु की वंदना करें।"

    try:
        print("💬 Posting Pinned Engagement Comment...")
        youtube.commentThreads().insert(
            part="snippet",
            body={
                "snippet": {
                    "videoId": video_id,
                    "topLevelComment": {"snippet": {"textOriginal": pinned_comment}}
                }
            }
        ).execute()
        print("✅ Engagement Comment posted successfully!")
    except Exception as ce:
        print(f"Notice: Pinned comment notice: {ce}")

    # Update state.json
    try:
        with open(state_file, "r", encoding="utf-8") as f:
            sdata = json.load(f)
        if "history" not in sdata:
            sdata["history"] = []
        sdata["history"].append({
            "episode_number": episode_num,
            "video_id": video_id,
            "title": title,
            "uploaded_at": datetime.now().isoformat(),
            "publish_at": publish_at or "IMMEDIATE"
        })
        sdata["current_episode"] = episode_num + 1
        with open(state_file, "w", encoding="utf-8") as f:
            json.dump(sdata, f, indent=2, ensure_ascii=False)
        print(f"📈 State updated. Next episode pointer advanced to: Ep {episode_num + 1:02d}")
    except Exception as se:
        print(f"Notice: State update error: {se}")

    return video_id, video_url

def upload_and_schedule_episode(episode_num, video_path, thumbnail_path=None, force_immediate=False):
    yt = get_youtube_client()
    if not yt:
        raise RuntimeError("YouTube client could not be initialized.")
    publish_at = None if force_immediate else get_next_optimal_publish_time()
    return upload_episode_to_youtube(
        yt, episode_num, video_path, thumbnail_path, publish_at=publish_at, force_immediate=force_immediate
    )

def run_pipeline(force_immediate=False, quality="1080p"):
    print("=" * 75)
    print("🏹 DIGITAL IMMORTALS (@DigitalImmortals) — AUTONOMOUS PIPELINE")
    print("=" * 75)

    yt = get_youtube_client()
    if not yt:
        return

    # 1. Pre-Upload Algorithmic Analytics Audit
    audit_data = audit_previous_episode(yt)

    # 2. State & Episode Resolution (Synchronized with Live YouTube)
    with open(state_file, "r", encoding="utf-8") as f:
        state = json.load(f)

    current_ep = state.get("current_episode", 1)

    # Automatically check live YouTube to skip already uploaded episodes
    try:
        try:
            from channels.common.youtube_duplicate_checker import check_existing_upload
        except ImportError:
            sys.path.insert(0, os.path.abspath(os.path.join(script_dir, "..", "..")))
            from channels.common.youtube_duplicate_checker import check_existing_upload

        while current_ep <= 54:
            dup = check_existing_upload(yt, episode_number=current_ep, channel_type="DigitalImmortals")
            if dup.get("exists"):
                print(f"🛑 [LIVE YOUTUBE CHECK] Episode {current_ep:02d} is ALREADY uploaded on YouTube!")
                print(f"   Video ID: {dup.get('video_id')} | Title: '{dup.get('title')}'")
                print(f"   ⏩ Skipping render/upload. Advancing to Episode {current_ep + 1:02d}...")
                current_ep += 1
                state["current_episode"] = current_ep
                with open(state_file, "w", encoding="utf-8") as f:
                    json.dump(state, f, indent=2, ensure_ascii=False)
            else:
                break
    except Exception as pe_err:
        print(f"Notice: Pre-check duplicate notice: {pe_err}")

    if current_ep > 54:
        print("🎉 All 54 episodes of Valmiki Ramayana are uploaded on YouTube! Complete.")
        return None, None

    print(f"\n🎬 Processing Episode {current_ep:02d} / 54...")

    video_path = os.path.join(output_dir, f"DigitalImmortals_Ep{current_ep:02d}_{quality}.mp4")
    thumbnail_path = os.path.join(script_dir, "thumbnails", f"thumbnail_ep{current_ep:02d}.jpg")

    if not os.path.exists(video_path):
        import video_producer
        video_producer.render_episode_video(current_ep, target_quality=quality)

    if not os.path.exists(thumbnail_path):
        import generate_thumbnail
        generate_thumbnail.generate_master_thumbnail(current_ep)

    publish_at = None if force_immediate else get_next_optimal_publish_time()
    video_id, url = upload_episode_to_youtube(
        yt, current_ep, video_path, thumbnail_path, publish_at=publish_at, force_immediate=force_immediate
    )
    return video_id, url

if __name__ == "__main__":
    force_now = "--now" in sys.argv or "--public" in sys.argv
    run_pipeline(force_immediate=force_now)

