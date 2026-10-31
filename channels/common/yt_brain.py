"""
YT brain: improves title / description / tags and picks a playlist right before every upload.

Rules come from the yt-package / yt-seo skills, plus this channel's own insights.json
(written weekly by channel_insights.py from real view data):
  * title <= 60 chars (hard cap 95), concrete noun/number/name, curiosity gap, no lies,
    <= 2 ALL-CAPS words, same language as the original
  * never drop an episode marker ("Ep 06", "#12", "कहानी 3") -> duplicate checkers rely on it
  * description keeps every URL, email, credit and hashtag line from the original
  * first 2 lines = hook + comment question (that's what shows above "...more")

Failsafe: any error, missing key or YT_BRAIN=off -> original metadata is used unchanged.

In a scheduler:
    body = before_insert("EpicBharatSaga", youtube, body)   # right before videos().insert
    after_insert("EpicBharatSaga", youtube, video_id)       # right after the id is known
"""
import json
import os
import re

from . import channel_profiles
from .channel_insights import load as load_insights

_PENDING_PLAYLIST = {}
_EP_MARKER = re.compile(
    r"(\(?\s*(?:ep|episode|भाग|अध्याय|part|story|कहानी)\.?\s*#?\s*\d+\s*\)?|#\d+\b)", re.I)
_KEEP_LINE = re.compile(r"https?://|@\w|[\w.+-]+@[\w-]+\.\w+|©|credit|image:|📷|📩|business|wikimedia|museum|public domain|cc by|cc0|^\s*•", re.I)


def _enabled():
    return os.environ.get("YT_BRAIN", "on").lower() != "off" and bool(os.environ.get("ANTHROPIC_API_KEY"))


def _ask_claude(prompt):
    import anthropic

    msg = anthropic.Anthropic().messages.create(
        model=os.environ.get("CLAUDE_MODEL", "claude-sonnet-5-5"), max_tokens=1600,
        messages=[{"role": "user", "content": prompt}])
    text = "".join(b.text for b in msg.content if getattr(b, "type", "") == "text")
    return json.loads(re.search(r"\{.*\}", text, re.S).group(0))


def _caps_ok(title):
    words = [w for w in re.findall(r"[A-Za-z]{3,}", title) if w.isupper()]
    return len(words) <= 2


