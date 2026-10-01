"""
DigitalImmortals Pre-Upload Algorithmic Analytics Engine
======================================================
Audits previous video performance before scheduling the next episode:
- Checks total views, likes, comments, and engagement ratio.
- Evaluates audience feedback to optimize next episode's hook and pacing.
- Logs performance insights to state.json.
"""

import os
import sys
import json
from datetime import datetime

script_dir = os.path.dirname(os.path.abspath(__file__))
state_file = os.path.join(script_dir, "state.json")

def audit_previous_episode(youtube):
    """
    Fetches analytics for the last uploaded episode to inform the next release.
    """
    if not os.path.exists(state_file):
        return {"status": "NO_STATE_FILE"}

    with open(state_file, "r", encoding="utf-8") as f:
        state = json.load(f)

    history = state.get("history", [])
    if not history:
        print("📊 [ANALYTICS] No previous episode found. Ready for Episode 01 Genesis Launch!")
        return {"status": "FIRST_EPISODE"}

    last_ep = history[-1]
    video_id = last_ep.get("video_id")
    ep_num = last_ep.get("episode_number")

    if not video_id:
        print(f"📊 [ANALYTICS] Episode {ep_num} has no video ID recorded.")
        return {"status": "NO_VIDEO_ID"}

    print(f"\n" + "=" * 70)
    print(f"🔍 [ALGORITHMIC AUDIT] Auditing Episode {ep_num} ({video_id})...")
    print("=" * 70)

    try:
        res = youtube.videos().list(
            part="statistics,snippet",
            id=video_id
        ).execute()

        items = res.get("items", [])
        if not items:
            print(f"⚠️ Video {video_id} not found on YouTube.")
            return {"status": "NOT_FOUND"}

        stats = items[0]["statistics"]
        views = int(stats.get("viewCount", 0))
        likes = int(stats.get("likeCount", 0))
        comments = int(stats.get("commentCount", 0))

        like_ratio = (likes / views * 100) if views > 0 else 0
        comment_ratio = (comments / views * 100) if views > 0 else 0

        print(f"  📈 Views: {views:,}")
        print(f"  👍 Likes: {likes:,} (Engagement: {like_ratio:.2f}%)")
        print(f"  💬 Comments: {comments:,} (Velocity: {comment_ratio:.2f}%)")

        # Algorithmic Health Diagnosis
        if like_ratio >= 4.0:
            sentiment = "🔥 EXCEPTIONAL: High community resonance! Pacing and narrative voice are winning."
        elif like_ratio >= 2.0:
            sentiment = "✅ HEALTHY: Good baseline engagement. Maintain storytelling depth."
        else:
            sentiment = "⚠️ LOW ENGAGEMENT: Increase emotional stakes and refine thumbnail hook."

        print(f"  🧠 Diagnosis: {sentiment}")

        # Fetch top viewer comments to discover topics for next episode
        try:
            comment_res = youtube.commentThreads().list(
                part="snippet",
                videoId=video_id,
                maxResults=5,
                order="relevance"
            ).execute()
            print("\n  🗣️ Top Community Questions / Reactions:")
            for c in comment_res.get("items", []):
                text = c["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
                author = c["snippet"]["topLevelComment"]["snippet"]["authorDisplayName"]
                print(f"    - {author}: \"{text[:80]}...\"")
        except Exception:
            pass

        audit_data = {
            "episode_number": ep_num,
            "video_id": video_id,
            "views": views,
            "likes": likes,
            "comments": comments,
            "like_ratio": round(like_ratio, 2),
            "audited_at": datetime.now().isoformat(),
            "sentiment": sentiment
        }

        # Store in state
        state["last_audit"] = audit_data
        with open(state_file, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2, ensure_ascii=False)

        print("=" * 70)
        return audit_data

    except Exception as e:
        print(f"❌ Failed to audit video {video_id}: {e}")
        return {"status": "ERROR", "error": str(e)}

if __name__ == "__main__":
    print("Pre-Upload Algorithmic Analytics Engine Ready.")
