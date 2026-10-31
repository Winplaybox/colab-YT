"""
Weekly channel audit -> channels/<dir>/insights.json

Same method as the yt-analyze / yt-audit skills, in code:
  * rank recent uploads by multiple over the channel's own MEDIAN views (not raw views)
  * outliers >= 1.5x median = what the audience wants more of; bottom quartile = what to avoid
  * label each title with a hook formula, then ask Claude for patterns, title examples and
    next topics. yt_brain (titles/descriptions) and the script generators read this file.

Run:  python channels/common/channel_insights.py <ChannelKey>
Creds (env): <dir>_TOKEN_JSON style secrets are passed by the workflow as YT_TOKEN_JSON
             (several can be joined with '|||' for multi-language networks).
Quota: ~3-5 units per channel (playlistItems.list + videos.list). Safe to run weekly.
"""
import datetime as dt
import json
import os
import re
import statistics
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from channels.common import channel_profiles  # noqa: E402

HOOK_FORMULAS = [
    ("Question", r"\?|क्या|क्यों|कैसे|kya|kyun|kaise|why|how|what"),
    ("Statistic", r"\d"),
    ("Reveal", r"रहस्य|सच|secret|truth|rahasya|reveal|hidden|छिपा"),
    ("Superlative", r"सबसे|fastest|biggest|oldest|longest|highest|craziest|world's|duniya"),
    ("Warning", r"मत|never|don't|danger|खतरनाक|warning"),
    ("Comparison", r"\bvs\b|बनाम|versus"),
    ("Impossible Claim", r"फिर भी|still|impossible|असंभव|without"),
]


def label_formula(title):
    t = title.lower()
    return [name for name, pat in HOOK_FORMULAS if re.search(pat, t)] or ["Statement"]


def _client(token_json):
    import google.auth.transport.requests
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build

    creds = Credentials.from_authorized_user_info(json.loads(token_json))
    creds.refresh(google.auth.transport.requests.Request())
    return build("youtube", "v3", credentials=creds, cache_discovery=False)


def _iso_seconds(d):
    m = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", d or "")
    if not m:
        return 0
    h, mi, s = (int(x or 0) for x in m.groups())
    return h * 3600 + mi * 60 + s


def fetch_recent(youtube, limit=60):
    ch = youtube.channels().list(mine=True, part="contentDetails,snippet,statistics").execute()["items"][0]
    uploads = ch["contentDetails"]["relatedPlaylists"]["uploads"]
    ids, token = [], None
    while len(ids) < limit:
        r = youtube.playlistItems().list(playlistId=uploads, part="contentDetails",
                                         maxResults=50, pageToken=token).execute()
        ids += [it["contentDetails"]["videoId"] for it in r.get("items", [])]
        token = r.get("nextPageToken")
        if not token:
            break
    vids = []
    for i in range(0, len(ids[:limit]), 50):
        r = youtube.videos().list(id=",".join(ids[i:i + 50]),
                                  part="snippet,statistics,contentDetails,status").execute()
        for v in r.get("items", []):
            if v["status"].get("privacyStatus") != "public":
                continue
            st = v.get("statistics", {})
            vids.append({
                "id": v["id"],
                "title": v["snippet"]["title"],
                "published": v["snippet"]["publishedAt"][:10],
                "seconds": _iso_seconds(v["contentDetails"].get("duration")),
                "views": int(st.get("viewCount", 0)),
                "likes": int(st.get("likeCount", 0)),
                "comments": int(st.get("commentCount", 0)),
            })
    return {"channel_title": ch["snippet"]["title"],
            "subscribers": int(ch["statistics"].get("subscriberCount", 0)), "videos": vids}


