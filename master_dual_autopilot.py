"""
========================================================================================
🚀 MASTER DUAL-CHANNEL AUTOPILOT ENGINE — 24/7 CONTINUOUS PRODUCTION & SCHEDULING
========================================================================================
Channels Managed:
  1. 🏹 Digital Immortals (@DigitalImmortals)
     - Epic: 54-Episode Valmiki Ramayana Definitive Uncut
     - Format: 16:9 Landscape 1080p/8K NVENC Hardware Acceleration
     - Release Slots: Sundays @ 08:30 AM IST & Tuesdays @ 06:30 PM IST

  2. 🦁 MindNest Tales (11-Language Global Network)
     - Epic: 51-Story 3D Pixar Animation Moral Tales
     - Channels: Hindi, English, Spanish, Portuguese, French, German,
                 Arabic, Japanese, Korean, Vietnamese, Filipino
     - Release Slots: Wednesdays, Saturdays, Sundays at localized peak times

Key Capabilities:
  - 🔄 Continuous 24/7 non-stop execution with automatic recovery and retry
  - 🛡️ YouTube API Quota-Safe management & automatic midnight PST quota hibernation
  - ⚡ Sequential GPU/CPU hardware scheduling (prevents NVENC or RAM contention)
  - 📊 Unified terminal dashboard & persistent autopilot.log telemetry
========================================================================================
"""

import os
import sys
import time
import json
import traceback
import argparse
from datetime import datetime, timedelta, timezone

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
if hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Setup paths
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
CHANNELS_DIR = os.path.join(ROOT_DIR, "channels")
DI_DIR = os.path.join(CHANNELS_DIR, "DigitalImmortals")
MN_DIR = os.path.join(CHANNELS_DIR, "MindNestTales")
LOG_FILE = os.path.join(ROOT_DIR, "autopilot.log")

# Add channel folders to sys.path
for p in [ROOT_DIR, CHANNELS_DIR, DI_DIR, MN_DIR]:
    if p not in sys.path:
        sys.path.insert(0, p)

def log_event(message, level="INFO"):
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted = f"[{now_str}] [{level}] {message}"
    print(formatted)
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(formatted + "\n")
    except Exception:
        pass

def get_di_state():
    state_file = os.path.join(DI_DIR, "state.json")
    if os.path.exists(state_file):
        with open(state_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"current_episode": 1, "history": [], "total_episodes": 54}

def get_mn_state():
    state_file = os.path.join(MN_DIR, "state.json")
    if os.path.exists(state_file):
        with open(state_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"current_story": 1, "history": [], "total_stories": 51, "completed_stories": []}

def get_mn_config():
    cfg_file = os.path.join(MN_DIR, "channels_config.json")
    if os.path.exists(cfg_file):
        with open(cfg_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"channels": []}

def print_master_status():
    di_state = get_di_state()
    mn_state = get_mn_state()
    mn_config = get_mn_config()

    print("\n" + "=" * 82)
    print("🌐 MASTER DUAL-CHANNEL AUTOPILOT STATUS DASHBOARD")
    print(f"🕒 Current Local Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} IST")
    print("=" * 82)

    # 1. Digital Immortals Status
    print("\n🏹 CHANNEL 1: DIGITAL IMMORTALS (@DigitalImmortals)")
    print(f"   • Total Episodes Planned:   {di_state.get('total_episodes', 54)}")
    print(f"   • Uploaded / Scheduled:     {len(di_state.get('history', []))}")
    print(f"   • Next Episode in Queue:    Episode #{di_state.get('current_episode', 1):02d}")
    
    di_history = di_state.get("history", [])
    if di_history:
        print("   • Scheduled Release Slots:")
        for h in di_history[-4:]:
            print(f"     - Ep {h.get('episode_number'):02d} | Slot: {h.get('publish_at', 'Immediate')} | ID: {h.get('video_id')}")

    di_audit = di_state.get("last_audit")
    if di_audit:
        print(f"   • Live Analytics Audit (Ep {di_audit.get('episode_number', '?')}): {di_audit.get('views', 0):,} views, {di_audit.get('likes', 0):,} likes | {di_audit.get('sentiment', '')}")

    # 2. MindNest Tales Status
    print("\n🦁 CHANNEL 2: MINDNEST TALES (11-Language Global Network)")
    print(f"   • Total Stories Planned:    {mn_state.get('total_stories', 51)}")
    print(f"   • Completed Stories:        {mn_state.get('completed_stories', [])}")
    print(f"   • Next Story in Queue:      Story #{mn_state.get('current_story', 1):02d}")
    print(f"   • Recorded Releases:        {len(mn_state.get('history', []))}")

    mn_audit = mn_state.get("last_audit")
    if mn_audit:
        print(f"   • Live Analytics Audit (Story #{mn_audit.get('story_number', '?')}): {mn_audit.get('views', 0):,} views, {mn_audit.get('likes', 0):,} likes | {mn_audit.get('sentiment', '')}")
    
    creds_dir = os.path.join(MN_DIR, "credentials")
    ch_list = mn_config.get("channels", [])
    ready_count = 0
    for ch in ch_list:
        tok = os.path.join(creds_dir, f"token_{ch['lang_code']}.json")
        if os.path.exists(tok):
            ready_count += 1
    print(f"   • Language Channels Ready:  {ready_count}/{len(ch_list)} Channels Authenticated")

    print("\n" + "=" * 82 + "\n")

