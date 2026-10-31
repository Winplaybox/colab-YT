"""Frames (Ken Burns scenes + talking Amar) piped to ffmpeg, with ASS captions,
hopping watermark and ducked background music."""
import math
import os
import random
import subprocess
from pathlib import Path

import numpy as np
from PIL import Image

from . import config

W, H, FPS = config.W, config.H, config.FPS

# ---------------- layout (Shorts safe zones) ----------------
MASCOT_W = 360                      # Amar size on screen
MASCOT_X, MASCOT_BOTTOM = 28, 1500  # bottom-left, above the Shorts title overlay
CAPTION_Y = 900                     # caption centre line
HOOK_Y = 330
FADE = 0.35                         # crossfade between scenes
WM_EVERY = 5.0                      # watermark hops every N seconds
WM_SPOTS = [  # (x, y, ASS alignment) — four corners inside safe area
    (50, 120, 7), (1030, 120, 9), (50, 1560, 1), (1030, 1250, 3)]


# ---------------- captions + watermark (ASS) ----------------
def _ts(t: float) -> str:
    t = max(t, 0)
    return f"{int(t // 3600)}:{int(t % 3600 // 60):02d}:{t % 60:05.2f}"


def _chunks(words, max_words=3, max_chars=20):
    cur = []
    for w in words:
        if cur and (len(cur) >= max_words or sum(len(x[2]) + 1 for x in cur) + len(w[2]) > max_chars
                    or w[0] - cur[-1][1] > 0.45):
            yield cur
            cur = []
        cur.append(w)
    if cur:
        yield cur


def _clean(s: str) -> str:
    return s.replace("{", "(").replace("}", ")").replace("\\", "")


def write_ass(path: Path, words, duration: float, hook_text: str, seed: str):
    font = "Baloo 2"
    head = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,{font} ExtraBold,86,&H00FFFFFF,&H00FFFFFF,&H00101010,&H90000000,-1,0,0,0,100,100,0,0,1,7,4,5,60,60,0,1
Style: Hook,{font} ExtraBold,104,&H0028D7FF,&H0028D7FF,&H00101010,&H90000000,-1,0,0,0,100,100,0,0,1,9,5,5,70,70,0,1
Style: Out,{font} ExtraBold,78,&H00FFFFFF,&H00FFFFFF,&H00101010,&H90000000,-1,0,0,0,100,100,0,0,1,7,4,5,60,60,0,1
Style: WM,{font} Bold,42,&H70FFFFFF,&H70FFFFFF,&H90000000,&H00000000,-1,0,0,0,100,100,0,0,1,2,0,7,0,0,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    ev = []
    HL = "{\\c&H0028D7FF&}"   # gold highlight (BGR)
    for ch in _chunks(words):
        end_chunk = ch[-1][1] + 0.25
        for j, w in enumerate(ch):
            s = w[0]
            e = ch[j + 1][0] if j + 1 < len(ch) else end_chunk
            txt = " ".join((HL + _clean(x[2]) + "{\\c&H00FFFFFF&}") if k == j else _clean(x[2])
                           for k, x in enumerate(ch))
            pop = "{\\fscx108\\fscy108\\t(0,90,\\fscx100\\fscy100)}" if j == 0 else ""
            ev.append(f"Dialogue: 1,{_ts(s)},{_ts(e)},Cap,,0,0,0,,{{\\pos({W // 2},{CAPTION_Y})}}{pop}{txt}")
    if hook_text:
        ev.append(f"Dialogue: 2,{_ts(0)},{_ts(2.3)},Hook,,0,0,0,,{{\\pos({W // 2},{HOOK_Y})\\fad(120,200)"
                  f"\\fscx60\\fscy60\\t(0,180,\\fscx100\\fscy100)}}{_clean(hook_text)}")
    ev.append(f"Dialogue: 2,{_ts(duration - config.OUTRO_SECONDS)},{_ts(duration)},Out,,0,0,0,,"
              f"{{\\pos({W // 2},{HOOK_Y + 40})\\fad(200,0)}}Subscribe करें\\N{{\\c&H0028D7FF&}}{config.CHANNEL_HANDLE}")
    # hopping watermark (deterministic per video, never the same corner twice in a row)
    rnd, t, last = random.Random(seed), 0.0, None
    while t < duration:
        x, y, an = rnd.choice([p for p in WM_SPOTS if p != last])
        last = (x, y, an)
        ev.append(f"Dialogue: 0,{_ts(t)},{_ts(min(t + WM_EVERY, duration))},WM,,0,0,0,,"
                  f"{{\\an{an}\\pos({x},{y})\\fad(250,250)}}{config.CHANNEL_HANDLE}")
        t += WM_EVERY
    path.write_text(head + "\n".join(ev) + "\n", encoding="utf-8")


# ---------------- frames ----------------
def _cover(img: Image.Image, w: int, h: int) -> Image.Image:
    s = max(w / img.width, h / img.height)
    img = img.resize((math.ceil(img.width * s), math.ceil(img.height * s)), Image.LANCZOS)
    l, t = (img.width - w) // 2, (img.height - h) // 2
    return img.crop((l, t, l + w, t + h))


def _mascot_states():
    st = {}
    for n in ("idle", "talk", "blink", "blink_talk"):
        im = Image.open(config.MASCOT_DIR / f"amar_{n}.png").convert("RGBA")
        st[n] = im.resize((MASCOT_W, int(im.height * MASCOT_W / im.width)), Image.LANCZOS)
    return st


