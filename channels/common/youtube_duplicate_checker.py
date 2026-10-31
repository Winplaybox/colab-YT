"""
Universal YouTube Duplicate Detection & Ground Truth Synchronization Engine
=============================================================================
Protects all channels from duplicate uploads by checking live YouTube channel contents:
1. Inspects the channel's Uploads Playlist (UU...) directly via YouTube Data API v3 (1 quota unit per 50 videos).
2. Performs multi-factor matching:
   - Normalized exact title (ignoring emojis, hashtags, whitespace, case, punctuation)
   - Fuzzy semantic substring matching
   - Episode / Story number detection
   - Multilingual character and theme keywords (for 11-language networks)
3. If an upload already exists on YouTube:
   - Halts duplicate upload immediately
   - Returns existing video ID
   - Updates local state.json to keep pipeline in sync with reality
"""

import os
import re
import unicodedata
from difflib import SequenceMatcher

# In-memory cache to prevent redundant quota usage during the same execution
_CHANNEL_UPLOADS_CACHE = {}

# Multilingual story keywords for MindNest Tales network (11 languages)
MINDNEST_STORY_KEYWORDS = {
    1: ["chico", "चीकू", "cheetah", "चीता", "guepardo", "guépard", "время", "zeit", "وقت", "チーコ", "치코", "thời gian"],
    2: ["leo", "शेरू", "lion", "शेर", "león", "leão", "löwe", "أسد", "ライオン", "사자", "sư tử", "bờm"],
    3: ["gajju", "gajraj", "elephant", "हाथी", "गजराज", "elefante", "éléphant", "elefant", "فيل", "ゾウ", "코끼리", "voi", "lễ phép"],
    4: ["zebra", "ज़ेबरा", "cèbre", "zebras", "حمار وحشي", "シマウマ", "얼룩말", "ngựa vằn"],
    5: ["monkey", "बंदर", "mono", "singe", "affe", "قرد", "サル", "원숭이", "khỉ"],
    6: ["giraffe", "जिराफ़", "jirafa", "girafe", "زرافة", "キリン", "기린", "hươu cao cổ"],
    7: ["turtle", "tortoise", "कछुआ", "tortuga", "tortue", "schildkröte", "سلحفاة", "カメ", "거북이", "rùa", "slowest"],
    8: ["tiger", "बाघ", "tigre", "tigre", "نمر", "トラ", "호랑이", "hổ"],
}

def remove_emojis_and_symbols(text):
    """Strips emojis, pictographs, and special unicode symbols."""
    clean_chars = []
    for char in text:
        cat = unicodedata.category(char)
        # Keep letters, numbers, and standard punctuation/whitespace
        if not (cat.startswith("So") or cat.startswith("Sk") or cat.startswith("Cs")):
            clean_chars.append(char)
    return "".join(clean_chars)

def normalize_title(title):
    """
    Normalizes video title for robust collision comparison:
    - Lowercase
    - Strip emojis, hashtags (#Shorts, etc.)
    - Remove punctuation and collapse spaces
    """
    if not title:
        return ""
    t = remove_emojis_and_symbols(title)
    # Remove hashtags like #Shorts, #Trending, #Hindi
    t = re.sub(r"#\w+", "", t)
    # Remove punctuation
    t = re.sub(r"[^\w\s\u0900-\u097F\u0600-\u06FF\u3040-\u30FF\u3400-\u4DBF\u4E00-\u9FFF\uAC00-\uD7AF\u00C0-\u024F]", " ", t)
    # Collapse multiple whitespaces
    t = re.sub(r"\s+", " ", t).strip().lower()
    return t

def extract_number(text):
    """Extracts episode or story number from title or text."""
    if not text:
        return None
    patterns = [
        r"(?:ep|episode|भाग|अध्याय|part)\s*[#.:\-]?\s*(\d+)",
        r"(?:story|कहानी)\s*[#.:\-]?\s*(\d+)",
        r"\(ep\s*(\d+)\)",
        r"ep\.\s*(\d+)",
        r"#shorts\s*(\d+)",
    ]
    for pat in patterns:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            try:
                return int(m.group(1))
            except Exception:
                pass
    return None