def analyse(videos, min_age_days=3):
    """Pure stats (no API). Ignores videos younger than min_age_days (views not settled)."""
    today = dt.date.today()
    settled = [v for v in videos
               if (today - dt.date.fromisoformat(v["published"])).days >= min_age_days]
    if len(settled) < 4:
        return {"enough_data": False, "count": len(settled)}
    med = statistics.median(v["views"] for v in settled) or 1
    for v in settled:
        v["multiple"] = round(v["views"] / med, 2)
        v["formulas"] = label_formula(v["title"])
        v["engagement"] = round((v["likes"] + 2 * v["comments"]) / max(v["views"], 1) * 100, 2)
    ranked = sorted(settled, key=lambda v: v["multiple"], reverse=True)
    q = max(1, len(ranked) // 4)
    shorts = [v for v in settled if v["seconds"] <= 180]
    longs = [v for v in settled if v["seconds"] > 180]
    return {
        "enough_data": True,
        "count": len(settled),
        "median_views": med,
        "median_views_shorts": statistics.median([v["views"] for v in shorts]) if shorts else None,
        "median_views_long": statistics.median([v["views"] for v in longs]) if longs else None,
        "outliers": [v for v in ranked if v["multiple"] >= 1.5][:10],
        "bottom": ranked[-q:][:10],
    }


def summarise_with_claude(channel, stats):
    if not os.environ.get("ANTHROPIC_API_KEY"):
        return {}
    import anthropic

    prof = channel_profiles.get(channel)
    slim = lambda vs: [{k: v[k] for k in ("title", "views", "multiple", "formulas", "engagement", "seconds")} for v in vs]
    prompt = f"""You are auditing the YouTube channel "{channel}" ({prof['niche']}; audience: {prof['audience']}; language: {prof['language']}).
Median views per video: {stats['median_views']}.
TOP videos by multiple over median (what the audience wants):
{json.dumps(slim(stats['outliers']), ensure_ascii=False)}
BOTTOM videos (what they ignore):
{json.dumps(slim(stats['bottom']), ensure_ascii=False)}

Find what the winners share that the losers lack: topic type, how the title hooks (name hidden vs revealed, real place, number, question), length.
Be concrete, only claim patterns visible in this data. Return ONLY JSON:
{{"winning_patterns": ["3-5 short rules"], "avoid": ["2-4 short rules"],
  "title_examples": ["5 new titles in the channel's language that follow the winning rules, max 60 chars"],
  "topic_ideas": ["8 specific new video topics likely to perform, not already in the list above"],
  "one_fix": "the single most important change for the next 2 weeks"}}"""
    msg = anthropic.Anthropic().messages.create(
        model=os.environ.get("CLAUDE_MODEL", "claude-sonnet-5-5"), max_tokens=1500,
        messages=[{"role": "user", "content": prompt}])
    text = "".join(b.text for b in msg.content if getattr(b, "type", "") == "text")
    m = re.search(r"\{.*\}", text, re.S)
    return json.loads(m.group(0)) if m else {}


def run(channel):
    tokens = [t for t in os.environ.get("YT_TOKEN_JSON", "").split("|||") if t.strip()]
    if not tokens:
        print(f"[insights] {channel}: no YT_TOKEN_JSON, skipping")
        return None
    videos, subs, names = [], 0, []
    for t in tokens:
        data = fetch_recent(_client(t))
        videos += data["videos"]
        subs += data["subscribers"]
        names.append(data["channel_title"])
    stats = analyse(videos)
    out = {"channel": channel, "updated": dt.date.today().isoformat(), "youtube_channels": names,
           "subscribers": subs, **{k: v for k, v in stats.items() if k not in ("outliers", "bottom")}}
    if stats.get("enough_data"):
        out["top_titles"] = [{"title": v["title"], "multiple": v["multiple"], "views": v["views"]} for v in stats["outliers"]]
        out["bottom_titles"] = [{"title": v["title"], "multiple": v["multiple"], "views": v["views"]} for v in stats["bottom"]]
        try:
            out.update(summarise_with_claude(channel, stats))
        except Exception as e:
            print(f"[insights] Claude summary notice: {e}")
    path = channel_profiles.insights_path(channel)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f"[insights] {channel}: {stats.get('count')} videos, median {stats.get('median_views')} -> {path}")
    if out.get("one_fix"):
        print(f"[insights] ONE FIX: {out['one_fix']}")
    return out


def load(channel):
    try:
        with open(channel_profiles.insights_path(channel), encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


if __name__ == "__main__":
    run(sys.argv[1])
