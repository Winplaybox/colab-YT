"""
IndianHorrorTapes YouTube OAuth Authenticator:
- Authorizes your Google / YouTube account specifically for IndianHorrorTapes
- Target Channel ID: UCNRr8A9gVZQZJi1eMKiXIJw
- Generates token.json and token.pickle
- Provides ready-to-copy token string for GitHub Actions secret (INDIANHORRORTAPES_TOKEN_JSON)
"""

import os
import sys
import glob
import json
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow

EXPECTED_CHANNEL_ID = "UCNRr8A9gVZQZJi1eMKiXIJw"
EXPECTED_NAME = "IndianHorrorTapes"

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

def inspect_channel_info(credentials):
    try:
        from googleapiclient.discovery import build
        service = build("youtube", "v3", credentials=credentials)
        ch_resp = service.channels().list(mine=True, part="snippet").execute()
        if ch_resp.get("items"):
            return ch_resp["items"][0]["snippet"]["title"], ch_resp["items"][0]["id"]
    except Exception as e:
        print(f"Channel inspection error: {e}")
    return "Unknown", "Unknown"

def main():
    secret_file = find_client_secret()
    if not secret_file:
        print(f"❌ Error: No client secret found at '{client_secret_path}'.")
        return

    print("=" * 70)
    print(f"👉 AUTHENTICATING: {EXPECTED_NAME} ({EXPECTED_CHANNEL_ID})")
    print("=" * 70)
    print(f"Using client secret: {secret_file}")
    print("A browser window will open. Sign into Google and choose IndianHorrorTapes!\n")

    flow = InstalledAppFlow.from_client_secrets_file(
        secret_file,
        scopes=SCOPES
    )
    credentials = flow.run_local_server(port=0, prompt='select_account consent', access_type='offline')

    token_json_path = os.path.join(script_dir, "token.json")
    token_pickle_path = os.path.join(script_dir, "token.pickle")

    token_str = credentials.to_json()
    with open(token_json_path, "w", encoding="utf-8") as f:
        f.write(token_str)

    with open(token_pickle_path, "wb") as f:
        pickle.dump(credentials, f)

    actual_title, actual_id = inspect_channel_info(credentials)
    print("\n" + "=" * 70)
    if actual_id == EXPECTED_CHANNEL_ID:
        print(f"🎉 VERIFIED SUCCESS! Connected to target channel: '{actual_title}' ({actual_id})")
    else:
        print(f"⚠️ NOTICE: Connected to '{actual_title}' ({actual_id}). Expected '{EXPECTED_NAME}' ({EXPECTED_CHANNEL_ID}).")
    print(f"Tokens saved locally:")
    print(f" - {token_json_path}")
    print(f" - {token_pickle_path}")
    print("=" * 70)
    print("\n📋 For GitHub Actions 24/7 autonomous scheduling:")
    print("Go to GitHub -> Repo Settings -> Secrets and variables -> Actions")
    print("Add new repository secret: INDIANHORRORTAPES_TOKEN_JSON")
    print("Secret value:\n")
    print(token_str)
    print("\n" + "=" * 70)

if __name__ == "__main__":
    main()
