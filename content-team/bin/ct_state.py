#!/usr/bin/env python3
import sys
if sys.platform == 'win32':
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8')

"""
Content-team state machine. Agent ko sirf yeh batata hai ki AGLA step kya hai.
Agent kabhi khud plan nahi karta — isse har call ka context chhota rehta hai.

  ct_state.py next --channel indian-horror-tapes
  ct_state.py ideas-add --channel indian-horror-tapes        # data/<ch>/ideas_new.json merge
  ct_state.py status --channel indian-horror-tapes
  ct_state.py abandon --channel indian-horror-tapes          # current episode chhod do

Output (next) hamesha ek JSON:
  kind = code     -> "run" command chalao, phir next
  kind = llm      -> khud likho (sasta model): "context" padho, "write" file banao, "then_run" ho toh chalao
  kind = delegate -> "run" command chalao (alag BEST-model Hermes call), phir next
  kind = blocked  -> ruk jao, "message" user ko bhejo
  kind = done     -> episode publish ho gaya, "message" user ko bhejo
"""
import argparse
import datetime as dt
import json
import os
import re
import shlex
import sys
from pathlib import Path

import yaml

HOME = Path(os.environ.get("CT_HOME", Path(__file__).resolve().parent.parent)).resolve()
BIN = HOME / "bin"


def load_yaml(p: Path):
    return yaml.safe_load(p.read_text(encoding="utf-8"))


CFG = load_yaml(HOME / "config.yaml")
PY = CFG.get("python", "python3")


def emit(d, code=0):
    print(json.dumps(d, ensure_ascii=False, indent=1))
    sys.exit(code)


def chan_cfg(ch):
    p = HOME / "channels" / f"{ch}.yaml"
    if not p.exists():
        emit({"kind": "blocked", "message": f"Channel config nahi mila: {p}"}, 1)
    return load_yaml(p)


def read_json(p: Path, default=None):
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else default


def write_json(p: Path, d):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")


def norm(s: str) -> str:
    return re.sub(r"[^a-z0-9ऀ-ॿ]+", "", str(s).lower())


def rel(p: Path) -> str:
    try:
        return str(p.relative_to(HOME))
    except ValueError:
        return str(p)


def cmd(*parts) -> str:
    return " ".join(shlex.quote(str(x)) for x in parts)


# ---------- ideas ----------

def ideas_file(ch):
    return HOME / "data" / ch / "ideas.json"


