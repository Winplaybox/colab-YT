#!/usr/bin/env python3
import sys
if sys.platform == 'win32':
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8')

"""
voice_segments.json -> subs.srt (0 tokens, Whisper ki zarurat nahi — timing TTS se hi pata hai)
Har segment ko chhote cues mein todta hai (Shorts style, 3-5 words), time chars ke hisaab se baant ke.

  make_subs.py <episode_dir> [--words 4]
"""
import argparse
import json
from pathlib import Path


def ts(sec: float) -> str:
    ms = int(round(sec * 1000))
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("episode", type=Path)
    ap.add_argument("--words", type=int, default=4)
    a = ap.parse_args()

    segs = json.loads((a.episode / "voice_segments.json").read_text(encoding="utf-8"))
    cues = []
    for s in segs:
        words = s["text"].split()
        chunks = [" ".join(words[i:i + a.words]) for i in range(0, len(words), a.words)]
        total = sum(len(c) for c in chunks) or 1
        dur, t = s["end"] - s["start"], s["start"]
        for c in chunks:
            d = dur * len(c) / total
            cues.append((t, t + d, c))
            t += d

    out = []
    for i, (st, en, txt) in enumerate(cues, 1):
        out.append(f"{i}\n{ts(st)} --> {ts(max(en - 0.02, st + 0.1))}\n{txt}\n")
    (a.episode / "subs.srt").write_text("\n".join(out), encoding="utf-8")
    print(json.dumps({"cues": len(cues)}))


if __name__ == "__main__":
    main()
