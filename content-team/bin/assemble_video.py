#!/usr/bin/env python3
import sys
if sys.platform == 'win32':
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8')

"""
voice.mp3 + subs.srt + background (+ music) -> video.mp4   (ffmpeg, 0 tokens)

  assemble_video.py --channel indian-horror-tapes --episode episodes/indian-horror-tapes/20261031-01

Background: channel ke bg_dir se ek file, episode id ke hash se (har episode alag, rerun pe same).
  video (.mp4/.mov/.webm) -> loop | image (.jpg/.png/.webp) -> slow zoom | kuch nahi -> black
"""
import argparse
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

import yaml

try:
    import static_ffmpeg
    static_ffmpeg.add_paths()
except Exception:
    pass

HOME = Path(os.environ.get("CT_HOME", Path(__file__).resolve().parent.parent)).resolve()
VID = {".mp4", ".mov", ".webm", ".mkv"}
IMG = {".jpg", ".jpeg", ".png", ".webp"}


def duration(p: Path) -> float:
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "csv=p=0", str(p)], capture_output=True, text=True, check=True)
    return float(r.stdout.strip())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--channel", required=True)
    ap.add_argument("--episode", required=True, type=Path)
    a = ap.parse_args()

    d = a.episode.resolve()
    cc = yaml.safe_load((HOME / "channels" / f"{a.channel}.yaml").read_text(encoding="utf-8"))
    v = cc["video"]
    W, H, fps = v["width"], v["height"], v.get("fps", 30)
    voice = d / "voice.mp3"
    dur = duration(voice) + 0.4

    bg_dir = HOME / v.get("bg_dir", "")
    bgs = sorted(p for p in bg_dir.glob("*") if p.suffix.lower() in VID | IMG) if bg_dir.is_dir() else []
    bg = bgs[int(hashlib.md5(d.name.encode()).hexdigest(), 16) % len(bgs)] if bgs else None

    inputs, fit = [], f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},setsar=1"
    if bg is None:
        inputs += ["-f", "lavfi", "-i", f"color=c=black:s={W}x{H}:r={fps}"]
        vchain = f"[0:v]fps={fps}"
    elif bg.suffix.lower() in VID:
        inputs += ["-stream_loop", "-1", "-i", str(bg)]
        vchain = f"[0:v]{fit},fps={fps}"
    else:
        frames = int(dur * fps) + fps
        inputs += ["-loop", "1", "-framerate", str(fps), "-i", str(bg)]
        # 2x scale pe zoompan -> smooth slow push-in
        vchain = (f"[0:v]scale={W * 2}:{H * 2}:force_original_aspect_ratio=increase,crop={W * 2}:{H * 2},"
                  f"zoompan=z='min(zoom+0.0006,1.15)':d={frames}:s={W}x{H}:fps={fps}"
                  f":x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)',setsar=1")
    if v.get("bg_brightness"):
        vchain += f",eq=brightness={v['bg_brightness']}"
    style = v.get("sub_style", "").replace("'", "")
    vchain += f",subtitles=subs.srt:force_style='{style}'[v]"

    inputs += ["-i", str(voice)]
    music = HOME / v["music"] if v.get("music") else None
    if music and music.exists():
        inputs += ["-stream_loop", "-1", "-i", str(music)]
        achain = (f"[2:a]volume={v.get('music_db', -22)}dB[m];"
                  f"[1:a][m]amix=inputs=2:duration=first:dropout_transition=0:normalize=0[a]")
    else:
        achain = "[1:a]anull[a]"

    cmd = ["ffmpeg", "-y", "-loglevel", "error", *inputs,
           "-filter_complex", f"{vchain};{achain}",
           "-map", "[v]", "-map", "[a]", "-t", f"{dur:.2f}",
           "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p",
           "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "video.mp4"]
    # cwd = episode folder, taaki subtitles filter ko path escaping na jhelni pade
    r = subprocess.run(cmd, cwd=d)
    if r.returncode != 0:
        sys.exit(r.returncode)
    print(json.dumps({"video": str(d / "video.mp4"), "seconds": round(dur, 1),
                      "background": bg.name if bg else "black"}, ensure_ascii=False))


if __name__ == "__main__":
    main()
