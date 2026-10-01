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

script_dir = os.path.dirname(os.path.abspath(__file__))
output_dir = os.path.join(script_dir, "output")
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
    """
    now = datetime.utcnow()
    # Schedule for upcoming Sunday or Tuesday
    for days_ahead in range(1, 8):
        candidate = now + timedelta(days=days_ahead)
        weekday = candidate.weekday() # 1 = Tuesday, 6 = Sunday
        if weekday == 6: # Sunday
            target_utc = candidate.replace(hour=3, minute=0, second=0, microsecond=0)
            if target_utc > now:
                return target_utc.strftime("%Y-%m-%dT%H:%M:%SZ")
        elif weekday == 1: # Tuesday
            target_utc = candidate.replace(hour=13, minute=0, second=0, microsecond=0)
            if target_utc > now:
                return target_utc.strftime("%Y-%m-%dT%H:%M:%SZ")
    
    # Fallback to tomorrow 13:00 UTC
    return (now + timedelta(days=1)).replace(hour=13, minute=0, second=0, microsecond=0).strftime("%Y-%m-%dT%H:%M:%SZ")

from googleapiclient.http import MediaFileUpload

def upload_episode_to_youtube(youtube, episode_num, video_path, thumbnail_path=None, publish_at=None, force_immediate=False):
    """Uploads the rendered episode to YouTube with metadata, thumbnail, and playlist sync."""
    title = "एक पक्षी की मौत से कैसे रचा गया पूरा इतिहास? 🏹 (Ep 01)"
    desc = """क्या रामायण का पहला श्लोक वास्तव में एक शिकारी को दिया गया भयंकर शाप था? वाल्मीकि रामायण की इस ऐतिहासिक और प्रामाणिक शृंखला के पहले एपिसोड में जानिए वह सत्य, जो सदियों से इतिहास के पन्नों में दबा रहा।

तिरुमाला तिरुपति देवस्थानम (TTD) द्वारा संरक्षित मूल वाल्मीकि रामायण के आधार पर, यह शृंखला महर्षि वाल्मीकि के तपोवन, क्रौंच पक्षी के वध, आदि-कवि की उत्पत्ति और अयोध्या के चक्रवर्ती सम्राट दशरथ के वैभव को 8K सिनेमैटिक प्रारूप में सजीव करती है।

प्रकरण सूची (Timestamps):
00:00 - प्रलयंकारी प्रस्तावना (The Ultimate Hook)
00:22 - देवर्षि नारद का दिव्य आगमन (The 16 Divine Virtues)
00:57 - तमसा नदी का पावन तट और निषाद का क्रूर बाण
01:30 - आदि-श्लोक का प्रकटीकरण: 'मा निषाद प्रतिष्ठां...'
02:03 - परमपिता ब्रह्मा का साक्षात प्रकटीकरण
02:42 - सूर्यवंशी अयोध्या का दिव्य साम्राज्य
03:15 - महा-उत्सुकता पूर्ण समापन (The Cliffhanger)

🎧 सर्वोत्तम अनुभव के लिए हेडफ़ोन (Headphones) का उपयोग करें।

#ValmikiRamayan #HinduMythology #RamayanExplained #DigitalImmortals #Ayodhya #SanatanDharma #SriRama #MaharishiValmiki"""

    tags = ["valmiki ramayan", "valmiki ramayana explained", "ramayan in hindi", "ramayan episode 1", "digital immortals", "hindu mythology explained", "krauncha vadha", "maharishi valmiki", "ayodhya king dasharatha", "brahma and valmiki", "vedic stories", "ancient indian history", "4k ramayan movie"]

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
    pinned_comment = "🏹 क्या आप जानते थे कि रामायण का पहला श्लोक वास्तव में एक शिकारी के लिए शाप था? कमेंट में 'जय श्री राम' लिखकर बताइए कि क्या आप इस 54-एपिसोड की पूरी अखंड यात्रा के लिए तैयार हैं? 👇 (हर सच्चे सनातनी का कमेंट पिन किया जाएगा!)"
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

def run_pipeline(force_immediate=False, quality="1080p"):
    print("=" * 75)
    print("🏹 DIGITAL IMMORTALS (@DigitalImmortals) — AUTONOMOUS PIPELINE")
    print("=" * 75)

    yt = get_youtube_client()
    if not yt:
        return

    # 1. Pre-Upload Algorithmic Analytics Audit
    audit_data = audit_previous_episode(yt)

    # 2. State & Episode Resolution
    with open(state_file, "r", encoding="utf-8") as f:
        state = json.load(f)

    current_ep = state.get("current_episode", 1)
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