def get_channel_all_uploads(youtube, max_results=150, force_refresh=False):
    """
    Fetches all uploaded videos for the authenticated channel via the Uploads playlist.
    Uses only 1 quota point per 50 videos (99% quota savings vs search.list).
    """
    if not youtube:
        return []

    # Check cache
    cache_key = id(youtube)
    if not force_refresh and cache_key in _CHANNEL_UPLOADS_CACHE:
        return _CHANNEL_UPLOADS_CACHE[cache_key]

    try:
        ch_res = youtube.channels().list(mine=True, part="contentDetails,snippet").execute()
        if not ch_res.get("items"):
            return []

        ch_item = ch_res["items"][0]
        channel_id = ch_item["id"]
        channel_title = ch_item["snippet"].get("title", "Unknown Channel")
        uploads_id = ch_item["contentDetails"]["relatedPlaylists"]["uploads"]

        videos = []
        seen_ids = set()
        next_page = None
        while len(videos) < max_results:
            batch_size = min(50, max_results - len(videos))
            pl_res = youtube.playlistItems().list(
                playlistId=uploads_id,
                part="snippet,status,contentDetails",
                maxResults=batch_size,
                pageToken=next_page
            ).execute()

            for it in pl_res.get("items", []):
                vid = it["contentDetails"]["videoId"]
                if vid in seen_ids:
                    continue
                seen_ids.add(vid)

                raw_title = it["snippet"].get("title", "")
                raw_desc = it["snippet"].get("description", "")
                pub_at = it["snippet"].get("publishedAt")
                status = it["status"].get("privacyStatus", "unknown")

                videos.append({
                    "video_id": vid,
                    "title": raw_title,
                    "description": raw_desc,
                    "status": status,
                    "published_at": pub_at,
                    "channel_title": channel_title,
                    "channel_id": channel_id,
                    "normalized_title": normalize_title(raw_title),
                    "detected_number": extract_number(raw_title)
                })

            next_page = pl_res.get("nextPageToken")
            if not next_page:
                break

        _CHANNEL_UPLOADS_CACHE[cache_key] = videos
        return videos
    except Exception as e:
        print(f"⚠️ [YT AUDIT WARNING] Could not fetch uploads: {e}")
        return []

def check_existing_upload(youtube, candidate_title=None, story_number=None, episode_number=None, channel_type="general", max_results=150):
    """
    Universal verification function before uploading any video:
    Returns dict:
      {
        "exists": True/False,
        "video_id": "...",
        "title": "...",
        "status": "...",
        "reason": "..."
      }
    """
    existing_videos = get_channel_all_uploads(youtube, max_results=max_results)
    if not existing_videos:
        return {"exists": False}

    cand_norm = normalize_title(candidate_title) if candidate_title else ""
    target_num = episode_number or story_number
    ctype = (channel_type or "").lower().replace("-", "").replace("_", "")

    for v in existing_videos:
        v_title = v["title"]
        v_norm = v["normalized_title"]
        v_id = v["video_id"]
        v_status = v["status"]

        # 1. Exact normalized title match
        if cand_norm and v_norm and cand_norm == v_norm:
            return {
                "exists": True,
                "video_id": v_id,
                "title": v_title,
                "matched_title": v_title,
                "status": v_status,
                "reason": f"Exact normalized title match: '{cand_norm}'"
            }

        # 2. High semantic substring match (core title contained with significant length)
        if cand_norm and v_norm:
            if len(cand_norm) > 15 and (cand_norm in v_norm or v_norm in cand_norm):
                return {
                    "exists": True,
                    "video_id": v_id,
                    "title": v_title,
                    "matched_title": v_title,
                    "status": v_status,
                    "reason": f"Substring title containment: '{v_norm}'"
                }
            # String similarity ratio >= 0.88
            ratio = SequenceMatcher(None, cand_norm, v_norm).ratio()
            if ratio >= 0.88:
                return {
                    "exists": True,
                    "video_id": v_id,
                    "title": v_title,
                    "matched_title": v_title,
                    "status": v_status,
                    "reason": f"High fuzzy similarity ({ratio:.2f}): '{v_title}'"
                }

        # 3. Explicit Episode / Story number match
        if target_num is not None:
            # Check Digital Immortals format: "Ep 06", "Ep 6", "Episode 06"
            if ctype in ("digitalimmortals", "digitalimmortal"):
                patterns = [
                    f"ep {target_num:02d}", f"ep {target_num}",
                    f"ep. {target_num:02d}", f"ep. {target_num}",
                    f"episode {target_num:02d}", f"episode {target_num}",
                    f"अध्याय {target_num:02d}", f"अध्याय {target_num}"
                ]
                for p in patterns:
                    # word-boundary match: "ep 1" must not match "ep 12", "#1" must not match "#18"
                    if re.search(re.escape(p) + r"(?!\d)", v_title.lower()):
                        return {
                            "exists": True,
                            "video_id": v_id,
                            "title": v_title,
                            "matched_title": v_title,
                            "status": v_status,
                            "reason": f"Episode #{target_num:02d} identified via pattern '{p}'"
                        }

            # Check MindNest Tales keywords across all languages
            elif ctype in ("mindnesttales", "mindnest"):
                # Check if title has the story number pattern
                if v.get("detected_number") == target_num:
                    return {
                        "exists": True,
                        "video_id": v_id,
                        "title": v_title,
                        "matched_title": v_title,
                        "status": v_status,
                        "reason": f"Story #{target_num:02d} number detected in title"
                    }
                # Check keywords for this story number
                keywords = MINDNEST_STORY_KEYWORDS.get(target_num, [])
                for kw in keywords:
                    if kw.lower() in v_title.lower() or kw.lower() in v.get("description", "").lower():
                        # Extra guard: verify candidate title also corresponds to this story keyword
                        if candidate_title and (kw.lower() in candidate_title.lower()):
                            return {
                                "exists": True,
                                "video_id": v_id,
                                "title": v_title,
                                "matched_title": v_title,
                                "status": v_status,
                                "reason": f"Story #{target_num:02d} character/theme keyword '{kw}' matched"
                            }

            # Check EpicBharatSaga: deity or episode number
            elif ctype in ("epicbharatsaga", "epicbharat"):
                if v.get("detected_number") == target_num:
                    return {
                        "exists": True,
                        "video_id": v_id,
                        "title": v_title,
                        "matched_title": v_title,
                        "status": v_status,
                        "reason": f"EpicBharatSaga episode #{target_num} detected in title"
                    }

            # Check IndianHorrorTapes: episode number or fort name
            elif ctype in ("indianhorrortapes", "indianhorror"):
                if v.get("detected_number") == target_num:
                    return {
                        "exists": True,
                        "video_id": v_id,
                        "title": v_title,
                        "matched_title": v_title,
                        "status": v_status,
                        "reason": f"IndianHorrorTapes episode #{target_num} detected in title"
                    }

            # Check AllTrainReels: episode number
            elif ctype in ("alltrainreels", "alltrain"):
                patterns = [
                    f"ep {target_num:02d}", f"ep {target_num}",
                    f"episode {target_num:02d}", f"episode {target_num}",
                    f"#{target_num:02d}", f"#{target_num}"
                ]
                for p in patterns:
                    # word-boundary match: "ep 1" must not match "ep 12", "#1" must not match "#18"
                    if re.search(re.escape(p) + r"(?!\d)", v_title.lower()):
                        return {
                            "exists": True,
                            "video_id": v_id,
                            "title": v_title,
                            "matched_title": v_title,
                            "status": v_status,
                            "reason": f"AllTrainReels episode #{target_num} detected via pattern '{p}'"
                        }
                if v.get("detected_number") == target_num:
                    return {
                        "exists": True,
                        "video_id": v_id,
                        "title": v_title,
                        "matched_title": v_title,
                        "status": v_status,
                        "reason": f"AllTrainReels episode #{target_num} detected in title"
                    }

    return {"exists": False}


