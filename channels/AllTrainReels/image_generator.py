"""
AllTrainReels 8K Cinematic Image & Asset Generator
==================================================
- Generates photorealistic 9:16 vertical scene assets for train shorts.
- Anti-poisoning cache: detects .fallback markers so procedural cards are regenerated
  automatically once real connectivity is restored.
- PIL validation: verifies that downloaded image bytes form a valid JPEG/PNG before saving.
- Text-free prompts: prevents AI models from rendering garbled gibberish text/speedometers.
"""

import os
import sys
import json
import time
import requests
from PIL import Image

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

def enhance_train_prompt(base_prompt):
    """
    Enhances base prompt into a clean, photorealistic cinematic railway prompt.
    Avoids brand spam and text tokens that cause AI gibberish.
    """
    aesthetic = (
        "cinematic railway photography, 35mm anamorphic lens, crisp sharp focus, "
        "hyper-detailed mechanical bogie and rail textures, glistening metallic reflections, "
        "volumetric golden hour lighting, dynamic speed blur, 9:16 vertical portrait"
    )
    clean = base_prompt.replace("portrait 9:16", "").replace("8k resolution", "").replace("8k", "").strip()
    return f"{clean}, {aesthetic}"

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

def validate_and_save_image(image_bytes, output_path):
    """Validates image with PIL to guarantee it's not an HTML error page before saving."""
    import io
    try:
        img = Image.open(io.BytesIO(image_bytes))
        img.verify()
        with open(output_path, "wb") as f:
            f.write(image_bytes)
        # Clear fallback marker if previously marked
        marker = output_path + ".fallback"
        if os.path.exists(marker):
            os.remove(marker)
        return True
    except Exception as e:
        print(f"Image validation rejected invalid payload: {e}")
        return False

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
        print(f"✅ [FLUX.1-schnell Free Tier] Generated: {output_path} ({os.path.getsize(output_path)} bytes)")
        return True
    except Exception as e:
        err_msg = str(e)
        if "402" in err_msg or "Payment Required" in err_msg or "depleted" in err_msg:
            return False
        return False

def generate_via_pollinations(prompt, output_path, width=768, height=1360):
    """Generates visual via Pollinations with PIL validation."""
    import urllib.parse
    encoded_prompt = urllib.parse.quote(prompt)
    headers = {"User-Agent": "AllTrainReels/1.0 (Mozilla/5.0; Windows NT 10.0; Win64; x64)"}

    models_to_try = ["flux", "turbo", ""]
    for model in models_to_try:
        model_arg = f"&model={model}" if model else ""
        seed = abs(hash(prompt)) % 999999 # Stable seed for reproducibility
        url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width={width}&height={height}{model_arg}&nologo=true&nofeed=true&seed={seed}"
        try:
            resp = requests.get(url, headers=headers, timeout=35)
            if resp.status_code == 200 and len(resp.content) > 1000:
                if validate_and_save_image(resp.content, output_path):
                    print(f"✅ [Pollinations {model or 'default'}] Generated: {output_path} ({os.path.getsize(output_path)} bytes)")
                    return True
            elif resp.status_code in [402, 429]:
                time.sleep(1)
                continue
        except Exception:
            continue
    return False

def generate_procedural_fallback(title, subtitle, output_path, width=1080, height=1920):
    """
    Generates a dark navy & signal red railway canvas as fallback.
    Marks with .fallback so future runs know to regenerate when online.
    """
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
        # Touch .fallback marker to prevent cache poisoning
        open(output_path + ".fallback", "w").close()
        print(f"⚠️ [Procedural Fallback] Marked for future regeneration: {output_path}")
        return True
    except Exception as e:
        print(f"Procedural canvas error: {e}")
        return False

def generate_shot_asset(shot, title, output_path):
    """Attempts multi-tier generation for a single video shot."""
    if is_real_cached(output_path):
        print(f"⏩ Verified asset cached: {output_path}")
        return True

    prompt = enhance_train_prompt(shot.get("prompt", title))
    hf_token = get_hf_token()

    if hf_token:
        success = generate_via_huggingface_flux(prompt, output_path, hf_token)
        if success:
            return True

    success = generate_via_pollinations(prompt, output_path)
    if success:
        return True

    return generate_procedural_fallback(title, shot.get("subtitle", ""), output_path)

def generate_story_assets(story_json_path):
    """Generates all 5 scene assets for a story JSON file."""
    with open(story_json_path, "r", encoding="utf-8") as f:
        story_data = json.load(f)

    story_id = story_data["story_id"]
    title = story_data["title"]
    shots = story_data.get("shots", [])

    episode_dir = os.path.join(assets_base, story_id)
    os.makedirs(episode_dir, exist_ok=True)

    print(f"\n🚂 Processing Visual Assets for '{title}' ({len(shots)} shots)...")
    for idx, shot in enumerate(shots, 1):
        shot_filename = f"shot_{idx:02d}.jpg"
        shot_path = os.path.join(episode_dir, shot_filename)
        generate_shot_asset(shot, title, shot_path)

    return episode_dir

# ==========================================
# 🎨 BRANDING PROMPTS (TRADEMARK-SAFE)
# ==========================================

CHHUKKU_PROMPTS = {
    "mascot_avatar": (
        "3D stylized animated character of a cute friendly steam locomotive character named Chhukku, "
        "smiling face on the boiler smokebox door with large expressive cartoon headlight eyes, "
        "wearing an official dark blue Indian Railways station master peaked cap, "
        "puffy white cloud of cartoon steam emerging from chimney, holding a bright green railway signal flag, "
        "Signal Red (#E63946) glossy painted body with golden brass boiler bands (#FFC300), Midnight Navy background, "
        "dynamic 3D octane render, ultra-charming stylized character design, clean circle composition, 1:1 square"
    ),
    "mascot_hero_fullbody": (
        "Full body 3D stylized animated steam locomotive character named Chhukku standing on shiny railway tracks, "
        "smiling friendly face, large animated headlight eyes, wearing an Indian Railways station master cap, "
        "one cartoon arm waving a green flag and the other giving a cheerful thumbs up, "
        "bright red and golden yellow glossy metallic finish, sunny railway station background, "
        "cinematic lighting, ultra-detailed 3D render, 9:16 vertical"
    ),
    "channel_banner_2560x1440": (
        "High-octane YouTube channel banner for AllTrainReels: sleek futuristic aerodynamic bullet train on the left side with electric blue and golden speed light trails, "
        "colossal Chenab arch railway bridge spanning across misty mountain valleys in background, "
        "cute 3D steam train mascot on the right side waving a green flag, "
        "Midnight Navy (#0B1F3A) and deep space blue sky, golden sunset glow, high energy cinematic speed, "
        "ultra-clean composition leaving central safe area for text, 16:9 widescreen"
    )
}

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1].endswith(".json"):
        generate_story_assets(sys.argv[1])
    else:
        ep1_file = os.path.join(stories_dir, "story_01_01_scmaglev_603kmh.json")
        if os.path.exists(ep1_file):
            generate_story_assets(ep1_file)
