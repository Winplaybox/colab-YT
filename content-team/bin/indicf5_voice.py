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


# Monkeypatch torchaudio.load for Windows DLL compatibility
try:
    import torchaudio
    def soundfile_audio_load(path, **kwargs):
        data, sr = sf.read(str(path), dtype="float32")
        t = torch.from_numpy(data)
        return (t.unsqueeze(0) if t.ndim == 1 else t.t()), sr
    torchaudio.load = soundfile_audio_load
except Exception:
    pass


class IndicF5NativeWrapper:
    def __init__(self, device="cuda"):
        from huggingface_hub import hf_hub_download
        from safetensors.torch import load_file
        from f5_tts.infer.utils_infer import load_vocoder, get_tokenizer
        from f5_tts.model import DiT, CFM

        self.device = device
        print(f"Loading Vocos Vocoder on {self.device}...", flush=True)
        self.vocoder = load_vocoder(vocoder_name="vocos", is_local=False, device=self.device)

        vocab_path = hf_hub_download("ai4bharat/IndicF5", filename="checkpoints/vocab.txt")
        vocab_char_map, vocab_size = get_tokenizer(vocab_path, "custom")

        self.model = CFM(
            transformer=DiT(dim=1024, depth=22, heads=16, ff_mult=2, text_dim=512, conv_layers=4,
                            text_num_embeds=vocab_size, mel_dim=100),
            mel_spec_kwargs=dict(n_fft=1024, hop_length=256, win_length=1024, n_mel_channels=100,
                                target_sample_rate=24000, mel_spec_type="vocos"),
            odeint_kwargs=dict(method="euler"),
            vocab_char_map=vocab_char_map,
        ).to(self.device)

        model_path = hf_hub_download("ai4bharat/IndicF5", filename="model.safetensors")
        raw_sd = load_file(model_path, device=self.device)
        clean_sd = {}
        for k, v in raw_sd.items():
            if k in ["initted", "step"]: continue
            clean_k = k
            if clean_k.startswith("ema_model."): clean_k = clean_k[len("ema_model."):]
            if clean_k.startswith("_orig_mod."): clean_k = clean_k[len("_orig_mod."):]
            clean_sd[clean_k] = v
        for bad in ["mel_spec.mel_stft.mel_scale.fb", "mel_spec.mel_stft.spectrogram.window"]:
            clean_sd.pop(bad, None)
        self.model.load_state_dict(clean_sd, strict=False)
        print("✅ IndicF5 weights successfully loaded into GPU memory!", flush=True)

    def __call__(self, text: str, ref_audio_path: str, ref_text: str):
        from f5_tts.infer.utils_infer import infer_process
        audio, sr, _ = infer_process(
            ref_audio_path,
            ref_text,
            text,
            self.model,
            self.vocoder,
            mel_spec_type="vocos",
            speed=1.0,
            nfe_step=16,
            device=self.device
        )
        return audio


def load_model():
    token = os.environ.get("HF_TOKEN")
    try:
        import torch
        if token:
            from huggingface_hub import login
            login(token=token, add_to_git_credential=False)
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Initializing IndicF5 on {device} ({torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU'})...", flush=True)
        return IndicF5NativeWrapper(device=device)
    except Exception as e:
        print(f"ℹ️ [IndicF5 Notice] Native IndicF5 GPU unavailable ({e}). Using Edge-TTS fallback...", flush=True)
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