def _talking(t, words, idx):
    while idx < len(words) and words[idx][1] < t:
        idx += 1
    on = idx < len(words) and words[idx][0] <= t <= words[idx][1]
    return on and int(t * 9) % 2 == 0, idx


def _shade():
    """Soft dark band behind captions + bottom vignette for readability."""
    a = np.zeros((H, W), np.float32)
    y = np.arange(H, dtype=np.float32)[:, None]
    a += 0.38 * np.exp(-((y - CAPTION_Y) / 210) ** 2)
    a += 0.45 * np.clip((y - 1350) / 570, 0, 1)
    return np.clip(a, 0, 0.7)[..., None]


def render_video(images, spans, words, narration_wav: Path, music: Path | None,
                 duration: float, hook_text: str, out: Path, work: Path, seed: str):
    ass = work / "subs.ass"
    write_ass(ass, words, duration, hook_text, seed)
    audio = mix_audio(narration_wav, music, duration, work)

    Z = 1.12  # pre-scale headroom for Ken Burns
    bigs = [_cover(Image.open(p).convert("RGB"), int(W * Z), int(H * Z)) for p in images]
    mascot = _mascot_states()
    shade = _shade()
    starts = [s for s, _ in spans]
    # scene i is shown from starts[i] until starts[i+1]; last runs to the end
    bounds = [(starts[i], starts[i + 1] if i + 1 < len(starts) else duration) for i in range(len(starts))]
    bounds[0] = (0.0, bounds[0][1])

    def bg(i, t):
        s, e = bounds[i]
        p = min(max((t - s) / max(e - s, 0.01), 0), 1)
        p = p * p * (3 - 2 * p)
        zoom = 1.0 + 0.10 * (p if i % 2 == 0 else 1 - p)
        bw, bh = bigs[i].size
        cw, chh = bw / zoom, bh / zoom
        dx = (bw - cw) * (0.5 + (0.25 if i % 3 == 0 else -0.25 if i % 3 == 1 else 0) * (p - 0.5) * 2)
        dy = (bh - chh) * (0.5 - 0.2 * (p - 0.5))
        box = (dx, dy, dx + cw, dy + chh)
        return np.asarray(bigs[i].resize((W, H), Image.BILINEAR, box=box), np.float32)

    tmp = out.with_name(out.stem + ".part.mp4")
    # Windows-safe filter paths: C:/x -> 'C\\:/x' (colon must be escaped inside -vf)
    def _ffp(p):
        return "'" + str(p).replace("\\", "/").replace(":", "\\:").replace("'", "\\'") + "'"
    cmd = ["ffmpeg", "-y", "-loglevel", "error",
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-i", str(audio),
           "-vf", f"ass={_ffp(ass)}:fontsdir={_ffp(config.FONTS_DIR)}",
           "-map", "0:v", "-map", "1:a",
           "-c:v", "libx264", "-preset", os.getenv("X264_PRESET", "veryfast"), "-crf", "19",
           "-pix_fmt", "yuv420p", "-profile:v", "high", "-c:a", "aac", "-b:a", "192k",
           "-shortest", "-movflags", "+faststart", str(tmp)]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    n = int(duration * FPS)
    widx = 0
    for f in range(n):
        t = f / FPS
        i = max(k for k, (s, _) in enumerate(bounds) if s <= t + 1e-6)
        frame = bg(i, t)
        if i + 1 < len(bounds) and bounds[i][1] - t < FADE:
            a = 1 - (bounds[i][1] - t) / FADE
            frame = frame * (1 - a) + bg(i + 1, t) * a
        frame = frame * (1 - shade)
        img = Image.fromarray(frame.clip(0, 255).astype(np.uint8))
        talk, widx = _talking(t, words, widx)
        blink = (t % 3.3) < 0.12
        m = mascot["blink_talk" if blink and talk else "talk" if talk else "blink" if blink else "idle"]
        bob = int(7 * math.sin(2 * math.pi * t / 1.7))
        img.paste(m, (MASCOT_X, MASCOT_BOTTOM - m.height + bob), m)
        proc.stdin.write(img.tobytes())
    proc.stdin.close()
    if proc.wait() != 0:
        raise RuntimeError("ffmpeg render failed")
    tmp.replace(out)
    return out


# ---------------- audio ----------------
def pick_music(mood: str, seed: str) -> Path | None:
    files = sorted((config.MUSIC_DIR / mood).glob("*.mp3")) or sorted(config.MUSIC_DIR.rglob("*.mp3"))
    return random.Random(seed).choice(files) if files else None


def mix_audio(narr: Path, music: Path | None, duration: float, work: Path) -> Path:
    out = work / "final_audio.m4a"
    if music:
        fc = (f"[1:a]aloop=loop=-1:size=2e9,atrim=0:{duration:.2f},volume=0.22,"
              f"afade=t=in:d=1,afade=t=out:st={max(duration - 1.5, 0):.2f}:d=1.5[m];"
              f"[0:a]asplit=2[v][sc];"
              f"[m][sc]sidechaincompress=threshold=0.03:ratio=8:attack=20:release=350[md];"
              f"[v][md]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=11[a]")
        cmd = ["ffmpeg", "-y", "-loglevel", "error", "-i", str(narr), "-i", str(music),
               "-filter_complex", fc, "-map", "[a]"]
    else:
        cmd = ["ffmpeg", "-y", "-loglevel", "error", "-i", str(narr), "-af", "loudnorm=I=-14:TP=-1.5:LRA=11"]
    subprocess.run(cmd + ["-ar", "44100", "-c:a", "aac", "-b:a", "192k", str(out)], check=True)
    return out
