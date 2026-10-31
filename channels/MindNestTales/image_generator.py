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
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)
stories_dir = os.path.join(script_dir, "stories")
assets_base = os.path.join(stories_dir, "assets")
thumbs_base = os.path.join(stories_dir, "thumbnails")

os.makedirs(assets_base, exist_ok=True)
os.makedirs(thumbs_base, exist_ok=True)

def enhance_pixar_prompt(base_prompt):
    """
    MindNest Tales visual style (changed Oct 2026): clean 2D FLAT EXPLAINER animation.
    Name kept for compatibility with existing callers.
    """
    clean = base_prompt
    for junk in ("portrait 9:16", "3D Pixar-style", "Pixar", "Disney", "3D", "photorealistic",
                 "hyper-realistic", "8K", "8k", "octane render", "Unreal Engine"):
        clean = clean.replace(junk, "")
    clean = " ".join(clean.split()).strip(" ,")
    style = (
        "flat 2D vector illustration, children's explainer animation style, simple rounded shapes, "
        "cute friendly animal characters with big expressive eyes, bold clean colours, soft flat shading, "
        "no outlines or thin outlines, simple uncluttered background, warm cheerful palette, "
        "vertical 9:16 composition, main character centred in the upper two-thirds, "
        "family-friendly, no text, no letters, no watermark"
    )
    return f"{clean}, {style}"

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

def apply_8k_detail_enhancement(img):
    """
    Applies hyper-realistic 8K detail post-processing:
    - High-fidelity Lanczos upscaling to 1080p+ portrait if needed
    - Dynamic color & contrast pop
    - Micro-fur unsharp mask for razor-sharp whisker details and eye sparkles
    """
    from PIL import ImageEnhance, ImageFilter, Image
    w, h = img.size
    if w < 1080 or h < 1920:
        target_w = 1080
        target_h = int(h * (target_w / w))
        if target_h < 1920:
            target_h = 1920
            target_w = int(w * (target_h / h))
        img = img.resize((target_w, target_h), Image.Resampling.LANCZOS)
    
    c = ImageEnhance.Color(img).enhance(1.08)
    k = ImageEnhance.Contrast(c).enhance(1.06)
    s = k.filter(ImageFilter.UnsharpMask(radius=1.8, percent=145, threshold=2))
    return s

def strip_and_save_clean_image(pil_or_bytes_or_path, output_path):
    """
    Strips 100% of EXIF, C2PA, generator headers, and software signatures.
    Applies hyper-realistic 8K detail enhancement and saves as an ultra-clean JPEG.
    """
    import io
    from PIL import Image
    if isinstance(pil_or_bytes_or_path, str):
        img = Image.open(pil_or_bytes_or_path)
    elif isinstance(pil_or_bytes_or_path, bytes):
        img = Image.open(io.BytesIO(pil_or_bytes_or_path))
    else:
        img = pil_or_bytes_or_path
    clean = img.convert("RGB")
    enhanced = apply_8k_detail_enhancement(clean)
    enhanced.save(output_path, "JPEG", quality=96, optimize=True)

_gradio_client = None

def get_z_image_client():
    global _gradio_client
    if _gradio_client is None:
        try:
            from gradio_client import Client
            token = get_hf_token()
            _gradio_client = Client("mcp-tools/Z-Image-Turbo", token=token) if token else Client("mcp-tools/Z-Image-Turbo")
        except Exception as e:
            print(f"Notice initializing Z-Image Client: {e}")
            _gradio_client = None
    return _gradio_client

def generate_via_z_image_turbo(prompt, output_path):
    """
    Generates Photorealistic 3D image via Diffusion Transformer (mcp-tools/Z-Image-Turbo).
    100% Free, ZeroGPU powered, lightning-fast studio quality.
    """
    try:
        client = get_z_image_client()
        if not client:
            return False
        res, _ = client.predict(
            prompt=prompt,
            resolution="720x1280 ( 9:16 )",
            seed=42,
            steps=8,
            shift=3.0,
            random_seed=True,
            api_name="/generate"
        )
        if res and os.path.exists(res):
            strip_and_save_clean_image(res, output_path)
            print(f"✅ [Z-Image-Turbo Studio Render] Clean 9:16: {output_path} ({os.path.getsize(output_path)} bytes)")
            return True
    except Exception as e:
        print(f"Z-Image-Turbo generation notice: {e}")
    return False

def _shared_ai_image(prompt, output_path, width, height):
    """Shared Gemini/OpenAI generator (channels/common/ai_images.py). HF free credits ended 15 Oct 2026."""
    try:
        root = os.path.abspath(os.path.join(script_dir, "..", ".."))
        if root not in sys.path:
            sys.path.insert(0, root)
        from channels.common.ai_images import generate
        return generate(prompt, output_path, width, height)
    except Exception as e:
        print(f"Shared AI image notice: {e}")
        return False