def run_digital_immortals_step(dry_run=False):
    """Executes production for the next Digital Immortals episode."""
    log_event("Starting Digital Immortals production cycle...", level="INFO")
    try:
        import channel_autopilot as di_autopilot
        state = get_di_state()
        ep_no = state.get("current_episode", 1)
        total = state.get("total_episodes", 54)

        if ep_no > total:
            log_event(f"Digital Immortals is 100% complete! All {total} episodes produced.", level="INFO")
            return True

        import importlib.util
        di_story_path = os.path.join(DI_DIR, "story_generator.py")
        spec = importlib.util.spec_from_file_location("di_story_generator", di_story_path)
        di_story = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(di_story)

        script_data = di_story.get_episode_script(ep_no)
        if not script_data or not script_data.get("scenes"):
            log_event(f"[DI] Episode #{ep_no:02d} script is not yet authored in story_generator.py. All 5 produced episodes (Ep 01-05) remain actively scheduled on YouTube through Oct 18.", level="INFO")
            return True

        di_autopilot_path = os.path.join(DI_DIR, "channel_autopilot.py")
        spec_ap = importlib.util.spec_from_file_location("di_channel_autopilot", di_autopilot_path)
        di_autopilot = importlib.util.module_from_spec(spec_ap)
        spec_ap.loader.exec_module(di_autopilot)

        log_event(f"Producing Digital Immortals Episode #{ep_no:02d} (Dry Run: {dry_run})...", level="INFO")
        success = di_autopilot.produce_and_schedule_episode(ep_no, dry_run=dry_run)
        if success:
            log_event(f"Digital Immortals Episode #{ep_no:02d} successfully produced & scheduled!", level="SUCCESS")
            return True
        else:
            log_event(f"Digital Immortals Episode #{ep_no:02d} returned false during production.", level="WARN")
            return False
    except Exception as e:
        err_msg = str(e)
        if "quotaExceeded" in err_msg:
            log_event("YouTube API Quota Exceeded during Digital Immortals upload.", level="WARN")
            raise e
        log_event(f"Error during Digital Immortals step: {e}\n{traceback.format_exc()}", level="ERROR")
        return False

