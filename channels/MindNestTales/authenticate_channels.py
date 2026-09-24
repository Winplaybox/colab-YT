"""
MindNest Tales Multi-Channel YouTube OAuth Authenticator:
- Authorizes your Google / YouTube account for MindNest Tales channels
- Supports single-channel (e.g. 'hi', 'en') or interactive 'batch' mode across all channels
- Exports both single-secret (e.g. MINDNEST_TOKEN_HI_JSON) and unified master secret (MINDNEST_ALL_TOKENS_JSON)
"""

import os
import sys
import glob
import json
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

def load_channels():
    cfg = os.path.join(script_dir, "channels_config.json")
    with open(cfg, "r", encoding="utf-8") as f:
        return json.load(f)["channels"]

def inspect_channel_info(credentials):
    try:
        from googleapiclient.discovery import build
        service = build("youtube", "v3", credentials=credentials)
        ch_resp = service.channels().list(mine=True, part="snippet").execute()
        if ch_resp.get("items"):
            return ch_resp["items"][0]["snippet"]["title"], ch_resp["items"][0]["id"]
    except Exception:
        pass
    return "Unknown", "Unknown"

def export_all_tokens():
    creds_dir = os.path.join(script_dir, "credentials")
    all_tokens = {}
    if os.path.exists(creds_dir):
        for f in os.listdir(creds_dir):
            if f.startswith("token_") and f.endswith(".json"):
                lang = f.replace("token_", "").replace(".json", "")
                with open(os.path.join(creds_dir, f), "r", encoding="utf-8") as tf:
                    try:
                        all_tokens[lang] = json.load(tf)
                    except Exception:
                        pass
    return all_tokens

def authenticate_single_channel(secret_file, lang_code, channel_name=""):
    creds_dir = os.path.join(script_dir, "credentials")
    os.makedirs(creds_dir, exist_ok=True)
    token_out = os.path.join(creds_dir, f"token_{lang_code}.json")

    print("\n" + "=" * 65)
    print(f"👉 AUTHENTICATING: {channel_name or lang_code.upper()} ({lang_code})")
    print("=" * 65)
    print("A browser window will open. Sign into Google and select this specific Brand Channel!")
    
    flow = InstalledAppFlow.from_client_secrets_file(secret_file, scopes=SCOPES)
    credentials = flow.run_local_server(port=0, prompt='select_account consent', access_type='offline')

    token_json_str = credentials.to_json()
    with open(token_out, "w", encoding="utf-8") as f:
        f.write(token_json_str)

    actual_title, actual_id = inspect_channel_info(credentials)
    print(f"\n🎉 SUCCESS! Authorized for Channel: '{actual_title}' (ID: {actual_id})")
    print(f"Saved locally: {token_out}")
    return token_json_str

def main():
    secret_file = find_client_secret()
    if not secret_file:
        print("❌ Error: No 'youtube_client_secret.json' found.")
        print(f"Please ensure client secret is placed at: {client_secret_path}")
        return

    channels = load_channels()
    arg = sys.argv[1].lower() if len(sys.argv) > 1 else "menu"

    if arg == "export":
        all_tokens = export_all_tokens()
        if not all_tokens:
            print("No saved tokens found in credentials/ directory yet.")
            return
        print("\n" + "=" * 65)
        print("📦 UNIFIED MASTER GITHUB SECRET (MINDNEST_ALL_TOKENS_JSON):")
        print("=" * 65)
        print(json.dumps(all_tokens))
        print("=" * 65)
        return

    if arg == "batch":
        print("=" * 65)
        print("🚀 BATCH AUTHENTICATION WIZARD ACROSS ALL 11 CHANNELS")
        print("=" * 65)
        for ch in channels:
            l = ch["lang_code"]
            n = ch["channel_name"]
            ans = input(f"\nAuthenticate '{n}' ({l})? [Y/n/q]: ").strip().lower()
            if ans == "q":
                break
            if ans != "n":
                authenticate_single_channel(secret_file, l, n)
        
        all_tokens = export_all_tokens()
        print("\n" + "=" * 65)
        print("🎉 ALL-IN-ONE BUNDLE READY!")
        print("You can add this SINGLE secret to GitHub instead of 11 separate ones:")
        print("Secret Name: MINDNEST_ALL_TOKENS_JSON")
        print("Secret Value:")
        print(json.dumps(all_tokens))
        print("=" * 65)
        return

    # Check if arg matches a valid language code
    matched_ch = next((c for c in channels if c["lang_code"] == arg), None)
    if matched_ch:
        token_str = authenticate_single_channel(secret_file, matched_ch["lang_code"], matched_ch["channel_name"])
        print("\n" + "=" * 65)
        print(f"📋 GITHUB SECRET FOR THIS CHANNEL:")
        print(f"Name : {matched_ch.get('secret_token_name', f'MINDNEST_TOKEN_{arg.upper()}_JSON')}")
        print(f"Value:\n{token_str}")
        print("=" * 65)
        
        all_tokens = export_all_tokens()
        if all_tokens:
            print("\n💡 TIP: If you prefer ONE single secret for all channels, use:")
            print(f"Name : MINDNEST_ALL_TOKENS_JSON")
            print(f"Value: {json.dumps(all_tokens)}")
        return

    # Default interactive menu
    print("=" * 65)
    print("🔐 MINDNEST TALES MULTI-CHANNEL AUTHENTICATOR")
    print("=" * 65)
    print("Usage:")
    print("  python authenticate_channels.py hi     -> Authenticate Hindi channel")
    print("  python authenticate_channels.py en     -> Authenticate English channel")
    print("  python authenticate_channels.py batch  -> Interactive step-by-step for all channels")
    print("  python authenticate_channels.py export -> Export unified MINDNEST_ALL_TOKENS_JSON")
    print("=" * 65)

if __name__ == "__main__":
    main()
