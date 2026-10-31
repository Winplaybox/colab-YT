"""
DigitalImmortals Autonomous YouTube Playlist Management Engine
==============================================================
Manages high-retention, binge-optimized playlists for the Valmiki Ramayana saga:
1. Master Series Playlist: 🔴 वाल्मीकि रामायण: संपूर्ण महागाथा (All 54 Episodes)
2. Thematic Kanda Playlists (Bala, Ayodhya, Aranya, Kishkindha, Sundara, Yuddha)
3. Caches playlist IDs in state.json for zero-redundancy execution.
"""

import os
import sys
import json

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

script_dir = os.path.dirname(os.path.abspath(__file__))
state_file = os.path.join(script_dir, "state.json")

RAMAYANA_PLAYLISTS = {
    "MASTER_SERIES": {
        "title": "🔴 वाल्मीकि रामायण: संपूर्ण महागाथा | Valmiki Ramayana Full Series (4K)",
        "description": "महर्षि वाल्मीकि रचित मूल 'श्रीमद् वाल्मीकि रामायण' की संपूर्ण प्रामाणिक कथा 8K सिनेमैटिक शॉर्ट-मूवी प्रारूप में। बालकाण्ड से युद्धकाण्ड तक के सभी 54 विस्तृत एपिसोड्स को क्रमानुसार देखें।\n\nतिरुमाला तिरुपति देवस्थानम (TTD) द्वारा संरक्षित मूल पाठ पर आधारित, बिना किसी मिलावट, विशुद्ध देवनागरी हिंदी में।\n\n🎧 सर्वोत्तम अनुभव के लिए हेडफ़ोन का उपयोग करें।\n🔔 संपूर्ण शृंखला देखने के लिए @DigitalImmortals को सब्सक्राइब करें!\n\n#ValmikiRamayan #HinduMythology #DigitalImmortals #RamayanInHindi #SanatanDharma #Ayodhya"
    },
    "BALA_KANDA": {
        "title": "🏹 बालकाण्ड (Bala Kanda) — वाल्मीकि रामायण | Ep 01-08 (4K)",
        "description": "भगवान श्री राम का प्राकट्य, महर्षि विश्वामित्र के साथ सिद्धाश्रम यात्रा, ताड़का वध, गंगावतरण, अहल्या उद्धार, जनकपुरी में शिव धनुष भंग और सीता-राम महाविवाह।\n\n#BalaKanda #ValmikiRamayan #ShivaDhanush #SitaRamVivah #DigitalImmortals"
    },
    "AYODHYA_KANDA": {
        "title": "👑 अयोध्याकाण्ड (Ayodhya Kanda) — वाल्मीकि रामायण | Ep 09-18 (4K)",
        "description": "अयोध्या में राज्याभिषेक की तैयारी, मंथरा का कुचक्र, कैकेयी के दो वरदान, श्री राम का 14 वर्ष वनवास, राजा दशरथ का देहत्याग और चित्रकूट में भावुक भरत मिलाप।\n\n#AyodhyaKanda #BharatMilap #Kaikeyi #Vanvas #DigitalImmortals #Ramayan"
    },
    "ARANYA_KANDA": {
        "title": "🌿 अरण्यकाण्ड (Aranya Kanda) — वाल्मीकि रामायण | Ep 19-26 (4K)",
        "description": "दंडकारण्य में ऋषियों की रक्षा, शूर्पणखा का मानमर्दन, खर-दूषण संहार, मारीच की स्वर्ण मृग माया, रावण द्वारा सीता हरण, जटायु का महाबलिदान और शबरी का मोक्ष।\n\n#AranyaKanda #SitaHaran #GoldenDeer #Jatayu #Shabari #ValmikiRamayan"
    },
    "KISHKINDHA_KANDA": {
        "title": "🐒 किष्किन्धाकाण्ड (Kishkindha Kanda) — वाल्मीकि रामायण | Ep 27-33 (4K)",
        "description": "पंपा सरोवर, पवनपुत्र हनुमान का श्री राम से प्रथम मिलन, सुग्रीव से मित्रता, बालि वध, वानर सेना का विश्व भ्रमण और सम्पाती द्वारा लंका का रहस्योद्घाटन।\n\n#KishkindhaKanda #HanumanJi #Sugriva #ValiVadh #DigitalImmortals #Ramayan"
    },
    "SUNDARA_KANDA": {
        "title": "🔥 सुन्दरकाण्ड (Sundara Kanda) — वाल्मीकि रामायण | Ep 34-42 (4K)",
        "description": "हनुमान जी की 100 योजन समुद्र छलांग, स्वर्ण लंका में प्रवेश, अशोक वाटिका में माता सीता के दर्शन, राम-मुद्रिका अर्पण, अक्षय कुमार वध और लंका दहन।\n\n#SundaraKanda #LankaDahan #HanumanChowki #AshokaVatika #DigitalImmortals"
    },
    "YUDDHA_KANDA": {
        "title": "⚔️ युद्धकाण्ड (Yuddha Kanda) — वाल्मीकि रामायण | Ep 43-54 (4K)",
        "description": "विभीषण शरणागति, नल-नील द्वारा 'राम सेतु' निर्माण, भीषण लंका युद्ध, कुंभकर्ण वध, संजीवनी बूटी, मेघनाद वध, ब्रह्मास्त्र से रावण संहार और अयोध्या पट्टाभिषेक (रामराज्य)।\n\n#YuddhaKanda #RamSetu #Kumbhakarna #RavanVadh #Ramarajya #DigitalImmortals"
    }
}

