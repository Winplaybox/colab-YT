#!/usr/bin/env python3
import sys
if sys.platform == 'win32':
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8')

"""
WinPlayBox Batch Autopilot
Autonomous Multi-Episode Producer & YouTube Scheduler.

Features:
- Selects unused story ideas from channel's ideas.json
- Generates 100% Devanagari TTS-optimized script adhering to all channel rules
- Auto-validates and auto-repairs script (0 defects)
- Zero-shot Voice Cloning via AI4Bharat IndicF5 (T4 GPU accelerated)
- Auto subtitle cue generation
- Assembles 1080x1920 portrait video with zoompan & burnt subtitles
- Auto-schedules to YouTube Private queue at channel's scheduled time slots (IST)
- Updates channel state and saves git history

Usage:
  python batch_autopilot.py --channel indian-horror-tapes --count 1
  python batch_autopilot.py --channel indian-horror-tapes --count 5 --gemini-key AIzaSy...
"""

import argparse
import datetime as dt
import json
import os
import re
import subprocess
import sys
import urllib.request
import urllib.error
from pathlib import Path
from zoneinfo import ZoneInfo

import yaml

HOME = Path(os.environ.get("CT_HOME", Path(__file__).resolve().parent.parent)).resolve()
BIN = HOME / "bin"
IST = ZoneInfo("Asia/Kolkata")

# Auto-load .env file if present
for p in [HOME / ".env", HOME.parent / ".env"]:
    if p.exists():
        for line in p.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def log(msg: str):
    now = dt.datetime.now(IST).strftime("%H:%M:%S")
    print(f"[{now} IST] {msg}", flush=True)


def call_gemini(prompt: str, api_key: str) -> str:
    """Zero-dependency Gemini API caller with automatic model fallback."""
    models = ["gemini-2.5-flash-lite", "gemini-2.5-flash"]
    last_err = ""
    for model in models:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 1000,
            }
        }
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                res = json.loads(resp.read().decode("utf-8"))
                return res["candidates"][0]["content"]["parts"][0]["text"].strip()
        except urllib.error.HTTPError as e:
            last_err = e.read().decode("utf-8")
            if e.code in (429, 404):
                continue
            raise RuntimeError(f"Gemini API Error {e.code}: {last_err}")
    raise RuntimeError(f"Gemini API quota exceeded or error: {last_err}")


def generate_script(brief: dict, api_key: str) -> str:
    rules = brief["rules"]
    idea = brief["idea"]

    prompt = f"""You are a professional Hindi YouTube Shorts script writer for a popular horror storytelling channel.
Write an authentic, bone-chilling 1-minute storytelling script in HINDI (DEVANAGARI SCRIPT ONLY).

STORY IDEA:
Title: {idea.get('title')}
Angle: {idea.get('angle')}
Hook Idea: {idea.get('hook')}

MANDATORY RULES (STRICT COMPLIANCE REQUIRED):
1. SCRIPT LANGUAGE & CHARACTERS:
   - 100% PURE DEVANAGARI SCRIPT ONLY. Do NOT include a single Roman/English letter (e.g. no 'A-Z', no 'a-z').
   - English words MUST be written phonetically in Devanagari: हाईवे, फ़ोन, कार, ढाबा, किलोमीटर, टिकट, टॉर्च.
2. NUMBERS:
   - Absolutely NO numeric digits (0-9). All numbers must be written as Hindi words (e.g., 'दो बजे', 'पंद्रह साल', 'तीन किलोमीटर').
3. WORD COUNT:
   - Total words must be between {rules['min_words']} and {rules['max_words']} words (aim for ~130 words).
4. HOOK (LINE 1):
   - The very first line is the hook. It MUST be under {rules['hook_max_words']} words. Direct, shocking mystery/premise. No greetings, no intro.
5. PACING:
   - Each line represents one or two short spoken sentences (under {rules['max_line_chars']} characters per line).
   - You may use '[pause 600]' on its own line up to 2 times for dramatic suspense.
6. ENDING:
   - The last line MUST end with a question mark (?) asking the audience about their opinion or experience to drive comments.
7. NO MARKDOWN:
   - Do NOT include title headers, bullet points, asterisks (*), stage directions, character names, emojis, or quotes.
   - Return ONLY the raw script lines.

Example script structure:
रात के दो बजे हाईवे पर अचानक वो ढाबा दिखाई दिया।
चारों तरफ सन्नाटा था और वहां बिजली का कोई बल्ब नहीं था।
दुकानदार एक बूढ़ा था जिसकी आंखें पलकें नहीं झपका रही थीं।
[pause 600]
...
क्या आपके साथ भी कभी ऐसी रात गुजरी है?
"""
    raw_script = call_gemini(prompt, api_key)
    return clean_script_lines(raw_script, rules)


