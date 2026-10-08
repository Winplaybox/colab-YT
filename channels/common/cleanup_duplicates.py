"""
YouTube Duplicate Content Manager Utility
=========================================
Safely manages redundant duplicate video uploads identified on live YouTube channels:
- ALWAYS preserves the canonical (first/oldest uploaded) video public.
- Modes:
  1. '--private' (Recommended): Changes privacy of all redundant duplicate videos to PRIVATE.
     Keeps views/analytics/history intact, but hides duplicates from public feeds and channel page.
  2. '--unlisted': Changes privacy of redundant duplicate videos to UNLISTED.
  3. '--delete --confirm': Permanently deletes redundant duplicates from YouTube.
  4. Default: Dry-run / audit report showing what would be updated.
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

def set_video_privacy(service, video_id, target_privacy="private"):
    """
    Safely changes video status to 'private' or 'unlisted' while preserving all metadata.
    """
    try:
        res = service.videos().list(id=video_id, part="snippet,status").execute()
        items = res.get("items", [])
        if not items:
            return False, "Video not found on YouTube"
        item = items[0]
        current_status = item.get("status", {}).get("privacyStatus")
        if current_status == target_privacy:
            return True, f"Already {target_privacy}"

        status = item.get("status", {})
        status["privacyStatus"] = target_privacy

        body = {
            "id": video_id,
            "snippet": item.get("snippet", {}),
            "status": status
        }
        service.videos().update(part="snippet,status", body=body).execute()
        return True, f"Privacy changed from '{current_status}' -> '{target_privacy}'"
    except Exception as e:
        return False, str(e)

def run_manager(channel_filter=None, action="audit", confirm_delete=False):
    print("=" * 80)
    print("🛡️ YOUTUBE DUPLICATE CONTENT MANAGER")
    if action == "private":
        print("   Action: 🔒 UPDATE REDUNDANT DUPLICATES TO PRIVATE (Safe & Recommended)")
    elif action == "unlisted":
        print("   Action: 🔗 UPDATE REDUNDANT DUPLICATES TO UNLISTED")
    elif action == "delete":
        print("   Action: ⚠️ PERMANENTLY DELETE REDUNDANT DUPLICATES")
    else:
        print("   Action: 🔍 AUDIT ONLY (Dry-Run: No changes applied)")
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
        try:
            with open(mn_cfg, "r", encoding="utf-8") as f:
                cfg = json.load(f)
            for ch in cfg.get("channels", []):
                channels.append((
                    ch["channel_name"],
                    os.path.join(mn_creds, f"token_{ch['lang_code']}.json")
                ))
        except Exception:
            pass

    total_redundant = 0
    updated_count = 0

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
            if not redundant_ids:
                continue

            total_redundant += len(redundant_ids)
            print(f"   📌 '{g['title']}' ({g['count']} copies on channel)")
            print(f"      ✅ KEEPING Canonical (oldest): {canon_id} (https://youtu.be/{canon_id})")

            for rid in redundant_ids:
                if action == "private":
                    print(f"      🔒 Setting PRIVATE: {rid}...", end=" ", flush=True)
                    ok, msg = set_video_privacy(service, rid, target_privacy="private")
                    if ok:
                        print(f"SUCCESS ✅ ({msg})")
                        updated_count += 1
                    else:
                        print(f"FAILED ❌ ({msg})")

                elif action == "unlisted":
                    print(f"      🔗 Setting UNLISTED: {rid}...", end=" ", flush=True)
                    ok, msg = set_video_privacy(service, rid, target_privacy="unlisted")
                    if ok:
                        print(f"SUCCESS ✅ ({msg})")
                        updated_count += 1
                    else:
                        print(f"FAILED ❌ ({msg})")

                elif action == "delete":
                    if not confirm_delete:
                        print(f"      ⚠️ DRY RUN Delete: {rid}")
                    else:
                        try:
                            print(f"      🗑️ DELETING: {rid}...", end=" ", flush=True)
                            service.videos().delete(id=rid).execute()
                            print("DONE ✅")
                            updated_count += 1
                        except Exception as de:
                            print(f"FAILED ❌ ({de})")
                else:
                    print(f"      ⚠️ REDUNDANT Duplicate: {rid} (https://youtu.be/{rid})")

    print("\n" + "=" * 80)
    if action in ("private", "unlisted"):
        print(f"🎉 Updated {updated_count} duplicate video(s) to '{action}'. Canonical originals remain untouched.")
    elif action == "delete" and confirm_delete:
        print(f"🎉 Permanently deleted {updated_count} duplicate video(s).")
    else:
        print(f"🔍 Found {total_redundant} redundant duplicate video(s) across audited channels.")
        print("💡 Quick Actions:")
        print("   1. To set all redundant duplicates to PRIVATE (Recommended):")
        print("      python channels/common/cleanup_duplicates.py --private")
        print("   2. To set them to UNLISTED:")
        print("      python channels/common/cleanup_duplicates.py --unlisted")
        print("   3. To permanently DELETE them:")
        print("      python channels/common/cleanup_duplicates.py --delete --confirm")
    print("=" * 80)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="YouTube Duplicate Content Manager")
    parser.add_argument("--channel", type=str, default=None, help="Filter by channel name")
    parser.add_argument("--private", action="store_true", help="Set redundant duplicates to private")
    parser.add_argument("--unlisted", action="store_true", help="Set redundant duplicates to unlisted")
    parser.add_argument("--delete", action="store_true", help="Delete redundant duplicates")
    parser.add_argument("--confirm", action="store_true", help="Explicit confirmation required for delete")
    args = parser.parse_args()

    act = "audit"
    if args.private:
        act = "private"
    elif args.unlisted:
        act = "unlisted"
    elif args.delete:
        if not args.confirm:
            print("⛔ SAFETY HALT: You must pass '--confirm' along with '--delete' to permanently remove videos.")
            sys.exit(1)
        act = "delete"

    run_manager(channel_filter=args.channel, action=act, confirm_delete=args.confirm)
