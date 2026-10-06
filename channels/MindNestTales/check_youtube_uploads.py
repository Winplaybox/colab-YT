import os
import sys
import json

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

script_dir = os.path.dirname(os.path.abspath(__file__))
creds_dir = os.path.join(script_dir, "credentials")
cfg_file = os.path.join(script_dir, "channels_config.json")

with open(cfg_file, "r", encoding="utf-8") as f:
    cfg = json.load(f)

# Keywords to identify story numbers
STORY_KEYWORDS = {
    1: ["chico", "चीकू", "cheetah", "चीता", "guepardo", "guépard", "время", "সময়", "zeit", "وقت", "チーコ", "치코", "thời gian"],
    2: ["leo", "शेरू", "lion", "शेर", "león", "leão", "löwe", "أسد", "ライオン", "사자", "sư tử"],
    3: ["elephant", "हाथी", "elefante", "éléphant", "elefant", "فيل", "ゾウ", "코끼리", "voi"],
    4: ["zebra", "ज़ेबरा", "cèbre", "zebras", "حمار وحشي", "シマウマ", "얼룩말", "ngựa vằn"]
}

def identify_story_number(title):
    lower = title.lower()
    for s_no, kws in STORY_KEYWORDS.items():
        for kw in kws:
            if kw.lower() in lower:
                return s_no
    return None

def audit_youtube_network():
    print("=" * 80)
    print("🔍 LIVE YOUTUBE NETWORK AUDIT — MINDNEST TALES (11 CHANNELS)")
    print("=" * 80)
    
    story_counts = {}
    channel_uploads = {}
    
    for ch in cfg["channels"]:
        lang = ch["lang_code"]
        name = ch["channel_name"]
        tok_file = os.path.join(creds_dir, f"token_{lang}.json")
        if not os.path.exists(tok_file):
            print(f"[{lang.upper()}] ❌ No credentials token found.")
            continue
            
        with open(tok_file, "r", encoding="utf-8") as tf:
            tdata = json.load(tf)
            
        try:
            creds = Credentials.from_authorized_user_info(tdata)
            yt = build("youtube", "v3", credentials=creds)
            res = yt.channels().list(mine=True, part="contentDetails").execute()
            uploads_id = res["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
            
            # Fetch uploads
            vids = yt.playlistItems().list(
                playlistId=uploads_id,
                part="snippet,status",
                maxResults=15
            ).execute()
            
            items = vids.get("items", [])
            print(f"\n📺 [{lang.upper()}] {name} (Total Uploads on Channel: {len(items)})")
            
            ch_stories = set()
            for v in items:
                title = v["snippet"]["title"]
                vid = v["snippet"]["resourceId"]["videoId"]
                pub = v["snippet"].get("publishedAt", "")[:10]
                status = v.get("status", {}).get("privacyStatus", "unknown")
                s_num = identify_story_number(title)
                s_tag = f"Story #{s_num:02d}" if s_num else "Compilation/Other"
                print(f"   • [{status.upper()}] {pub} | {s_tag:<18} | {title} (ID: {vid})")
                
                if s_num:
                    ch_stories.add(s_num)
                    story_counts[s_num] = story_counts.get(s_num, 0) + 1
                    
            channel_uploads[lang] = list(ch_stories)
            
        except Exception as e:
            print(f"[{lang.upper()}] ❌ Error: {e}")

    print("\n" + "=" * 80)
    print("📊 YOUTUBE AUDIT SUMMARY:")
    for s_no in sorted(story_counts.keys()):
        print(f"   • Story #{s_no:02d}: Uploaded on {story_counts[s_no]} channel(s)")
    print("=" * 80)
    
    return story_counts, channel_uploads

if __name__ == "__main__":
    audit_youtube_network()
