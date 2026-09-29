"""
EpicBharatSaga YouTube OAuth Authenticator
==========================================
- Authorizes the Google account for EpicBharatSaga (@EpicBharatSaga).
- Same Google account as @TigerVlogs-2026 (epicbharat.official@gmail.com).
- When the browser opens, make sure to select the EpicBharatSaga CHANNEL
  (not the main account) — or you can switch channel after sign-in.
- Generates permanent offline credentials with refresh_token.
- Saves token.json & token.pickle locally.
- Formats ready-to-paste single-line JSON for GitHub Actions Secret (EPICBHARATSAGA_TOKEN_JSON).
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

EXPECTED_NAME    = "EpicBharatSaga"
EXPECTED_CHANNEL = "UCakmjqTBA6KgCF2F30Tnpjg"

SCOPES = [
    'https://www.googleapis.com/auth/youtube.upload',
    'https://www.googleapis.com/auth/youtube'
]

script_dir         = os.path.dirname(os.path.abspath(__file__))
client_secret_path = os.path.join(script_dir, "youtube_client_secret.json")


def find_client_secret():
    """Locates the client secret JSON — checks channel dir, repo root, then any client_secret*.json."""
    if os.path.exists(client_secret_path):
        return client_secret_path
    root_secret = os.path.join(script_dir, "..", "..", "youtube_client_secret.json")
    if os.path.exists(root_secret):
        return os.path.normpath(root_secret)
    # Also check the AllTrainReels folder (same project, same account)
    shared = os.path.join(script_dir, "..", "AllTrainReels", "youtube_client_secret.json")
    if os.path.exists(shared):
        return os.path.normpath(shared)
    matches = glob.glob(os.path.join(script_dir, "client_secret*.json"))
    if matches:
        return matches[0]
    return None


def inspect_channel_info(credentials):
    """Retrieves authenticated YouTube channel title and ID."""
    try:
        from googleapiclient.discovery import build
        service = build("youtube", "v3", credentials=credentials)
        ch_resp = service.channels().list(mine=True, part="snippet").execute()
        if ch_resp.get("items"):
            item = ch_resp["items"][0]
            return item["snippet"]["title"], item["id"]
    except Exception as e:
        print(f"Channel inspection notice: {e}")
    return "Unknown", "Unknown"


def update_channel_config(channel_title, channel_id):
    """Updates config.json and state.json with confirmed channel info."""
    config_file = os.path.join(script_dir, "config.json")
    if os.path.exists(config_file):
        try:
            with open(config_file, "r", encoding="utf-8") as f:
                cfg = json.load(f)
            if channel_id and channel_id != "Unknown":
                cfg["channel_id"]  = channel_id
                cfg["channel_url"] = f"https://www.youtube.com/channel/{channel_id}"
            with open(config_file, "w", encoding="utf-8") as f:
                json.dump(cfg, f, indent=2, ensure_ascii=False)
        except Exception:
            pass

    state_file = os.path.join(script_dir, "state.json")
    if os.path.exists(state_file):
        try:
            with open(state_file, "r", encoding="utf-8") as f:
                st = json.load(f)
            if channel_id and channel_id != "Unknown":
                st["channel_id"]   = channel_id
                st["channel_name"] = channel_title
            with open(state_file, "w", encoding="utf-8") as f:
                json.dump(st, f, indent=2, ensure_ascii=False)
        except Exception:
            pass


def main():
    secret_file = find_client_secret()
    if not secret_file:
        print(f"\n[ERROR] No client_secret / youtube_client_secret.json found.")
        print("Options:")
        print(f"  1. Copy from AllTrainReels: channels/AllTrainReels/youtube_client_secret.json")
        print(f"     -> channels/EpicBharatSaga/youtube_client_secret.json")
        print(f"  2. Or place it at: {client_secret_path}")
        return

    print("=" * 72)
    print(f">> AUTHENTICATING YOUTUBE CHANNEL: {EXPECTED_NAME}")
    print(f"   Email: epicbharat.official@gmail.com")
    print("=" * 72)
    print(f"Using client secret: {secret_file}")
    print()
    print("IMPORTANT: A browser window will open.")
    print("Sign in with epicbharat.official@gmail.com.")
    print("If you see multiple channels, select 'EpicBharatSaga' specifically.")
    print()

    flow = InstalledAppFlow.from_client_secrets_file(secret_file, scopes=SCOPES)
    credentials = flow.run_local_server(port=0, prompt='select_account consent', access_type='offline')

    actual_title, actual_id = inspect_channel_info(credentials)

    # Warn if wrong channel selected
    if actual_id != EXPECTED_CHANNEL and actual_id != "Unknown":
        print(f"\n⚠️  WARNING: Connected to '{actual_title}' ({actual_id})")
        print(f"   Expected: EpicBharatSaga ({EXPECTED_CHANNEL})")
        print("   If this is wrong, re-run and select the correct channel.")
    elif actual_id == EXPECTED_CHANNEL:
        print(f"\n✅ Correct channel confirmed: '{actual_title}' ({actual_id})")

    update_channel_config(actual_title, actual_id)

    token_json_path   = os.path.join(script_dir, "token.json")
    token_pickle_path = os.path.join(script_dir, "token.pickle")

    token_str = credentials.to_json()
    with open(token_json_path, "w", encoding="utf-8") as f:
        f.write(token_str)
    with open(token_pickle_path, "wb") as f:
        pickle.dump(credentials, f)

    print("\n" + "=" * 72)
    print(f"[SUCCESS] Connected to: '{actual_title}' ({actual_id})")
    print(f"Tokens saved:")
    print(f"  {token_json_path}")
    print(f"  {token_pickle_path}")
    print("=" * 72)

    one_line = json.dumps(json.loads(token_str))
    print("\n" + "=" * 72)
    print("GITHUB ACTIONS SECRET (EPICBHARATSAGA_TOKEN_JSON):")
    print("Go to: GitHub -> Repo Settings -> Secrets -> Actions -> New secret")
    print("Name:  EPICBHARATSAGA_TOKEN_JSON")
    print("Value:")
    print()
    print(one_line)
    print("=" * 72 + "\n")


if __name__ == "__main__":
    main()
