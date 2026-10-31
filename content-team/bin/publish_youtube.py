#!/usr/bin/env python3
import sys
if sys.platform == 'win32':
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8')

"""
YouTube upload — hamesha PRIVATE. mode=schedule ho toh publishAt set hota hai
(video us time khud public hogi; beech mein Studio se rok sakte ho).

Pehli baar (har channel ke YouTube account ke liye ek baar):
  publish_youtube.py --channel indian-horror-tapes --auth
  -> credentials/client_secret.json chahiye (Google Cloud > YouTube Data API v3 > OAuth Desktop app)
  -> credentials/token_<channel>.json ban jayega

Roz:
  publish_youtube.py --channel indian-horror-tapes --episode <episode_dir>
  publish_youtube.py ... --dry-run     # upload ke bina sab check

Quota: ek upload ~1600 units, default 10,000/day -> ~6 uploads/day per Google project.
"""
import argparse
import datetime as dt
import json
import os
import sys
from pathlib import Path
from zoneinfo import ZoneInfo

import yaml

HOME = Path(os.environ.get("CT_HOME", Path(__file__).resolve().parent.parent)).resolve()
CRED = HOME / "credentials"
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
IST = ZoneInfo("Asia/Kolkata")


def fail(msg):
    print(json.dumps({"ok": False, "error": msg}, ensure_ascii=False))
    sys.exit(1)


def creds(ch, interactive=False):
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    tok = CRED / f"token_{ch}.json"
    c = Credentials.from_authorized_user_file(str(tok), SCOPES) if tok.exists() else None
    if c and c.expired and c.refresh_token:
        c.refresh(Request())
    if not c or not c.valid:
        if not interactive:
            fail(f"YouTube login nahi hai. Ek baar chalao: publish_youtube.py --channel {ch} --auth")
        from google_auth_oauthlib.flow import InstalledAppFlow
        secret = CRED / "client_secret.json"
        if not secret.exists():
            fail(f"{secret} missing")
        c = InstalledAppFlow.from_client_secrets_file(str(secret), SCOPES).run_local_server(
            port=0, open_browser=True)
    tok.parent.mkdir(exist_ok=True)
    tok.write_text(c.to_json())
    return c


def check_meta(meta, pc):
    t = (meta.get("title") or "").strip()
    if not t or len(t) > 100 or "<" in t or ">" in t:
        fail("meta.json: title khaali / 100+ chars / < > hai")
    desc = (meta.get("description") or "").strip()
    tags_line = " ".join(pc.get("hashtags", []))
    if tags_line and tags_line not in desc:
        desc = f"{desc}\n\n{tags_line}"
    if len(desc) > 5000:
        fail("description 5000 chars se lambi")
    tags, total = [], 0
    for tg in list(meta.get("tags", [])) + pc.get("default_tags", []):
        tg = str(tg).strip().lstrip("#").replace("<", "").replace(">", "")
        if not tg or tg.lower() in (x.lower() for x in tags):
            continue
        cost = len(tg) + (2 if " " in tg else 0) + 1
        if total + cost > 480:
            break
        tags.append(tg)
        total += cost
    return t, desc, tags


def next_slot(ch, pc):
    sched_p = HOME / "data" / ch / "schedule.json"
    used = set(json.loads(sched_p.read_text())) if sched_p.exists() else set()
    earliest = dt.datetime.now(IST) + dt.timedelta(hours=pc.get("min_lead_hours", 3))
    day = earliest.date()
    for _ in range(60):
        for s in sorted(pc.get("slots_ist", ["19:30"])):
            hh, mm = map(int, s.split(":"))
            t = dt.datetime(day.year, day.month, day.day, hh, mm, tzinfo=IST)
            iso = t.astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            if t >= earliest and iso not in used:
                return iso, sched_p, used
        day += dt.timedelta(days=1)
    fail("Agle 60 din mein koi slot khaali nahi")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--channel", required=True)
    ap.add_argument("--episode", type=Path)
    ap.add_argument("--auth", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    if a.auth:
        creds(a.channel, interactive=True)
        print(json.dumps({"ok": True, "message": "Login save ho gaya"}))
        return
    if not a.episode:
        fail("--episode chahiye")

    d = a.episode.resolve()
    if (d / "published.json").exists():
        fail("Ye episode pehle hi upload ho chuka hai")
    cc = yaml.safe_load((HOME / "channels" / f"{a.channel}.yaml").read_text(encoding="utf-8"))
    pc = cc["publish"]
    video = d / "video.mp4"
    if not video.exists():
        fail("video.mp4 nahi hai")
    title, desc, tags = check_meta(json.loads((d / "meta.json").read_text(encoding="utf-8")), pc)

    status = {"privacyStatus": "private",
              "selfDeclaredMadeForKids": bool(pc.get("made_for_kids", False)),
              "containsSyntheticMedia": bool(pc.get("synthetic_media", True))}
    publish_at = sched_p = used = None
    if pc.get("mode", "schedule") == "schedule":
        publish_at, sched_p, used = next_slot(a.channel, pc)
        status["publishAt"] = publish_at
    body = {"snippet": {"title": title, "description": desc, "tags": tags,
                        "categoryId": str(pc.get("category_id", "24")),
                        "defaultLanguage": "hi", "defaultAudioLanguage": "hi"},
            "status": status}

    if a.dry_run:
        print(json.dumps({"ok": True, "dry_run": True, "body": body}, ensure_ascii=False, indent=1))
        return

    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload
    yt = build("youtube", "v3", credentials=creds(a.channel))
    req = yt.videos().insert(part="snippet,status", body=body,
                             media_body=MediaFileUpload(str(video), chunksize=-1, resumable=True))
    resp = None
    while resp is None:
        _, resp = req.next_chunk()
    vid = resp["id"]
    rec = {"video_id": vid, "url": f"https://youtu.be/{vid}", "studio":
           f"https://studio.youtube.com/video/{vid}/edit", "publishAt": publish_at,
           "uploaded_at": dt.datetime.now(IST).isoformat(), "title": title}
    (d / "published.json").write_text(json.dumps(rec, ensure_ascii=False, indent=2), encoding="utf-8")
    if publish_at:
        used.add(publish_at)
        sched_p.parent.mkdir(parents=True, exist_ok=True)
        sched_p.write_text(json.dumps(sorted(used)))
    print(json.dumps({"ok": True, **rec}, ensure_ascii=False))


if __name__ == "__main__":
    main()
