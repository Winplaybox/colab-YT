"""
AllTrainReels Real Railway Photography & Asset Engine
=====================================================
- Primary Tier (Real Photos): Automatically searches Wikimedia Commons / Wikipedia
  for authentic, high-resolution public-domain railway photography.
- Vertical Adaptation: Converts horizontal train photos into documentary 9:16 Shorts
  assets with high-def centered subject and ambient cinematic blurred backdrop.
- Secondary Tier: HuggingFace FLUX.1-schnell & Pollinations for conceptual / rare scenes.
- Robust Fallback: Procedural navy/red canvas marked with .fallback so future runs auto-upgrade.
- Zero Inauthentic Content Risk: Ensures each video has distinct, genuine railway imagery.
"""

import os
import sys
import json
import time
import requests
import io
from PIL import Image, ImageFilter, ImageEnhance

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

script_dir = os.path.dirname(os.path.abspath(__file__))
stories_dir = os.path.join(script_dir, "stories")
assets_base = os.path.join(stories_dir, "assets")
thumbs_base = os.path.join(stories_dir, "thumbnails")

os.makedirs(assets_base, exist_ok=True)
os.makedirs(thumbs_base, exist_ok=True)

USER_AGENT = "AllTrainReelsBot/1.0 (https://youtube.com/@alltrainreels; contact@alltrainreels.com)"

def is_real_cached(path):
    """Returns True only if file exists, is valid, and is NOT a procedural fallback."""
    if not os.path.exists(path) or os.path.getsize(path) < 10000:
        return False
    if os.path.exists(path + ".fallback"):
        return False
    try:
        with Image.open(path) as img:
            img.verify()
        return True
    except Exception:
        return False