def improve(channel, title, description, tags, is_short=True):
    """Pure function: returns dict(title, description, tags, playlist) or None to keep original."""
    prof = channel_profiles.get(channel)
    ins = load_insights(channel)
    learn = {k: ins.get(k) for k in ("winning_patterns", "avoid", "title_examples", "top_titles", "hook_rules") if ins.get(k)}
    if ins.get("niche_outliers"):   # /yt-viral: what beats other channels in this niche
        learn["niche_outliers"] = [{"title": o["title"], "multiple": o["multiple"], "formula": o.get("formula")}
                                   for o in ins["niche_outliers"][:5]]
    if "top_titles" in learn:
        learn["top_titles"] = learn["top_titles"][:6]
    playlists = prof.get("playlists") or []
    prompt = f"""You are the packaging editor of the YouTube channel "{channel}".
Niche: {prof['niche']}. Audience: {prof['audience']}. Language: {prof['language']}.
Format: {"YouTube Short (vertical, <60s)" if is_short else "long-form video"}.

What THIS channel's audience responds to (from its own analytics; empty = not enough data yet):
{json.dumps(learn, ensure_ascii=False)}

Original metadata (the video content is fixed; describe it truthfully):
TITLE: {title}
DESCRIPTION:
{description[:2500]}
TAGS: {", ".join(tags or [])}

Rewrite for maximum click-through AND accuracy:
- title: max 60 characters, same language as the original title, concrete (name, place, number), curiosity gap,
  at most 2 ALL-CAPS words, at most 1 emoji, no false promises. Follow the winning patterns above.
- description: line 1 = hook sentence; line 2 = one question inviting comments; then 2-4 short lines about the video
  with natural search keywords; then a subscribe line. Do NOT invent facts beyond the original.
- tags: 10-15 search phrases (mix of the channel language and English/Hinglish), most specific first.
- target_queries (/yt-seo): the 3 real searches this video should win; use the first one naturally in the title or
  first description line, and all three in the tags.
- the subject must survive the ~40-character mobile cut (front-load the name/place/number).
- playlist: choose exactly one from {json.dumps(playlists, ensure_ascii=False)} or "" if the list is empty.
Return ONLY JSON: {{"title": "...", "description": "...", "tags": ["..."], "target_queries": ["...", "...", "..."], "playlist": "..."}}"""
    out = _ask_claude(prompt)
    new_title = (out.get("title") or "").strip()
    if not new_title or len(new_title) > 95 or not _caps_ok(new_title):
        new_title = title
    # /yt-package lint (vendored title.py + Hindi layer): reject repeats of existing titles and worse titles
    try:
        from . import skills
        recent = ins.get("recent_titles") or [t["title"] for t in ins.get("top_titles", []) + ins.get("bottom_titles", [])]
        new_l = skills.lint_title(new_title, recent_titles=recent)
        old_l = skills.lint_title(title)
        if any(i[0] == "repeat" for i in new_l["issues"]) or new_l["score"] + 10 < old_l["score"]:
            print(f"[yt_brain] lint rejected '{new_title}' ({[i[0] for i in new_l['issues']]}); keeping original title")
            new_title = title
    except Exception as e:
        print(f"[yt_brain] lint notice: {e}")
    # keep episode marker so duplicate checkers keep working
    m = _EP_MARKER.search(title)
    if m and not _EP_MARKER.search(new_title):
        marker = m.group(1).strip()
        new_title = (new_title[: 95 - len(marker) - 3].rstrip() + " | " + marker)
    if "#shorts" in title.lower() and "#shorts" not in new_title.lower() and len(new_title) <= 88:
        new_title += " #Shorts"

    new_desc = (out.get("description") or "").strip() or description
    kept = [ln for ln in description.splitlines() if _KEEP_LINE.search(ln) and ln.strip() not in new_desc]
    hashtags = " ".join(dict.fromkeys(re.findall(r"#\w+", description)))
    if kept:
        new_desc += "\n\n" + "\n".join(kept)
    if hashtags and hashtags not in new_desc:
        new_desc += "\n\n" + hashtags
    if is_short and "#shorts" not in new_desc.lower():
        new_desc += " #Shorts"

    new_tags, total = [], 0
    for t in list(dict.fromkeys([*(out.get("target_queries") or []), *(out.get("tags") or []), *(tags or [])])):
        t = str(t).strip().lstrip("#")
        if t and total + len(t) + 1 <= 480:
            new_tags.append(t)
            total += len(t) + 1
    pl = out.get("playlist") if out.get("playlist") in playlists else ""
    return {"title": new_title, "description": new_desc[:4900], "tags": new_tags, "playlist": pl}


def before_insert(channel, youtube, body, is_short=None):
    """Mutates and returns the videos().insert body. Never raises."""
    try:
        if not _enabled():
            return body
        sn = body.setdefault("snippet", {})
        if is_short is None:   # infer from #Shorts in title/description
            is_short = "#shorts" in (sn.get("title", "") + sn.get("description", "")).lower()
        res = improve(channel, sn.get("title", ""), sn.get("description", ""), sn.get("tags", []), is_short)
        if res:
            print(f"🧠 [yt_brain] title: '{sn.get('title')}'  ->  '{res['title']}'")
            sn["title"], sn["description"], sn["tags"] = res["title"], res["description"], res["tags"]
            if res["playlist"] and not channel_profiles.get(channel).get("own_playlists"):
                _PENDING_PLAYLIST[id(youtube)] = res["playlist"]
    except Exception as e:
        print(f"[yt_brain] keeping original metadata ({e})")
    return body


def _playlist_id(youtube, title):
    tok = None
    while True:
        r = youtube.playlists().list(mine=True, part="snippet", maxResults=50, pageToken=tok).execute()
        for it in r.get("items", []):
            if it["snippet"]["title"].strip() == title.strip():
                return it["id"]
        tok = r.get("nextPageToken")
        if not tok:
            break
    r = youtube.playlists().insert(part="snippet,status", body={
        "snippet": {"title": title[:150]}, "status": {"privacyStatus": "public"}}).execute()
    print(f"📁 [yt_brain] created playlist '{title}'")
    return r["id"]


def after_insert(channel, youtube, video_id):
    """Adds the video to the playlist chosen in before_insert. Never raises."""
    title = _PENDING_PLAYLIST.pop(id(youtube), None)
    if not (title and video_id):
        return
    try:
        pid = _playlist_id(youtube, title)
        youtube.playlistItems().insert(part="snippet", body={"snippet": {
            "playlistId": pid, "resourceId": {"kind": "youtube#video", "videoId": video_id}}}).execute()
        print(f"📁 [yt_brain] added to playlist '{title}'")
    except Exception as e:
        print(f"[yt_brain] playlist notice: {e}")
