"""
MindNest Tales YouTube Algorithm Intelligence & Analytics Engine:
- Connects to all 11 YouTube channels via OAuth API.
- Pulls live subscriber counts, total views, video counts, and video-by-video performance.
- Computes Engagement Rate, Velocity (views/hour), and Shorts-to-Long conversion rates.
- Generates algorithmic insights & content recommendations for upcoming videos.
"""

import os
import sys
import json
from datetime import datetime, timezone

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

try:
    from googleapiclient.discovery import build
    from google.oauth2.credentials import Credentials
    HAS_GOOGLE = True
except ImportError:
    HAS_GOOGLE = False

analytics_dir = os.path.join(script_dir, "analytics")
os.makedirs(analytics_dir, exist_ok=True)

def parse_iso8601_duration(duration_str):
    """Converts ISO 8601 duration (e.g. PT3M2S) to seconds."""
    import re
    match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', duration_str)
    if not match:
        return 0
    h, m, s = match.groups()
    return int(h or 0) * 3600 + int(m or 0) * 60 + int(s or 0)

def fetch_channel_analytics(lang_code, channel_info):
    """Fetches real-time channel statistics and recent video metrics for a specific channel."""
    if not HAS_GOOGLE:
        return {"error": "Google API client library not available"}

    token_file = os.path.join(script_dir, "credentials", f"token_{lang_code}.json")
    if not os.path.exists(token_file):
        return {"error": f"No token found for {lang_code}"}

    try:
        creds = Credentials.from_authorized_user_file(token_file)
        youtube = build("youtube", "v3", credentials=creds)

        # 1. Channel Profile & Lifetime Stats
        ch_res = youtube.channels().list(mine=True, part="snippet,statistics,contentDetails").execute()
        if not ch_res.get("items"):
            return {"error": "No channel found for credentials"}

        ch_item = ch_res["items"][0]
        ch_snippet = ch_item["snippet"]
        ch_stats = ch_item["statistics"]
        uploads_playlist_id = ch_item["contentDetails"]["relatedPlaylists"]["uploads"]

        channel_summary = {
            "lang_code": lang_code,
            "channel_name": ch_snippet["title"],
            "handle": ch_snippet.get("customUrl", channel_info.get("handle", "")),
            "subscribers": int(ch_stats.get("subscriberCount", 0)),
            "total_views": int(ch_stats.get("viewCount", 0)),
            "video_count": int(ch_stats.get("videoCount", 0)),
            "videos": []
        }

        # 2. Fetch Recent Uploads
        playlist_items = youtube.playlistItems().list(
            playlistId=uploads_playlist_id,
            part="snippet,contentDetails",
            maxResults=15
        ).execute()

        video_ids = [item["contentDetails"]["videoId"] for item in playlist_items.get("items", [])]
        if video_ids:
            v_res = youtube.videos().list(
                id=",".join(video_ids),
                part="snippet,statistics,contentDetails"
            ).execute()

            now_utc = datetime.now(timezone.utc)
            for v_item in v_res.get("items", []):
                vid = v_item["id"]
                v_snip = v_item["snippet"]
                v_stat = v_item["statistics"]
                v_content = v_item["contentDetails"]

                dur_sec = parse_iso8601_duration(v_content.get("duration", "PT0S"))
                is_short = dur_sec <= 180

                pub_dt = datetime.fromisoformat(v_snip["publishedAt"].replace("Z", "+00:00"))
                hours_live = max((now_utc - pub_dt).total_seconds() / 3600.0, 0.1)

                views = int(v_stat.get("viewCount", 0))
                likes = int(v_stat.get("likeCount", 0))
                comments = int(v_stat.get("commentCount", 0))

                eng_rate = ((likes + comments) / views * 100.0) if views > 0 else 0.0
                velocity = views / hours_live

                channel_summary["videos"].append({
                    "video_id": vid,
                    "title": v_snip["title"],
                    "duration_seconds": dur_sec,
                    "format": "Short (3 Min)" if is_short else "Long Video (10 Min)",
                    "views": views,
                    "likes": likes,
                    "comments": comments,
                    "engagement_rate_pct": round(eng_rate, 2),
                    "views_per_hour": round(velocity, 2),
                    "published_at": v_snip["publishedAt"],
                    "url": f"https://youtu.be/{vid}"
                })

        return channel_summary
    except Exception as e:
        return {"error": str(e)}