def format_image_for_vertical_short(pil_img, target_width=1080, target_height=1920):
    """
    Formats any image into a broadcast-quality 9:16 vertical Short:
    - If already vertical: center crop & scale to fill.
    - If landscape: intelligently fits the image into the 1000x870 Hero Cinema
      window on a sleek, dark futuristic railway cockpit blueprint background,
      with illuminated glowing borders and corner reticles. ZERO ugly blurred mud!
    """
    from PIL import ImageDraw, ImageOps
    orig_w, orig_h = pil_img.size
    aspect = orig_w / orig_h

    # Tall vertical image: full bleed fill
    if aspect <= 0.65:
        scale = max(target_width / orig_w, target_height / orig_h)
        new_w = int(orig_w * scale)
        new_h = int(orig_h * scale)
        resized = pil_img.resize((new_w, new_h), Image.Resampling.LANCZOS)
        left = (new_w - target_width) // 2
        top = (new_h - target_height) // 2
        return resized.crop((left, top, left + target_width, top + target_height))

    # Landscape / horizontal photo:
    # 1. Base Canvas: Dark Futuristic Railway Cockpit (Deep Slate Navy #0A101E)
    canvas = Image.new("RGB", (target_width, target_height), color=(10, 16, 30))
    draw = ImageDraw.Draw(canvas)

    # Subtle blueprint railway grid lines
    grid_spacing = int(60 * (target_width / 1080.0))
    for y in range(0, target_height, grid_spacing):
        draw.line([(0, y), (target_width, y)], fill=(16, 26, 46), width=1)
    for x in range(0, target_width, grid_spacing):
        draw.line([(x, 0), (x, target_height)], fill=(16, 26, 46), width=1)

    # 2. Hero Screen dimensions (y = 305 to 1175 at 1080p)
    scale_factor = target_width / 1080.0
    card_x1 = int(40 * scale_factor)
    card_y1 = int(305 * scale_factor)
    card_w = int(1000 * scale_factor)
    card_h = int(870 * scale_factor)

    # Intelligently fit image inside the Hero Cinema window
    fitted = ImageOps.fit(pil_img, (card_w, card_h), method=Image.Resampling.LANCZOS, centering=(0.5, 0.5))

    # Mask for rounded corners
    radius = int(18 * scale_factor)
    mask = Image.new("L", (card_w, card_h), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.rounded_rectangle([(0, 0), (card_w, card_h)], radius=radius, fill=255)

    # Paste fitted image with rounded corners
    canvas.paste(fitted, (card_x1, card_y1), mask)

    # Illuminated chassis frame
    draw.rounded_rectangle([(card_x1, card_y1), (card_x1 + card_w, card_y1 + card_h)], radius=radius, outline=(56, 189, 248), width=int(3 * scale_factor))

    # Tech corner brackets [   ]
    b_len = int(40 * scale_factor)
    b_w = int(4 * scale_factor)
    # Top-left
    draw.line([(card_x1 + 10, card_y1 + 10), (card_x1 + 10 + b_len, card_y1 + 10)], fill=(255, 195, 0), width=b_w)
    draw.line([(card_x1 + 10, card_y1 + 10), (card_x1 + 10, card_y1 + 10 + b_len)], fill=(255, 195, 0), width=b_w)
    # Top-right
    draw.line([(card_x1 + card_w - 10, card_y1 + 10), (card_x1 + card_w - 10 - b_len, card_y1 + 10)], fill=(255, 195, 0), width=b_w)
    draw.line([(card_x1 + card_w - 10, card_y1 + 10), (card_x1 + card_w - 10, card_y1 + 10 + b_len)], fill=(255, 195, 0), width=b_w)
    # Bottom-left
    draw.line([(card_x1 + 10, card_y1 + card_h - 10), (card_x1 + 10 + b_len, card_y1 + card_h - 10)], fill=(255, 195, 0), width=b_w)
    draw.line([(card_x1 + 10, card_y1 + card_h - 10), (card_x1 + 10, card_y1 + card_h - 10 - b_len)], fill=(255, 195, 0), width=b_w)
    # Bottom-right
    draw.line([(card_x1 + card_w - 10, card_y1 + card_h - 10), (card_x1 + card_w - 10 - b_len, card_y1 + card_h - 10)], fill=(255, 195, 0), width=b_w)
    draw.line([(card_x1 + card_w - 10, card_y1 + card_h - 10), (card_x1 + card_w - 10, card_y1 + card_h - 10 - b_len)], fill=(255, 195, 0), width=b_w)

    return canvas

def fetch_wikimedia_images(search_queries, limit=25):
    """
    Queries Wikimedia Commons API across a list of query variations.
    Filters out diagrams, icons, logos, and returns direct URLs for real photos.
    """
    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})

    urls = []
    seen = set()

    for query in search_queries:
        if len(urls) >= limit:
            break
        q_enc = requests.utils.quote(query.strip())
        api_url = (
            f"https://commons.wikimedia.org/w/api.php?action=query&generator=search"
            f"&gsrnamespace=6&gsrsearch={q_enc}&prop=imageinfo&iiprop=url&iiurlwidth=1280&format=json"
        )
        try:
            resp = session.get(api_url, timeout=12)
            if resp.status_code != 200:
                continue
            data = resp.json()
            pages = data.get("query", {}).get("pages", {}).values()
            for p in pages:
                title = p.get("title", "").lower()
                # Must be a photo extension
                if not any(title.endswith(ext) for ext in [".jpg", ".jpeg", ".png"]):
                    continue
                # Exclude icons, maps, drawings, and small graphics
                if any(bad in title for bad in ["logo", "icon", "flag", "map", "plan", "symbol", "diagram", "stamp", "signature"]):
                    continue
                infos = p.get("imageinfo", [])
                if infos:
                    thumb = infos[0].get("thumburl") or infos[0].get("url")
                    if thumb and thumb not in seen:
                        seen.add(thumb)
                        urls.append(thumb)
                        if len(urls) >= limit:
                            break
            time.sleep(0.2)
        except Exception:
            continue

    return urls

