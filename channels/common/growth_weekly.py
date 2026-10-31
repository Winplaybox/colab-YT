"""
Weekly growth loop for one channel — the yt-* skills run end to end, in code:

  1. /yt-audit      own uploads: multiple over median, title lint, upload rhythm   (channel_insights)
  2. /yt-retention  YouTube Analytics: avg % viewed + hook leak / cliffs / slide for best & worst
  3. /yt-viral      niche: search -> competitor channels -> outliers >= 2x THEIR OWN median, formula
  4. /yt-comment    last 7 days of comments -> 4 piles, reply drafts in channel voice, what to pin
  5. /yt-plan       next 7 days: topics + hook + title, built from 1-4
  6. Claude merges everything into insights.json (+ one_fix); also writes
     comments_report.md and content_plan.json next to it.

Scripts (DI Shorts, Tiger) read content_plan.json; yt_brain reads insights.json on every upload.

    YT_TOKEN_JSON='<token json>[|||<token2>]' python channels/common/growth_weekly.py <ChannelKey>

Every step is optional and fails soft: a missing scope, quota error or missing key skips that step.
Quota: ~250 units per channel (2 search.list + cheap list calls). Auto-replies are OFF unless
COMMENT_AUTO_REPLY=true (then only the "questions" pile, max 10 replies).
"""
import datetime as dt
import json
import os
import re
import sys
from collections import Counter

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from channels.common import channel_insights as CI  # noqa: E402
from channels.common import channel_profiles as CP  # noqa: E402
from channels.common import skills as S  # noqa: E402


def _claude(prompt, max_tokens=2500):
    import anthropic

    msg = anthropic.Anthropic().messages.create(
        model=os.environ.get("CLAUDE_MODEL", "claude-sonnet-5-5"), max_tokens=max_tokens,
        messages=[{"role": "user", "content": prompt}])
    text = "".join(b.text for b in msg.content if getattr(b, "type", "") == "text")
    m = re.search(r"\{.*\}", text, re.S)
    return json.loads(m.group(0)) if m else {}


def _creds(token_json):
    import google.auth.transport.requests
    from google.oauth2.credentials import Credentials

    c = Credentials.from_authorized_user_info(json.loads(token_json))
    c.refresh(google.auth.transport.requests.Request())
    return c


def _yt(creds):
    from googleapiclient.discovery import build
    return build("youtube", "v3", credentials=creds, cache_discovery=False)


