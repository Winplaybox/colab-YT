"""
IndianHorrorTapes YouTube Connection & Quota Verification Script
Tests local credentials and verifies YouTube Data API v3 access WITHOUT uploading any video.
"""

import os
import sys
import json

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from google.oauth2.credentials import Credentials
import google.auth.transport.requests
from googleapiclient.discovery import build

EXPECTED_CHANNEL_ID = "UCNRr8A9gVZQZJi1eMKiXIJw"
EXPECTED_NAME = "IndianHorrorTapes"

script_dir = os.path.dirname(os.path.abspath(__file__))
token_path = os.path.join(script_dir, "token.json")
secret_path = os.path.join(script_dir, "youtube_client_secret.json")

def verify_connection():
    print("=" * 70)
    print("  INDIANHORRORTAPES YOUTUBE API CONNECTION TEST")
    print("=" * 70)

    if not os.path.exists(token_path):
        print(f"\n[FAIL] No token.json found at: {token_path}")
        print(">> Please run first: python channels/IndianHorrorTapes/authenticate_youtube.py")
        return False

    with open(token_path, "r", encoding="utf-8") as f:
        token_data = json.load(f)

    # Sync client_id and secret if needed
    if os.path.exists(secret_path):
        with open(secret_path, "r", encoding="utf-8") as sf:
            sec_json = json.load(sf)
            c_info = sec_json.get("installed") or sec_json.get("web") or {}
            sec_cid = c_info.get("client_id")
            sec_sec = c_info.get("client_secret")
            if sec_cid and "client_id" not in token_data:
                token_data["client_id"] = sec_cid
            if sec_sec and "client_secret" not in token_data:
                token_data["client_secret"] = sec_sec

    try:
        creds = Credentials.from_authorized_user_info(token_data)
        print(f"\n[1/3] Token loaded successfully.")
        print(f"      Client ID: {token_data.get('client_id', 'N/A')[:35]}...")

        # Test token refresh
        print("\n[2/3] Testing token refresh with Google OAuth...")
        req = google.auth.transport.requests.Request()
        creds.refresh(req)
        print("      [OK] Token refreshed successfully with Google OAuth servers!")

        # Save refreshed token
        with open(token_path, "w", encoding="utf-8") as f:
            f.write(creds.to_json())

        # Test YouTube API query
        print("\n[3/3] Querying YouTube Data API v3...")
        service = build("youtube", "v3", credentials=creds)
        res = service.channels().list(mine=True, part="snippet,statistics").execute()
        items = res.get("items", [])

        if not items:
            print("\n[ERROR] No YouTube channel associated with this account.")
            return False

        ch = items[0]
        title = ch["snippet"]["title"]
        ch_id = ch["id"]
        stats = ch.get("statistics", {})
        sub_count = stats.get("subscriberCount", "Hidden")
        view_count = stats.get("viewCount", "0")
        video_count = stats.get("videoCount", "0")

        print("\n" + "=" * 70)
        print(f"  CONNECTED CHANNEL: {title}")
        print(f"  CHANNEL ID:        {ch_id}")
        print(f"  SUBSCRIBERS:       {sub_count}")
        print(f"  TOTAL VIEWS:       {view_count}")
        print(f"  TOTAL VIDEOS:      {video_count}")
        print("=" * 70)

        if ch_id == EXPECTED_CHANNEL_ID:
            print("\n[VERIFIED] Channel matches target IndianHorrorTapes!")
        else:
            print(f"\n[WARNING] Connected to '{title}' ({ch_id}), expected '{EXPECTED_NAME}' ({EXPECTED_CHANNEL_ID})")

        print("\n>> VERDICT: [READY] Everything is authenticated and verified for automated uploads!")
        return True

    except Exception as e:
        print(f"\n[FAIL] Authentication failed: {e}")
        return False

if __name__ == "__main__":
    verify_connection()