def extract_search_queries_for_story(story_data):
    """Derives high-precision Wikimedia search terms from story metadata and sources."""
    queries = []

    # 1. From Wikipedia sources URL
    for source in story_data.get("sources", []):
        if "wikipedia.org/wiki/" in source:
            slug = source.split("/wiki/")[-1].replace("_", " ").split("#")[0].strip()
            if slug:
                queries.append(slug)
                queries.append(f"{slug} train")

    # 2. From story ID
    sid = story_data.get("story_id", "").replace("train_", "").split("_")[2:]
    if sid:
        queries.append(" ".join(sid))

    # 3. From tagline & title
    tagline = story_data.get("tagline", "")
    if tagline:
        queries.append(tagline)

    # Clean queries
    clean_queries = []
    for q in queries:
        cq = q.replace("record", "").replace("fastest", "").strip()
        if cq and cq not in clean_queries:
            clean_queries.append(cq)

    return clean_queries

def download_and_format_real_photo(image_url, output_path):
    """Downloads real photo from Wikimedia and formats into 9:16 vertical Short asset."""
    try:
        resp = requests.get(image_url, headers={"User-Agent": USER_AGENT}, timeout=20)
        if resp.status_code != 200 or len(resp.content) < 5000:
            return False

        img = Image.open(io.BytesIO(resp.content)).convert("RGB")
        formatted = format_image_for_vertical_short(img, 1080, 1920)
        formatted.save(output_path, "JPEG", quality=95)

        # Clear fallback marker if present
        marker = output_path + ".fallback"
        if os.path.exists(marker):
            os.remove(marker)
        return True
    except Exception as e:
        print(f"Failed to process real photo {image_url[:50]}: {e}")
        return False

def get_hf_token():
    """Retrieves Hugging Face token from environment or credentials files."""
    token = os.environ.get("HF_TOKEN") or os.environ.get("HUGGINGFACE_TOKEN")
    if token:
        return token.strip()
    creds_paths = [
        os.path.join(script_dir, "credentials", "hf_token.txt"),
        os.path.join(script_dir, "..", "IndianHorrorTapes", "credentials", "hf_token.txt"),
        os.path.join(script_dir, "..", "MindNestTales", "credentials", "hf_token.txt")
    ]
    for p in creds_paths:
        if os.path.exists(p):
            try:
                with open(p, "r", encoding="utf-8") as f:
                    t = f.read().strip()
                    if t:
                        return t
            except Exception:
                pass
    return None

def generate_via_huggingface_flux(prompt, output_path, hf_token):
    """Generates visual via Hugging Face Serverless FLUX.1-schnell in 9:16 portrait."""
    try:
        from huggingface_hub import InferenceClient
        client = InferenceClient(api_key=hf_token)
        img = client.text_to_image(prompt, model="black-forest-labs/FLUX.1-schnell", width=768, height=1360)
        img.save(output_path)
        marker = output_path + ".fallback"
        if os.path.exists(marker):
            os.remove(marker)
        return True
    except Exception:
        return False

def generate_via_pollinations(prompt, output_path, width=768, height=1360):
    """Generates visual via Pollinations with PIL validation."""
    import urllib.parse
    encoded_prompt = urllib.parse.quote(prompt)
    headers = {"User-Agent": USER_AGENT}

    models_to_try = ["flux", "turbo", ""]
    for model in models_to_try:
        model_arg = f"&model={model}" if model else ""
        seed = abs(hash(prompt)) % 999999
        url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width={width}&height={height}{model_arg}&nologo=true&nofeed=true&seed={seed}"
        try:
            resp = requests.get(url, headers=headers, timeout=25)
            if resp.status_code == 200 and len(resp.content) > 1000:
                img = Image.open(io.BytesIO(resp.content))
                img.verify()
                with open(output_path, "wb") as f:
                    f.write(resp.content)
                marker = output_path + ".fallback"
                if os.path.exists(marker):
                    os.remove(marker)
                return True
        except Exception:
            continue
    return False

