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

# Master Thematic Playlists Definition (Optimized for High-CTR and YouTube Search Algorithm)
THEMATIC_PLAYLISTS = {
    "ALL_EPISODES": {
        "title": "🔴 Indian Horror Tapes — Complete Series | Real Horror Stories Hindi (4K)",
        "description": "Watch the complete archive of Indian Horror Tapes in chronological order. Declassified true paranormal investigations, ancient curses, and unsolved supernatural incidents across India — remastered in 4K with binaural sound design.\n\nFrom banned ASI archaeological sites and cursed railway tunnels to sealed royal fortresses, each episode documents verified eyewitness testimonies, historical archives, and terrifying local lore.\n\n🎧 HEADPHONES STRONGLY RECOMMENDED for immersive 4K horror experience.\n⚠️ Warning: Contains intense psychological horror and disturbing ambient soundscapes.\n\nSubscribe to @IndianHorrorTapes for new declassified horror tapes every week.\n\n#IndianHorrorTapes #HindiHorrorStories #RealGhostStories #HorrorPodcastHindi #HauntedIndia"
    },
    "HAUNTED FORTS & PALACES": {
        "title": "🏰 Haunted Forts & Palaces of India | Real Horror Stories Hindi",
        "description": "Explore the darkest secrets of India's ancient citadels, royal palaces, and banned ASI monuments. Real historical curses, royal court murders, and unexplained paranormal activity recorded inside India’s most haunted forts.\n\nFeaturing investigations and eyewitness chronicles from:\n• Bhangarh Fort (Rajasthan) — ASI warning after sunset\n• Shaniwar Wada (Pune) — Cries of 'Kaka Mala Vachva'\n• Golconda Fort & Nahargarh Citadel\n• Kuldhara Ruined Village & Royal Mausoleums\n\n🎧 Use headphones for deep binaural atmospheric horror. New 4K tapes updated weekly.\n\n#HauntedForts #BhangarhFort #HindiHorrorStories #IndianHorrorTapes #RealGhostStories"
    },
    "HAUNTED SCHOOLS, HOSPITALS & INSTITUTIONS": {
        "title": "🏫 Haunted Schools, Hospitals & Asylums of India | Real Horror Tapes",
        "description": "Chilling true horror cases from sealed asylum wards, abandoned boarding schools, mortuaries, and colonial sanatoriums across India. Unclosed coroner logs and terrifying night-shift testimonies.\n\nFeatured locations and urban legends:\n• Dow Hill & Victoria Boys School (Kurseong) — The Headless Boy\n• King Edward Memorial (KEM) Hospital corridors\n• Agra & Ranchi Mental Asylums abandoned wings\n• British Raj colonial hostels and sealed dissection labs\n\n🎧 High-quality 4K narration with 3D spatial horror soundscape. Put on your headphones and turn off the lights.\n\n#HauntedSchool #HauntedHospital #HindiHorror #IndianHorrorTapes #TrueHorrorStories"
    },
    "HAUNTED BEACHES, WATER BODIES & FORESTS": {
        "title": "🌊 Haunted Forests, Beaches & Cursed Lakes of India | Horror Tapes",
        "description": "Mysterious disappearances, crematorium coastlines, and paranormal entities lurking in India’s deepest jungles, black sand beaches, and misty ghats.\n\nParanormal files covered:\n• Dumas Beach (Surat) — Black sands & midnight whispers\n• Sanjay Van & Malcha Mahal deep forest anomalies (Delhi)\n• Kasara Ghat & Western Ghat waterfalls\n• Cursed rivers, stepwells (Baolis), and midnight fog incidents\n\n🎧 Best experienced with headphones in a dark room. 4K visuals with 45Hz sub-bass sound design.\n\n#HauntedForest #DumasBeach #HindiHorrorStories #IndianHorrorTapes #BhootKiKahani"
    },
    "HAUNTED RAILWAY STATIONS & TUNNELS": {
        "title": "🚂 Haunted Railway Stations & Tunnels of India | Real Horror Tapes",
        "description": "Declassified Indian Railways incident logs, phantom train sightings, and abandoned railway platforms shut down by supernatural terror.\n\nFamous railway mysteries and tracks:\n• Begunkodor Railway Station (Purulia, West Bengal) — The Lady in White\n• Barog Tunnel 33 (Kalka-Shimla Railway) — Colonel Barog's spirit\n• Rabindra Sarobar Metro Station (Kolkata)\n• Cursed tracks, midnight signals, and solitary station masters' logs\n\n🎧 Experience the tension in ultra-high clarity 4K with spatial train audio. Subscribe for weekly declassified tapes.\n\n#HauntedRailwayStation #Tunnel33 #IndianHorrorTapes #HindiHorrorStories #RealGhostStories"
    },
    "HAUNTED ROADS & HIGHWAYS": {
        "title": "🛣️ Haunted Roads, Ghats & Highways of India | Night Horror Tapes",
        "description": "True horror encounters on lonely Indian expressways, foggy mountain ghats, and accident-prone national highways after 2:00 AM. Driver testimonies and police night-patrol records.\n\nFeaturing infamous haunted roads:\n• Delhi Cantonment Road — The Hitchhiking Figure\n• Kashedi Ghat (Mumbai-Goa Highway) — Paranormal meat interceptor\n• Sathyamangalam Wildlife Sanctuary Highway\n• Blue Cross Road & Kasara Ghat hairpin turns\n\n🎧 Put on your headphones for an immersive highway night drive horror audio story in 4K.\n\n#HauntedRoads #DelhiCantt #HighwayHorror #HindiHorrorStories #IndianHorrorTapes"
    },
    "HAUNTED HOUSES, COLONIES & BUILDINGS": {
        "title": "🏚️ Haunted Houses, Colonies & Mansions of India | Real Horror Tapes",
        "description": "Dark secrets buried inside locked British colonial bungalows, sealed DDA apartments, ghost towns, and heritage estates where tragedies occurred.\n\nHaunted residential files:\n• GP Block (Meerut) — The Four Figures on the Rooftop\n• Mukesh Mills (Mumbai) — Possessions on film sets\n• D'Souza Chawl (Mahim) & Agrasen ki Baoli\n• Abandoned zamindar havelis and generational curses\n\n🎧 4K horror experience with cinematic sub-bass narration. Subscribe to @IndianHorrorTapes for new episodes.\n\n#HauntedHouse #MukeshMills #HindiHorrorStories #IndianHorrorTapes #TrueParanormal"
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

def update_channel_playlists_seo(youtube):
    """
    Updates all channel thematic playlists with optimized SEO titles,
    rich keyword-dense descriptions, and default language.
    """
    cached = load_cached_playlists()
    if not cached:
        print("No cached playlists found in state.json.")
        return

    print("🚀 Pushing SEO-optimized Titles & Descriptions to YouTube Playlists...")
    for key, p_id in cached.items():
        if key not in THEMATIC_PLAYLISTS:
            continue
        meta = THEMATIC_PLAYLISTS[key]
        title = meta["title"]
        desc = meta["description"]
        try:
            print(f"🔄 Updating '{key}' ({p_id})...")
            youtube.playlists().update(
                part="snippet,status",
                body={
                    "id": p_id,
                    "snippet": {
                        "title": title,
                        "description": desc,
                        "defaultLanguage": "hi"
                    },
                    "status": {
                        "privacyStatus": "public"
                    }
                }
            ).execute()
            print(f"✅ Successfully updated: '{title}'")
        except Exception as e:
            print(f"❌ Failed to update {key} ({p_id}): {e}")

if __name__ == "__main__":
    import google.auth.transport.requests
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build

    if len(sys.argv) > 1 and sys.argv[1] == "--update-seo":
        token_path = os.path.join(script_dir, "token.json")
        if not os.path.exists(token_path):
            print(f"❌ token.json not found at {token_path}")
            sys.exit(1)
        with open(token_path, "r", encoding="utf-8") as f:
            token_data = json.load(f)
        creds = Credentials.from_authorized_user_info(token_data)
        req = google.auth.transport.requests.Request()
        creds.refresh(req)
        yt = build("youtube", "v3", credentials=creds)
        update_channel_playlists_seo(yt)
    else:
        print("📋 Master Thematic Playlists Available:")
        for k, v in THEMATIC_PLAYLISTS.items():
            print(f"  - [{k}]: {v['title']}")
        print("\n💡 Run with '--update-seo' to apply these titles & descriptions directly to YouTube!")