def run_mindnest_step(target_lang="all", mode="short", quality="1080p", dry_run=False):
    """Executes production for the next MindNest Tales story."""
    log_event(f"Starting MindNest Tales production cycle (Lang: {target_lang.upper()}, Mode: {mode.upper()})...", level="INFO")
    try:
        import importlib.util
        # Stage 0: Live YouTube Ground Truth Sync
        try:
            syncer_path = os.path.join(MN_DIR, "youtube_syncer.py")
            spec_s = importlib.util.spec_from_file_location("mn_youtube_syncer", syncer_path)
            syncer = importlib.util.module_from_spec(spec_s)
            spec_s.loader.exec_module(syncer)
            next_story, completed, _ = syncer.sync_mindnest_from_youtube(verbose=False)
            log_event(f"[MN YouTube Sync] Ground Truth on YouTube: Completed {completed} | Next Unreleased: Story #{next_story:02d}", level="INFO")
        except Exception as se:
            log_event(f"[MN YouTube Sync] Note: {se}", level="WARN")

        sched_path = os.path.join(MN_DIR, "scheduler.py")
        spec_m = importlib.util.spec_from_file_location("mn_scheduler", sched_path)
        mn_scheduler = importlib.util.module_from_spec(spec_m)
        spec_m.loader.exec_module(mn_scheduler)

        state = get_mn_state()
        story_no = state.get("current_story", 3)

        log_event(f"Producing MindNest Tales Story #{story_no:02d} (Dry Run: {dry_run})...", level="INFO")
        results = mn_scheduler.run_mindnest_release(
            story_number=story_no,
            target_lang=target_lang,
            quality=quality,
            auto_advance=True,
            mode=mode,
            dry_run=dry_run
        )
        log_event(f"MindNest Tales Story #{story_no:02d} complete across {len(results or [])} targets.", level="SUCCESS")
        return True
    except Exception as e:
        err_msg = str(e)
        if "quotaExceeded" in err_msg:
            log_event("YouTube API Quota Exceeded during MindNest Tales upload.", level="WARN")
            raise e
        log_event(f"Error during MindNest Tales step: {e}\n{traceback.format_exc()}", level="ERROR")
        return False

def calculate_quota_reset_sleep_seconds():
    """Calculates seconds until next midnight Pacific Time (00:00 PST = 12:30/13:30 IST) + 15 min buffer."""
    now_utc = datetime.now(timezone.utc)
    # Pacific Time is UTC-7 (PDT) or UTC-8 (PST). Mid-point approx UTC 08:00 (13:30 IST)
    target_utc_hour = 8
    target_dt = now_utc.replace(hour=target_utc_hour, minute=15, second=0, microsecond=0)
    if target_dt <= now_utc:
        target_dt += timedelta(days=1)
    diff = (target_dt - now_utc).total_seconds()
    return max(diff, 300)

