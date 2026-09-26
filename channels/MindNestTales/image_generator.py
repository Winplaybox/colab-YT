"""
MindNest Tales Autonomous 3D Pixar Image Generator:
- Automatically generates high-resolution, ultra-detailed 8K 3D Pixar scene assets & thumbnails.
- Supports 100% FREE Tier generation:
  1. Hugging Face Serverless FLUX.1-schnell (via free HF_TOKEN) - Masterpiece 8K Pixar quality
  2. Pollinations Flux Engine (100% Free, zero-config, no API key required)
  3. Pre-generated local assets cache
- Automatically integrates into GitHub Actions workflow before video rendering.
"""

import os
import sys
import json
import time
import requests

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

def enhance_pixar_prompt(base_prompt):
    """Enhances base prompt into an ultra-detailed 8K Pixar/Disney 3D animation prompt."""
    style_suffix = (
        "3D Pixar Disney animated feature film aesthetic, hyper-detailed expressive character, "
        "intricate fur and skin texture, warm cinematic volumetric lighting, raytracing, "
        "subsurface scattering, 8k resolution, Unreal Engine 5 render, cinematic depth of field, "
        "masterpiece quality, vertical portrait 9:16"
    )
    # Avoid repeating tokens
    clean = base_prompt.replace("portrait 9:16", "").replace("3D Pixar-style", "").strip()
    return f"3D Pixar-style animated {clean}, {style_suffix}"

def get_hf_token():
    """Retrieves Hugging Face token from environment or local credentials file."""
    token = os.environ.get("HF_TOKEN") or os.environ.get("HUGGINGFACE_TOKEN")
    if token:
        return token.strip()
    local_creds = os.path.join(script_dir, "credentials", "hf_token.txt")
    if os.path.exists(local_creds):
        try:
            with open(local_creds, "r", encoding="utf-8") as f:
                t = f.read().strip()
                if t:
                    return t
        except Exception:
            pass
    return None

def generate_via_huggingface_flux(prompt, output_path, hf_token):
    """Generates 8K Pixar image via Hugging Face Serverless Inference (FLUX.1-schnell). 100% Free."""
    try:
        from huggingface_hub import InferenceClient
        client = InferenceClient(api_key=hf_token)
        img = client.text_to_image(prompt, model="black-forest-labs/FLUX.1-schnell")
        img.save(output_path)
        print(f"✅ [FLUX.1-schnell Free Tier] Generated: {output_path} ({os.path.getsize(output_path)} bytes)")
        return True
    except Exception as e:
        print(f"Hugging Face FLUX error: {e}")
        try:
            from huggingface_hub import InferenceClient
            client = InferenceClient(api_key=hf_token)
            img = client.text_to_image(prompt, model="stabilityai/stable-diffusion-xl-base-1.0")
            img.save(output_path)
            print(f"✅ [SDXL Free Tier] Generated: {output_path} ({os.path.getsize(output_path)} bytes)")
            return True
        except Exception as e2:
            print(f"Hugging Face SDXL fallback error: {e2}")
    return False

def generate_via_pollinations_flux(prompt, output_path, seed=None):
    """Generates 3D Pixar image via Pollinations Flux Engine. 100% Free, zero setup required."""
    if seed is None:
        seed = int(time.time() * 1000) % 999999
    encoded = requests.utils.quote(prompt)
    url = f"https://image.pollinations.ai/prompt/{encoded}?width=1080&height=1920&model=flux&nologo=true&seed={seed}"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    try:
        resp = requests.get(url, headers=headers, timeout=90)
        if resp.status_code == 200 and len(resp.content) > 1000:
            with open(output_path, "wb") as f:
                f.write(resp.content)
            print(f"✅ [Pollinations Flux Free Tier] Generated: {output_path} ({len(resp.content)} bytes)")
            return True
        else:
            print(f"Pollinations error ({resp.status_code})")
    except Exception as e:
        print(f"Pollinations generation error: {e}")
    return False