def clean_script_lines(raw_text: str, rules: dict) -> str:
    cleaned = []
    for line in raw_text.splitlines():
        l = line.strip()
        if not l or l.startswith("```") or l.startswith("#") or l.startswith("*"):
            continue
        # Remove any conversational prefixes
        if any(w in l for w in ["प्रस्तुत है", "स्क्रिप्ट:", "शीर्षक:", "यहाँ है", "कहानी:"]):
            continue
        cleaned.append(l)

    if not cleaned:
        return raw_text

    # 1. Enforce line 1 hook <= hook_max_words (default 12)
    max_hook = rules.get("hook_max_words", 12)
    hook_words = cleaned[0].split()
    if len(hook_words) > max_hook:
        for sep in [",", "।", " - "]:
            if sep in cleaned[0]:
                parts = cleaned[0].split(sep, 1)
                if len(parts[0].split()) <= max_hook and parts[0].strip():
                    cleaned[0] = parts[0].strip()
                    cleaned.insert(1, parts[1].strip())
                    break
        else:
            cleaned.insert(1, " ".join(hook_words[10:]))
            cleaned[0] = " ".join(hook_words[:10])

    # 2. Ensure last line ends with question mark (?) if required
    if rules.get("end_with_question") and cleaned:
        last = cleaned[-1]
        if not last.rstrip().endswith("?"):
            cleaned[-1] = last.rstrip("। .!") + "?"

    return "\n".join(cleaned)


def generate_metadata(brief: dict, script_text: str, api_key: str) -> dict:
    idea = brief["idea"]
    prompt = f"""You are a YouTube Shorts SEO expert. Generate high-CTR metadata for this horror video.
Story: {idea.get('title')} - {idea.get('angle')}
Script snippet: {script_text[:200]}

Format output strictly as JSON with keys:
- "title": (max 70 characters, gripping Hinglish/Hindi, curiosity driven, e.g. "Highway 48 Ka Khooni Dhaba! 😱 #Shorts")
- "description": (2-3 lines teaser in Hinglish + comment question. Do NOT add hashtags)
- "tags": (array of 8-10 high-traffic search terms in Hinglish/English, each <= 30 chars, e.g. ["horror story", "sachi ghatna", "haunted highway", "hindi kahaniya"])

Output JSON only, no markdown:
"""
    res = call_gemini(prompt, api_key)
    # clean code fences if present
    res = re.sub(r"^```json\s*", "", res.strip(), flags=re.MULTILINE)
    res = re.sub(r"```$", "", res.strip(), flags=re.MULTILINE)
    return json.loads(res.strip())


def run_cmd(cmd_list, cwd=None):
    res = subprocess.run(cmd_list, cwd=cwd or HOME, capture_output=True, text=True, encoding="utf-8")
    if res.returncode != 0:
        raise RuntimeError(f"Command failed ({' '.join(cmd_list)}):\n{res.stderr}\n{res.stdout}")
    return res.stdout.strip()


