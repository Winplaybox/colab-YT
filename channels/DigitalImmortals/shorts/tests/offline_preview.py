"""Renders a full video with NO network: silent narration + placeholder art.
Checks timing, captions, watermark, Amar and music ducking.
python -m tests.offline_preview"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from pipeline import config, images, main, tts  # noqa: E402

WPS = 2.7  # spoken Hindi words per second


async def fake_synth(text, out_mp3):
    dur = max(len(text.split()) / WPS, 1.0)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i",
                    f"sine=frequency=180:sample_rate=44100:duration={dur:.2f}", "-af", "volume=0.05",
                    str(out_mp3)], check=True)
    return tts.even_words(text, dur)


tts._synth = fake_synth
config.IMAGE_PROVIDER = "placeholder"
config.UPLOAD = False
sys.argv = ["main", "--script", str(ROOT / "data" / "sample_script.json"), "--no-upload"]
main.HISTORY = ROOT / "out" / "history_preview.json"
import os; os.environ.pop("DIGITALIMMORTALS_TOKEN_JSON", None)
main.main()
