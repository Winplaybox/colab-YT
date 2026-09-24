"""
Authenticate YouTube Data API locally and generate token.pickle.
Run this script locally to open a browser window, grant permissions to your
YouTube channel, and produce token.pickle.

You can then upload `token.pickle` directly to Google Colab, allowing your
automated pipeline to upload videos without authentication errors.
"""

import os
import glob
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
PREFERRED_SECRET = 'youtube_client_secret.json'

def find_client_secret():
    if os.path.exists(PREFERRED_SECRET):
        return PREFERRED_SECRET
    matches = glob.glob('client_secret*.json')
    if matches:
        return matches[0]
    return None

def main():
    secret_file = find_client_secret()
    if not secret_file:
        print(f"Error: Neither '{PREFERRED_SECRET}' nor any 'client_secret*.json' found in current directory.")
        return

    print(f"Using client secret file: {secret_file}")
    print("Launching browser for Google/YouTube authorization...")
    print("Please select the Google account associated with your YouTube channel.")

    flow = InstalledAppFlow.from_client_secrets_file(
        secret_file,
        scopes=SCOPES
    )
    credentials = flow.run_local_server(port=0)

    with open('token.pickle', 'wb') as token:
        pickle.dump(credentials, token)

    print("\n" + "=" * 60)
    print("SUCCESS: 'token.pickle' generated successfully!")
    print("=" * 60)
    print("Steps for Google Colab:")
    print("1. Open your notebook in Google Colab.")
    print("2. In the left panel, click the folder (Files) icon.")
    print("3. Drag & drop 'token.pickle' into the files panel.")
    print("4. Run Step 6 in the notebook. It will load token.pickle automatically!")
    print("=" * 60)

if __name__ == '__main__':
    main()