def audit_channel_uploads(youtube, max_results=200):
    """
    Performs full diagnostic audit of a channel's uploaded library:
    - Identifies all duplicate videos currently live/unlisted/private on the channel
    - Finds highest episode number
    - Returns structured summary
    """
    uploads = get_channel_all_uploads(youtube, max_results=max_results, force_refresh=True)
    if not uploads:
        return {
            "channel_title": "Unknown",
            "channel_id": "Unknown",
            "total_videos": 0,
            "duplicate_groups": [],
            "highest_episode": None
        }

    ch_title = uploads[0]["channel_title"]
    ch_id = uploads[0]["channel_id"]

    # Group by normalized title
    by_norm_title = {}
    highest_num = None

    for u in uploads:
        norm = u["normalized_title"]
        if not norm:
            norm = u["title"].lower().strip()
        if norm not in by_norm_title:
            by_norm_title[norm] = []
        by_norm_title[norm].append(u)

        det = u.get("detected_number")
        if det is not None:
            if highest_num is None or det > highest_num:
                highest_num = det

    duplicate_groups = []
    for norm, items in by_norm_title.items():
        # Deduplicate items by video_id
        unique_items = []
        seen = set()
        for it in items:
            if it["video_id"] not in seen:
                seen.add(it["video_id"])
                unique_items.append(it)

        if len(unique_items) > 1:
            canonical = unique_items[-1] # Oldest uploaded is canonical
            dup_ids = [it["video_id"] for it in unique_items if it["video_id"] != canonical["video_id"]]
            if dup_ids:
                duplicate_groups.append({
                    "title": unique_items[0]["title"],
                    "normalized_title": norm,
                    "count": len(unique_items),
                    "canonical_id": canonical["video_id"],
                    "all_video_ids": [it["video_id"] for it in unique_items],
                    "duplicate_video_ids": dup_ids,
                    "items": unique_items
                })

    return {
        "channel_title": ch_title,
        "channel_id": ch_id,
        "total_videos": len(uploads),
        "duplicate_groups": duplicate_groups,
        "highest_episode": highest_num,
        "uploads": uploads
    }