def continuous_autopilot_loop(interval_minutes=30, dry_run=False, mn_batch_langs=None, mn_mode="short"):
    """
    Master Non-Stop 24/7 Autopilot Loop:
    - Alternates production between Digital Immortals and MindNest Tales
    - Never terminates on errors; logs and backs off
    - Respects YouTube quota and hibernates until reset when reached
    """
    log_event("=" * 82, level="INFO")
    log_event("🚀 STARTING 24/7 CONTINUOUS MASTER DUAL-CHANNEL AUTOPILOT", level="INFO")
    log_event(f"   • Interval between cycles: {interval_minutes} minutes", level="INFO")
    log_event(f"   • Dry Run Mode:            {dry_run}", level="INFO")
    log_event(f"   • MindNest Release Mode:    {mn_mode.upper()} (Languages: {mn_batch_langs or 'all'})", level="INFO")
    log_event("=" * 82, level="INFO")

    cycle_count = 0
    while True:
        cycle_count += 1
        print("\n" + "#" * 82)
        log_event(f"🔄 BEGINNING MASTER AUTOPILOT CYCLE #{cycle_count}", level="INFO")
        print("#" * 82)

        try:
            print_master_status()

            # -------------------------------------------------------------
            # STEP 1: Process Digital Immortals
            # -------------------------------------------------------------
            di_state = get_di_state()
            di_ep = di_state.get("current_episode", 1)
            di_total = di_state.get("total_episodes", 54)
            di_history = di_state.get("history", [])

            # Check if DI has room in scheduled buffer (e.g. up to 6 scheduled ahead)
            if di_ep <= di_total:
                log_event(f"[DI] Checking production readiness for Episode #{di_ep:02d}...", level="INFO")
                run_digital_immortals_step(dry_run=dry_run)
                # Polite breathing room between GPU/API workloads
                time.sleep(15)
            else:
                log_event("[DI] All Ramayana episodes are already fully produced.", level="INFO")

            # -------------------------------------------------------------
            # STEP 2: Process MindNest Tales
            # -------------------------------------------------------------
            mn_state = get_mn_state()
            mn_story = mn_state.get("current_story", 1)
            mn_total = mn_state.get("total_stories", 51)

            if mn_story <= mn_total:
                log_event(f"[MN] Checking production readiness for Story #{mn_story:02d}...", level="INFO")
                target_languages = mn_batch_langs if mn_batch_langs else "all"
                run_mindnest_step(
                    target_lang=target_languages,
                    mode=mn_mode,
                    quality="1080p",
                    dry_run=dry_run
                )
            else:
                log_event("[MN] All MindNest Tales stories have completed their cycle.", level="INFO")

            log_event(f"Cycle #{cycle_count} completed smoothly.", level="SUCCESS")

        except Exception as e:
            err_text = str(e)
            if "quotaExceeded" in err_text:
                sleep_sec = calculate_quota_reset_sleep_seconds()
                hours = sleep_sec / 3600.0
                log_event(f"⚠️ YouTube API Daily Quota Exceeded! Entering Quota Hibernation for {hours:.1f} hours...", level="WARN")
                time.sleep(sleep_sec)
                log_event("Quota hibernation concluded. Resuming autopilot loop!", level="INFO")
                continue
            else:
                log_event(f"Exception encountered in Master Cycle #{cycle_count}: {e}", level="ERROR")
                log_event(traceback.format_exc(), level="ERROR")
                log_event("Entering 10-minute error backoff before retry...", level="WARN")
                time.sleep(600)
                continue

        # Normal cycle resting interval
        log_event(f"Sleeping for {interval_minutes} minutes until the next scheduled inspection...", level="INFO")
        for remaining in range(interval_minutes, 0, -5):
            print(f"⏳ [Heartbeat] Autopilot running active. Next cycle in {remaining} min...", end="\r")
            time.sleep(min(300, remaining * 60))
        print(" " * 60, end="\r")

def main():
    parser = argparse.ArgumentParser(description="Master Dual-Channel Autonomous Studio Engine")
    parser.add_argument("--status", "-s", action="store_true", help="Print unified channel dashboard & schedule status")
    parser.add_argument("--continuous", "-c", action="store_true", help="Run 24/7 continuous non-stop autopilot loop")
    parser.add_argument("--step-di", action="store_true", help="Trigger a single episode step for Digital Immortals")
    parser.add_argument("--step-mn", action="store_true", help="Trigger a single story step for MindNest Tales")
    parser.add_argument("--interval", type=int, default=30, help="Interval in minutes between continuous checks (default: 30)")
    parser.add_argument("--lang", type=str, default="all", help="Target language code for MindNest Tales or 'all'")
    parser.add_argument("--mn-mode", type=str, default="short", choices=["short", "dual", "long"], help="MindNest release mode")
    parser.add_argument("--dry-run", action="store_true", help="Render and produce locally without uploading to YouTube")

    args = parser.parse_args()

    if args.status:
        print_master_status()
    elif args.step_di:
        run_digital_immortals_step(dry_run=args.dry_run)
    elif args.step_mn:
        run_mindnest_step(target_lang=args.lang, mode=args.mn_mode, dry_run=args.dry_run)
    elif args.continuous:
        continuous_autopilot_loop(
            interval_minutes=args.interval,
            dry_run=args.dry_run,
            mn_batch_langs=args.lang,
            mn_mode=args.mn_mode
        )
    else:
        # Default action when run with no flags: show status and instructions
        print_master_status()
        print("💡 Usage Options:")
        print("   python master_dual_autopilot.py --continuous          # Start 24/7 Non-Stop Autopilot")
        print("   python master_dual_autopilot.py --status              # View Real-Time Channel Status")
        print("   python master_dual_autopilot.py --step-di             # Produce Next Digital Immortals Episode")
        print("   python master_dual_autopilot.py --step-mn             # Produce Next MindNest Story")
        print("   python master_dual_autopilot.py --continuous --dry-run # Run loop locally without uploading\n")

if __name__ == "__main__":
    main()
