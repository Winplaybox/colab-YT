"""
IndianHorrorTapes Autonomous YouTube Playlist Management Engine
================================================================
Organizes videos into thematic YouTube playlists to maximize binge-watching,
viewer session duration, and channel watch-time algorithms:
- Automatically maps story category to designated thematic playlist
- Checks if playlist exists on the authenticated channel; if missing, creates it via YouTube API
- Adds newly uploaded video to both:
  1. The thematic category playlist (e.g. "Haunted Forts & Palaces")
  2. The master chronological series playlist ("Indian Horror Tapes — Complete Series")
- Caches playlist IDs in state.json for fast zero-redundancy execution.
"""

import os
import sys
import json

script_dir = os.path.dirname(os.path.abspath(__file__))
state_file = os.path.join(script_dir, "state.json")

# Master Thematic Playlists Definition
THEMATIC_PLAYLISTS = {
    "HAUNTED FORTS & PALACES": {
        "title": "🏰 Haunted Forts & Palaces of India | Real Horror Tapes",
        "description": "Declassified paranormal investigations and historical curses inside India's most ancient forts, royal palaces, and citadel ruins. ASI-banned sites, royal court murders, and declassified records."
    },
    "HAUNTED ROADS & HIGHWAYS": {
        "title": "🛣️ Haunted Highways & Desolate Roads (Night Patrol Tapes)",
        "description": "True eyewitness encounters, police dashcam logs, and accident-prone highway stretches across India. What happens on NH-8, Delhi Cantt, and Kashedi Ghat after 2:00 AM."
    },
    "HAUNTED RAILWAY STATIONS & TUNNELS": {
        "title": "🚂 Ghost Stations & Cursed Railway Tunnels of India",
        "description": "Unclassified Indian Railways accident logs, abandoned platforms, and cursed railway tunnels. Featuring Begunkodor's 42-year shutdown, Tunnel 33, and Rabindra Sarobar."
    },
    "HAUNTED BEACHES & WATER BODIES": {
        "title": "🌊 Dark Shores & Haunted Waters of India",
        "description": "Black sand beaches, crematorium coastlines, and cursed lakes. The chilling truth behind Dumas Beach, Kasara Ghat waterfalls, and Arabian Sea anomalies."
    },
    "HAUNTED VILLAGES & TOWNS": {
        "title": "🏚️ Cursed Villages & Ghost Towns of India",
        "description": "Entire settlements abandoned overnight. The 200-year curse of Kuldhara, the Paliwal Brahmins, and the forgotten ruins of the Thar Desert."
    },
    "HAUNTED HOSPITALS & ASYLUMS": {
        "title": "🏥 Sealed Asylums & Colonial Mortuaries",
        "description": "Medical wings locked for decades, abandoned lunatic asylums, and unclosed coroner files from the British Raj to modern day."
    },
    "HAUNTED FORESTS, HILLS & NATURAL SITES": {
        "title": "🌲 Forbidden Forests & Haunted Hills of India",
        "description": "Dense mountain corridors, headless sentries, and mass animal anomalies. Dow Hill Kurseong, Jatinga bird suicides, and Sanjay Van."
    },
    "HAUNTED HOUSES & BUNGALOWS": {
        "title": "🚪 Haunted Bungalows & Colonial Mansions of India",
        "description": "Sealed British bungalows, heritage estates, and cursed residences with dark histories of poison, murder, and restless spirits."
    },
    "HAUNTED MINES, MILLS & INDUSTRIAL SITES": {
        "title": "🏭 Abandoned Mines & Industrial Ruins of India",
        "description": "Disused textile mills, flooded coal mines, and industrial disasters where trapped voices still linger in the rusted machinery."
    },
    "URBAN LEGENDS & PARANORMAL PHENOMENA": {
        "title": "👁️ Unsolved Indian Paranormal Legends & Entities",
        "description": "Documented urban panic, Nale Ba, Churel sightings, and folklore verified through municipal records and newspaper headlines."
    },
    "ALL_EPISODES": {
        "title": "🔴 Indian Horror Tapes — Complete Series (All Episodes)",
        "description": "Watch every declassified tape from Episode 1 to 103 in chronological order. Verified Indian real horror stories and paranormal investigations."
    }
}

def load_cached_playlists():
    """Loads playlist IDs cached in state.json."""
    if os.path.exists(state_file):
        try:
            with open(state_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("playlists", {})
        except Exception:
            pass
    return {}

def save_cached_playlists(playlists_dict):
    """Saves playlist IDs into state.json."""
    data = {}
    if os.path.exists(state_file):
        try:
            with open(state_file, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            pass
    data["playlists"] = playlists_dict
    with open(state_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def get_or_create_playlist(youtube, playlist_key):
    """
    Finds existing playlist by title on channel or creates a new public playlist via API.
    Returns playlist_id.
    """
    if playlist_key not in THEMATIC_PLAYLISTS:
        playlist_key = "ALL_EPISODES"

    meta = THEMATIC_PLAYLISTS[playlist_key]
    title = meta["title"]
    desc = meta["description"]

    cached = load_cached_playlists()
    if playlist_key in cached:
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
        print(f"✨ Creating new thematic playlist: '{title}'...")
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
    """Inserts video into specified playlist using playlistItems.insert."""
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
        # Might already be in playlist or quota exceeded
        print(f"Notice: Could not add video to playlist {playlist_id}: {e}")
        return False

def sync_video_to_playlists(youtube, video_id, category):
    """
    Syncs the uploaded video into:
    1. The category-specific playlist
    2. The master chronological series playlist
    """
    if not youtube or not video_id:
        return

    # 1. Category Playlist
    cat_key = category.upper().strip() if category else "ALL_EPISODES"
    matched_key = None
    for k in THEMATIC_PLAYLISTS:
        if k in cat_key or cat_key in k:
            matched_key = k
            break
    if not matched_key:
        matched_key = "ALL_EPISODES"

    cat_p_id = get_or_create_playlist(youtube, matched_key)
    if cat_p_id:
        add_video_to_playlist(youtube, video_id, cat_p_id)

    # 2. Master Chronological Series Playlist
    master_p_id = get_or_create_playlist(youtube, "ALL_EPISODES")
    if master_p_id and master_p_id != cat_p_id:
        add_video_to_playlist(youtube, video_id, master_p_id)

if __name__ == "__main__":
    print("📋 Master Thematic Playlists Available:")
    for k, v in THEMATIC_PLAYLISTS.items():
        print(f"  - [{k}]: {v['title']}")