def run_network_analytics_audit():
    """Scans all 11 channels and generates an actionable intelligence dossier."""
    from video_producer import load_network_config
    config = load_network_config()

    print(f"\n=======================================================")
    print(f"📊 INITIATING NETWORK-WIDE YOUTUBE ALGORITHM AUDIT")
    print(f"Channels: {len(config['channels'])} Languages")
    print(f"=======================================================")

    network_report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "total_network_subscribers": 0,
        "total_network_views": 0,
        "total_network_videos": 0,
        "channel_reports": {},
        "top_performing_videos": [],
        "recommendations": []
    }

    all_videos = []
    for ch in config["channels"]:
        lang = ch["lang_code"]
        name = ch["channel_name"]
        print(f"Scanning [{lang.upper()}] {name}...")

        ch_data = fetch_channel_analytics(lang, ch)
        network_report["channel_reports"][lang] = ch_data

        if "error" not in ch_data:
            network_report["total_network_subscribers"] += ch_data["subscribers"]
            network_report["total_network_views"] += ch_data["total_views"]
            network_report["total_network_videos"] += ch_data["video_count"]
            all_videos.extend(ch_data["videos"])

    # Rank top videos by views and engagement
    all_videos.sort(key=lambda v: (v["views"], v["engagement_rate_pct"]), reverse=True)
    network_report["top_performing_videos"] = all_videos[:10]

    # Algorithm Intelligence & Strategic Deductions
    recs = []
    if all_videos:
        short_views = sum(v["views"] for v in all_videos if "Short" in v["format"])
        long_views = sum(v["views"] for v in all_videos if "Long" in v["format"])
        
        recs.append({
            "category": "Format Dynamics",
            "insight": f"Shorts generated {short_views} views while Long videos generated {long_views} views.",
            "action": "Ensure all Shorts have an active 'Related Video' link pinned to the 10-minute compilation in YouTube Studio to convert viral swipe traffic into watch-hour gold."
        })

        top_video = all_videos[0]
        recs.append({
            "category": "High-Retention Themes",
            "insight": f"Top performing video: '{top_video['title']}' ({top_video['views']} views, {top_video['engagement_rate_pct']}% engagement).",
            "action": "Produce follow-up episodes featuring the same lead animal and pacing style in the next 10-minute anthology."
        })
    else:
        recs.append({
            "category": "Launch Ramp",
            "insight": "Initial uploads are seeding into the YouTube recommendation system.",
            "action": "Publish the 180s Short + 10-Minute Compilation dual-pair across all 11 languages to trigger algorithmic momentum and initial watch-hour velocity."
        })

    network_report["recommendations"] = recs

    # Save JSON summary
    json_path = os.path.join(analytics_dir, "analytics_summary.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(network_report, f, indent=2, ensure_ascii=False)

    # Generate Markdown Dossier
    md_path = os.path.join(analytics_dir, "ALGORITHM_INTELLIGENCE_REPORT.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("# 🏆 MindNest Tales: Algorithm Intelligence & Performance Audit\n\n")
        f.write(f"**Audit Timestamp**: `{network_report['timestamp']}`\n\n")
        f.write(f"### 🌐 Network Overview\n")
        f.write(f"- **Total Subscribers**: `{network_report['total_network_subscribers']:,}`\n")
        f.write(f"- **Total Lifetime Views**: `{network_report['total_network_views']:,}`\n")
        f.write(f"- **Total Active Videos**: `{network_report['total_network_videos']}`\n\n")

        f.write("### 📺 11-Channel Health Matrix\n\n")
        f.write("| Channel | Lang | Subs | Views | Videos | Status |\n")
        f.write("| :--- | :---: | :---: | :---: | :---: | :--- |\n")
        for lang, c_info in network_report["channel_reports"].items():
            if "error" in c_info:
                f.write(f"| {lang.upper()} | `{lang}` | - | - | - | ⚠️ `{c_info['error'][:30]}` |\n")
            else:
                f.write(f"| [{c_info['channel_name']}](https://youtube.com/{c_info['handle']}) | `{lang}` | {c_info['subscribers']} | {c_info['total_views']} | {c_info['video_count']} | ✅ Active |\n")

        f.write("\n### 🎯 Strategic Algorithm Recommendations\n\n")
        for r in network_report["recommendations"]:
            f.write(f"#### 💡 {r['category']}\n")
            f.write(f"- **Insight**: {r['insight']}\n")
            f.write(f"- **Action Plan**: **{r['action']}**\n\n")

    print(f"\n=======================================================")
    print(f"✅ AUDIT COMPLETE! Reports saved to:")
    print(f"   • {json_path}")
    print(f"   • {md_path}")
    print(f"=======================================================\n")
    return network_report

if __name__ == "__main__":
    run_network_analytics_audit()
