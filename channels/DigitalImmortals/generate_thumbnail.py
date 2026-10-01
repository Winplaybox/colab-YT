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
from PIL import Image, ImageDraw, ImageFont, ImageFilter

script_dir = os.path.dirname(os.path.abspath(__file__))
thumbnails_dir = os.path.join(script_dir, "thumbnails")
os.makedirs(thumbnails_dir, exist_ok=True)

def find_devanagari_font():
    """Searches for installed Devanagari fonts on Windows / Project."""
    candidates = [
        r"C:\Windows\Fonts\mangal.ttf",
        r"C:\Windows\Fonts\aparaj.ttf",
        r"C:\Windows\Fonts\nirmala.ttf",
        r"C:\Windows\Fonts\arial.ttf"
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

    # Base background: Load scene image or create rich mythical canvas
    asset_path = os.path.join(script_dir, "episodes", f"episode_{episode_num:02d}", "assets", "scene_04.jpg")
    if os.path.exists(asset_path):
        base_img = Image.open(asset_path).convert("RGB").resize((width, height), Image.Resampling.LANCZOS)
    else:
        base_img = Image.new("RGB", (width, height), color=(20, 12, 10))

    # Apply right-hand dark gradient overlay (Right 45% dark void safe-zone)
    gradient = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    g_draw = ImageDraw.Draw(gradient)

    split_x = int(width * 0.52)
    for x in range(split_x, width):
        alpha = int(245 * ((x - split_x) / (width - split_x)) ** 0.8)
        g_draw.line([(x, 0), (x, height)], fill=(10, 6, 8, alpha))

    base_img = Image.alpha_composite(base_img.convert("RGBA"), gradient).convert("RGB")
    draw = ImageDraw.Draw(base_img)

    font_path = find_devanagari_font()
    try:
        title_font = ImageFont.truetype(font_path, 72) if font_path else ImageFont.load_default()
        sub_font = ImageFont.truetype(font_path, 66) if font_path else ImageFont.load_default()
        badge_font = ImageFont.truetype(font_path, 32) if font_path else ImageFont.load_default()
    except Exception:
        title_font = sub_font = badge_font = ImageFont.load_default()

    # Draw Corner Pill Badge: 'EPISODE 01'
    badge_x, badge_y = int(width * 0.62), 70
    badge_w, badge_h = 240, 52
    draw.rounded_rectangle([badge_x, badge_y, badge_x + badge_w, badge_y + badge_h], radius=12, fill=(185, 28, 28))
    badge_text = f"EPISODE {episode_num:02d}"
    draw.text((badge_x + 30, badge_y + 8), badge_text, fill=(255, 255, 255), font=badge_font)

    # Draw Line 1 (Golden Glow): 'पहला श्लोक'
    text_x = int(width * 0.58)
    y1 = 220
    # Shadow
    draw.text((text_x + 3, y1 + 3), line1, fill=(0, 0, 0), font=title_font)
    draw.text((text_x, y1), line1, fill=(255, 215, 0), font=title_font)

    # Draw Line 2 (Crisp White): 'या भयंकर शाप?'
    y2 = 330
    draw.text((text_x + 3, y2 + 3), line2, fill=(0, 0, 0), font=sub_font)
    draw.text((text_x, y2), line2, fill=(255, 255, 255), font=sub_font)

    # Channel Tagline / Branding: DIGITAL IMMORTALS
    draw.text((text_x, 480), "DIGITAL IMMORTALS", fill=(218, 165, 32), font=badge_font)

    base_img.save(out_path, "JPEG", quality=95)
    print(f"✅ Generated High-CTR Master Thumbnail: {out_path} ({width}x{height})")
    return out_path

if __name__ == "__main__":
    ep = 1
    if len(sys.argv) > 2 and sys.argv[1] == "--episode":
        ep = int(sys.argv[2])
    generate_master_thumbnail(ep)
