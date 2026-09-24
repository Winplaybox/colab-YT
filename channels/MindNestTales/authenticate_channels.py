"""
MindNest Tales Multi-Channel YouTube OAuth Authenticator:
- Authorizes your Google / YouTube account for MindNest Tales channels
- Generates master token.json or individual channel tokens (credentials/token_<lang>.json)
- Outputs GitHub Secret formatted JSON for 100% Zero-Touch autonomous cloud publishing
"""

import os
import sys
import glob
import json
from google_auth_oauthlib.flow import InstalledAppFlow

# YouTube Data API upload and thumbnail management scopes
SCOPES = [
    'https://www.googleapis.com/auth/youtube.upload',
    'https://www.googleapis.com/auth/youtube'
]

script_dir = os.path.dirname(os.path.abspath(__file__))
client_secret_path = os.path.join(script_dir, "youtube_client_secret.json")

def find_client_secret():
    if os.path.exists(client_secret_path):
        return client_secret_path
    root_secret = os.path.join(script_dir, "..", "..", "youtube_client_secret.json")
    if os.path.exists(root_secret):
        return root_secret
    matches = glob.glob(os.path.join(script_dir, "client_secret*.json"))
    if matches:
        return matches[0]
    return None

def main():
    secret_file = find_client_secret()
    if not secret_file:
        print("❌ Error: No 'youtube_client_secret.json' found.")
        print(f"Please ensure client secret is placed at: {client_secret_path}")
        return

    print("=" * 65)
    print("🔐 MINDNEST TALES MULTI-CHANNEL AUTHENTICATION ENGINE")
    print("=" * 65)
    print(f"Using Client Secret: {secret_file}")

    target_lang = sys.argv[1].lower() if len(sys.argv) > 1 else "master"

    creds_dir = os.path.join(script_dir, "credentials")
    os.makedirs(creds_dir, exist_ok=True)

    if target_lang in ["master", "all"]:
        token_out = os.path.join(script_dir, "token.json")
        secret_name = "MINDNEST_TOKEN_JSON"
        print("\nTarget: Master Account (All 11 Channels)")
    else:
        token_out = os.path.join(creds_dir, f"token_{target_lang}.json")
        secret_name = f"MINDNEST_TOKEN_{target_lang.upper()}_JSON"
        print(f"\nTarget: {target_lang.upper()} Channel Token")

    print("\nOpening browser for Google authorization...")
    print("👉 If prompted, choose the Google Account and select your MindNest Tales Channel!")

    flow = InstalledAppFlow.from_client_secrets_file(secret_file, scopes=SCOPES)
    credentials = flow.run_local_server(port=0)

    token_json_str = credentials.to_json()
    with open(token_out, "w", encoding="utf-8") as f:
        f.write(token_json_str)

    # Inspect authorized channel name
    channel_title = "Unknown"
    channel_id = "Unknown"
    try:
        from googleapiclient.discovery import build
        service = build("youtube", "v3", credentials=credentials)
        ch_resp = service.channels().list(mine=True, part="snippet").execute()
        if ch_resp.get("items"):
            channel_title = ch_resp["items"][0]["snippet"]["title"]
            channel_id = ch_resp["items"][0]["id"]
    except Exception:
        pass

    print("\n" + "=" * 65)
    print(f"🎉 SUCCESS! Authorized for Channel: '{channel_title}' (ID: {channel_id})")
    print(f"Token saved to: {token_out}")
    print("=" * 65)
    print(f"\n📋 TO ENABLE GITHUB ACTIONS CLOUD UPLOAD:")
    print(f"1. Go to your GitHub repository -> Settings -> Secrets and variables -> Actions")
    print(f"2. Click 'New repository secret'")
    print(f"3. Name: {secret_name}")
    print(f"4. Value: Paste the text below:\n")
    print(token_json_str)
    print("\n" + "=" * 65)

if __name__ == "__main__":
    main()
