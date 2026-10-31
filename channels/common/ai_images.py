"""
Shared AI image generator for all channels.

Why: Hugging Face removed free Inference credits on 15 Oct 2026, so every
FLUX/SDXL call from the channels now fails with 402. This module is tried
FIRST by each channel's image_generator; their old chains stay as fallback.

Providers (tried in order, skipped silently when the key is missing):
  gemini  -> GEMINI_API_KEY   (google-genai, model GEMINI_IMAGE_MODEL)
  openai  -> OPENAI_API_KEY   (model OPENAI_IMAGE_MODEL)
Order is set with AI_IMAGE_PROVIDERS="gemini,openai".
Cost guard: AI_IMAGE_MAX_PER_RUN (default 60) caps paid calls per process.

Usage:
    from channels.common.ai_images import generate
    ok = generate(prompt, "out.jpg", 1080, 1920)
"""
import base64
import io
import math
import os
import time

_CALLS = 0
_DISABLED = set()   # providers that failed hard (bad key / billing) this run


def _env(name, default=""):
    return (os.environ.get(name) or default).strip()


def _aspect(width, height):
    r = width / float(height)
    options = {"9:16": 9 / 16, "3:4": 3 / 4, "1:1": 1.0, "4:3": 4 / 3, "16:9": 16 / 9}
    return min(options, key=lambda k: abs(options[k] - r))


def _save_cover(data, output_path, width, height):
    from PIL import Image

    img = Image.open(io.BytesIO(data)).convert("RGB")
    s = max(width / img.width, height / img.height)
    img = img.resize((math.ceil(img.width * s), math.ceil(img.height * s)), Image.LANCZOS)
    left, top = (img.width - width) // 2, (img.height - height) // 2
    img = img.crop((left, top, left + width, top + height))
    out_dir = os.path.dirname(output_path)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    img.save(output_path, "JPEG", quality=94)


def _gemini(prompt, width, height):
    key = _env("GEMINI_API_KEY") or _env("GOOGLE_API_KEY")
    if not key:
        return None
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=key)
    try:
        cfg = types.GenerateContentConfig(
            response_modalities=["IMAGE"],
            image_config=types.ImageConfig(aspect_ratio=_aspect(width, height)),
        )
    except Exception:
        cfg = types.GenerateContentConfig(response_modalities=["IMAGE"])
    resp = client.models.generate_content(
        model=_env("GEMINI_IMAGE_MODEL", "gemini-2.5-flash-image"), contents=prompt, config=cfg)
    for cand in resp.candidates or []:
        for part in (cand.content.parts if cand.content else []) or []:
            blob = getattr(part, "inline_data", None)
            if blob and blob.data:
                return blob.data if isinstance(blob.data, bytes) else base64.b64decode(blob.data)
    raise RuntimeError("Gemini returned no image (possibly blocked by safety filter)")


def _openai(prompt, width, height):
    if not _env("OPENAI_API_KEY"):
        return None
    from openai import OpenAI

    size = "1024x1536" if height > width else "1536x1024" if width > height else "1024x1024"
    r = OpenAI().images.generate(model=_env("OPENAI_IMAGE_MODEL", "gpt-image-1"), prompt=prompt, size=size)
    return base64.b64decode(r.data[0].b64_json)


_PROVIDERS = {"gemini": _gemini, "openai": _openai}


def available():
    """True if at least one provider key is configured."""
    return bool(_env("GEMINI_API_KEY") or _env("GOOGLE_API_KEY") or _env("OPENAI_API_KEY"))


def generate(prompt, output_path, width=1080, height=1920, retries=2):
    """Returns True and writes a JPEG of exactly width x height on success."""
    global _CALLS
    if not available():
        return False
    limit = int(_env("AI_IMAGE_MAX_PER_RUN", "60") or 60)
    order = [p.strip() for p in _env("AI_IMAGE_PROVIDERS", "gemini,openai").split(",") if p.strip()]
    prompt = (prompt + " No text, no letters, no watermark, no logo.").strip()

    for name in order:
        fn = _PROVIDERS.get(name)
        if not fn or name in _DISABLED:
            continue
        for attempt in range(retries + 1):
            if _CALLS >= limit:
                print(f"[ai_images] per-run cap reached ({limit}); using channel fallback")
                return False
            try:
                _CALLS += 1
                data = fn(prompt, width, height)
                if data is None:          # no key for this provider
                    break
                _save_cover(data, output_path, width, height)
                print(f"✅ [ai_images:{name}] {os.path.basename(output_path)}")
                return True
            except Exception as e:
                msg = str(e)
                print(f"[ai_images:{name}] attempt {attempt + 1} failed: {msg[:160]}")
                hard = any(k in msg for k in ("API key", "PERMISSION_DENIED", "billing", "401", "403", "insufficient_quota"))
                if hard:
                    _DISABLED.add(name)
                    break
                time.sleep(3 * (attempt + 1))
    return False
