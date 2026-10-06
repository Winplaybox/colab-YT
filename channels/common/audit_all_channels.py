"""
Master Network YouTube Channel Auditor & Ground Truth Synchronizer
==================================================================
Audits ALL channels across the entire network:
- Fetches all uploaded videos directly from live YouTube channel Playlists (1 quota unit / 50 vids).
- Identifies any existing duplicate videos currently on YouTube (with exact video IDs).
- Synchronizes local state.json across all channels with real ground truth.
"""

import os
import sys
import json
from datetime import datetime

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from google.oauth2.credentials import Credentials
import google.auth.transport.requests
from googleapiclient.discovery import build

script_dir = os.path.dirname(os.path.abspath(__file__))
repo_root = os.path.abspath(os.path.join(script_dir, "..", ".."))
sys.path.insert(0, repo_root)

from channels.common.youtube_duplicate_checker import (
    audit_channel_uploads,
    normalize_title,
    check_existing_upload
)

def get_authenticated_service(token_path):
    """Loads and refreshes OAuth credentials for a token file."""
    if not os.path.exists(token_path):
        return None, f"Token file missing: {token_path}"
    try:
        with open(token_path, "r", encoding="utf-8") as f:
            tdata = json.load(f)
        creds = Credentials.from_authorized_user_info(tdata)
        if creds.expired and creds.refresh_token:
            creds.refresh(google.auth.transport.requests.Request())
            with open(token_path, "w", encoding="utf-8") as f:
                f.write(creds.to_json())
        service = build("youtube", "v3", credentials=creds)
        return service, None
    except Exception as e:
        return None, str(e)

