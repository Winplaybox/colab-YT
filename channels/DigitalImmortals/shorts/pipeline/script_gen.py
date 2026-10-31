"""Writes one Short's script + metadata with Claude, avoiding topics already used."""
import datetime as dt
import json
import re

from . import config

FORMATS = {
    "mandir_rahasya": (
        "A real temple / sacred site / ancient structure of India with a genuine mystery or "
        "engineering marvel (e.g. Kailasa Ellora, Konark wheel, Lepakshi hanging pillar, "
        "Brihadeeswara, Stambheshwar, Bijli Mahadev, Kamakhya). Real place, concrete detail."
    ),
    "chhupa_hook": (
        "A Puranic / Ramayana / Mahabharata story told so the hook does NOT reveal the famous "
        "name up front. Example that worked: 'एक बच्चा इतना भूखा था कि उसने सूरज निगल लिया' "
        "(Bal Hanuman). Name the deity only in the middle or at the reveal."
    ),
    "anokhi_katha": (
        "A lesser-known story or symbolism from scriptures that most viewers have NOT heard "
        "(not Eklavya / Samudra Manthan / Narasimha level famous). Strong twist at the end."
    ),
}

SYSTEM = """You are the head writer of "Digital Immortals" (@DigitalImmortals), a Hindi YouTube Shorts channel on Sanatan Dharma: temple mysteries and Puranic stories, narrated by a friendly cartoon young rishi called Amar.

Hard rules:
- Narration in natural spoken Hindi (Devanagari). Simple words, short sentences, like telling a friend.
- Total narration 95–125 words (about 38–48 seconds). 6–8 scenes, 1–2 sentences each.
- Scene 1 is the hook: max 14 words, a shocking image or question that makes people stop scrolling. Never start with "नमस्ते" or the channel name.
- Last scene: the payoff + one question for comments (e.g. "आप क्या मानते हैं? कमेंट में बताइए।").
- Accuracy: never invent numbers, dates, measurements or scripture references. For legends say "मान्यता है" / "कथा के अनुसार". Respectful tone toward all deities and traditions. No gore.
- Title: Hindi, max 60 characters, curiosity gap, concrete. Do NOT use the patterns "का सच", "असली सच", "सच चौंका देगा", "रहस्य?" at the end. At most one emoji.
- image_prompt (English) describes ONLY what is visible in that scene: setting, characters, action, lighting. No text in image. Do not include the narrator Amar.
- archive_query (English, 2-5 words): search terms for a REAL public-domain painting or photo on Wikimedia Commons / The Met that shows this scene (e.g. "Raja Ravi Varma Markandeya", "Konark Sun Temple wheel", "Kailasa temple Ellora"). Use the real place or a classical painter's name. Empty string if no real artwork/photo would fit.
- Every video must feel different: new topic, new angle. Never repeat a topic from the used list."""

USER_TMPL = """Today is {date}. Write today's Short.

Format for today: {fmt_name} — {fmt_desc}
(If a major Hindu festival is certainly within the next 5 days, you may instead make a festival-related story or darshan — only if you are sure of the date.)

Topics already used (do not repeat): {used}

What this channel's audience responds to (weekly analytics of real views; follow it, empty = no data yet):
{insights}

Return ONLY JSON:
{{
  "topic": "short english slug",
  "format": "{fmt_name}",
  "title": "...",
  "hook_text": "2-5 Hindi words for big on-screen text in first 2 seconds",
  "mood": "mystery | epic | devotional | calm",
  "scenes": [{{"narration": "...", "image_prompt": "...", "archive_query": "..."}}],
  "description": "2-3 Hindi lines about the video + the comment question",
  "hashtags": ["#Shorts", "#DigitalImmortals", "... 4-6 more relevant"],
  "tags": ["8-12 search tags, Hindi + English/Hinglish"]
}}"""


def _channel_insights() -> str:
    """channels/DigitalImmortals/insights.json, written weekly by channels/common/channel_insights.py"""
    path = config.CHANNEL_DIR / "insights.json"
    try:
        d = json.loads(path.read_text(encoding="utf-8"))
        keep = {k: d[k] for k in ("winning_patterns", "avoid", "title_examples", "topic_ideas", "one_fix") if d.get(k)}
        if d.get("top_titles"):
            keep["top_titles"] = d["top_titles"][:6]
        return json.dumps(keep, ensure_ascii=False)
    except Exception:
        return "{}"


def _pick_format(today: dt.date) -> str:
    keys = list(FORMATS)
    return keys[today.toordinal() % len(keys)]


def _extract_json(text: str) -> dict:
    m = re.search(r"\{.*\}", text, re.S)
    if not m:
        raise ValueError("No JSON in model output")
    return json.loads(m.group(0))


def validate(s: dict) -> dict:
    scenes = [x for x in s.get("scenes", []) if x.get("narration", "").strip()]
    if not 4 <= len(scenes) <= 10:
        raise ValueError(f"bad scene count {len(scenes)}")
    s["scenes"] = scenes
    s["title"] = s["title"].strip()[:95]
    s["mood"] = s.get("mood", "mystery").split("|")[0].strip().lower()
    if s["mood"] not in {"mystery", "epic", "devotional", "calm"}:
        s["mood"] = "mystery"
    s.setdefault("hook_text", "")
    s.setdefault("hashtags", ["#Shorts", "#DigitalImmortals"])
    s.setdefault("tags", [])
    return s


def generate(history: list, today: dt.date | None = None) -> dict:
    import anthropic

    today = today or dt.date.today()
    fmt = _pick_format(today)
    used = ", ".join(h["topic"] for h in history[-150:]) or "none yet"
    prompt = USER_TMPL.format(date=today.isoformat(), fmt_name=fmt, fmt_desc=FORMATS[fmt], used=used,
                              insights=_channel_insights())

    client = anthropic.Anthropic()
    last_err = None
    for _ in range(3):
        msg = client.messages.create(
            model=config.CLAUDE_MODEL,
            max_tokens=3000,
            system=SYSTEM,
            messages=[{"role": "user", "content": prompt}],
        )
        text = "".join(b.text for b in msg.content if getattr(b, "type", "") == "text")
        try:
            return validate(_extract_json(text))
        except Exception as e:  # retry on malformed output
            last_err = e
    raise RuntimeError(f"Script generation failed: {last_err}")
