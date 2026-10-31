import sys
if sys.platform == 'win32':
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8')

"""
IndicF5 Voiceover Generator — WinPlayBox content pipeline (zero LLM tokens)

Colab setup (Runtime -> T4 GPU):
  !pip install -q git+https://github.com/AI4Bharat/IndicF5.git soundfile numpy huggingface_hub
  # Model gated hai: huggingface.co/ai4bharat/IndicF5 pe terms accept karo, phir HF_TOKEN set karo
  import os; os.environ["HF_TOKEN"] = "hf_xxx"

Run:
  !python indicf5_voice.py --script script.txt --ref ref.wav --ref-text ref.txt --out ep01

script.txt format (ek line = ek segment):
  Raat ke do baje the... gaon mein sannata tha.
  [pause 800]
  Aur tabhi... darwaze pe dastak hui.

ref.wav  = 5-10 sec clean clip (APNI awaaz ya permission wali), mono
ref.txt  = us clip mein exactly jo bola gaya hai

Output:
  ep01.mp3            -> final voiceover, -14 LUFS (YouTube standard)
  ep01.wav            -> raw master
  ep01_segments.json  -> har line ka start/end time (subtitles / video sync ke liye)
  .tts_cache/         -> pehle se bani lines dobara generate nahi hoti
"""

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

import numpy as np
import soundfile as sf

SR = 24000
MODEL_ID = "ai4bharat/IndicF5"
MAX_CHARS = 220  # lambi line ko sentence pe todo — F5 lambe text pe bigadta hai
PAUSE_RE = re.compile(r"^\[pause\s+(\d+)\]$", re.I)


def parse_script(path: Path):
    """Script ko segments mein todo: ('text', str) ya ('pause', ms)."""
    segs = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line:
            continue
        m = PAUSE_RE.match(line)
        if m:
            segs.append(("pause", int(m.group(1))))
            continue
        if len(line) <= MAX_CHARS:
            segs.append(("text", line))
            continue
        # sentence boundaries: । . ? ! …
        buf = ""
        for part in re.split(r"(?<=[।\.\?\!…])\s+", line):
            if buf and len(buf) + len(part) + 1 > MAX_CHARS:
                segs.append(("text", buf))
                buf = part
            else:
                buf = f"{buf} {part}".strip()
        if buf:
            segs.append(("text", buf))
    return segs


def cache_key(text: str, ref_bytes: bytes, ref_text: str) -> str:
    h = hashlib.sha1()
    for chunk in (MODEL_ID.encode(), ref_bytes, ref_text.encode(), text.encode()):
        h.update(chunk)
    return h.hexdigest()[:16]


def to_float32(audio) -> np.ndarray:
    audio = np.asarray(audio)
    if audio.dtype == np.int16:
        return audio.astype(np.float32) / 32768.0
    return audio.astype(np.float32)


try:
    import static_ffmpeg
    static_ffmpeg.add_paths()
except Exception:
    pass


def load_model():
    token = os.environ.get("HF_TOKEN")
    try:
        import torch
        if token:
            from huggingface_hub import login
            login(token=token, add_to_git_credential=False)
        from transformers import AutoModel
        print(f"Loading {MODEL_ID} ...", flush=True)
        return AutoModel.from_pretrained(MODEL_ID, trust_remote_code=True)
    except Exception as e:
        print(f"ℹ️ [IndicF5 Notice] IndicF5 / PyTorch not available ({e}). Using Edge-TTS neural fallback...", flush=True)
        return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--script", required=True, type=Path)
    ap.add_argument("--ref", required=True, type=Path, help="reference wav")
    ap.add_argument("--ref-text", required=True, type=Path, help="reference transcript .txt")
    ap.add_argument("--out", required=True, help="output basename, e.g. ep01")
    ap.add_argument("--gap", type=int, default=250, help="lines ke beech default gap (ms)")
    ap.add_argument("--lufs", type=float, default=-14.0)
    ap.add_argument("--cache", type=Path, default=Path(".tts_cache"))
    args = ap.parse_args()

    ref_text = args.ref_text.read_text(encoding="utf-8").strip()
    ref_bytes = args.ref.read_bytes()
    args.cache.mkdir(exist_ok=True)

    segs = parse_script(args.script)
    if not segs:
        sys.exit("Script khaali hai.")

    # Model sirf tab load ho jab koi line cache mein na ho
    todo = [t for k, t in segs if k == "text"
            and not (args.cache / f"{cache_key(t, ref_bytes, ref_text)}.wav").exists()]
    model = load_model() if todo else None
    print(f"{len(segs)} segments | {len(todo)} naye generate honge | baaki cache se", flush=True)

    gap = np.zeros(int(SR * args.gap / 1000), dtype=np.float32)
    pieces, timeline, t = [], [], 0.0

    for i, (kind, val) in enumerate(segs, 1):
        if kind == "pause":
            sil = np.zeros(int(SR * val / 1000), dtype=np.float32)
            pieces.append(sil)
            t += len(sil) / SR
            continue

        wav_path = args.cache / f"{cache_key(val, ref_bytes, ref_text)}.wav"
        if wav_path.exists():
            audio, _ = sf.read(wav_path, dtype="float32")
        else:
            print(f"[{i}/{len(segs)}] {val[:60]}", flush=True)
            if model is not None:
                audio = to_float32(model(val, ref_audio_path=str(args.ref), ref_text=ref_text))
            else:
                import asyncio
                import edge_tts
                tmp_mp3 = args.cache / f"temp_{i}.mp3"
                tmp_wav = args.cache / f"temp_{i}.wav"
                async def _synth():
                    comm = edge_tts.Communicate(val, voice="hi-IN-MadhurNeural")
                    await comm.save(str(tmp_mp3))
                asyncio.run(_synth())
                subprocess.run(["ffmpeg", "-y", "-i", str(tmp_mp3), "-ar", str(SR), "-ac", "1", str(tmp_wav)],
                               check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                audio, _ = sf.read(tmp_wav, dtype="float32")
                tmp_mp3.unlink(missing_ok=True)
                tmp_wav.unlink(missing_ok=True)
            sf.write(wav_path, audio, SR)

        timeline.append({"text": val, "start": round(t, 3), "end": round(t + len(audio) / SR, 3)})
        pieces += [audio, gap]
        t += (len(audio) + len(gap)) / SR

    master = np.concatenate(pieces)
    wav_out, mp3_out = f"{args.out}.wav", f"{args.out}.mp3"
    sf.write(wav_out, master, SR)
    Path(f"{args.out}_segments.json").write_text(
        json.dumps(timeline, ensure_ascii=False, indent=2), encoding="utf-8")

    # YouTube loudness normalize + MP3
    subprocess.run([
        "ffmpeg", "-y", "-loglevel", "error", "-i", wav_out,
        "-af", f"loudnorm=I={args.lufs}:TP=-1.5:LRA=11",
        "-ar", "44100", "-b:a", "192k", mp3_out,
    ], check=True)

    print(f"Done -> {mp3_out} ({t:.1f}s), {args.out}_segments.json")


if __name__ == "__main__":
    main()
