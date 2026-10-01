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

# Master Thematic Playlists Definition (Directly mapped to Channel Playlists)
THEMATIC_PLAYLISTS = {
    "HAUNTED FORTS & PALACES": {
        "title": "🏰 HAUNTED FORTS & PALACES",
        "description": "Declassified paranormal investigations and historical curses inside India's most ancient forts, royal palaces, and citadel ruins. ASI-banned sites, royal court murders, and declassified records."
    },
    "HAUNTED SCHOOLS, HOSPITALS & INSTITUTIONS": {
        "title": "🏫 HAUNTED SCHOOLS, HOSPITALS & INSTITUTIONS",
        "description": "Medical wings locked for decades, abandoned schools, lunatic asylums, and unclosed coroner files from the British Raj to modern day."
    },
    "HAUNTED BEACHES, WATER BODIES & FORESTS": {
        "title": "🌊 HAUNTED BEACHES, WATER BODIES & FORESTS",
        "description": "Black sand beaches, crematorium coastlines, and cursed lakes. The chilling truth behind Dumas Beach, Kasara Ghat waterfalls, and Arabian Sea anomalies."
    },
    "HAUNTED RAILWAY STATIONS & TUNNELS": {
        "title": "🚂 HAUNTED RAILWAY STATIONS & TUNNELS",
        "description": "Unclassified Indian Railways accident logs, abandoned platforms, and cursed railway tunnels. Begunkodor, Tunnel 33, and Rabindra Sarobar."
    },
    "HAUNTED ROADS & HIGHWAYS": {
        "title": "HAUNTED ROADS & HIGHWAYS",
        "description": "True eyewitness encounters, police dashcam logs, and accident-prone highway stretches across India. What happens on NH-8, Delhi Cantt, and Kashedi Ghat after 2:00 AM."
    },
    "HAUNTED HOUSES, COLONIES & BUILDINGS": {
        "title": "HAUNTED HOUSES, COLONIES & BUILDINGS",
        "description": "Sealed British bungalows, heritage estates, ghost towns, and cursed residences with dark histories of poison, murder, and restless spirits."
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
    cat_upper = category.upper() if category else ""
    matched_key = None

    if any(w in cat_upper for w in ["FORT", "PALACE", "KILA", "MAHAL"]):
        matched_key = "HAUNTED FORTS & PALACES"
    elif any(w in cat_upper for w in ["SCHOOL", "HOSPITAL", "ASYLUM", "INSTITUTION", "COLLEGE", "MORTUARY"]):
        matched_key = "HAUNTED SCHOOLS, HOSPITALS & INSTITUTIONS"
    elif any(w in cat_upper for w in ["BEACH", "WATER", "FOREST", "HILL", "JUNGLE", "LAKE", "RIVER", "NATURE"]):
        matched_key = "HAUNTED BEACHES, WATER BODIES & FORESTS"
    elif any(w in cat_upper for w in ["RAILWAY", "STATION", "TUNNEL", "TRAIN", "TRACK"]):
        matched_key = "HAUNTED RAILWAY STATIONS & TUNNELS"
    elif any(w in cat_upper for w in ["ROAD", "HIGHWAY", "GHAT", "STRETCH", "EXPRESSWAY"]):
        matched_key = "HAUNTED ROADS & HIGHWAYS"
    elif any(w in cat_upper for w in ["HOUSE", "COLONY", "BUILDING", "BUNGALOW", "TOWN", "VILLAGE", "RUIN"]):
        matched_key = "HAUNTED HOUSES, COLONIES & BUILDINGS"
    else:
        matched_key = "HAUNTED FORTS & PALACES"

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