def generate_scene_image(prompt, output_path):
    """Autonomous Free-Tier generator with multi-provider fallback."""
    out_dir = os.path.dirname(output_path)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    enhanced = enhance_pixar_prompt(prompt)

    # 1. Check for free Hugging Face token (from env or credentials/hf_token.txt)
    hf_token = get_hf_token()
    if hf_token:
        print(f"🎨 Generating via Hugging Face FLUX.1 (Free Tier)...")
        if generate_via_huggingface_flux(enhanced, output_path, hf_token):
            return output_path

    # 2. Fallback to free Pollinations Flux engine (zero credentials required)
    print(f"🎨 Generating via Pollinations Flux Engine (100% Free)...")
    if generate_via_pollinations_flux(enhanced, output_path):
        return output_path

    print(f"❌ Failed to generate image for prompt: {prompt[:60]}...")
    return None

def ensure_story_assets(story_number, force_regenerate=False):
    """
    Ensures that 3D Pixar scene assets and thumbnail exist for the given story number.
    If assets already exist, re-uses them.
    If assets are missing, generates 3 key visual scenes + thumbnail autonomously using Free AI.
    """
    story_dir = os.path.join(assets_base, f"story_{story_number:02d}")
    thumb_path = os.path.join(thumbs_base, f"story_{story_number:02d}_thumbnail.jpg")
    os.makedirs(story_dir, exist_ok=True)

    existing_scenes = [
        os.path.join(story_dir, f)
        for f in sorted(os.listdir(story_dir))
        if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))
    ]

    if len(existing_scenes) >= 3 and os.path.exists(thumb_path) and not force_regenerate:
        print(f"✨ Found {len(existing_scenes)} existing 3D Pixar scenes for Story #{story_number}. Ready for production.")
        return existing_scenes

    # Load story definition
    from story_generator import get_or_create_story
    story_data = get_or_create_story(story_number)

    clips = story_data.get("clips", [])
    # 3 core story beats: Hook (clip 1 or 2), Action/Climax (clip 4 or 5), Resolution (clip 11 or 12)
    beat_hooks = [
        ("scene_01_hook.jpg", clips[0]["prompt"] if len(clips) > 0 else f"3D Pixar {story_data['base_title']} opening scene"),
        ("scene_02_action.jpg", clips[min(4, len(clips)-1)]["prompt"] if len(clips) > 4 else f"3D Pixar {story_data['base_title']} dynamic exciting scene"),
        ("scene_03_resolution.jpg", clips[-1]["prompt"] if len(clips) > 0 else f"3D Pixar {story_data['base_title']} heartwarming moral lesson ending")
    ]

    print(f"\n=======================================================")
    print(f"🎬 AUTONOMOUS 3D PIXAR ASSET GENERATION: Story #{story_number}")
    print(f"Title: {story_data.get('base_title')}")
    print(f"=======================================================")

    generated_scenes = []
    for filename, prompt in beat_hooks:
        target_path = os.path.join(story_dir, filename)
        if os.path.exists(target_path) and not force_regenerate:
            print(f"Reusing existing: {filename}")
            generated_scenes.append(target_path)
            continue
        print(f"\n--> Generating 8K Scene: {filename}...")
        img = generate_scene_image(prompt, target_path)
        if img:
            generated_scenes.append(img)
            time.sleep(1) # respectful API pacing

    # Generate custom 3D thumbnail if not present
    if not os.path.exists(thumb_path) or force_regenerate:
        thumb_prompt = f"3D Pixar YouTube thumbnail, {story_data.get('base_title')}, close-up highly expressive cute animated animal, dramatic Pixar lighting, high contrast, portrait 9:16"
        print(f"\n--> Generating 8K Custom Thumbnail: story_{story_number:02d}_thumbnail.jpg...")
        generate_scene_image(thumb_prompt, thumb_path)

    print(f"\n🎉 Story #{story_number} has {len(generated_scenes)} 3D Pixar scenes ready for 8K video render!")
    return generated_scenes

if __name__ == "__main__":
    s_no = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    force = "--force" in sys.argv
    scenes = ensure_story_assets(s_no, force_regenerate=force)
    print("Assets list:", scenes)