def run_batch_autopilot(channel: str, count: int, gemini_key: str = None, dry_run: bool = False, do_push: bool = False):
    chan_cfg_path = HOME / "channels" / f"{channel}.yaml"
    if not chan_cfg_path.exists():
        sys.exit(f"❌ Channel config not found: {chan_cfg_path}")
    cc = yaml.safe_load(chan_cfg_path.read_text(encoding="utf-8"))

    ref_wav = HOME / "channels" / channel / "ref.wav"
    ref_txt = HOME / "channels" / channel / "ref.txt"
    if not ref_wav.exists() or not ref_txt.exists():
        sys.exit(f"❌ Missing ref.wav or ref.txt in {HOME / 'channels' / channel}")

    token_path = HOME / "credentials" / f"token_{channel}.json"
    if not token_path.exists() and not dry_run:
        sys.exit(f"❌ YouTube token missing: {token_path}")

    ideas_path = HOME / "data" / channel / "ideas.json"
    if not ideas_path.exists():
        sys.exit(f"❌ Ideas file missing: {ideas_path}")
    ideas = json.loads(ideas_path.read_text(encoding="utf-8"))
    if not ideas:
        sys.exit("❌ No unused ideas left in ideas.json!")

    api_key = gemini_key or os.environ.get("GEMINI_API_KEY")
    if not api_key:
        sys.exit("❌ GEMINI_API_KEY is required to generate scripts automatically. Pass --gemini-key or set in env.")

    log(f"🎬 Starting WinPlayBox Autopilot for channel '{channel}'")
    log(f"📋 Requested: {count} episode(s) | Available ideas: {len(ideas)}")

    py_exe = sys.executable

    produced_episodes = []

    for ep_idx in range(1, count + 1):
        if not ideas:
            log("⚠️ No more ideas available!")
            break

        idea = ideas.pop(0)
        today_str = dt.datetime.now(IST).strftime("%Y%m%d")
        
        # Determine episode id
        ep_base = f"{today_str}-{ep_idx:02d}"
        ep_dir = HOME / "episodes" / channel / ep_base
        n = ep_idx
        while ep_dir.exists():
            n += 1
            ep_base = f"{today_str}-{n:02d}"
            ep_dir = HOME / "episodes" / channel / ep_base
        ep_dir.mkdir(parents=True, exist_ok=True)

        log(f"\n=======================================================")
        log(f"⚡ Processing Episode {ep_idx}/{count}: [{ep_base}] '{idea.get('title')}'")
        log(f"=======================================================")

        # 1. Write brief.json
        chan_rules = cc.get("script") or cc.get("rules") or {}
        brief = {
            "channel": channel,
            "episode": ep_base,
            "idea": idea,
            "rules": {
                "min_words": chan_rules.get("min_words", 110),
                "max_words": chan_rules.get("max_words", 150),
                "hook_max_words": chan_rules.get("hook_max_words", 12),
                "max_line_chars": chan_rules.get("max_line_chars", 100),
                "end_with_question": chan_rules.get("end_with_question", True),
                "banned": chan_rules.get("banned", [])
            }
        }
        (ep_dir / "brief.json").write_text(json.dumps(brief, ensure_ascii=False, indent=2), encoding="utf-8")

        # 2. Generate and Validate Script
        log("✍️ Generating Devanagari voiceover script via Gemini...")
        script_text = generate_script(brief, api_key)
        script_file = ep_dir / "script.txt"
        script_file.write_text(script_text, encoding="utf-8")

        # Validation loop (max 3 repair attempts)
        for attempt in range(1, 4):
            val_out = run_cmd([py_exe, str(BIN / "validate_script.py"), str(ep_dir)])
            res = json.loads(val_out)
            if res.get("ok"):
                log(f"✅ Script passed validation ({res.get('words')} words) on attempt {attempt}")
                break
            log(f"⚠️ Validation issues found (attempt {attempt}). Auto-repairing...")
            # Repair prompt
            issues_file = ep_dir / "script_issues.json"
            issues_data = json.loads(issues_file.read_text(encoding="utf-8"))
            repair_prompt = f"""The following Hindi voiceover script has validation errors:
CURRENT SCRIPT:
{script_file.read_text(encoding='utf-8')}

VALIDATION ISSUES:
{json.dumps(issues_data['issues'], ensure_ascii=False, indent=2)}

STRICT RULES:
- 100% Devanagari script. No English letters, no numeric digits.
- Line 1 hook <= {brief['rules']['hook_max_words']} words.
- Total words must be between {brief['rules']['min_words']} and {brief['rules']['max_words']} words (aim for ~125 words). If script is too long, trim/shorten sentences!
- End with question mark (?).
- Under {brief['rules']['max_line_chars']} chars per line.

Fix the issues and output ONLY the corrected script:"""
            repaired = call_gemini(repair_prompt, api_key)
            cleaned_repaired = clean_script_lines(repaired, brief["rules"])
            script_file.write_text(cleaned_repaired, encoding="utf-8")
        else:
            log("❌ Script validation failed after 3 attempts, skipping episode.")
            continue

        # 3. Voice Cloning via IndicF5
        log("🎙️ Synthesizing Voiceover with User's Cloned Voice (IndicF5 GPU)...")
        voice_cmd = [
            py_exe, str(BIN / "indicf5_voice.py"),
            "--script", str(script_file),
            "--ref", str(ref_wav),
            "--ref-text", str(ref_txt),
            "--out", str(ep_dir / "voice")
        ]
        run_cmd(voice_cmd)
        log("✅ Voice audio generated: voice.mp3 & voice_segments.json")

        # 4. Make Subtitles
        log("📝 Generating burned subtitles (subs.srt)...")
        sub_cmd = [py_exe, str(BIN / "make_subs.py"), str(ep_dir)]
        run_cmd(sub_cmd)
        log("✅ Subtitles ready!")

        # 5. Metadata Generation
        log("🏷️ Generating YouTube SEO Title, Description & Tags...")
        metadata = generate_metadata(brief, script_file.read_text(encoding="utf-8"), api_key)
        (ep_dir / "metadata.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
        log(f"✅ Metadata saved: '{metadata.get('title')}'")

        # 6. Assemble Video
        log("🎥 Assembling 1080x1920 60s portrait video with FFmpeg...")
        asm_cmd = [py_exe, str(BIN / "assemble_video.py"), "--channel", channel, "--episode", str(ep_dir)]
        run_cmd(asm_cmd)
        log("✅ Video rendered: video.mp4")

        # 7. Publish / Schedule to YouTube
        if dry_run:
            log("🔎 [DRY-RUN] Skipping YouTube upload.")
            produced_episodes.append({
                "episode": ep_base,
                "title": metadata.get("title"),
                "status": "Dry Run Completed"
            })
        else:
            log("🚀 Uploading & Scheduling on YouTube...")
            pub_cmd = [py_exe, str(BIN / "publish_youtube.py"), "--channel", channel, "--episode", str(ep_dir)]
            pub_out = run_cmd(pub_cmd)
            pub_res = json.loads(pub_out)
            if pub_res.get("ok"):
                log(f"🎉 SUCCESS! Video scheduled on YouTube:")
                log(f"   Video ID: {pub_res.get('video_id')}")
                log(f"   URL: {pub_res.get('url')}")
                log(f"   Scheduled Time: {pub_res.get('publish_at')}")
                produced_episodes.append({
                    "episode": ep_base,
                    "title": metadata.get("title"),
                    "url": pub_res.get("url"),
                    "scheduled": pub_res.get("publish_at"),
                    "video_id": pub_res.get("video_id")
                })
            else:
                log(f"❌ YouTube upload error: {pub_res}")

        # Update ideas.json (persist remaining unused ideas)
        ideas_path.write_text(json.dumps(ideas, ensure_ascii=False, indent=2), encoding="utf-8")

    # Git push if requested
    if do_push:
        log("🔄 Pushing episode updates to GitHub...")
        try:
            run_cmd(["git", "add", "."])
            run_cmd(["git", "commit", "-m", f"Autopilot: Produced {len(produced_episodes)} episodes for {channel}"])
            run_cmd(["git", "push", "origin", "main"])
            log("✅ Changes synced with GitHub!")
        except Exception as e:
            log(f"⚠️ Git push failed: {e}")

    log("\n=======================================================")
    log("🏁 WINPLAYBOX AUTOPILOT RUN FINISHED!")
    log(f"Total Produced: {len(produced_episodes)} episodes")
    for ep in produced_episodes:
        log(f"  • {ep.get('episode')}: {ep.get('title')} -> {ep.get('url', 'N/A')} (Scheduled: {ep.get('scheduled', 'N/A')})")
    log("=======================================================\n")
    return produced_episodes


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="WinPlayBox Batch Autopilot")
    parser.add_argument("--channel", required=True, help="Target channel name (e.g. indian-horror-tapes)")
    parser.add_argument("--count", type=int, default=1, help="Number of episodes to generate (1 to 7)")
    parser.add_argument("--gemini-key", default=None, help="Gemini API Key for script and metadata generation")
    parser.add_argument("--dry-run", action="store_true", help="Generate video without uploading to YouTube")
    parser.add_argument("--push", action="store_true", help="Git commit & push upon completion")
    args = parser.parse_args()

    run_batch_autopilot(
        channel=args.channel,
        count=args.count,
        gemini_key=args.gemini_key,
        dry_run=args.dry_run,
        do_push=args.push
    )
