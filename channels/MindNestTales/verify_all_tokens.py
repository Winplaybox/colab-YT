import os
import sys
import json

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

script_dir = os.path.dirname(os.path.abspath(__file__))
creds_dir = os.path.join(script_dir, "credentials")
bundle_path = os.path.join(creds_dir, "all_tokens.json")

if not os.path.exists(bundle_path):
    print("No all_tokens.json found!")
    sys.exit(1)

with open(bundle_path, "r", encoding="utf-8") as f:
    all_tokens = json.load(f)

print(f"===========================================================")
print(f"🔍 VERIFYING ALL {len(all_tokens)} YOUTUBE CHANNELS VIA API")
print(f"===========================================================")

verified_count = 0
for lang, token_data in sorted(all_tokens.items()):
    token_file = os.path.join(creds_dir, f"token_{lang}.json")
    with open(token_file, "w", encoding="utf-8") as tf:
        json.dump(token_data, tf, indent=2)

    try:
        creds = Credentials.from_authorized_user_file(token_file)
        service = build("youtube", "v3", credentials=creds)
        res = service.channels().list(mine=True, part="snippet,id").execute()
        item = res["items"][0]
        title = item["snippet"]["title"]
        ch_id = item["id"]
        print(f"[{lang.upper()}] ✅ Channel: '{title}' (ID: {ch_id})")
        verified_count += 1
    except Exception as e:
        print(f"[{lang.upper()}] ❌ Failed to verify: {e}")

print(f"===========================================================")
print(f"🎉 VERIFIED {verified_count}/{len(all_tokens)} CHANNELS SUCCESSFULLY!")
print(f"===========================================================")
