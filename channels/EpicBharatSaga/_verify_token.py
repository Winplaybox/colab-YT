import json
from google.oauth2.credentials import Credentials
import google.auth.transport.requests
from googleapiclient.discovery import build

with open('channels/EpicBharatSaga/token.json') as f:
    data = json.load(f)

creds = Credentials.from_authorized_user_info(data)
if creds.expired and creds.refresh_token:
    print('Token expired - refreshing...')
    creds.refresh(google.auth.transport.requests.Request())
    with open('channels/EpicBharatSaga/token.json', 'w') as f:
        f.write(creds.to_json())
    print('Refreshed and saved.')

yt = build('youtube', 'v3', credentials=creds)
resp = yt.channels().list(mine=True, part='snippet').execute()
if resp.get('items'):
    ch = resp['items'][0]
    name = ch['snippet']['title']
    cid = ch['id']
    handle = ch['snippet'].get('customUrl', 'N/A')
    print(f'Channel : {name}')
    print(f'ID      : {cid}')
    print(f'Handle  : {handle}')
    expected = 'UCakmjqTBA6KgCF2F30Tnpjg'
    if cid == expected:
        print('SUCCESS - CORRECT EpicBharatSaga channel confirmed!')
    else:
        print(f'WARNING: Expected {expected} but got {cid}')
else:
    print('No channel found in response')