def audit_and_sync_all(sync_state=True):
    print("=" * 80)
    print("🌐 UNIVERSAL YOUTUBE CHANNELS AUDIT & DUPLICATE DETECTION")
    print(f"   Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

    channels_to_audit = [
        # 1. Main Thematic Channels
        {
            "name": "Digital Immortals",
            "type": "DigitalImmortals",
            "token_path": os.path.join(repo_root, "channels", "DigitalImmortals", "token.json"),
            "state_path": os.path.join(repo_root, "channels", "DigitalImmortals", "state.json"),
        },
        {
            "name": "Epic Bharat Saga",
            "type": "EpicBharatSaga",
            "token_path": os.path.join(repo_root, "channels", "EpicBharatSaga", "token.json"),
            "state_path": os.path.join(repo_root, "channels", "EpicBharatSaga", "state.json"),
        },
        {
            "name": "Indian Horror Tapes",
            "type": "IndianHorrorTapes",
            "token_path": os.path.join(repo_root, "channels", "IndianHorrorTapes", "token.json"),
            "state_path": os.path.join(repo_root, "channels", "IndianHorrorTapes", "state.json"),
        },
        {
            "name": "All Train Reels",
            "type": "AllTrainReels",
            "token_path": os.path.join(repo_root, "channels", "AllTrainReels", "token.json"),
            "state_path": os.path.join(repo_root, "channels", "AllTrainReels", "state.json"),
        },
        {
            "name": "Tiger Vlogs",
            "type": "TigerVlogs",
            "token_path": os.path.join(repo_root, "channels", "TigerVlogs-2026", "token.json"),
            "state_path": os.path.join(repo_root, "channels", "TigerVlogs-2026", "state.json"),
        },
    ]

    # 2. MindNest Tales Multilingual Channels
    mindnest_creds_dir = os.path.join(repo_root, "channels", "MindNestTales", "credentials")
    mindnest_config_path = os.path.join(repo_root, "channels", "MindNestTales", "channels_config.json")
    mindnest_state_path = os.path.join(repo_root, "channels", "MindNestTales", "state.json")

    if os.path.exists(mindnest_config_path):
        try:
            with open(mindnest_config_path, "r", encoding="utf-8") as cf:
                mn_conf = json.load(cf)
            for ch in mn_conf.get("channels", []):
                lang = ch["lang_code"]
                ch_name = ch["channel_name"]
                tpath = os.path.join(mindnest_creds_dir, f"token_{lang}.json")
                channels_to_audit.append({
                    "name": ch_name,
                    "type": "MindNestTales",
                    "lang_code": lang,
                    "token_path": tpath,
                    "state_path": mindnest_state_path,
                })
        except Exception as me:
            print(f"Notice: Could not parse MindNestTales channels config: {me}")

    grand_total_videos = 0
    total_duplicate_clusters = 0
    results = []

    for cinfo in channels_to_audit:
        cname = cinfo["name"]
        ctype = cinfo["type"]
        tpath = cinfo["token_path"]
        spath = cinfo.get("state_path")
        lang = cinfo.get("lang_code")

        if not os.path.exists(tpath):
            print(f"\n⚪ [{cname}] Skipped: No token at {os.path.basename(tpath)}")
            continue

        service, err = get_authenticated_service(tpath)
        if err or not service:
            print(f"\n⚠️ [{cname}] Auth issue: {err}")
            continue

        audit_res = audit_channel_uploads(service, max_results=150)
        total_vids = audit_res["total_videos"]
        dup_groups = audit_res["duplicate_groups"]
        highest_ep = audit_res["highest_episode"]
        ch_title = audit_res["channel_title"]
        ch_id = audit_res["channel_id"]

        grand_total_videos += total_vids
        total_duplicate_clusters += len(dup_groups)

        print(f"\n📺 [{cname}] Channel: '{ch_title}' ({ch_id})")
        print(f"   📊 Total Uploads on YouTube: {total_vids}")
        if highest_ep:
            print(f"   🔝 Highest Episode Detected: #{highest_ep}")

        if dup_groups:
            print(f"   🚨 WARNING: Found {len(dup_groups)} duplicate group(s) currently on YouTube:")
            for dg in dup_groups:
                print(f"      • '{dg['title']}' ({dg['count']} copies)")
                print(f"        Canonical (oldest): {dg['canonical_id']}")
                print(f"        Redundant duplicates: {dg['duplicate_video_ids']}")
        else:
            print(f"   ✅ Clean: No duplicates detected on YouTube.")

        # State synchronization
        if sync_state and spath and os.path.exists(spath):
            try:
                with open(spath, "r", encoding="utf-8") as sf:
                    st = json.load(sf)
                updated = False

                if ctype == "DigitalImmortals":
                    saga_eps = []
                    for u in audit_res.get("uploads", []):
                        det = u.get("detected_number")
                        raw_title = u.get("title", "").lower()
                        if det and 1 <= det <= 54 and "(ep" in raw_title:
                            saga_eps.append(det)
                    if saga_eps:
                        max_saga = max(saga_eps)
                        st["current_episode"] = max_saga + 1
                        updated = True
                        print(f"   🔄 Synchronized state.json -> next episode: Ep {max_saga + 1:02d}")

                elif ctype == "EpicBharatSaga" and highest_ep:
                    if st.get("current_episode", 1) <= highest_ep:
                        st["current_episode"] = highest_ep + 1
                        updated = True
                        print(f"   🔄 Synchronized state.json -> next episode: Ep #{highest_ep + 1:03d}")

                elif ctype == "IndianHorrorTapes" and highest_ep:
                    if st.get("current_story_number", 1) <= highest_ep:
                        st["current_story_number"] = (highest_ep % 103) + 1
                        updated = True
                        print(f"   🔄 Synchronized state.json -> next story: #{st['current_story_number']}")

                elif ctype == "AllTrainReels" and highest_ep:
                    if st.get("current_story_number", 1) <= highest_ep:
                        st["current_story_number"] = highest_ep + 1
                        updated = True
                        print(f"   🔄 Synchronized state.json -> next episode: #{highest_ep + 1:02d}")

                elif ctype == "MindNestTales" and lang:
                    if "channels_progress" not in st:
                        st["channels_progress"] = {}
                    if lang not in st["channels_progress"]:
                        st["channels_progress"][lang] = {"completed_stories": []}

                    # Detect all completed stories on this channel from uploads
                    comp_list = set(st["channels_progress"][lang].get("completed_stories", []))
                    for u in audit_res.get("uploads", []):
                        det = u.get("detected_number")
                        if det:
                            comp_list.add(det)
                    st["channels_progress"][lang]["completed_stories"] = sorted(list(comp_list))
                    updated = True

                if updated:
                    with open(spath, "w", encoding="utf-8") as sf:
                        json.dump(st, sf, indent=2, ensure_ascii=False)
            except Exception as se:
                print(f"   ⚠️ Could not sync state: {se}")

        results.append({
            "channel_name": cname,
            "youtube_title": ch_title,
            "channel_id": ch_id,
            "total_videos": total_vids,
            "duplicate_groups_count": len(dup_groups),
            "duplicate_groups": dup_groups,
            "highest_episode": highest_ep
        })

    print("\n" + "=" * 80)
    print("📋 AUDIT SUMMARY:")
    print(f"   • Total Active Channels Audited: {len(results)}")
    print(f"   • Total Videos Analyzed:         {grand_total_videos}")
    print(f"   • Duplicate Content Clusters:   {total_duplicate_clusters}")
    print("=" * 80)

    return results

if __name__ == "__main__":
    audit_and_sync_all(sync_state=True)
