"""
MindNest Tales High-CTR 16:9 Thumbnail Generator:
- Creates professional, high-CTR YouTube landscape thumbnails (1280x720).
- Applies the Rule of Thirds, split-second facial expression recognition,
  feathered gradient transitions, and zero background clutter.
- Features high-contrast '10 MIN' badge and clear, emotional headlines.
"""

import os
import sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

def resolve_font():
    """Finds best bold font for thumbnail typography."""
    local_font = os.path.join(script_dir, "fonts", "Poppins-Bold.ttf")
    if os.path.exists(local_font):
        return local_font
    is_win = sys.platform.startswith("win")
    if is_win:
        win_fonts = os.environ.get("WINDIR", "C:\\Windows") + "\\Fonts\\"
        for f in ["segoeuib.ttf", "arialbd.ttf", "calibrib.ttf"]:
            full = os.path.join(win_fonts, f)
            if os.path.exists(full):
                return full
    return None

def generate_10min_master_thumbnail(
    hero_img_path,
    output_path,
    badge_text="10 MIN",
    headline_l1="3 STORIES",
    headline_l2="EVERY KID SHOULD HEAR"
):
    """
    Renders the 16:9 Master Landscape Thumbnail:
    - Left ~52%: Hero character with huge sparkling eyes and warm gold rim light.
    - Soft feathered transition across the center to eliminate harsh split lines.
    - Right ~48%: Deep navy background (#080d1a) for maximum text contrast.
    - Top Right: High-visibility rounded pill badge (#f59e0b) with bold black text.
    - Center Right: Crisp two-line headline with drop shadow for mobile clarity.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    W, H = 1280, 720

    # 1. Base Canvas in Deep Midnight Navy
    canvas = Image.new("RGB", (W, H), (8, 13, 26))

    # 2. Crop & Position Hero Character (Enlarge face to dominate left half)
    if os.path.exists(hero_img_path):
        src_img = Image.open(hero_img_path).convert("RGB")
        sw, sh = src_img.size

        # Zoom into face / upper body: eliminate feet / excess dirt / top sky
        crop_box = (int(sw * 0.04), int(sh * 0.18), int(sw * 0.96), int(sh * 0.75))
        cropped = src_img.crop(crop_box)

        # Scale to full canvas height H
        target_h = H
        target_w = int(cropped.width * (target_h / cropped.height))
        hero_resized = cropped.resize((target_w, target_h), Image.Resampling.LANCZOS)

        canvas.paste(hero_resized, (0, 0))

    # 3. Smooth Feathered Gradient Overlay (Soft transition between character & text)
    grad = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gdraw = ImageDraw.Draw(grad)
    grad_start = int(W * 0.38)
    grad_end = int(W * 0.54)

    for x in range(grad_start, W):
        if x < grad_end:
            alpha = int(255 * ((x - grad_start) / (grad_end - grad_start)))
        else:
            alpha = 255
        gdraw.line([(x, 0), (x, H)], fill=(8, 13, 26, alpha))

    canvas = Image.alpha_composite(canvas.convert("RGBA"), grad).convert("RGB")
    draw = ImageDraw.Draw(canvas)

    # 4. Typography Setup
    font_file = resolve_font()
    if font_file:
        try:
            font_badge = ImageFont.truetype(font_file, 30)
            font_h1 = ImageFont.truetype(font_file, 74)
            font_h2 = ImageFont.truetype(font_file, 44)
        except Exception:
            font_badge = font_h1 = font_h2 = ImageFont.load_default()
    else:
        font_badge = font_h1 = font_h2 = ImageFont.load_default()

    # 5. Top-Right "10 MIN" Badge (High-Contrast Amber-Gold Pill)
    badge_w = 140
    badge_h = 52
    badge_x = W - badge_w - 55
    badge_y = 50

    draw.rounded_rectangle(
        [badge_x, badge_y, badge_x + badge_w, badge_y + badge_h],
        radius=14,
        fill=(245, 158, 11)
    )

    bbox_b = font_badge.getbbox(badge_text)
    bw = bbox_b[2] - bbox_b[0]
    bh = bbox_b[3] - bbox_b[1]
    draw.text(
        (badge_x + (badge_w - bw) / 2, badge_y + (badge_h - bh) / 2 - 3),
        badge_text,
        fill=(0, 0, 0),
        font=font_badge
    )

    # 6. Main Headline (High-Contrast White & Warm Gold)
    text_x = int(W * 0.48)
    text_y1 = 265
    text_y2 = 360

    # Line 1: "3 STORIES" (Bold White with heavy black outline/shadow)
    for dx, dy in [(-3, -3), (3, -3), (-3, 3), (3, 3), (0, 4), (0, -4), (4, 0), (-4, 0)]:
        draw.text((text_x + dx, text_y1 + dy), headline_l1, fill=(0, 0, 0), font=font_h1)
    draw.text((text_x, text_y1), headline_l1, fill=(255, 255, 255), font=font_h1)

    # Line 2: "EVERY KID SHOULD HEAR" (Warm Gold #FBBF24 with shadow)
    for dx, dy in [(-2, -2), (2, -2), (-2, 2), (2, 2), (0, 3), (0, -3), (3, 0), (-3, 0)]:
        draw.text((text_x + dx, text_y2 + dy), headline_l2, fill=(0, 0, 0), font=font_h2)
    draw.text((text_x, text_y2), headline_l2, fill=(251, 191, 36), font=font_h2)

    # Save Thumbnail
    canvas.save(output_path, "JPEG", quality=95)
    print(f"✅ Generated High-CTR 16:9 Thumbnail: {output_path} ({os.path.getsize(output_path)} bytes)")
    return output_path

if __name__ == "__main__":
    hero_img = os.path.join(script_dir, "stories", "assets", "story_01", "scene_03_pride.jpg")
    out_img = os.path.join(script_dir, "stories", "thumbnails", "compilation_01_thumbnail.jpg")
    generate_10min_master_thumbnail(hero_img, out_img)
