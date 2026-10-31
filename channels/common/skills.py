"""
The yt-* skills as pipeline functions.

Wraps the vendored tools in channels/common/ytskills/ (hookscore, title, swipe, retention, chapters
rules) and adds a Hindi / Hinglish layer so Devanagari titles and hooks are scored properly.

  score_hook(text)            -> {"verdict", "band", "properties", "formula", "weakest"}   (/yt-script)
  rank_hooks([..])            -> sorted list, best first                                    (/yt-script)
  lint_title(title, thumb, recent_titles) -> {"score", "issues", "good"}                   (/yt-package)
  classify(title)             -> hook-formula name                                          (/yt-viral)
  niche_outliers(rows, min_multiple) -> outliers by multiple over each channel's median    (/yt-viral)
  retention_summary(curve, duration) -> hook leak / cliffs / slide                         (/yt-retention)
  validate_chapters([(sec, title)]) -> (ok, problems)                                      (/yt-chapters)
"""
import json
import os
import re
import statistics
import sys
from difflib import SequenceMatcher

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "ytskills"))
import hookscore as _hs  # noqa: E402
import title as _title   # noqa: E402

DEV = "ऀ-ॿ"
_B1, _B2 = rf"(?<![\w{DEV}])", rf"(?![\w{DEV}])"


def _alt(words):
    return _B1 + "(" + "|".join(sorted(map(re.escape, words), key=len, reverse=True)) + ")" + _B2


HI_YOU = ["आप", "आपका", "आपकी", "आपके", "आपको", "तुम", "तुम्हारा", "तुम्हारी", "तुम्हें", "तू", "तेरा", "तुझे"]
HI_STAKE = ["मत", "कभी", "खतरा", "खतरनाक", "नुकसान", "मौत", "मर", "खत्म", "पहले", "बर्बाद", "गलती", "डर", "शाप", "श्राप", "बंद"]
HI_CURIOSITY = ["क्यों", "कैसे", "क्या", "कौन", "किसने", "कहाँ", "लेकिन", "पर", "रहस्य", "सच", "वजह", "आखिर",
                "फिर", "भी", "अंजाम", "कोई", "नहीं", "आज", "तक", "अनसुलझा", "छिपा", "राज़", "राज"]
HI_FILLER = ["नमस्ते", "दोस्तों", "आज", "हम", "वीडियो", "चैनल", "सब्सक्राइब"]
HI_VAGUE = ["अद्भुत", "अविश्वसनीय", "जबरदस्त", "सबसे", "धमाकेदार", "चौंकाने", "चौंका", "हैरान"]

# Hindi / Hinglish patterns for the same 21 formula names (extends hooks.json, does not replace it)
HI_FORMULAS = {
    "The Statistic": [r"\d+\s*(साल|फीट|किलो|km|kmh|मीटर|लाख|करोड़|%)"],
    "The Mistake": [r"गलती", r"galti", r"मत करो", r"band karo"],
    "Contrarian Flip": [r"सब (कहते|सोचते)", r"गलत है", r"sab (kehte|sochte)"],
    "The Superlative": [r"सबसे", r"sabse", r"duniya ka"],
    "The Question": [r"(क्यों|कैसे|क्या|कौन|किसने|kyun|kaise|kya|kaun)", r"\?\s*$"],
    "The Warning": [r"मत (जाना|करना|देना|रुकना)", r"kabhi mat", r"सावधान"],
    "The Insider": [r"कोई नहीं जानता", r"koi nahi jaanta", r"अनसुनी", r"अनकही", r"छिपा", r"रहस्य", r"rahasya"],
    "The Impossible Claim": [r"फिर भी", r"बिना", r"bina", r"phir bhi", r"आज तक"],
    "The Comparison": [r"\bvs\b", r"बनाम", r"ya phir", r"कौन जीता", r"kaun best"],
    "The Origin": [r"असली (वजह|कहानी)", r"asli (wajah|kahani)", r"कैसे (बना|शुरू)"],
    "The Direct Address": [r"^(अगर आप|agar aap|aap bhi)"],
    "Before and After": [r"पहले .* अब", r"pehle .* ab"],
}


def _words(t):
    return re.findall(rf"[a-z0-9'%$.{DEV}]+", t.lower())


def _patch():
    """Make the vendored hookscore understand Devanagari (module globals are swapped once)."""
    if getattr(_hs, "_hi_patched", False):
        return
    _hs.words = _words
    _hs.YOU = re.compile(_hs.YOU.pattern + "|" + _alt(HI_YOU), re.I)
    _hs.STAKE = re.compile(_hs.STAKE.pattern + "|" + _alt(HI_STAKE), re.I)
    _hs.CURIOSITY = re.compile(_hs.CURIOSITY.pattern + "|" + _alt(HI_CURIOSITY), re.I)
    _hs.FILLER = set(_hs.FILLER) | set(HI_FILLER)
    _hs.VAGUE = set(_hs.VAGUE) | set(HI_VAGUE)
    _title.words = _words
    _title.VAGUE = set(_title.VAGUE) | set(HI_VAGUE)
    _hs._hi_patched = True


_patch()


