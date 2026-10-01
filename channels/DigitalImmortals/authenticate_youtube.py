"""
DigitalImmortals YouTube OAuth Authenticator
=============================================
Authorizes your Google / YouTube account for DigitalImmortals:
- Target Channel ID: UCO_AVV1aoIjGEgbj50HTJLw
- Target Handle: @DigitalImmortals
- Requested Scopes: YouTube Full Management, Upload, Readonly, and YouTube Analytics Readonly
- Saves token.json locally and outputs secret string for GitHub Actions (DIGITALIMMORTALS_TOKEN_JSON)
"""

import os
import sys
import glob
import json
import pickle

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

from google_auth_oauthlib.flow import InstalledAppFlow

EXPECTED_CHANNEL_ID = "UCO_AVV1aoIjGEgbj50HTJLw"
EXPECTED_NAME = "DigitalImmortals"

SCOPES = [
    'https://www.googleapis.com/auth/youtube',
    'https://www.googleapis.com/auth/youtube.upload',
    'https://www.googleapis.com/auth/youtube.readonly',
    'https://www.googleapis.com/auth/yt-analytics.readonly'
]

script_dir = os.path.dirname(os.path.abspath(__file__))
client_secret_path = os.path.join(script_dir, "client_secret.json")

def find_client_secret():
    if os.path.exists(client_secret_path):
        return client_secret_path
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
        print(f"Notice: Channel inspection error: {e}")
    return "Unknown", "Unknown"

def main():
    secret_file = find_client_secret()
    if not secret_file:
        print(f"[ERROR] No client secret found at '{client_secret_path}'.")
        return

    print("=" * 75)
    print(f">> AUTHENTICATING: {EXPECTED_NAME} ({EXPECTED_CHANNEL_ID})")
    print("=" * 75)
    print(f"Using client secret: {secret_file}")
    print("Scopes: YouTube Full + YouTube Analytics (for pre-upload retention audits)")
    print("A browser window will open. Sign into Google and choose @DigitalImmortals!\n")

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
    print("\n" + "=" * 75)
    if actual_id == EXPECTED_CHANNEL_ID:
        print(f"[SUCCESS] VERIFIED! Connected to target channel: '{actual_title}' ({actual_id})")
    else:
        print(f"[INFO] Connected to '{actual_title}' ({actual_id}). Target is: '{EXPECTED_NAME}' ({EXPECTED_CHANNEL_ID}).")
    print(f"Tokens saved locally:")
    print(f" - {token_json_path}")
    print(f" - {token_pickle_path}")
    print("=" * 75)
    print("\n[GITHUB SECRETS] For autonomous cloud workflows:")
    print("Add repository secret: DIGITALIMMORTALS_TOKEN_JSON")
    print("=" * 75)

if __name__ == "__main__":
    main()
