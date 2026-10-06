"""
YouTube Duplicate Content Cleaner Utility
=========================================
Safely identifies and optionally removes redundant duplicate video uploads
identified on live YouTube channels:
- ALWAYS preserves the canonical (first/oldest uploaded) video.
- Only targets redundant duplicates created by accidental re-uploads.
- Runs in DRY-RUN / LIST mode by default for 100% safety.
- Requires explicit '--delete --confirm' to delete redundant duplicates via YouTube API.
"""

import os
import sys
import json
import argparse
from datetime import datetime

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

script_dir = os.path.dirname(os.path.abspath(__file__))
repo_root = os.path.abspath(os.path.join(script_dir, "..", ".."))
sys.path.insert(0, repo_root)

from channels.common.audit_all_channels import get_authenticated_service
from channels.common.youtube_duplicate_checker import audit_channel_uploads

def run_cleanup(channel_filter=None, delete_mode=False):
    print("=" * 80)
    print("🧹 YOUTUBE DUPLICATE VIDEO CLEANER")
    print(f"   Mode: {'⚠️ DELETE REDUNDANT COPIES' if delete_mode else '🔍 AUDIT / DRY-RUN (Safe - No deletions)'}")
    print("=" * 80)

    # 1. Main channels
    channels = [
        ("Digital Immortals", os.path.join(repo_root, "channels", "DigitalImmortals", "token.json")),
        ("Epic Bharat Saga", os.path.join(repo_root, "channels", "EpicBharatSaga", "token.json")),
        ("Indian Horror Tapes", os.path.join(repo_root, "channels", "IndianHorrorTapes", "token.json")),
        ("All Train Reels", os.path.join(repo_root, "channels", "AllTrainReels", "token.json")),
    ]

    # 2. MindNest Tales multilingual channels
    mn_cfg = os.path.join(repo_root, "channels", "MindNestTales", "channels_config.json")
    mn_creds = os.path.join(repo_root, "channels", "MindNestTales", "credentials")
    if os.path.exists(mn_cfg):
        with open(mn_cfg, "r", encoding="utf-8") as f:
            cfg = json.load(f)
        for ch in cfg.get("channels", []):
            channels.append((
                ch["channel_name"],
                os.path.join(mn_creds, f"token_{ch['lang_code']}.json")
            ))

    total_redundant = 0
    deleted_count = 0

    for ch_name, tok_path in channels:
        if channel_filter and channel_filter.lower() not in ch_name.lower():
            continue
        if not os.path.exists(tok_path):
            continue

        service, err = get_authenticated_service(tok_path)
        if err or not service:
            continue

        audit = audit_channel_uploads(service, max_results=150)
        dup_groups = audit.get("duplicate_groups", [])
        if not dup_groups:
            continue

        print(f"\n📺 [{ch_name}]")
        for g in dup_groups:
            canon_id = g["canonical_id"]
            redundant_ids = g["duplicate_video_ids"]
            total_redundant += len(redundant_ids)
            print(f"   📌 '{g['title']}' ({g['count']} copies on channel)")
            print(f"      ✅ KEEPING Canonical (oldest): {canon_id} (https://youtu.be/{canon_id})")

            for rid in redundant_ids:
                if delete_mode:
                    try:
                        print(f"      🗑️ DELETING Redundant: {rid}...", end=" ", flush=True)
                        service.videos().delete(id=rid).execute()
                        print("DONE ✅")
                        deleted_count += 1
                    except Exception as de:
                        print(f"FAILED ❌ ({de})")
                else:
                    print(f"      ⚠️ REDUNDANT Duplicate: {rid} (https://youtu.be/{rid})")

    print("\n" + "=" * 80)
    if delete_mode:
        print(f"🎉 Cleanup completed. Deleted {deleted_count} redundant duplicate videos.")
    else:
        print(f"🔍 Found {total_redundant} redundant duplicate videos across audited channels.")
        print("💡 To delete these redundant duplicates, run:")
        print("   python channels/common/cleanup_duplicates.py --delete --confirm")
    print("=" * 80)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="YouTube Duplicate Cleaner")
    parser.add_argument("--channel", type=str, default=None, help="Filter by channel name")
    parser.add_argument("--delete", action="store_true", help="Delete redundant duplicates")
    parser.add_argument("--confirm", action="store_true", help="Explicit confirmation required for delete")
    args = parser.parse_args()

    if args.delete and not args.confirm:
        print("⛔ SAFETY HALT: You must pass '--confirm' along with '--delete' to permanently remove videos.")
        sys.exit(1)

    run_cleanup(channel_filter=args.channel, delete_mode=(args.delete and args.confirm))
