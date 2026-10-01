"""
DigitalImmortals Master Autonomous Studio Runner
=================================================
Unified CLI controller to execute the complete production pipeline:
- Usage:
    python run_studio_agent.py --episode 1       # Run full pipeline for Episode 1
    python run_studio_agent.py --audit           # Audit previous video analytics
    python run_studio_agent.py --thumbnail 1     # Generate master thumbnail
    python run_studio_agent.py --publish         # Execute scheduled publish pipeline
"""

import os
import sys
import json
import argparse

script_dir = os.path.dirname(os.path.abspath(__file__))
state_file = os.path.join(script_dir, "state.json")

import story_generator
import image_generator
import generate_thumbnail
import scheduler
from analytics_tracker import audit_previous_episode

def run_episode_pipeline(episode_num=1, dry_run=False):
    print("\n" + "=" * 75)
    print(f"🏹 DIGITAL IMMORTALS (@DigitalImmortals) — PRODUCING EPISODE {episode_num:02d}")
    print("=" * 75)

    # 1. Step 1: Pre-Upload Analytics Audit
    print("\n[Step 1/5] Auditing Previous Video Performance...")
    try:
        yt = scheduler.get_youtube_client()
        if yt:
            audit_previous_episode(yt)
    except Exception as e:
        print(f"Notice: Analytics audit skipped: {e}")

    # 2. Step 2: Generate Canonical Script
    print(f"\n[Step 2/5] Generating Canonical Hindi Script for Episode {episode_num:02d}...")
    script_path = story_generator.save_episode_json(episode_num)

    # 3. Step 3: Generate 16:9 Landscape Visuals
    print(f"\n[Step 3/5] Generating 16:9 Landscape Imagery for Episode {episode_num:02d}...")
    image_generator.generate_episode_images(episode_num)

    # 4. Step 4: Generate Master Thumbnail
    print(f"\n[Step 4/5] Rendering High-CTR Master Thumbnail...")
    thumb_path = generate_thumbnail.generate_master_thumbnail(episode_num)

    # 5. Step 5: Scheduler & YouTube Readiness
    print(f"\n[Step 5/5] Checking YouTube Schedule & Playlists...")
    publish_slot = scheduler.get_next_optimal_publish_time()
    print(f"⏰ Next Optimal Release Slot: {publish_slot} (UTC)")

    print("\n" + "=" * 75)
    print(f"🎉 EPISODE {episode_num:02d} PRODUCTION READY!")
    print(f"📁 Script:    {script_path}")
    print(f"🖼️ Thumbnail: {thumb_path}")
    print(f"🎯 Target:    @DigitalImmortals (54-Episode Valmiki Ramayana Saga)")
    print("=" * 75 + "\n")

def main():
    parser = argparse.ArgumentParser(description="DigitalImmortals Autonomous Studio Runner")
    parser.add_argument("--episode", type=int, default=1, help="Episode number to produce")
    parser.add_argument("--audit", action="store_true", help="Audit previous video analytics")
    parser.add_argument("--thumbnail", type=int, help="Generate thumbnail for specific episode")
    parser.add_argument("--publish", action="store_true", help="Execute scheduler & publish check")
    parser.add_argument("--dry-run", action="store_true", help="Run without uploading")

    args = parser.parse_args()

    if args.audit:
        yt = scheduler.get_youtube_client()
        if yt:
            audit_previous_episode(yt)
    elif args.thumbnail:
        generate_thumbnail.generate_master_thumbnail(args.thumbnail)
    elif args.publish:
        scheduler.run_pipeline()
    else:
        run_episode_pipeline(args.episode, dry_run=args.dry_run)

if __name__ == "__main__":
    main()
