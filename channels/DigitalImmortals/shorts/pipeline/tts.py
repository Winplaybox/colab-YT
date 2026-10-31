"""Hindi narration with word timings (edge-tts), plus the joined narration track."""
import asyncio
import subprocess
import wave
from pathlib import Path

from . import config

SR = 44100


async def _synth(text: str, out_mp3: Path) -> list:
    import edge_tts

    try:
        comm = edge_tts.Communicate(text, config.TTS_VOICE, rate=config.TTS_RATE, boundary="WordBoundary")
    except TypeError:  # older edge-tts
        comm = edge_tts.Communicate(text, config.TTS_VOICE, rate=config.TTS_RATE)
    words = []
    with open(out_mp3, "wb") as f:
        async for chunk in comm.stream():
            if chunk["type"] == "audio":
                f.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                s = chunk["offset"] / 1e7
                words.append([s, s + chunk["duration"] / 1e7, chunk["text"]])
    return words


def _to_wav(src: Path, dst: Path):
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(src), "-ac", "1", "-ar", str(SR), str(dst)], check=True)


def _read(path: Path) -> bytes:
    with wave.open(str(path)) as w:
        return w.readframes(w.getnframes())


def even_words(text: str, dur: float) -> list:
    """Fallback timing: spread words by character length over the clip."""
    toks = text.split()
    total = sum(len(t) for t in toks) or 1
    t, out = 0.0, []
    for tok in toks:
        d = dur * len(tok) / total
        out.append([t, t + d * 0.92, tok])
        t += d
    return out


def build_narration(scenes: list, work: Path) -> dict:
    """Returns {"wav": path, "scenes": [(start, end)], "words": [[s, e, text]], "duration": float}"""
    pcm = bytearray()
    gap = b"\x00\x00" * int(SR * config.SCENE_GAP)
    spans, words, t = [], [], 0.0
    for i, sc in enumerate(scenes):
        mp3, wav = work / f"vo_{i}.mp3", work / f"vo_{i}.wav"
        w = asyncio.run(_synth(sc["narration"], mp3))
        _to_wav(mp3, wav)
        data = _read(wav)
        dur = len(data) / 2 / SR
        if not w:
            w = even_words(sc["narration"], dur)
        spans.append((t, t + dur))
        words += [[t + a, t + b, txt] for a, b, txt in w]
        pcm += data + gap
        t += dur + config.SCENE_GAP
    pcm += b"\x00\x00" * int(SR * config.OUTRO_SECONDS)
    out = work / "narration.wav"
    with wave.open(str(out), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(bytes(pcm))
    return {"wav": out, "scenes": spans, "words": words, "duration": len(pcm) / 2 / SR}