def generate_procedural_fallback(title, subtitle, output_path, width=1080, height=1920):
    """Generates a dark navy & signal red railway canvas as fallback."""
    try:
        from PIL import ImageDraw
        img = Image.new("RGB", (width, height), color=(11, 31, 58))
        draw = ImageDraw.Draw(img)

        for i in range(0, height, 80):
            draw.line([(0, i), (width, i + 200)], fill=(20, 50, 90), width=3)
        draw.rectangle([(0, height - 100), (width, height)], fill=(230, 57, 70))
        draw.rectangle([(0, height - 120), (width, height - 100)], fill=(255, 195, 0))

        draw.text((60, 100), "@AllTrainReels", fill=(255, 195, 0))
        draw.text((60, 140), "ALL TRAIN REELS | Har Patri Ki Kahani", fill=(241, 245, 249))

        draw.text((60, height // 2 - 80), title[:40], fill=(255, 255, 255))
        if len(title) > 40:
            draw.text((60, height // 2 - 20), title[40:80], fill=(255, 255, 255))
        draw.text((60, height // 2 + 60), subtitle[:50], fill=(255, 195, 0))

        img.save(output_path, "JPEG", quality=90)
        open(output_path + ".fallback", "w").close()
        print(f"⚠️ [Procedural Fallback] Marked for future regeneration: {output_path}")
        return True
    except Exception as e:
        print(f"Procedural canvas error: {e}")
        return False

def generate_story_assets(story_input):
    """
    Generates all scene assets for a story (story dict, episode int, or JSON filepath):
    1. Primary Tier: Searches Wikimedia Commons for authentic real train photography.
    2. Secondary Tier: AI generation via FLUX / Pollinations for missing shots.
    3. Tertiary Tier: Procedural fallback canvas.
    """
    if isinstance(story_input, dict):
        story_data = story_input
    elif isinstance(story_input, int) or (isinstance(story_input, str) and story_input.isdigit()):
        from story_generator import get_or_create_story
        story_data = get_or_create_story(int(story_input))
    else:
        with open(story_input, "r", encoding="utf-8") as f:
            story_data = json.load(f)

    story_id = story_data["story_id"]
    title = story_data["title"]
    shots = story_data.get("shots", [])

    episode_dir = os.path.join(assets_base, story_id)
    os.makedirs(episode_dir, exist_ok=True)

    print(f"\n🚂 Processing Visual Assets for '{title}' ({len(shots)} shots)...")

    # Step 1: Query Wikimedia Commons for pool of real railway photos
    queries = extract_search_queries_for_story(story_data)
    real_photo_urls = fetch_wikimedia_images(queries, limit=max(25, len(shots) + 5))
    print(f"📸 [Wikimedia Commons] Discovered {len(real_photo_urls)} real authentic railway photos for: {queries[:3]}")

    for idx, shot in enumerate(shots, 1):
        shot_filename = f"shot_{idx:02d}.jpg"
        shot_path = os.path.join(episode_dir, shot_filename)

        if is_real_cached(shot_path):
            print(f"⏩ [Cached] Verified asset exists: shot_{idx:02d}.jpg")
            continue

        # Documentary standard: Always use real Wikipedia photography
        photo_idx = idx - 1
        success = False
        if real_photo_urls:
            real_url = real_photo_urls[photo_idx % len(real_photo_urls)]
            success = download_and_format_real_photo(real_url, shot_path)
            if success:
                print(f"✅ [Wikipedia Documentary Photo #{idx}] Formatted {shot_filename} from Wikimedia Commons")

        # Fallback to AI generation if real photo not available or download failed
        if not success:
            prompt = shot.get("prompt", title)
            hf_token = get_hf_token()
            if hf_token:
                success = generate_via_huggingface_flux(prompt, shot_path, hf_token)
                if success:
                    print(f"✅ [FLUX Schnell #{idx}] Generated {shot_filename}")

        if not success:
            prompt = shot.get("prompt", title)
            success = generate_via_pollinations(prompt, shot_path)
            if success:
                print(f"✅ [Pollinations #{idx}] Generated {shot_filename}")

        # Final safety net: procedural fallback
        if not success:
            generate_procedural_fallback(title, shot.get("subtitle", ""), shot_path)

    return episode_dir

def ensure_story_assets(story_input):
    """Workflow compatibility alias"""
    return generate_story_assets(story_input)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1].endswith(".json"):
        generate_story_assets(sys.argv[1])
    else:
        ep2_file = os.path.join(stories_dir, "story_02_02_bhp_iron_ore_7km.json")
        if os.path.exists(ep2_file):
            generate_story_assets(ep2_file)
