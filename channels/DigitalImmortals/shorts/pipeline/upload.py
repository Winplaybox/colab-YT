"""Uploads the finished Short to YouTube using the configured channel privacy policy."""
import json
import os

from . import config


def _credentials():
    from google.oauth2.credentials import Credentials

    raw = os.environ.get("DIGITALIMMORTALS_TOKEN_JSON", "").strip()
    if raw:
        return Credentials.from_authorized_user_info(json.loads(raw))
    if os.environ.get("YT_REFRESH_TOKEN"):
        required = ("YT_CLIENT_ID", "YT_CLIENT_SECRET")
        missing = [key for key in required if not os.environ.get(key)]
        if missing:
            raise RuntimeError("Missing YouTube OAuth settings: " + ", ".join(missing))
        return Credentials(
            None,
            refresh_token=os.environ["YT_REFRESH_TOKEN"],
            client_id=os.environ["YT_CLIENT_ID"],
            client_secret=os.environ["YT_CLIENT_SECRET"],
            token_uri="https://oauth2.googleapis.com/token",
        )
    token_file = config.CHANNEL_DIR / "token.json"
    if token_file.exists():
        return Credentials.from_authorized_user_info(json.loads(token_file.read_text(encoding="utf-8")))
    raise RuntimeError("No YouTube credentials: set DIGITALIMMORTALS_TOKEN_JSON or run "
                       "channels/DigitalImmortals/authenticate_youtube.py")


def _brain():
    import sys
    try:
        root = str(config.CHANNEL_DIR.parent.parent)
        if root not in sys.path:
            sys.path.insert(0, root)
        from channels.common import yt_brain
        return yt_brain
    except Exception as e:
        print(f"[upload] yt_brain unavailable: {e}")
        return None


def upload(path, meta: dict) -> str:
    import google.auth.transport.requests
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload

    if config.PRIVACY not in {"public", "private", "unlisted"}:
        raise ValueError(f"Unsupported YouTube privacy status: {config.PRIVACY!r}")

    creds = _credentials()
    creds.refresh(google.auth.transport.requests.Request())
    yt = build("youtube", "v3", credentials=creds, cache_discovery=False)

    hashtags = " ".join(dict.fromkeys(["#Shorts", "#DigitalImmortals", *meta.get("hashtags", [])]))
    credit_txt = ""
    if meta.get("credits"):
        credit_txt = "\\n\\n📷 Image credits:\\n" + "\\n".join(f"• {c}" for c in dict.fromkeys(meta["credits"]))
    description = (
        f"{meta['description']}\\n\\n"
        f"🔔 ऐसे और रहस्यों के लिए Subscribe करें — {config.CHANNEL_HANDLE}{credit_txt}\\n\\n{hashtags}"
    )
    tags, total = [], 0
    for tag in meta.get("tags", []):
        if total + len(tag) + 1 > 480:
            break
        tags.append(tag)
        total += len(tag) + 1
    body = {
        "snippet": {
            "title": meta["title"][:100],
            "description": description[:4900],
            "tags": tags,
            "categoryId": config.CATEGORY_ID,
            "defaultLanguage": "hi",
            "defaultAudioLanguage": "hi",
        },
        "status": {
            "privacyStatus": config.PRIVACY,
            "selfDeclaredMadeForKids": False,
        },
    }
    brain = _brain()
    if brain:
        body = brain.before_insert("DigitalImmortals", yt, body, is_short=True)
    req = yt.videos().insert(
        part="snippet,status", body=body,
        media_body=MediaFileUpload(str(path), mimetype="video/mp4", chunksize=-1, resumable=True))
    response = None
    while response is None:
        _, response = req.next_chunk()
    video_id = response.get("id")
    if not video_id:
        raise RuntimeError("YouTube upload completed without returning a video ID.")
    if brain:
        brain.after_insert("DigitalImmortals", yt, video_id)
    return video_id
