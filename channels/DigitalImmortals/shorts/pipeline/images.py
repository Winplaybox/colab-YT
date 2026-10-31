"""Scene images: AI generation in the locked flat style, with a safe fallback."""
import base64
import hashlib
import io
import os
import random
import re
import time
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

from . import config


def _gemini(prompt: str) -> bytes:
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    try:
        cfg = types.GenerateContentConfig(
            response_modalities=["IMAGE"], image_config=types.ImageConfig(aspect_ratio="9:16"))
    except Exception:
        cfg = types.GenerateContentConfig(response_modalities=["IMAGE"])
    resp = client.models.generate_content(model=config.GEMINI_IMAGE_MODEL, contents=prompt, config=cfg)
    for part in resp.candidates[0].content.parts:
        if getattr(part, "inline_data", None) and part.inline_data.data:
            d = part.inline_data.data
            return d if isinstance(d, bytes) else base64.b64decode(d)
    raise RuntimeError("Gemini returned no image")


def _openai(prompt: str) -> bytes:
    from openai import OpenAI

    r = OpenAI().images.generate(model=config.OPENAI_IMAGE_MODEL, prompt=prompt, size="1024x1536")
    return base64.b64decode(r.data[0].b64_json)


def placeholder(prompt: str, out: Path):
    """Flat gradient scene so a run never fails; obvious enough that you'd reject it in review."""
    rnd = random.Random(hashlib.md5(prompt.encode()).hexdigest())
    pal = [(242, 140, 40), (40, 44, 92), (201, 161, 74), (128, 32, 48), (30, 120, 120)]
    a, b = rnd.sample(pal, 2)
    img = Image.new("RGB", (config.W, config.H))
    d = ImageDraw.Draw(img)
    for y in range(config.H):
        k = y / config.H
        d.line([(0, y), (config.W, y)], fill=tuple(int(a[i] * (1 - k) + b[i] * k) for i in range(3)))
    for _ in range(6):
        c = rnd.choice(pal)
        x, y, r = rnd.randint(0, config.W), rnd.randint(200, 1300), rnd.randint(80, 320)
        d.ellipse([x - r, y - r, x + r, y + r], fill=c)
    d.polygon([(0, 1500), (380, 1150), (760, 1450), (1080, 1200), (1080, 1920), (0, 1920)], fill=(25, 22, 48))
    img.filter(ImageFilter.GaussianBlur(2)).save(out, quality=92)


# ---------------- real archive art first (Wikimedia Commons, The Met) ----------------
UA = {"User-Agent": "DigitalImmortalsShorts/1.0 (YouTube education channel; contact via channel)"}
OK_LICENSES = ("public domain", "pd", "cc0", "cc by", "cc-by")


def _commons(query):
    import requests

    r = requests.get("https://commons.wikimedia.org/w/api.php", headers=UA, timeout=20, params={
        "action": "query", "format": "json", "generator": "search", "gsrnamespace": 6,
        "gsrsearch": f"filetype:bitmap {query}", "gsrlimit": 10,
        "prop": "imageinfo", "iiprop": "url|size|extmetadata", "iiurlwidth": 1600}).json()
    pages = sorted((r.get("query") or {}).get("pages", {}).values(), key=lambda p: p.get("index", 99))
    for p in pages:
        info = (p.get("imageinfo") or [{}])[0]
        meta = info.get("extmetadata", {})
        lic = (meta.get("LicenseShortName", {}).get("value") or "").lower()
        if info.get("height", 0) < 700 or not any(k in lic for k in OK_LICENSES) or "nonfree" in lic:
            continue
        artist = re.sub(r"<[^>]+>", "", meta.get("Artist", {}).get("value") or "Unknown").strip()[:80]
        url = info.get("thumburl") or info.get("url")
        img = requests.get(url, headers=UA, timeout=30).content
        title = p.get("title", "").replace("File:", "")
        return img, f"{title} — {artist}, {lic.upper()}, via Wikimedia Commons"
    return None, None


def _met(query):
    import requests

    ids = requests.get("https://collectionapi.metmuseum.org/public/collection/v1/search", timeout=20,
                       params={"hasImages": "true", "q": query}).json().get("objectIDs") or []
    for oid in ids[:8]:
        o = requests.get(f"https://collectionapi.metmuseum.org/public/collection/v1/objects/{oid}", timeout=20).json()
        if o.get("isPublicDomain") and o.get("primaryImage"):
            img = requests.get(o["primaryImage"], timeout=30).content
            return img, f"{o.get('title', 'Artwork')} — The Metropolitan Museum of Art (Public Domain)"
    return None, None


def _fit_vertical(data, out):
    """Paintings are often landscape: contain the art over a blurred, darkened copy (no ugly crop)."""
    src = Image.open(io.BytesIO(data)).convert("RGB")
    bg = src.copy()
    s = max(config.W / bg.width, config.H / bg.height)
    bg = bg.resize((int(bg.width * s) + 1, int(bg.height * s) + 1)).crop((0, 0, config.W, config.H))
    bg = bg.filter(ImageFilter.GaussianBlur(28)).point(lambda v: int(v * 0.55))
    k = min(config.W / src.width, (config.H * 0.62) / src.height)
    fg = src.resize((max(1, int(src.width * k)), max(1, int(src.height * k))), Image.LANCZOS)
    bg.paste(fg, ((config.W - fg.width) // 2, int(config.H * 0.12)))
    bg.save(out, quality=94)


def archive_image(query, out):
    """Returns credit string if a licensed real artwork/photo was saved, else None."""
    if not query or config.IMAGE_PROVIDER == "placeholder" or os.getenv("ARCHIVE_FIRST", "true") != "true":
        return None
    for fn in (_commons, _met):
        try:
            data, credit = fn(query)
            if data and len(data) > 20000:
                _fit_vertical(data, out)
                return credit
        except Exception as e:
            print(f"[images] archive {fn.__name__} notice: {e}")
    return None


def make_scene_images(scenes: list, work: Path):
    """Archive (museum/Wikimedia) first, then AI (Gemini/OpenAI), then placeholder.
    Returns (paths, credits)."""
    paths, credits = [], []
    for i, sc in enumerate(scenes):
        out = work / f"scene_{i}.jpg"
        credit = archive_image(sc.get("archive_query", ""), out)
        if credit:
            print(f"[images] scene {i}: archive -> {credit[:70]}")
            credits.append(credit)
            paths.append(out)
            continue
        prompt = f"{config.IMAGE_STYLE}\n\nScene: {sc['image_prompt']}"
        data = None
        if config.IMAGE_PROVIDER != "placeholder":
            for attempt in range(3):
                try:
                    data = _gemini(prompt) if config.IMAGE_PROVIDER == "gemini" else _openai(prompt)
                    break
                except Exception as e:
                    print(f"[images] scene {i} attempt {attempt + 1} failed: {e}")
                    time.sleep(4 * (attempt + 1))
        if data:
            Image.open(io.BytesIO(data)).convert("RGB").save(out, quality=94)
        else:
            print(f"[images] scene {i}: using placeholder")
            placeholder(sc["image_prompt"], out)
        paths.append(out)
    return paths, credits
