"""
BuzzStormNow - One-Click Blogger OAuth Authenticator
===================================================
Run this script locally to grant permissions for https://buzzstormnow.blogspot.com
and generate 'blog/credentials/blogger_token.json'.
"""

import os
import sys
import glob
import json

from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = [
    "https://www.googleapis.com/auth/blogger"
]

script_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(script_dir)
creds_dir = os.path.join(script_dir, "credentials")

def find_client_secret():
    """Searches for Google OAuth client secret files."""
    candidates = [
        os.path.join(script_dir, "client_secret.json"),
        os.path.join(root_dir, "youtube_client_secret.json"),
        os.path.join(root_dir, "client_secret_web.json")
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    matches = glob.glob(os.path.join(root_dir, "client_secret*.json"))
    if matches:
        return matches[0]
    return None

def main():
    secret_file = find_client_secret()
    if not secret_file:
        print("❌ Error: No Google OAuth client secret file ('client_secret*.json') found.")
        print("👉 Download your OAuth 2.0 Client ID credentials from Google Cloud Console and place it in the project root.")
        return

    print("=" * 65)
    print(f"🔑 Using Google OAuth Client Secret: {os.path.basename(secret_file)}")
    print("🌐 Target Blog: BuzzStormNow (ID: 7128783356419391680)")
    print("Launching browser for Blogger authorization...")
    print("Please select the Google account that manages your Blogger site.")
    print("=" * 65)

    try:
        flow = InstalledAppFlow.from_client_secrets_file(secret_file, scopes=SCOPES)
        credentials = flow.run_local_server(port=0)

        os.makedirs(creds_dir, exist_ok=True)
        dest_token = os.path.join(creds_dir, "blogger_token.json")
        with open(dest_token, "w", encoding="utf-8") as f:
            f.write(credentials.to_json())

        print("\n" + "=" * 65)
        print(f"🎉 SUCCESS: Blogger credentials saved to:")
        print(f"   -> {dest_token}")
        print("=" * 65)
        print("🚀 For GitHub Actions CI/CD:")
        print("Copy the JSON contents of 'blog/credentials/blogger_token.json' and add it as")
        print("a repository Secret named 'BLOGGER_TOKEN_JSON'.")
        print("=" * 65)
    except Exception as e:
        print(f"❌ Authorization failed: {e}")

if __name__ == "__main__":
    main()