# ---------------- 1. audit extras ----------------
def rhythm(videos):
    dates = sorted({v["published"] for v in videos})
    if len(dates) < 3:
        return {}
    ds = [dt.date.fromisoformat(d) for d in dates]
    gaps = [(b - a).days for a, b in zip(ds, ds[1:])]
    last30 = [d for d in ds if (dt.date.today() - d).days <= 30]
    return {"uploads_last_30d": len(last30), "median_gap_days": sorted(gaps)[len(gaps) // 2],
            "longest_gap_days": max(gaps), "days_since_last": (dt.date.today() - ds[-1]).days}


def title_audit(videos):
    recent = sorted(videos, key=lambda v: v["published"], reverse=True)[:10]
    rows = []
    for v in recent:
        lt = S.lint_title(v["title"])
        hs = S.score_hook(v["title"])
        rows.append({"title": v["title"], "lint": lt["score"], "issues": [i[0] for i in lt["issues"]],
                     "formula": hs["formula"]})
    shapes = Counter(r["formula"] for r in rows)
    same_shape = shapes.most_common(1)[0] if shapes else ("", 0)
    return {"last10": rows, "avg_lint": round(sum(r["lint"] for r in rows) / max(len(rows), 1)),
            "dominant_formula": same_shape[0], "dominant_share": round(same_shape[1] / max(len(rows), 1), 2)}


# ---------------- 2. retention ----------------
def retention(creds, videos):
    try:
        from googleapiclient.discovery import build
        ya = build("youtubeAnalytics", "v2", credentials=creds, cache_discovery=False)
        end = dt.date.today().isoformat()
        start = (dt.date.today() - dt.timedelta(days=90)).isoformat()
        r = ya.reports().query(ids="channel==MINE", startDate=start, endDate=end,
                               metrics="views,averageViewPercentage,averageViewDuration",
                               dimensions="video", sort="-views", maxResults=30).execute()
        by_id = {v["id"]: v for v in videos}
        rows = []
        for vid, views, avp, avd in r.get("rows", []):
            if vid in by_id:
                rows.append({"id": vid, "title": by_id[vid]["title"], "views": views,
                             "avg_view_pct": round(avp, 1), "avg_view_s": avd, "seconds": by_id[vid]["seconds"]})
        if not rows:
            return {}
        pick = rows[:3] + sorted(rows, key=lambda x: x["avg_view_pct"])[:2]
        curves = []
        for v in {p["id"]: p for p in pick}.values():
            c = ya.reports().query(ids="channel==MINE", startDate=start, endDate=end,
                                   metrics="audienceWatchRatio", dimensions="elapsedVideoTimeRatio",
                                   filters=f"video=={v['id']}").execute().get("rows", [])
            summ = S.retention_summary([(float(x), float(y)) for x, y in c], v["seconds"])
            if summ:
                curves.append({"title": v["title"], "avg_view_pct": v["avg_view_pct"], **summ})
        med = sorted(x["avg_view_pct"] for x in rows)[len(rows) // 2]
        return {"median_avg_view_pct": med, "videos": rows[:15], "curves": curves}
    except Exception as e:
        print(f"[growth] retention skipped ({str(e)[:120]})")
        return {}


# ---------------- 3. niche viral ----------------
def niche_viral(yt, own_channel_id, profile):
    rows, seen = [], Counter()
    after = (dt.datetime.utcnow() - dt.timedelta(days=45)).strftime("%Y-%m-%dT%H:%M:%SZ")
    try:
        for q in profile.get("niche_queries", [])[:2]:
            kw = dict(q=q, part="snippet", type="video", order="viewCount", maxResults=25, publishedAfter=after)
            if profile.get("region"):
                kw["regionCode"] = profile["region"]
            if profile.get("lang"):
                kw["relevanceLanguage"] = profile["lang"]
            for it in yt.search().list(**kw).execute().get("items", []):
                cid = it["snippet"]["channelId"]
                if cid != own_channel_id:
                    seen[cid] += 1
        for cid, _ in seen.most_common(5):
            ch = yt.channels().list(id=cid, part="contentDetails,snippet").execute()["items"][0]
            up = ch["contentDetails"]["relatedPlaylists"]["uploads"]
            ids = [i["contentDetails"]["videoId"] for i in yt.playlistItems().list(
                playlistId=up, part="contentDetails", maxResults=25).execute().get("items", [])]
            if not ids:
                continue
            for v in yt.videos().list(id=",".join(ids), part="snippet,statistics").execute().get("items", []):
                rows.append({"channel": ch["snippet"]["title"], "title": v["snippet"]["title"],
                             "views": int(v["statistics"].get("viewCount", 0)),
                             "url": f"https://youtu.be/{v['id']}"})
        out, thin = S.niche_outliers(rows, min_multiple=2.0)
        return {"channels_studied": len({r["channel"] for r in rows}), "outliers": out[:12], "thin": thin}
    except Exception as e:
        print(f"[growth] niche viral skipped ({str(e)[:120]})")
        return {}


# ---------------- 4. comments ----------------
def comments(yt, channel_id, channel, profile):
    try:
        since = dt.datetime.utcnow() - dt.timedelta(days=7)
        items = yt.commentThreads().list(allThreadsRelatedToChannelId=channel_id, part="snippet",
                                         maxResults=100, order="time", textFormat="plainText").execute().get("items", [])
        cs = []
        for it in items:
            top = it["snippet"]["topLevelComment"]["snippet"]
            if dt.datetime.fromisoformat(top["publishedAt"].replace("Z", "+00:00")).replace(tzinfo=None) < since:
                continue
            cs.append({"id": it["snippet"]["topLevelComment"]["id"], "video": it["snippet"]["videoId"],
                       "text": top["textDisplay"][:300], "likes": top.get("likeCount", 0),
                       "replied": it["snippet"].get("totalReplyCount", 0) > 0})
        return cs
    except Exception as e:
        print(f"[growth] comments skipped ({str(e)[:120]})")
        return []


def triage_comments(channel, profile, cs):
    if not cs or not os.environ.get("ANTHROPIC_API_KEY"):
        return {}
    prompt = f"""Triage this week's YouTube comments for "{channel}" ({profile['niche']}; language: {profile['language']}).
Piles: questions (answer them), praise (heart it), critique (fix or correct; incl. factual corrections), spam_or_abuse (hold/remove).
Write short, warm replies in the channel's voice and the commenter's language for questions and critique. Never argue; never invent facts.
Pick the ONE comment to pin (most likely to start replies). List content ideas viewers are asking for.
Comments: {json.dumps(cs[:80], ensure_ascii=False)}
Return ONLY JSON: {{"questions": [{{"id": "...", "reply": "..."}}], "praise": ["id"], "critique": [{{"id": "...", "reply": "...", "action": "..."}}],
"spam_or_abuse": ["id"], "pin": {{"id": "...", "why": "..."}}, "viewer_requests": ["..."]}}"""
    try:
        return _claude(prompt)
    except Exception as e:
        print(f"[growth] comment triage notice: {e}")
        return {}


def auto_reply(yt, tri, limit=10):
    if os.environ.get("COMMENT_AUTO_REPLY", "false").lower() != "true":
        return 0
    n = 0
    for q in (tri.get("questions") or [])[:limit]:
        try:
            yt.comments().insert(part="snippet", body={"snippet": {"parentId": q["id"], "textOriginal": q["reply"]}}).execute()
            n += 1
        except Exception as e:
            print(f"[growth] reply notice: {e}")
            break
    return n


def comments_md(channel, cs, tri, replied):
    by = {c["id"]: c for c in cs}
    L = [f"# {channel} — comments, week of {dt.date.today().isoformat()}", "",
         f"{len(cs)} new comments. Auto-replies posted: {replied} (COMMENT_AUTO_REPLY={'on' if replied else 'off'}).", ""]
    if tri.get("pin"):
        p = tri["pin"]
        L += ["## Pin this", f"> {by.get(p.get('id'), {}).get('text', p.get('id'))}", f"Why: {p.get('why', '')}", ""]
    for pile, title in (("questions", "Questions — reply drafts"), ("critique", "Critique / corrections")):
        if tri.get(pile):
            L.append(f"## {title}")
            for q in tri[pile]:
                c = by.get(q.get("id"), {})
                L += [f"- **{c.get('text', '')[:160]}**  (video {c.get('video', '?')})",
                      f"  → {q.get('reply', '')}" + (f"  _[{q['action']}]_" if q.get("action") else "")]
            L.append("")
    if tri.get("viewer_requests"):
        L += ["## Viewers are asking for"] + [f"- {r}" for r in tri["viewer_requests"]] + [""]
    if tri.get("spam_or_abuse"):
        L += [f"## Spam/abuse to hold: {len(tri['spam_or_abuse'])} comments", ""]
    return "\n".join(L)


# ---------------- 5. plan + merge ----------------
def plan_and_merge(channel, profile, base, extra):
    if not os.environ.get("ANTHROPIC_API_KEY"):
        return {}, {}
    prompt = f"""You run growth for the YouTube channel "{channel}" ({profile['niche']}; audience {profile['audience']}; language {profile['language']}).
Data from this week:
OWN CHANNEL (multiple over median, top/bottom): {json.dumps({k: base.get(k) for k in ("median_views", "top_titles", "bottom_titles")}, ensure_ascii=False)}
TITLE AUDIT (last 10): {json.dumps(extra.get("title_audit"), ensure_ascii=False)}
UPLOAD RHYTHM: {json.dumps(extra.get("rhythm"))}
RETENTION: {json.dumps(extra.get("retention", {}).get("curves"), ensure_ascii=False)} median avg % viewed: {extra.get("retention", {}).get("median_avg_view_pct")}
NICHE OUTLIERS (other channels, >=2x their own median): {json.dumps([{k: o[k] for k in ("channel", "title", "multiple", "formula")} for o in extra.get("viral", {}).get("outliers", [])], ensure_ascii=False)}
VIEWER REQUESTS: {json.dumps(extra.get("viewer_requests"), ensure_ascii=False)}

Only claim patterns visible in this data. Return ONLY JSON:
{{"winning_patterns": ["3-5 rules"], "avoid": ["2-4 rules"],
 "title_examples": ["5 titles in the channel language, <=60 chars, following the rules"],
 "topic_ideas": ["8 topics"],
 "hook_rules": ["2-3 rules for the first 2 seconds, from retention + outliers"],
 "one_fix": "the single biggest change for the next 2 weeks",
 "dont_do_yet": "one thing NOT to do yet and why",
 "plan": [{{"day": 1, "topic": "...", "format": "...", "hook": "...", "title": "..."}}, ... 7 days]}}"""
    try:
        out = _claude(prompt, 3500)
    except Exception as e:
        print(f"[growth] plan notice: {e}")
        return {}, {}
    plan = out.pop("plan", [])
    start = dt.date.today()
    for p in plan:
        p["date"] = (start + dt.timedelta(days=int(p.get("day", 1)) - 1)).isoformat()
    return out, {"channel": channel, "created": start.isoformat(), "days": plan}


def run(channel):
    tokens = [t for t in os.environ.get("YT_TOKEN_JSON", "").split("|||") if t.strip()]
    if not tokens:
        print(f"[growth] {channel}: no YT_TOKEN_JSON, skipping")
        return
    profile = CP.get(channel)
    folder = os.path.dirname(CP.insights_path(channel))

    # 1. audit (all tokens, e.g. several MindNest languages)
    videos, subs, names, creds_list = [], 0, [], []
    for t in tokens:
        cr = _creds(t)
        creds_list.append(cr)
        d = CI.fetch_recent(_yt(cr))
        videos += d["videos"]; subs += d["subscribers"]; names.append(d["channel_title"])
    stats = CI.analyse(videos)
    base = {"channel": channel, "updated": dt.date.today().isoformat(), "youtube_channels": names,
            "subscribers": subs, **{k: v for k, v in stats.items() if k not in ("outliers", "bottom")}}
    if stats.get("enough_data"):
        base["top_titles"] = [{"title": v["title"], "multiple": v["multiple"], "views": v["views"]} for v in stats["outliers"]]
        base["bottom_titles"] = [{"title": v["title"], "multiple": v["multiple"], "views": v["views"]} for v in stats["bottom"]]
    base["recent_titles"] = [v["title"] for v in sorted(videos, key=lambda v: v["published"], reverse=True)[:60]]
    extra = {"rhythm": rhythm(videos), "title_audit": title_audit(videos)}

    yt0 = _yt(creds_list[0])
    own_id = yt0.channels().list(mine=True, part="id").execute()["items"][0]["id"]
    extra["retention"] = retention(creds_list[0], videos)            # 2
    extra["viral"] = niche_viral(yt0, own_id, profile)                # 3

    all_cs, tri_all, replied = [], {}, 0                              # 4
    for cr in creds_list:
        y = _yt(cr)
        cid = y.channels().list(mine=True, part="id").execute()["items"][0]["id"]
        cs = comments(y, cid, channel, profile)
        tri = triage_comments(channel, profile, cs)
        replied += auto_reply(y, tri)
        all_cs += cs
        for k, v in tri.items():
            if isinstance(v, list):
                tri_all.setdefault(k, []).extend(v)
            else:
                tri_all.setdefault(k, v)
    extra["viewer_requests"] = tri_all.get("viewer_requests", [])
    if all_cs:
        with open(os.path.join(folder, "comments_report.md"), "w", encoding="utf-8") as f:
            f.write(comments_md(channel, all_cs, tri_all, replied))

    learn, plan = plan_and_merge(channel, profile, base, extra)       # 5
    insights = {**base, **learn, "rhythm": extra["rhythm"], "title_audit": extra["title_audit"],
                "retention": {k: v for k, v in extra["retention"].items() if k != "videos"},
                "niche_outliers": extra["viral"].get("outliers", [])[:8],
                "comments_this_week": len(all_cs)}
    with open(CP.insights_path(channel), "w", encoding="utf-8") as f:
        json.dump(insights, f, ensure_ascii=False, indent=2)
    if plan.get("days"):
        with open(os.path.join(folder, "content_plan.json"), "w", encoding="utf-8") as f:
            json.dump(plan, f, ensure_ascii=False, indent=2)
    print(f"[growth] {channel}: median {base.get('median_views')}, retention {bool(extra['retention'])}, "
          f"niche outliers {len(extra['viral'].get('outliers', []))}, comments {len(all_cs)}, plan {len(plan.get('days', []))}")
    if learn.get("one_fix"):
        print(f"[growth] ONE FIX: {learn['one_fix']}")


def todays_plan(channel):
    """Today's planned item (or the next unused one) for script writers. None if no plan."""
    path = os.path.join(os.path.dirname(CP.insights_path(channel)), "content_plan.json")
    try:
        days = json.load(open(path, encoding="utf-8")).get("days", [])
    except Exception:
        return None
    today = dt.date.today().isoformat()
    for d in days:
        if d.get("date") == today:
            return d
    return None


if __name__ == "__main__":
    run(sys.argv[1])
