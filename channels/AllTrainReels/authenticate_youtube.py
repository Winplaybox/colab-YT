"""
AllTrainReels YouTube OAuth Authenticator
=========================================
- Authorizes your Google / YouTube account for @AllTrainReels
- Uses youtube_client_secret.json (installed client)
- Generates token.json and outputs ready-to-copy token string for GitHub Actions secret (ALLTRAINREELS_TOKEN_JSON)
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
        print(f"[ERROR] No client secret found at '{client_secret_path}'.")
        return

    print(f"Loading client secret from: {secret_file}")
    flow = InstalledAppFlow.from_client_secrets_file(secret_file, SCOPES)

    print("\nOpening browser for Google OAuth Authentication...")
    creds = flow.run_local_server(port=0, prompt="consent")

    title, cid = inspect_channel_info(creds)
    print(f"\n=======================================================")
    print(f" Authenticated YouTube Channel: '{title}' ({cid})")
    print(f"=======================================================\n")

    token_json_path = os.path.join(script_dir, "token.json")
    with open(token_json_path, "w", encoding="utf-8") as f:
        f.write(creds.to_json())
    print(f"Saved token to: {token_json_path}")

    token_pickle_path = os.path.join(script_dir, "token.pickle")
    with open(token_pickle_path, "wb") as f:
        pickle.dump(creds, f)

    token_str = creds.to_json()
    one_line = json.dumps(json.loads(token_str))
    print("\n" + "="*70)
    print("GITHUB ACTIONS SECRET (ALLTRAINREELS_TOKEN_JSON):")
    print("Copy this single line string and paste into GitHub repo secret:")
    print("="*70)
    print(one_line)
    print("="*70 + "\n")

if __name__ == "__main__":
    main()
