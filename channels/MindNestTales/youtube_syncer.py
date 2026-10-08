"""
MindNest Tales Multi-Channel YouTube State Synchronizer & Pre-Flight Auditor
=============================================================================
Directly queries the YouTube Data API across all 11 channels in the MindNest network
to verify channel-by-channel what stories have been published/scheduled.
Maintains exact per-channel ground truth so no channel misses or duplicates any story.
"""

import os
import sys
import json
from datetime import datetime, timezone
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

script_dir = os.path.dirname(os.path.abspath(__file__))
creds_dir = os.path.join(script_dir, "credentials")
state_file = os.path.join(script_dir, "state.json")
config_file = os.path.join(script_dir, "channels_config.json")
stories_dir = os.path.join(script_dir, "stories")

_CACHED_STORIES = None

def load_all_stories():
    global _CACHED_STORIES
    if _CACHED_STORIES is not None:
        return _CACHED_STORIES
    _CACHED_STORIES = {}
    if os.path.exists(stories_dir):
        for fname in os.listdir(stories_dir):
            if fname.startswith("story_") and fname.endswith(".json"):
                try:
                    fpath = os.path.join(stories_dir, fname)
                    with open(fpath, "r", encoding="utf-8") as sf:
                        sd = json.load(sf)
                        s_num = sd.get("story_number")
                        if s_num:
                            _CACHED_STORIES[s_num] = sd
                except Exception:
                    pass
    return _CACHED_STORIES

import re
def clean_str(s):
    return re.sub(r"[#\W_]+", "", s).lower() if s else ""

def identify_story_from_title(title, lang=None):
    if not title:
        return None
    stories = load_all_stories()
    c_title = clean_str(title)
    tl = title.lower()

    # 1. Exact or substring match in translations
    for s_num, s_obj in sorted(stories.items()):
        translations = s_obj.get("translations", {})
        langs_to_check = [lang] if lang and lang in translations else list(translations.keys())
        for l in langs_to_check:
            tr = translations.get(l, {})
            for field in ["title", "short_title", "long_title"]:
                val = tr.get(field, "")
                if val:
                    c_val = clean_str(val)
                    if c_val and (c_val in c_title or c_title in c_val):
                        return s_num

    # 2. Hero character name and slug matching
    for s_num, s_obj in sorted(stories.items()):
        slug = s_obj.get("story_slug", "").lower().split("_")[0]
        if slug and slug in tl:
            return s_num
        hero = s_obj.get("characters", {}).get("hero", "").lower()
        for word in ["chico", "leo", "gajju", "gajraj", "sheldon", "zeppy", "momo", "gigi", "sammy", "stripy"]:
            if word in hero and word in tl:
                return s_num

    return None

