#!/usr/bin/env python3
import sys
if sys.platform == 'win32':
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8')

"""
Script checker — LLM ki jagah code se check (0 tokens).
Pass -> script.ok  |  Fail -> script_issues.json (line-wise), writer sirf wahi lines theek karega.

  validate_script.py episodes/indian-horror-tapes/20261031-01
"""
import json
import re
import sys
from pathlib import Path

PAUSE_RE = re.compile(r"^\[pause\s+\d+\]$", re.I)
DEVA = re.compile(r"[ऀ-ॿ]")
LATIN = re.compile(r"[A-Za-z]")
MARKUP = re.compile(r"[*#_`>\[\]{}<]|^\s*[-•]\s|^\s*\(.*\)\s*$")


def main(d: Path):
    brief = json.loads((d / "brief.json").read_text(encoding="utf-8"))
    r = brief["rules"]
    script = d / "script.txt"
    lines = [l.strip() for l in script.read_text(encoding="utf-8").splitlines()]
    text_lines = [(i + 1, l) for i, l in enumerate(lines) if l and not PAUSE_RE.match(l)]

    issues = []

    def add(line, msg):
        issues.append({"line": line, "problem": msg})

    if not text_lines:
        add(0, "Script khaali hai")
    words = sum(len(l.split()) for _, l in text_lines)
    if words < r["min_words"]:
        add(0, f"Bahut chhoti: {words} words, kam se kam {r['min_words']} chahiye")
    if words > r["max_words"]:
        add(0, f"Bahut lambi: {words} words, max {r['max_words']}")

    if text_lines:
        n, hook = text_lines[0]
        if len(hook.split()) > r["hook_max_words"]:
            add(n, f"Hook {len(hook.split())} words ka hai, max {r['hook_max_words']}")
        if r.get("end_with_question"):
            n, last = text_lines[-1]
            if not last.rstrip().endswith("?"):
                add(n, "Aakhri line sawaal (?) honi chahiye — comment ke liye")

    banned = [b.lower() for b in r.get("banned", [])]
    for n, l in text_lines:
        if len(l) > r["max_line_chars"]:
            add(n, f"Line {len(l)} chars ki hai, max {r['max_line_chars']} — todo")
        latin, deva = len(LATIN.findall(l)), len(DEVA.findall(l))
        if latin:
            add(n, "Roman/English letters hain — sab Devanagari mein likho (English shabd bhi: हाईवे, फ़ोन)")
        elif deva == 0:
            add(n, "Line mein Devanagari text nahi hai")
        if re.search(r"\d", l):
            add(n, "Ank (digits) hain — shabdon mein likho (दो बजे, उन्नीस सौ नब्बे)")
        if MARKUP.search(l):
            add(n, "Markdown / bracket / stage-direction hata do — sirf bolne wala text")
        low = l.lower()
        for b in banned:
            if b and b in low:
                add(n, f"Banned phrase: '{b}'")

    ok_p, iss_p = d / "script.ok", d / "script_issues.json"
    if issues:
        prev = json.loads(iss_p.read_text(encoding="utf-8")).get("attempt", 0) if iss_p.exists() else 0
        iss_p.write_text(json.dumps({"attempt": prev + 1, "words": words, "issues": issues},
                                    ensure_ascii=False, indent=2), encoding="utf-8")
        ok_p.unlink(missing_ok=True)
        print(json.dumps({"ok": False, "issues": len(issues), "file": str(iss_p)}, ensure_ascii=False))
        return 0  # fail bhi "handled" hai — ct_state agla step (fix) dega
    iss_p.unlink(missing_ok=True)
    ok_p.write_text(f"words={words}\n")
    print(json.dumps({"ok": True, "words": words}))
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("usage: validate_script.py <episode_dir>")
    sys.exit(main(Path(sys.argv[1])))