def generate_via_huggingface_flux(prompt, output_path, hf_token):
    """Generates Photorealistic 3D image via Hugging Face Serverless FLUX.1."""
    try:
        from huggingface_hub import InferenceClient
        client = InferenceClient(api_key=hf_token)
        img = client.text_to_image(prompt, model="black-forest-labs/FLUX.1-schnell")
        strip_and_save_clean_image(img, output_path)
        print(f"✅ [FLUX.1-schnell Free Tier] Clean Studio Render: {output_path} ({os.path.getsize(output_path)} bytes)")
        return True
    except Exception as e:
        print(f"Hugging Face FLUX notice: {e}")
        try:
            from huggingface_hub import InferenceClient
            client = InferenceClient(api_key=hf_token)
            img = client.text_to_image(prompt, model="stabilityai/stable-diffusion-xl-base-1.0")
            strip_and_save_clean_image(img, output_path)
            print(f"✅ [SDXL Free Tier] Clean Studio Render: {output_path} ({os.path.getsize(output_path)} bytes)")
            return True
        except Exception as e2:
            print(f"Hugging Face SDXL fallback notice: {e2}")
    return False

def generate_via_pollinations_flux(prompt, output_path, seed=None):
    """Generates Photorealistic 3D image via Pollinations Flux Engine with metadata sanitization."""
    if seed is None:
        seed = int(time.time() * 1000) % 999999
    encoded = requests.utils.quote(prompt)
    url = f"https://image.pollinations.ai/prompt/{encoded}?width=1080&height=1920&model=flux&nologo=true&seed={seed}"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    try:
        resp = requests.get(url, headers=headers, timeout=90)
        if resp.status_code == 200 and len(resp.content) > 1000:
            strip_and_save_clean_image(resp.content, output_path)
            print(f"✅ [Pollinations Flux Free Tier] Clean Studio Render: {output_path} ({os.path.getsize(output_path)} bytes)")
            return True
        else:
            print(f"Pollinations notice ({resp.status_code})")
    except Exception as e:
        print(f"Pollinations generation notice: {e}")
    return False

def generate_scene_image(prompt, output_path):
    """Autonomous generator with multi-provider fallback and zero AI fingerprinting."""
    out_dir = os.path.dirname(output_path)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    enhanced = enhance_pixar_prompt(prompt)

    # 0. Shared Gemini/OpenAI provider (reliable, paid per image)
    if _shared_ai_image(enhanced, output_path, 1080, 1920):
        return output_path

    # 1. Z-Image-Turbo ZeroGPU Space (free, but quota-limited on CI runners)
    print(f"🎨 Generating via Z-Image-Turbo Studio Engine (9:16 Photorealistic 3D)...")
    if generate_via_z_image_turbo(enhanced, output_path):
        return output_path

    # 2. Secondary: Hugging Face Serverless FLUX.1 (if user has active credits)
    hf_token = get_hf_token()
    if hf_token:
        print(f"🎨 Generating via Hugging Face FLUX.1...")
        if generate_via_huggingface_flux(enhanced, output_path, hf_token):
            return output_path

    # 3. Tertiary: Pollinations Engine fallback
    print(f"🎨 Generating via Pollinations Engine...")
    if generate_via_pollinations_flux(enhanced, output_path):
        return output_path

    print(f"❌ Failed to generate image for prompt: {prompt[:60]}...")
    return None

