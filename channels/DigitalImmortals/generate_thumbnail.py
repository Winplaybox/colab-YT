"""
DigitalImmortals High-CTR 16:9 Landscape Master Thumbnail Engine
================================================================
- 16:9 Landscape (1280x720 / 1920x1080)
- Rule of Thirds: Left 65% focal artwork + Right 35% dark gradient void
- Bold, high-contrast Devanagari typography
- Split-second cognition badge: 'EPISODE 01'
"""

import os
import sys
import json
import os
import sys
import json
from PIL import Image, ImageDraw, ImageFont, ImageFilter

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

script_dir = os.path.dirname(os.path.abspath(__file__))
thumbnails_dir = os.path.join(script_dir, "thumbnails")
os.makedirs(thumbnails_dir, exist_ok=True)

def find_devanagari_font():
    """Searches for verified Devanagari fonts."""
    candidates = [
        os.path.join(script_dir, "branding", "fonts", "NotoSansDevanagari.ttf"),
        r"C:\Windows\Fonts\Nirmala.ttc",
        r"C:\Windows\Fonts\mangal.ttf",
        r"C:\Windows\Fonts\aparaj.ttf"
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    return None

def generate_master_thumbnail(episode_num=1, line1="पहला श्लोक", line2="या भयंकर शाप?"):
    """
    Renders the high-CTR 16:9 Landscape thumbnail.
    """
    width, height = 1280, 720
    out_path = os.path.join(thumbnails_dir, f"thumbnail_ep{episode_num:02d}.jpg")

    # Base background: Load pristine generated artwork or scene asset
    brain_dir = os.path.abspath(os.path.join(script_dir, "..", "..", "..", ".gemini", "antigravity-ide", "brain", "e1e3a393-5c06-41cb-a159-f895fa0649aa"))
    candidate_arts = [
        os.path.join(brain_dir, "valmiki_narada_dialogue_1790916626818.jpg"),
        os.path.join(brain_dir, "valmiki_scene_test_1790916603573.jpg"),
        os.path.join(brain_dir, "valmiki_first_scene_1790916418297.jpg"),
        os.path.join(script_dir, "episodes", f"episode_{episode_num:02d}", "assets", "scene_01.jpg")
    ]
    
    base_img = None
    for art in candidate_arts:
        if os.path.exists(art):
            try:
                base_img = Image.open(art).convert("RGB").resize((width, height), Image.Resampling.LANCZOS)
                print(f"[THUMBNAIL] Using base artwork: {os.path.basename(art)}")
                break
            except Exception:
                continue

    if base_img is None:
        base_img = Image.new("RGB", (width, height), color=(20, 12, 10))

    # Apply right-hand dark gradient overlay (Right 45% dark void safe-zone for crisp readability)
    gradient = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    g_draw = ImageDraw.Draw(gradient)

    split_x = int(width * 0.48)
    for x in range(split_x, width):
        alpha = int(245 * ((x - split_x) / (width - split_x)) ** 0.8)
        g_draw.line([(x, 0), (x, height)], fill=(8, 5, 12, alpha))

    base_img = Image.alpha_composite(base_img.convert("RGBA"), gradient).convert("RGB")
    draw = ImageDraw.Draw(base_img)

    font_path = find_devanagari_font()
    print(f"[THUMBNAIL] Loaded Devanagari font: {font_path}")
    try:
        title_font = ImageFont.truetype(font_path, 76) if font_path else ImageFont.load_default()
        sub_font = ImageFont.truetype(font_path, 68) if font_path else ImageFont.load_default()
        badge_font = ImageFont.truetype(font_path, 34) if font_path else ImageFont.load_default()
    except Exception as e:
        print(f"[WARN] Font load issue: {e}")
        title_font = sub_font = badge_font = ImageFont.load_default()

    # Draw Corner Pill Badge: 'EPISODE 01'
    badge_x, badge_y = int(width * 0.58), 60
    badge_w, badge_h = 240, 54
    draw.rounded_rectangle([badge_x, badge_y, badge_x + badge_w, badge_y + badge_h], radius=14, fill=(185, 28, 28))
    badge_text = f"EPISODE {episode_num:02d}"
    draw.text((badge_x + 30, badge_y + 8), badge_text, fill=(255, 255, 255), font=badge_font)

    # Draw Line 1 (Golden Glow): 'पहला श्लोक'
    text_x = int(width * 0.55)
    y1 = 200
    # Shadow offset
    draw.text((text_x + 4, y1 + 4), line1, fill=(0, 0, 0), font=title_font)
    draw.text((text_x, y1), line1, fill=(255, 215, 0), font=title_font)

    # Draw Line 2 (Crisp Blood Red / Diamond White): 'या भयंकर शाप?'
    y2 = 320
    draw.text((text_x + 4, y2 + 4), line2, fill=(0, 0, 0), font=sub_font)
    draw.text((text_x, y2), line2, fill=(255, 255, 255), font=sub_font)

    # Sub-hook (Valmiki Ramayana authenticity badge)
    subhook_text = "वाल्मीकि रामायण रहस्य"
    try:
        subhook_font = ImageFont.truetype(font_path, 38)
        draw.text((text_x + 2, 452), subhook_text, fill=(0, 0, 0), font=subhook_font)
        draw.text((text_x, 450), subhook_text, fill=(255, 180, 50), font=subhook_font)
    except Exception:
        pass

    # Channel Tagline / Branding: DIGITAL IMMORTALS
    draw.text((text_x, 560), "DIGITAL IMMORTALS", fill=(218, 165, 32), font=badge_font)

    base_img.save(out_path, "JPEG", quality=98)
    print(f"[OK] Generated High-CTR Master Thumbnail: {out_path} ({width}x{height})")
    return out_path

if __name__ == "__main__":
    ep = 1
    if len(sys.argv) > 2 and sys.argv[1] == "--episode":
        ep = int(sys.argv[2])
    generate_master_thumbnail(ep)