def load_cached_playlists():
    if os.path.exists(state_file):
        try:
            with open(state_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("playlists", {})
        except Exception:
            pass
    return {}

def save_cached_playlists(playlists_dict):
    data = {}
    if os.path.exists(state_file):
        try:
            with open(state_file, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            pass
    data["playlists"] = playlists_dict
    with open(state_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def get_or_create_playlist(youtube, playlist_key):
    if playlist_key not in RAMAYANA_PLAYLISTS:
        playlist_key = "MASTER_SERIES"

    meta = RAMAYANA_PLAYLISTS[playlist_key]
    title = meta["title"]
    desc = meta["description"]

    cached = load_cached_playlists()
    # Real playlist IDs are ~34 chars ("PL" + 32). Old state.json had truncated
    # 13-char IDs, which broke playlist sync and description links -> re-resolve.
    if playlist_key in cached and len(str(cached[playlist_key])) >= 24:
        return cached[playlist_key]

    # Query channel playlists
    try:
        req = youtube.playlists().list(
            part="snippet",
            mine=True,
            maxResults=50
        )
        res = req.execute()
        for item in res.get("items", []):
            if item["snippet"]["title"].strip() == title.strip():
                p_id = item["id"]
                cached[playlist_key] = p_id
                save_cached_playlists(cached)
                print(f"📁 Found existing playlist: '{title}' ({p_id})")
                return p_id
    except Exception as e:
        print(f"Notice: Could not list playlists: {e}")

    # Create new playlist
    try:
        print(f"✨ Creating new playlist: '{title}'...")
        create_req = youtube.playlists().insert(
            part="snippet,status",
            body={
                "snippet": {
                    "title": title,
                    "description": desc,
                    "defaultLanguage": "hi"
                },
                "status": {
                    "privacyStatus": "public"
                }
            }
        )
        create_res = create_req.execute()
        p_id = create_res.get("id")
        cached[playlist_key] = p_id
        save_cached_playlists(cached)
        print(f"🎉 Created playlist successfully! ID: {p_id}")
        return p_id
    except Exception as e:
        print(f"Warning: Failed to create playlist '{title}': {e}")
        return None

def add_video_to_playlist(youtube, video_id, playlist_id):
    if not playlist_id or not video_id:
        return False
    try:
        youtube.playlistItems().insert(
            part="snippet",
            body={
                "snippet": {
                    "playlistId": playlist_id,
                    "resourceId": {
                        "kind": "youtube#video",
                        "videoId": video_id
                    }
                }
            }
        ).execute()
        print(f"✅ Added Video ({video_id}) to Playlist ({playlist_id})")
        return True
    except Exception as e:
        print(f"Notice: Could not add video to playlist {playlist_id}: {e}")
        return False

def sync_episode_to_playlists(youtube, video_id, episode_num):
    """Syncs an episode to its Kanda playlist and the Master playlist."""
    if not youtube or not video_id:
        return

    # Determine Kanda based on episode number (1 to 54)
    if episode_num <= 8:
        kanda_key = "BALA_KANDA"
    elif episode_num <= 18:
        kanda_key = "AYODHYA_KANDA"
    elif episode_num <= 26:
        kanda_key = "ARANYA_KANDA"
    elif episode_num <= 33:
        kanda_key = "KISHKINDHA_KANDA"
    elif episode_num <= 42:
        kanda_key = "SUNDARA_KANDA"
    else:
        kanda_key = "YUDDHA_KANDA"

    # 1. Add to Kanda Playlist
    kanda_p_id = get_or_create_playlist(youtube, kanda_key)
    if kanda_p_id:
        add_video_to_playlist(youtube, video_id, kanda_p_id)

    # 2. Add to Master Series Playlist
    master_p_id = get_or_create_playlist(youtube, "MASTER_SERIES")
    if master_p_id and master_p_id != kanda_p_id:
        add_video_to_playlist(youtube, video_id, master_p_id)

if __name__ == "__main__":
    print("📋 Valmiki Ramayana Thematic Playlists Initialized:")
    for k, v in RAMAYANA_PLAYLISTS.items():
        print(f"  - [{k}]: {v['title']}")