def classify(text):
    name, hits = _hs.classify(text)
    best = (hits, name)
    for fname, pats in HI_FORMULAS.items():
        n = sum(1 for p in pats if re.search(p, text, re.I))
        if n > best[0]:
            best = (n, fname)
    return best[1] if best[0] else "Unclassified"


def score_hook(text):
    parts, verdict, _, _ = _hs.score(text)
    weakest = min(parts, key=parts.get)
    return {"hook": text.strip(), "verdict": verdict, "band": _hs.band(verdict), "properties": parts,
            "formula": classify(text), "weakest": weakest, "fix": _hs.FIX[weakest]}


def rank_hooks(hooks):
    return sorted((score_hook(h) for h in hooks if h and h.strip()), key=lambda r: -r["verdict"])


def lint_title(title, thumb=None, recent_titles=None):
    r = _title.check(title, thumb)
    issues = list(r["issues"])
    norm = lambda x: re.sub(rf"[^\w{DEV}]+", " ", str(x).lower()).strip()
    for old in recent_titles or []:
        a, b = norm(title), norm(old)
        ratio = SequenceMatcher(None, a, b).ratio()
        contained = min(len(a), len(b)) > 15 and (a in b or b in a)
        if ratio >= 0.8 or contained:
            issues.append(("repeat", f"{int(ratio * 100)}% same as an existing title: '{old[:50]}'"))
            break
    score = max(0, min(100, 100 - 14 * len(issues) + 4 * len(r["good"])))
    return {"title": r["title"], "chars": r["chars"], "score": score, "issues": issues, "good": r["good"]}


def niche_outliers(rows, min_multiple=1.5, min_per_channel=4):
    """rows: [{"channel","title","views",...}] -> (outliers sorted by multiple, thin_channels)."""
    by = {}
    for r in rows:
        by.setdefault(r.get("channel", "?"), []).append(r)
    out, thin = [], []
    for ch, vids in by.items():
        if len(vids) < min_per_channel:
            thin.append(ch)
            continue
        med = statistics.median(float(v.get("views", 0) or 0) for v in vids) or 1
        for v in vids:
            m = float(v.get("views", 0) or 0) / med
            if m >= min_multiple:
                out.append({**v, "median": int(med), "multiple": round(m, 2), "formula": classify(v.get("title", ""))})
    return sorted(out, key=lambda r: -r["multiple"]), thin


def retention_summary(curve, duration_s):
    """curve: [(elapsed_ratio 0..1, audience_watch_ratio 0..1+)] from YouTube Analytics.
    Same three readings as the yt-retention skill: hook leak, cliffs, slide."""
    if len(curve) < 8 or not duration_s:
        return None
    pts = [(x * 100, y * 100) for x, y in curve]
    start = pts[0][1] or 100.0
    cutoff = min(30.0 / duration_s * 100, 25.0) if duration_s > 30 else 25.0   # Shorts: first quarter
    hook_end = min((y for x, y in pts if x <= cutoff), default=start)
    drops = []
    for i in range(1, len(pts)):
        d = pts[i - 1][1] - pts[i][1]
        span = (pts[i][0] - pts[i - 1][0]) or 1
        drops.append((d / span, pts[i - 1][0], d))
    cliffs = [{"at_pct": round(x0, 1), "at_seconds": round(x0 / 100 * duration_s, 1), "lost": round(d, 1)}
              for _, x0, d in sorted(drops, reverse=True)[:3] if d > 0.8]
    mid = [r for r, x0, _ in drops if x0 > cutoff]
    leak = start - hook_end
    return {"hook_leak": round(leak, 1), "hook_verdict": "healthy" if leak < 25 else "leaking" if leak < 40 else "severe",
            "cliffs": cliffs, "slide": round(sum(mid) / len(mid), 3) if mid else 0, "end_pct": round(pts[-1][1], 1)}


def validate_chapters(chapters, duration_s=None):
    """chapters: [(start_seconds, title)]. YouTube renders chapters only if: first at 00:00,
    3 or more, each >= 10 s, ascending. Returns (ok, problems)."""
    problems = []
    if len(chapters) < 3:
        problems.append("needs 3+ chapters")
    if not chapters or chapters[0][0] != 0:
        problems.append("first chapter must start at 00:00")
    for i, (t, _) in enumerate(chapters):
        end = chapters[i + 1][0] if i + 1 < len(chapters) else duration_s
        if i + 1 < len(chapters) and chapters[i + 1][0] <= t:
            problems.append(f"chapter {i + 1} not ascending")
        if end is not None and end - t < 10:
            problems.append(f"chapter {i + 1} shorter than 10s")
    return (not problems), problems


def fix_chapters(chapters, duration_s=None):
    """Drops/merges entries until validate_chapters passes (keeps the earliest of a too-short pair)."""
    ch = sorted(chapters)
    if ch and ch[0][0] != 0:
        ch[0] = (0, ch[0][1])
    out = []
    for t, title in ch:
        if out and t - out[-1][0] < 10:
            continue
        out.append((t, title))
    if duration_s and out and duration_s - out[-1][0] < 10:
        out.pop()
    return out


def mmss(t):
    t = int(t)
    return f"{t // 3600}:{t % 3600 // 60:02d}:{t % 60:02d}" if t >= 3600 else f"{t // 60:02d}:{t % 60:02d}"