def cmd_ideas_add(ch):
    cc = chan_cfg(ch)
    new_p = HOME / "data" / ch / "ideas_new.json"
    if not new_p.exists():
        emit({"kind": "blocked", "message": f"{rel(new_p)} nahi mila"}, 1)
    try:
        new = json.loads(new_p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        emit({"kind": "blocked", "message": f"ideas_new.json valid JSON nahi: {e}"}, 1)
    if isinstance(new, dict):
        new = new.get("ideas", [])
    ideas = read_json(ideas_file(ch), [])
    seen = {norm(i["title"]) for i in ideas}
    added, skipped = 0, 0
    for it in new:
        if not isinstance(it, dict) or not it.get("title") or not it.get("premise"):
            skipped += 1
            continue
        k = norm(it["title"])
        if k in seen:
            skipped += 1
            continue
        seen.add(k)
        ideas.append({
            "id": f"{ch[:3]}-{len(ideas) + 1:04d}",
            "title": it["title"].strip(),
            "premise": it["premise"].strip(),
            "theme": it.get("theme", ""),
            "twist": it.get("twist", ""),
            "used": None,
        })
        added += 1
    write_json(ideas_file(ch), ideas)
    new_p.unlink()
    unused = sum(1 for i in ideas if not i["used"])
    print(json.dumps({"added": added, "skipped": skipped, "unused_now": unused}))
    if added == 0 and unused < cc["ideas"]["refill_below"]:
        sys.exit(1)


# ---------- episodes ----------

def ep_root(ch):
    return HOME / "episodes" / ch


def current_episode(ch):
    root = ep_root(ch)
    if not root.exists():
        return None
    for d in sorted(root.iterdir(), reverse=True):
        if d.is_dir() and not (d / "published.json").exists() and not (d / "ABANDONED").exists():
            return d
    return None


def new_episode(ch, cc):
    ideas = read_json(ideas_file(ch), [])
    unused = [i for i in ideas if not i["used"]]
    if not unused:
        return None
    idea = unused[0]
    today = dt.datetime.now().strftime("%Y%m%d")
    root = ep_root(ch)
    root.mkdir(parents=True, exist_ok=True)
    n = 1 + sum(1 for d in root.iterdir() if d.name.startswith(today))
    d = root / f"{today}-{n:02d}"
    d.mkdir()
    sc = cc["script"]
    write_json(d / "brief.json", {
        "channel": cc.get("display_name", ch),
        "episode": d.name,
        "idea": {k: idea[k] for k in ("title", "premise", "theme", "twist")},
        "rules": {
            "min_words": sc["min_words"],
            "max_words": sc["max_words"],
            "hook_max_words": sc["hook_max_words"],
            "max_line_chars": sc["max_line_chars"],
            "end_with_question": sc.get("end_with_question", False),
            "banned": sc.get("banned", []),
            "style": sc["style"],
        },
    })
    idea["used"] = d.name
    write_json(ideas_file(ch), ideas)
    return d


def fresher(a: Path, b: Path) -> bool:
    """a exists and is newer-or-equal than b"""
    return a.exists() and (not b.exists() or a.stat().st_mtime >= b.stat().st_mtime)


def writer_step(d, mode):
    prompt = (f"Episode folder: {d}. ct-script-writer skill follow karo. MODE={mode}. "
              f"Sirf {d}/script.txt likhna hai, kuch aur nahi.")
    return {
        "kind": "delegate", "step": f"script_{mode}", "model": "BEST",
        "run": CFG["writer_cmd"].format(prompt=prompt.replace('"', "'")),
        "expect": rel(d / "script.txt"),
        "fallback": "Agar run fail ho: khud ct-script-writer skill follow karke script.txt likho.",
    }


def cmd_next(ch):
    cc = chan_cfg(ch)
    ideas = read_json(ideas_file(ch), [])
    unused = sum(1 for i in ideas if not i["used"])
    d = current_episode(ch)

    # 1. Idea bank khatam hone wala hai -> ek batch (sasta model)
    if d is None and unused < cc["ideas"]["refill_below"]:
        recent = [i["title"] for i in ideas[-60:]]
        emit({
            "kind": "llm", "step": "ideas", "model": "CHEAP", "skill": "ct-idea-bank",
            "context": {
                "channel": cc.get("display_name", ch),
                "count": cc["ideas"]["batch_size"],
                "themes": cc["ideas"]["themes"],
                "style": cc["script"]["style"],
                "avoid_titles": recent,
            },
            "write": rel(HOME / "data" / ch / "ideas_new.json"),
            "then_run": cmd(PY, BIN / "ct_state.py", "ideas-add", "--channel", ch),
        })

    # 2. Naya episode (code, 0 tokens)
    if d is None:
        d = new_episode(ch, cc)
        if d is None:
            emit({"kind": "blocked", "message": "Ideas nahi bache aur refill fail hua."}, 1)

    script, ok, issues = d / "script.txt", d / "script.ok", d / "script_issues.json"

    # 3. Script (BEST model, alag stateless call)
    if not script.exists():
        emit(writer_step(d, "write"))

    # 4. Script check (code)
    if not fresher(ok, script):
        if fresher(issues, script):
            att = read_json(issues, {}).get("attempt", 1)
            if att > CFG.get("max_fix_attempts", 2):
                emit({"kind": "blocked", "step": "script_fix",
                      "message": f"{d.name}: script {att - 1} baar fix ke baad bhi fail. "
                                 f"{rel(issues)} dekho, script.txt khud theek karo ya "
                                 f"'ct_state.py abandon' chalao."})
            emit(writer_step(d, "fix"))
        emit({"kind": "code", "step": "validate",
              "run": cmd(PY, BIN / "validate_script.py", d)})

    # 5. Voice (code, GPU)
    voice, segs = d / "voice.mp3", d / "voice_segments.json"
    if not (voice.exists() and segs.exists()):
        vc = cc["voice"]
        if CFG.get("voice_mode") == "external":
            emit({"kind": "blocked", "step": "voice",
                  "message": f"{d.name}: script ready ({rel(script)}). Colab pe indicf5_voice.py "
                             f"--out voice chalao aur voice.mp3 + voice_segments.json "
                             f"{rel(d)}/ mein daalo, phir pipeline dobara chalao."})
        for p in (vc["ref_wav"], vc["ref_txt"]):
            if not (HOME / p).exists():
                emit({"kind": "blocked", "step": "voice", "message": f"Reference file missing: {p}"})
        emit({"kind": "code", "step": "voice",
              "run": cmd(PY, BIN / "indicf5_voice.py", "--script", script,
                         "--ref", HOME / vc["ref_wav"], "--ref-text", HOME / vc["ref_txt"],
                         "--out", d / "voice", "--gap", vc.get("gap_ms", 250),
                         "--cache", HOME / CFG.get("tts_cache", ".tts_cache"))})

    # 6. Subtitles (code)
    if not fresher(d / "subs.srt", segs):
        emit({"kind": "code", "step": "subs",
              "run": cmd(PY, BIN / "make_subs.py", d,
                         "--words", cc.get("subs", {}).get("words_per_cue", 4))})

    # 7. Video (code)
    if not fresher(d / "video.mp4", d / "subs.srt"):
        emit({"kind": "code", "step": "video",
              "run": cmd(PY, BIN / "assemble_video.py", "--channel", ch, "--episode", d)})

    # 8. Metadata (sasta model, khud)
    if not (d / "meta.json").exists():
        mc = cc.get("metadata", {})
        brief = read_json(d / "brief.json")
        emit({
            "kind": "llm", "step": "metadata", "model": "CHEAP", "skill": "ct-metadata",
            "context": {
                "idea": brief["idea"],
                "script_file": rel(script),
                "language": mc.get("language", "Hinglish (Roman script)"),
                "title_max_chars": mc.get("title_max_chars", 70),
            },
            "write": rel(d / "meta.json"),
        })

    # 9. Publish (code)
    emit({"kind": "code", "step": "publish",
          "run": cmd(PY, BIN / "publish_youtube.py", "--channel", ch, "--episode", d)})


def cmd_status(ch):
    ideas = read_json(ideas_file(ch), [])
    root = ep_root(ch)
    eps = sorted(root.iterdir()) if root.exists() else []
    print(json.dumps({
        "ideas_unused": sum(1 for i in ideas if not i["used"]),
        "episodes_total": len(eps),
        "published": sum(1 for d in eps if (d / "published.json").exists()),
        "in_progress": (current_episode(ch).name if current_episode(ch) else None),
    }, ensure_ascii=False, indent=1))


def cmd_abandon(ch):
    d = current_episode(ch)
    if d:
        (d / "ABANDONED").write_text(dt.datetime.now().isoformat())
    print(json.dumps({"abandoned": d.name if d else None}))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("action", choices=["next", "ideas-add", "status", "abandon"])
    ap.add_argument("--channel", required=True)
    a = ap.parse_args()
    {"next": cmd_next, "ideas-add": cmd_ideas_add,
     "status": cmd_status, "abandon": cmd_abandon}[a.action](a.channel)
