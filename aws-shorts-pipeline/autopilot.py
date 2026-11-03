"""
=============================================================================
AWS SHORTS AUTOPILOT ENGINE (for EpicBharatSaga & YouTube Shorts)
=============================================================================
Features:
- Dual-Engine (AWS Bedrock + Polly Generative with Automatic Free Fallback)
- Automatic 9:16 Vertical Video Production
- Ready for YouTube Scheduling/Upload
=============================================================================
"""
import os
import sys
import argparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from generate_story import create_epic_bharat_story
from render_video import render_story_video

TOPIC_IDEAS = [
    ("Kailash Parvat Ka Rahasya", "Lord Shiva"),
    ("Mahadev Ne Neelkanth Kyun Dhaaran Kiya", "Lord Shiva"),
    ("Shiva Ka Teesri Aankh Ka Krodh", "Lord Shiva"),
    ("Kedarnath Mandir Ka Chamatkari Itihaas", "Lord Shiva"),
    ("Karna Ka Sabse Shaktishali Astra", "Lord Krishna"),
    ("Hanuman Ji Ne Surya Ko Kyun Nigla", "Lord Hanuman"),
    ("Sudarshana Chakra Ki Utpatti", "Lord Vishnu"),
]

def run_full_pipeline(topic="Kailash Parvat Ka Rahasya", deity="Lord Shiva", prefer_aws=True, render=True):
    print("=" * 60)
    print(f"🚀 LAUNCHING AWS SHORTS PIPELINE")
    print(f"   • Topic: {topic}")
    print(f"   • Deity: {deity}")
    print(f"   • Mode: {'AWS Cloud Engine (Bedrock + Polly)' if prefer_aws else 'Free Local Fallback'}")
    print("=" * 60)

    # Step 1: AI Script & Voiceover
    story, json_path = create_epic_bharat_story(topic=topic, deity=deity, prefer_aws=prefer_aws)

    # Step 2: Video Rendering
    video_path = None
    if render:
        try:
            video_path = render_story_video(json_path, quality="1080p")
        except Exception as e:
            print(f"[RENDER NOTICE] Video rendering step detail: {e}")
            print(f"[INFO] Story JSON and Audio MP3 are ready for video production.")

    print("\n" + "=" * 60)
    print("✅ PIPELINE EXECUTION SUMMARY")
    print("=" * 60)
    print(f"• Title: {story.get('title')}")
    print(f"• Story JSON: {json_path}")
    print(f"• Voiceover: {story.get('voiceover_path')}")
    if video_path:
        print(f"• Video MP4: {video_path}")
    print("=" * 60)
    return story, video_path

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AWS Shorts Autopilot Pipeline")
    parser.add_argument("--topic", type=str, default="Kailash Parvat Ka Rahasya", help="Shorts topic")
    parser.add_argument("--deity", type=str, default="Lord Shiva", help="Deity/Subject")
    parser.add_argument("--free", action="store_true", help="Force free local engine instead of AWS")
    parser.add_argument("--no-render", action="store_true", help="Skip video render (generate audio/script only)")

    args = parser.parse_args()
    prefer_aws = not args.free
    do_render = not args.no_render

    run_full_pipeline(topic=args.topic, deity=args.deity, prefer_aws=prefer_aws, render=do_render)
