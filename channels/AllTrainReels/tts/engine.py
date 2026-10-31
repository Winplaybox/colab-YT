"""
AllTrainReels TTS Engine — Edge-TTS
=====================================
Uses Microsoft Edge-TTS for all voiceover synthesis:
- Free, unmetered, no per-video/API bill, no local model weight downloads.
- Neural quality Hindi/Hinglish voice: hi-IN-MadhurNeural
- Chhukku personality: Rate +8%, Pitch +2Hz — cheerful, fast-paced, energetic.
- Offline fallback: pyttsx3/SAPI5 (Windows) if internet is unavailable.

Edge-TTS commercial note:
  Microsoft Edge-TTS is powered by Azure Cognitive Services. The free tier
  (via the edge-tts library) is technically unlimited but intended for
  personal/non-commercial use. For a fully commercial/monetized channel at
  scale, consider Azure TTS pay-per-use (~$1 per 1M characters) which gives
  the same voices with explicit commercial rights.

Add channel personality via sound effects in video_producer.py (whistle,
chhuk-chhuk, station bell) — not inside TTS.
"""
import os
import sys
import asyncio
import subprocess

try:
    from .normalizer import normalize_hinglish_script
except ImportError:
    from normalizer import normalize_hinglish_script

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

# ── Chhukku Voice Personality ─────────────────────────────────────────────────
# hi-IN-MadhurNeural  : Male, warm, energetic Hindi voice
# hi-IN-SwaraNeural   : Female, friendly Hindi voice (alternative)
CHHUKKU_VOICE  = "hi-IN-MadhurNeural"
CHHUKKU_RATE   = "+8%"   # Slightly fast-paced — keeps 90-120s videos punchy
CHHUKKU_PITCH  = "+2Hz"  # Just a touch brighter, not cartoonish


# ── Utility ───────────────────────────────────────────────────────────────────

def get_audio_duration(audio_path):
    """Returns audio duration in seconds using ffprobe."""
    try:
        import static_ffmpeg
        static_ffmpeg.add_paths()
    except Exception:
        pass
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        audio_path
    ]
    try:
        return float(subprocess.run(cmd, capture_output=True, text=True, check=True).stdout.strip())
    except Exception:
        return 90.0


# ── Primary Engine: Edge-TTS ──────────────────────────────────────────────────

async def _edge_tts_async(text, output_path, voice, rate, pitch):
    import edge_tts
    communicate = edge_tts.Communicate(text, voice=voice, rate=rate, pitch=pitch)
    await communicate.save(output_path)


def synthesize_edge_tts(text, output_path,
                        voice=CHHUKKU_VOICE,
                        rate=CHHUKKU_RATE,
                        pitch=CHHUKKU_PITCH):
    """
    Synthesizes narration using Microsoft Edge-TTS.
    Zero cost, no per-video billing, neural quality.
    """
    try:
        import edge_tts  # noqa — validates install
        asyncio.run(_edge_tts_async(text, output_path, voice, rate, pitch))
        return True
    except ImportError:
        raise RuntimeError("edge-tts not installed. Run: pip install edge-tts")
    except Exception as e:
        print(f"[Edge-TTS] Error: {e}")
        return False


# ── Offline Fallback: pyttsx3 / Windows SAPI5 ────────────────────────────────

def synthesize_pyttsx3_offline(text, output_path):
    """
    Last-resort offline synthesis via Windows SAPI5 (pyttsx3).
    Robotic quality but zero internet dependency.
    """
    try:
        import pyttsx3
        engine = pyttsx3.init()
        # Use Hindi voice if available on this Windows install
        for v in engine.getProperty("voices"):
            if "hindi" in v.name.lower() or "hin" in v.id.lower():
                engine.setProperty("voice", v.id)
                break
        wav_path = output_path.replace(".mp3", ".wav")
        engine.save_to_file(text, wav_path)
        engine.runAndWait()
        if output_path.endswith(".mp3") and os.path.exists(wav_path):
            os.replace(wav_path, output_path)
        return os.path.exists(output_path)
    except ImportError:
        return False
    except Exception as e:
        print(f"[pyttsx3] Error: {e}")
        return False


# ── Master Entry Point ────────────────────────────────────────────────────────

def synthesize_narration(raw_text, output_audio_path,
                         voice=None, rate=None, pitch=None):
    """
    Synthesizes Hindi/Hinglish narration for AllTrainReels.

    1. Normalizes the text (units: km/h, HP, Rs, etc.)
    2. Tries Edge-TTS (primary — free, neural, Chhukku personality)
    3. Falls back to pyttsx3/SAPI5 offline if internet unavailable

    Returns dict: {path, duration, engine, normalized_text}
    """
    normalized = normalize_hinglish_script(raw_text)

    # Apply Chhukku personality defaults
    v = voice or CHHUKKU_VOICE
    r = rate  or CHHUKKU_RATE
    p = pitch or CHHUKKU_PITCH

    print(f"\U0001f399\ufe0f  [Edge-TTS] Voice: {v} | Rate: {r} | Pitch: {p}")

    success = synthesize_edge_tts(normalized, output_audio_path, voice=v, rate=r, pitch=p)

    if not success:
        print("[TTS] Edge-TTS failed, trying pyttsx3 offline fallback...")
        success = synthesize_pyttsx3_offline(normalized, output_audio_path)
        if not success:
            raise RuntimeError(
                "TTS synthesis failed. Check internet connection (Edge-TTS) "
                "or install pyttsx3 (pip install pyttsx3) for offline fallback."
            )
        engine_label = "pyttsx3/SAPI5 (Offline)"
    else:
        engine_label = f"Edge-TTS ({v})"

    duration = get_audio_duration(output_audio_path)
    print(f"[TTS] Done: {engine_label} | {duration:.2f}s")
    return {
        "path": output_audio_path,
        "duration": duration,
        "engine": engine_label,
        "normalized_text": normalized
    }


# ── CLI Test ──────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    out = os.path.join(os.path.dirname(__file__), "..", "output", "test_chhukku_voice.mp3")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    test = (
        "Chhuk-chhuk! Aaj Chhukku leke aaya hai ek zabardast railway fact! "
        "Japan ki SCMaglev train 603 kilometer per hour ki speed se daudi! "
        "Ye train 10 centimeter hawa mein tairti hai! "
        "Kya India ko bhi aisi train chahiye?"
    )
    result = synthesize_narration(test, out)
    print("\nResult:", result)