def sync_mindnest_from_youtube(target_lang=None, verbose=True):
    """
    Scans the YouTube network to discover all uploaded stories per channel.
    Returns: (global_next_story, global_completed_stories, channel_progress_dict)
    """
    if verbose:
        print("\n" + "=" * 80)
        print("🔍 [PRE-FLIGHT] SYNCING 11-CHANNEL MINDNEST NETWORK FROM YOUTUBE...")
        print("=" * 80)

    if not os.path.exists(config_file):
        return 1, [], {}

    with open(config_file, "r", encoding="utf-8") as f:
        cfg = json.load(f)

    channels = cfg.get("channels", [])
    if target_lang and target_lang != "all":
        channels_to_scan = [c for c in channels if c["lang_code"] == target_lang]
    else:
        channels_to_scan = channels

    channel_progress = {}
    all_completed_stories = set()
    history_records = []
    latest_global_audit = None

    for ch in channels_to_scan:
        lang = ch["lang_code"]
        ch_name = ch["channel_name"]
        tok_file = os.path.join(creds_dir, f"token_{lang}.json")
        if not os.path.exists(tok_file):
            continue

        try:
            with open(tok_file, "r", encoding="utf-8") as tf:
                tdata = json.load(tf)
            creds = Credentials.from_authorized_user_info(tdata)
            if creds.expired and creds.refresh_token:
                import google.auth.transport.requests
                creds.refresh(google.auth.transport.requests.Request())
                with open(tok_file, "w", encoding="utf-8") as tf:
                    tf.write(creds.to_json())
            yt = build("youtube", "v3", credentials=creds)

            res = yt.channels().list(mine=True, part="contentDetails").execute()
            items = res.get("items", [])
            if not items:
                continue
            uploads_id = items[0]["contentDetails"]["relatedPlaylists"]["uploads"]

            vids = []
            page_token = None
            while len(vids) < 150:
                pl_res = yt.playlistItems().list(
                    playlistId=uploads_id,
                    part="snippet,status",
                    maxResults=50,
                    pageToken=page_token
                ).execute()
                vids.extend(pl_res.get("items", []))
                page_token = pl_res.get("nextPageToken")
                if not page_token:
                    break

            ch_completed = set()
            recent_video_id = None
            recent_video_title = None

            for item in vids:
                snippet = item["snippet"]
                status = item.get("status", {})
                title = snippet.get("title", "")
                vid = snippet.get("resourceId", {}).get("videoId", "")
                pub = snippet.get("publishedAt", "")
                privacy = status.get("privacyStatus", "public")

                s_num = identify_story_from_title(title, lang=lang)
                if s_num and "compilation" not in title.lower() and "special" not in title.lower():
                    ch_completed.add(s_num)
                    all_completed_stories.add(s_num)
                    history_records.append({
                        "story_number": s_num,
                        "language": lang,
                        "channel": ch_name,
                        "type": "SHORT",
                        "video_id": vid,
                        "title": title,
                        "privacy": privacy,
                        "publish_at": pub
                    })
                    if not recent_video_id and privacy == "public":
                        recent_video_id = vid
                        recent_video_title = title

            # Calculate next unreleased story for this specific channel
            ch_next = 1
            for s in range(1, 52):
                if s not in ch_completed:
                    ch_next = s
                    break

            # Fetch analytics for channel's most recent public video
            v_stats = {"views": 0, "likes": 0, "comments": 0, "engagement_rate": 0.0}
            if recent_video_id:
                try:
                    res_v = yt.videos().list(part="statistics", id=recent_video_id).execute()
                    if res_v.get("items"):
                        st = res_v["items"][0].get("statistics", {})
                        v_views = int(st.get("viewCount", 0))
                        v_likes = int(st.get("likeCount", 0))
                        v_comm = int(st.get("commentCount", 0))
                        eng = ((v_likes + v_comm) / v_views * 100.0) if v_views > 0 else 0.0
                        v_stats = {
                            "views": v_views,
                            "likes": v_likes,
                            "comments": v_comm,
                            "engagement_rate": round(eng, 2)
                        }
                except Exception:
                    pass

            channel_progress[lang] = {
                "channel_name": ch_name,
                "completed_stories": sorted(list(ch_completed)),
                "next_story": ch_next,
                "recent_video_title": recent_video_title,
                "recent_stats": v_stats
            }

            if not latest_global_audit and recent_video_id:
                latest_global_audit = {
                    "channel": ch_name,
                    "video_id": recent_video_id,
                    "title": recent_video_title,
                    "views": v_stats["views"],
                    "likes": v_stats["likes"],
                    "comments": v_stats["comments"],
                    "engagement_rate": v_stats["engagement_rate"],
                    "sentiment": "🔥 HIGH" if v_stats["engagement_rate"] >= 4.0 else ("✅ HEALTHY" if v_stats["engagement_rate"] >= 2.0 else "⚠️ MODERATE"),
                    "audited_at": datetime.now(timezone.utc).isoformat()
                }

        except Exception as e:
            if verbose:
                print(f"[{lang.upper()}] Notice during YouTube sync: {e}")

    # Determine next story across the multi-channel network:
    # If target_lang is specified, use that specific channel's next story
    if target_lang and target_lang != "all" and target_lang in channel_progress:
        global_next = channel_progress[target_lang]["next_story"]
    else:
        # Across the multi-channel network, identify the minimum next story.
        # This guarantees lagging channels catch up on missing stories before the network advances.
        all_channel_next_stories = [prog["next_story"] for prog in channel_progress.values()]
        global_next = min(all_channel_next_stories) if all_channel_next_stories else 1

    # Only mark a story completed globally if ALL channels have uploaded it
    if channel_progress:
        stories_completed_by_all = set.intersection(*(set(p["completed_stories"]) for p in channel_progress.values()))
    else:
        stories_completed_by_all = set()
    global_completed = sorted(list(stories_completed_by_all))

    # Update state.json
    state = {}
    if os.path.exists(state_file):
        try:
            with open(state_file, "r", encoding="utf-8") as sf:
                state = json.load(sf)
        except Exception:
            state = {}

    state["total_stories"] = 51
    state["completed_stories"] = global_completed
    state["current_story"] = global_next
    state["last_youtube_sync"] = datetime.now(timezone.utc).isoformat()
    state["channels_progress"] = channel_progress
    state["history"] = history_records
    if latest_global_audit:
        state["last_audit"] = latest_global_audit

    with open(state_file, "w", encoding="utf-8") as sf:
        json.dump(state, sf, indent=2, ensure_ascii=False)

    if verbose:
        print("📊 Channel-by-Channel YouTube Audit Summary:")
        print(f"{'Lang':<6} {'Channel Name':<28} {'Completed on YouTube':<24} {'Next Story'}")
        print("-" * 75)
        for lang, prog in sorted(channel_progress.items()):
            comp_str = str(prog["completed_stories"])
            nxt_str = f"Story #{prog['next_story']:02d}"
            print(f"{lang.upper():<6} {prog['channel_name'][:26]:<28} {comp_str:<24} {nxt_str}")
        print("-" * 75)
        if any(prog["next_story"] < max(all_channel_next_stories) for prog in channel_progress.values()):
            lagging = [l.upper() for l, prog in channel_progress.items() if prog["next_story"] == global_next]
            print(f"🎯 Network Target: Story #{global_next:02d} (Catching up lagging channels: {', '.join(lagging)})")
        else:
            print(f"🎯 Network Target: Story #{global_next:02d} (All channels synchronized)")
        if latest_global_audit:
            print(f"📈 Recent Video Audit: {latest_global_audit['title'][:35]}... ({latest_global_audit['views']} views, {latest_global_audit['engagement_rate']}% eng)")
        print("=" * 80 + "\n")

    return global_next, global_completed, channel_progress

if __name__ == "__main__":
    sync_mindnest_from_youtube(verbose=True)
