"""Central settings. Change values here (or via env vars) — no other file needs editing."""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent          # channels/DigitalImmortals/shorts
CHANNEL_DIR = ROOT.parent                              # channels/DigitalImmortals (has token.json)


def _load_dotenv(path: Path):
    """Local runs: put keys in shorts/.env (git-ignored). CI uses GitHub Secrets."""
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


_load_dotenv(ROOT / ".env")

# Use ffmpeg from PATH, else the pip "static-ffmpeg" binaries (already in repo requirements)
import shutil as _sh
if not _sh.which("ffmpeg"):
    try:
        import static_ffmpeg
        static_ffmpeg.add_paths()
    except Exception:
        pass

ASSETS = ROOT / "assets"
FONTS_DIR = ASSETS / "fonts"
MASCOT_DIR = ASSETS / "mascot"
MUSIC_DIR = ROOT / "music"          # music/<mood>/*.mp3  (mood: mystery, epic, devotional, calm)
DATA_DIR = ROOT / "data"
OUT_DIR = ROOT / "out"

# --- Video ---
W, H, FPS = 1080, 1920, 30
CHANNEL_HANDLE = "@DigitalImmortals"
OUTRO_SECONDS = 1.6
SCENE_GAP = 0.18                    # pause between scenes (sec)

# --- Script (Claude API) ---
CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-sonnet-5-5")

# --- Voice (Microsoft Edge neural TTS, free) ---
TTS_VOICE = os.getenv("TTS_VOICE", "hi-IN-MadhurNeural")   # male; female: hi-IN-SwaraNeural
TTS_RATE = os.getenv("TTS_RATE", "+8%")

# --- Images ---
IMAGE_PROVIDER = os.getenv("IMAGE_PROVIDER", "gemini")     # gemini | openai | placeholder
GEMINI_IMAGE_MODEL = os.getenv("GEMINI_IMAGE_MODEL", "gemini-2.5-flash-image")
OPENAI_IMAGE_MODEL = os.getenv("OPENAI_IMAGE_MODEL", "gpt-image-1")

# Locked art direction so every video looks like the same channel.
IMAGE_STYLE = (
    "Flat 2D vector illustration, clean modern explainer-video style, Indian mythology. "
    "Bold simple shapes, minimal soft flat shading, no heavy outlines. "
    "Warm palette: saffron, deep indigo, gold, maroon, teal. Soft gradient sky. "
    "Vertical 9:16 cinematic composition, main subject in the upper two-thirds; "
    "keep the lower-left corner simple and uncluttered. "
    "Deities and sages shown respectfully in traditional iconography. "
    "No text, no letters, no captions, no watermark, no logo, no border."
)

# --- Upload ---
UPLOAD = os.getenv("UPLOAD", "true").lower() == "true"
PRIVACY = os.getenv("PRIVACY", "private")   # private = you review & publish from YouTube app
CATEGORY_ID = "27"                           # Education