def build_narrative_shots(story_data):
    """
    Constructs a 16-scene cinematic narrative arc matching 180s (3-minute) Shorts pacing:
    ~11.25 seconds per shot across a 180s runtime, with smooth 0.5s crossfade transitions.
    """
    story_number = story_data.get("story_number", 1)
    base_title = story_data.get("base_title", "Moral Story")
    moral = story_data.get("moral", "")
    characters = story_data.get("characters", {})
    hero_char = characters.get("hero", "cute animated animal hero with round expressive eyes")
    mentor_char = characters.get("mentor", "wise tortoise elder with round spectacles")

    # Extract flaw if defined in master list
    from story_generator import STORIES_MASTER
    flaw = "impatience and rushing ahead"
    if story_number <= len(STORIES_MASTER):
        flaw = STORIES_MASTER[story_number - 1][2]

    return [
        ("scene_01_intro.jpg", f"{hero_char}, introducing character in their vibrant natural habitat with curious wide eyes and cheerful smile, lush morning sunlight"),
        ("scene_02_friends.jpg", f"{hero_char}, happily interacting with friendly animal neighbors and birds under acacia trees in golden morning light"),
        ("scene_03_pride.jpg", f"{hero_char}, showing off energetic personality and natural speed, sprinting playfully across the open fields"),
        ("scene_04_flaw.jpg", f"{hero_char}, displaying characteristic habit of {flaw}, dynamic action pose kicking up dust and rushing carelessly"),
        ("scene_05_announcement.jpg", f"{hero_char}, receiving invitation to the grand festival summit from joyful animal messengers"),
        ("scene_06_procrastination.jpg", f"{hero_char}, relaxing lazily by the riverbank and ignoring the ticking clock, confident they can rush later"),
        ("scene_07_the_storm.jpg", f"{hero_char}, facing a dramatic sudden thunderstorm gathering over the dark hills, wind sweeping across the trees"),
        ("scene_08_obstacle.jpg", f"{hero_char}, encountering a swollen roaring river and huge fallen baobab tree blocking the shortcut trail"),
        ("scene_09_predicament.jpg", f"{hero_char}, skidding into deep slippery mud and tangling into thorny bushes, wide panicked expressive eyes"),
        ("scene_10_hopeless.jpg", f"{hero_char}, struggling fruitlessly to break free from the thorny vines as the midday sun climbs higher"),
        ("scene_11_mentor_arrives.jpg", f"{mentor_char}, arriving with calm, dignified steps, wearing spectacles and holding a wooden walking staff"),
        ("scene_12_wisdom.jpg", f"{mentor_char}, speaking warmly with gentle grandfather smile, pointing toward the patient high ridge path"),
        ("scene_13_realization.jpg", f"{hero_char}, having an emotional lightbulb realization, taking a calm breath and listening humbly"),
        ("scene_14_teamwork.jpg", f"{hero_char} and {mentor_char}, working together patiently to untangle the vines and step safely onto the ridge"),
        ("scene_15_triumphant_arrival.jpg", f"{hero_char}, arriving proudly at the summit gathering just on time with the festive banner, crowd cheering"),
        ("scene_16_celebration.jpg", f"{hero_char} and {mentor_char}, surrounded by all animal friends enjoying a joyful fruit banquet under a golden sunset, moral victory")
    ]

def ensure_story_assets(story_number, force_regenerate=False):
    """
    Ensures that all 16 cinematic 3D Pixar scene assets and thumbnail exist for the given story.
    If assets already exist, re-uses them.
    If missing or incomplete, generates the complete 16-scene narrative sequence autonomously.
    """
    story_dir = os.path.join(assets_base, f"story_{story_number:02d}")
    thumb_path = os.path.join(thumbs_base, f"story_{story_number:02d}_thumbnail.jpg")
    os.makedirs(story_dir, exist_ok=True)

    # Load story definition
    from story_generator import get_or_create_story
    story_data = get_or_create_story(story_number)
    narrative_shots = build_narrative_shots(story_data)

    existing_scenes = [
        os.path.join(story_dir, filename)
        for filename, _ in narrative_shots
        if os.path.exists(os.path.join(story_dir, filename)) and os.path.getsize(os.path.join(story_dir, filename)) > 10000
    ]

    if len(existing_scenes) >= 12 and os.path.exists(thumb_path) and not force_regenerate:
        print(f"✨ Found {len(existing_scenes)} existing 3D Pixar scenes for Story #{story_number}. Ready for production.")
        return existing_scenes

    print(f"\n=======================================================")
    print(f"🎬 AUTONOMOUS 3D PIXAR ASSET GENERATION: Story #{story_number}")
    print(f"Title: {story_data.get('base_title')}")
    print(f"Shots: 16 Narrative Scenes (11s pacing for 180s Shorts)")
    print(f"=======================================================")

    generated_scenes = []
    for filename, prompt in narrative_shots:
        target_path = os.path.join(story_dir, filename)
        if os.path.exists(target_path) and os.path.getsize(target_path) > 10000 and not force_regenerate:
            print(f"Reusing existing: {filename}")
            generated_scenes.append(target_path)
            continue
        print(f"\n--> Generating 3D Scene: {filename}...")
        img = generate_scene_image(prompt, target_path)
        if img:
            generated_scenes.append(img)
            time.sleep(0.5)

    # Generate custom 3D thumbnail if not present
    if not os.path.exists(thumb_path) or force_regenerate:
        thumb_prompt = f"3D Pixar YouTube thumbnail, {story_data.get('base_title')}, close-up highly expressive cute animated animal, dramatic Pixar lighting, high contrast, portrait 9:16"
        print(f"\n--> Generating Custom Thumbnail: story_{story_number:02d}_thumbnail.jpg...")
        generate_scene_image(thumb_prompt, thumb_path)

    # Return all valid scenes sorted by filename
    final_scenes = [
        os.path.join(story_dir, f)
        for f in sorted(os.listdir(story_dir))
        if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')) and not f.startswith("test_")
    ]
    print(f"\n🎉 Story #{story_number} has {len(final_scenes)} 3D Pixar scenes ready for video render!")
    return final_scenes

if __name__ == "__main__":
    s_no = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    force = "--force" in sys.argv
    scenes = ensure_story_assets(s_no, force_regenerate=force)
    print("Assets list:", scenes)

