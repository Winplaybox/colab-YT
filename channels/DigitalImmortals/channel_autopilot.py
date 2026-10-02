"""
DigitalImmortals Autonomous Master Autopilot Engine
====================================================
Fully autonomous end-to-end production and YouTube scheduler for the
54-episode Valmiki Ramayana Saga on @DigitalImmortals.

Executes the complete 6-stage lifecycle hands-free:
  Stage 1: Pre-Upload Retention & Algorithmic Audit of previous video
  Stage 2: Canonical 20-22 min Shuddh Hindi Script Generation (30 scenes, ~2,400 words)
  Stage 3: Public Domain Museum Art Harvesting & 30 Widescreen 16:9 Scenes
  Stage 4: High-CTR Master Thumbnail Rendering (16:9 Devanagari typography)
  Stage 5: Hardware-Accelerated NVENC Video & Timed SRT Narration Generation
  Stage 6: YouTube Upload, Optimal Slot Scheduling, Playlist Sync, & State Advance

Usage:
  python channel_autopilot.py --next             # Auto-produces & schedules the next episode
  python channel_autopilot.py --count 3          # Batch-produces & schedules the next 3 episodes
  python channel_autopilot.py --status           # Displays current schedule & pipeline status
"""

import os
import sys
import json
import argparse
import subprocess
from datetime import datetime

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

script_dir = os.path.dirname(os.path.abspath(__file__))
state_file = os.path.join(script_dir, "state.json")
episodes_dir = os.path.join(script_dir, "episodes")
output_dir = os.path.join(script_dir, "output")

import story_generator
import image_generator
import generate_thumbnail
import video_producer
import scheduler
from art_harvester import harvest_episode_anchors
from analytics_tracker import audit_previous_episode

def get_current_state():
    if os.path.exists(state_file):
        with open(state_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"current_episode": 1, "history": []}

def print_channel_status():
    state = get_current_state()
    history = state.get("history", [])
    current_ep = state.get("current_episode", 1)
    
    print("\n" + "=" * 78)
    print("🏹 DIGITAL IMMORTALS (@DigitalImmortals) — AUTONOMOUS CHANNEL STATUS")
    print("=" * 78)
    print(f"📊 Total Episodes Planned: {state.get('total_episodes', 54)}")
    print(f"✅ Episodes Published / Scheduled: {len(history)}")
    print(f"🎯 Next Episode in Pipeline: Ep {current_ep:02d}")
    print("-" * 78)
    print(f"{'Ep #':<6} {'Video ID':<14} {'Release Slot (UTC)':<24} {'Title'}")
    print("-" * 78)
    for h in history:
        ep_no = f"Ep {h.get('episode_number'):02d}"
        vid = h.get("video_id", "N/A")
        slot = h.get("publish_at", "Immediate")
        title = h.get("title", "")[:32] + "..." if len(h.get("title", "")) > 32 else h.get("title", "")
        print(f"{ep_no:<6} {vid:<14} {slot:<24} {title}")
    
    next_slot = scheduler.get_next_optimal_publish_time()
    print("-" * 78)
    print(f"⏰ Next Available Publishing Slot: {next_slot} (UTC)")
    print("=" * 78 + "\n")

def produce_and_schedule_episode(episode_num, dry_run=False):
    print("\n" + "#" * 78)
    print(f"🎬 [AUTOPILOT] STARTING COMPLETE PRODUCTION FOR EPISODE {episode_num:02d} / 54")
    print("#" * 78)

    # Stage 1: Algorithmic & Retention Audit
    print(f"\n[Stage 1/6] Auditing Channel Performance...")
    try:
        yt = scheduler.get_youtube_client()
        if yt:
            audit_previous_episode(yt)
    except Exception as e:
        print(f"Notice: Analytics audit skipped: {e}")

    # Stage 2: Canonical Script Generation (Valmiki Ramayana 22-min format)
    print(f"\n[Stage 2/6] Generating Canonical 22-Minute Script for Episode {episode_num:02d}...")
    script_path = story_generator.save_episode_json(episode_num)

    # Stage 3: Public Domain Museum Art Harvesting & 30 Scenes
    print(f"\n[Stage 3/6] Sourcing Authentic Museum Artworks & Generating Visuals...")
    try:
        harvest_episode_anchors(episode_num)
    except Exception as ae:
        print(f"Notice: Museum art harvester notice: {ae}")
    image_generator.generate_episode_images(episode_num)

    # Stage 4: High-CTR Master Thumbnail
    print(f"\n[Stage 4/6] Rendering High-CTR 16:9 Landscape Thumbnail...")
    thumb_path = generate_thumbnail.generate_master_thumbnail(episode_num)

    # Stage 5: Video Narration & Hardware NVENC Video Rendering
    print(f"\n[Stage 5/6] Synthesizing Baritone Voice & Hardware-Accelerated Rendering...")
    master_video = video_producer.render_episode_video(episode_num, target_quality="1080p")

    # Stage 6: YouTube Upload, Optimal Scheduling, & Playlist Sync
    print(f"\n[Stage 6/6] Scheduling Video to YouTube & Updating Playlists...")
    if dry_run:
        print(f"🔍 [DRY RUN] Skipping YouTube upload. Video and assets ready at: {master_video}")
        return True

    video_id, video_url = scheduler.upload_and_schedule_episode(episode_num, master_video, thumb_path)
    
    print("\n" + "=" * 78)
    print(f"🎉 [AUTOPILOT SUCCESS] EPISODE {episode_num:02d} FULLY PRODUCED & SCHEDULED!")
    print(f"   Video ID:     {video_id}")
    print(f"   YouTube URL:  {video_url}")
    print("=" * 78 + "\n")
    return True

def run_batch_autopilot(count=1, dry_run=False):
    for i in range(count):
        state = get_current_state()
        current_ep = state.get("current_episode", 1)
        total_episodes = state.get("total_episodes", 54)
        
        if current_ep > total_episodes:
            print(f"🎊 All {total_episodes} episodes of the Valmiki Ramayana Saga are fully produced & scheduled!")
            break

        print(f"\n>>> Running Batch Iteration {i+1} of {count} (Episode {current_ep:02d}) <<<")
        success = produce_and_schedule_episode(current_ep, dry_run=dry_run)
        if not success:
            print(f"❌ Autopilot halted at Episode {current_ep:02d} due to an error.")
            break

def main():
    parser = argparse.ArgumentParser(description="DigitalImmortals Master Autonomous Channel Autopilot")
    parser.add_argument("--next", action="store_true", help="Automatically produce and schedule the next episode in queue")
    parser.add_argument("--count", type=int, default=1, help="Number of consecutive episodes to produce and schedule in batch")
    parser.add_argument("--status", action="store_true", help="Display current channel production and schedule status")
    parser.add_argument("--dry-run", action="store_true", help="Generate all scripts, audio, visuals, and video without uploading to YouTube")
    parser.add_argument("--episode", type=int, help="Force produce a specific episode number")

    args = parser.parse_args()

    if args.status:
        print_channel_status()
    elif args.episode:
        produce_and_schedule_episode(args.episode, dry_run=args.dry_run)
    elif args.next:
        state = get_current_state()
        produce_and_schedule_episode(state.get("current_episode", 1), dry_run=args.dry_run)
    else:
        run_batch_autopilot(count=args.count, dry_run=args.dry_run)

if __name__ == "__main__":
    main()
