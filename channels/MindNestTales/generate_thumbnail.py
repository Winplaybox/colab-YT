"""
MindNest Tales High-CTR 16:9 Landscape Master Thumbnail Engine:
- Generates 16:9 landscape thumbnails (1280x720) optimized for mobile feed CTR.
- High-contrast split panel: warm animated character (left) + dark navy void (right).
- Features '10 MIN' duration pill badge (top-right, safe from YouTube timestamps).
- Luminous gold separator line with center diamond accent.
- Razor-sharp supersampled vector leaf/nest brand mark + crisp geometric diamond separator.
- Full multi-language templating engine covering all 12 global channels with native fonts.
"""

import os
import sys
import math
from PIL import Image, ImageDraw, ImageFont

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

# Localized High-CTR Headline Hooks tailored for bedtime, parents, & moral values
LOCALIZED_THUMBNAIL_DATA = {
    "en": {
        "badge": "10 MIN",
        "l1": "3 STORIES",
        "l2": "EVERY KID SHOULD HEAR",
        "font_family": "latin",
        "brand_sub": "ORIGINAL"
    },
    "hi": {
        "badge": "10 MIN",
        "l1": "3 सीख भरी कहानियां",
        "l2": "जो हर बच्चे को सुननी चाहिए",
        "font_family": "devanagari",
        "brand_sub": "ORIGINAL"
    },
    "es": {
        "badge": "10 MIN",
        "l1": "3 CUENTOS MÁGICOS",
        "l2": "QUE TODO NIÑO DEBE OÍR",
        "font_family": "latin",
        "brand_sub": "ORIGINAL"
    },
    "pt": {
        "badge": "10 MIN",
        "l1": "3 HISTÓRIAS LINDAS",
        "l2": "QUE TODA CRIANÇA DEVE OUVIR",
        "font_family": "latin",
        "brand_sub": "ORIGINAL"
    },
    "fr": {
        "badge": "10 MIN",
        "l1": "3 CONTES MAGIQUES",
        "l2": "QUE CHAQUE ENFANT DOIT ENTENDRE",
        "font_family": "latin",
        "brand_sub": "ORIGINAL"
    },
    "de": {
        "badge": "10 MIN",
        "l1": "3 GESCHICHTEN",
        "l2": "DIE JEDES KIND HÖREN SOLLTE",
        "font_family": "latin",
        "brand_sub": "ORIGINAL"
    },
    "ar": {
        "badge": "10 دقائق",
        "l1": "3 قصص هادفة",
        "l2": "يجب أن يسمعها كل طفل",
        "font_family": "arabic",
        "brand_sub": "ORIGINAL"
    },
    "ja": {
        "badge": "10分",
        "l1": "3つのお話",
        "l2": "子どもに伝えたい大切なこと",
        "font_family": "japanese",
        "brand_sub": "ORIGINAL"
    },
    "ko": {
        "badge": "10분",
        "l1": "3가지 이야기",
        "l2": "모든 아이가 들어야 할 교훈",
        "font_family": "korean",
        "brand_sub": "ORIGINAL"
    },
    "vi": {
        "badge": "10 PHÚT",
        "l1": "3 BÀI HỌC Ý NGHĨA",
        "l2": "DÀNH CHO MỌI ĐỨA TRẺ",
        "font_family": "vietnamese",
        "brand_sub": "ORIGINAL"
    },
    "fil": {
        "badge": "10 MIN",
        "l1": "3 KWENTONG MAY ARAL",
        "l2": "NA DAPAT MAPAKINGGAN NG LAHAT",
        "font_family": "latin",
        "brand_sub": "ORIGINAL"
    },
    "ru": {
        "badge": "10 МИН",
        "l1": "3 МУДРЫЕ СКАЗКИ",
        "l2": "КОТОРЫЕ ДОЛЖЕН СЛЫШАТЬ КАЖДЫЙ",
        "font_family": "latin",
        "brand_sub": "ORIGINAL"
    }
}

def resolve_font_path(font_family="latin"):
    """Finds best bold font file matching the target writing system."""
    fonts_dir = os.path.join(script_dir, "fonts")
    
    font_map = {
        "devanagari": "NotoSansDevanagari-Bold.ttf",
        "arabic": "NotoSansArabic.ttf",
        "japanese": "NotoSansJP.ttf",
        "korean": "NotoSansKR.ttf",
        "vietnamese": "BeVietnamPro-Bold.ttf",
        "latin": "Poppins-Bold.ttf"
    }
    
    candidate = os.path.join(fonts_dir, font_map.get(font_family, "Poppins-Bold.ttf"))
    if os.path.exists(candidate):
        return candidate

    # Windows system fallback
    if sys.platform.startswith("win"):
        win_fonts = os.environ.get("WINDIR", "C:\\Windows") + "\\Fonts\\"
        fallbacks = {
            "devanagari": ["Nirmala.ttc", "arialbd.ttf"],
            "arabic": ["tahomabd.ttf", "arialbd.ttf"],
            "japanese": ["YuGothB.ttc", "meiryo.ttc", "msgothic.ttc"],
            "korean": ["malgunbd.ttf", "malgun.ttf"],
            "vietnamese": ["segoeuib.ttf", "arialbd.ttf"],
            "latin": ["segoeuib.ttf", "arialbd.ttf", "calibrib.ttf"]
        }
        for fb in fallbacks.get(font_family, ["arialbd.ttf"]):
            full = os.path.join(win_fonts, fb)
            if os.path.exists(full):
                return full

    return None

def shape_text(text, font_family="latin"):
    """Reshapes Arabic cursive text if needed."""
    if font_family == "arabic":
        try:
            import arabic_reshaper
            from bidi.algorithm import get_display
            reshaped = arabic_reshaper.reshape(text)
            return get_display(reshaped)
        except Exception:
            return text
    return text

def create_sharp_brand_icon(size=32, scale=4):
    """
    Renders an ultra-sharp, anti-aliased vector leaf and nest emblem
    using 4x supersampling to eliminate any blurriness or compression artifacts.
    """
    S = size * scale
    icon = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(icon)
    gold = (245, 158, 11, 200)
    gold_bright = (251, 191, 36, 240)
    cx, cy = S // 2, S // 2 + 2 * scale
    
    # Left Leaf
    leaf1 = [
        (cx - 2 * scale, cy + 1 * scale),
        (cx - 7 * scale, cy - 6 * scale),
        (cx - 15 * scale, cy - 13 * scale),
        (cx - 13 * scale, cy - 18 * scale),
        (cx - 3 * scale, cy - 16 * scale),
        (cx + 2 * scale, cy - 7 * scale),
        (cx - 2 * scale, cy + 1 * scale)
    ]
    d.polygon(leaf1, fill=gold)
    
    # Right Leaf
    leaf2 = [
        (cx + 2 * scale, cy + 1 * scale),
        (cx + 7 * scale, cy - 6 * scale),
        (cx + 16 * scale, cy - 12 * scale),
        (cx + 15 * scale, cy - 17 * scale),
        (cx + 5 * scale, cy - 16 * scale),
        (cx - 1 * scale, cy - 6 * scale),
        (cx + 2 * scale, cy + 1 * scale)
    ]
    d.polygon(leaf2, fill=gold_bright)
    
    # Nest Cradle Arc
    nest_box = [cx - 16 * scale, cy - 3 * scale, cx + 16 * scale, cy + 14 * scale]
    d.arc(nest_box, start=15, end=165, fill=gold_bright, width=int(2.5 * scale))
    
    return icon.resize((size, size), Image.Resampling.LANCZOS)

def draw_mindnest_brand_elements(draw, overlay, text_x, sep_y, W=1280, H=720):
    """
    Renders the signature MindNest Tales brand elements:
    1. Elegant glowing gold separator line with center diamond accent.
    2. Ultra-sharp supersampled leaf/nest emblem.
    3. 'MINDNEST TALES' with a geometric vector diamond separator and 'ORIGINAL'.
    Keeps the bottom-right timestamp zone completely clear.
    """
    # 1. Luminous Gold Separator Line
    sep_x1 = text_x
    sep_x2 = text_x + 560
    for x in range(sep_x1, sep_x2):
        t = (x - sep_x1) / (sep_x2 - sep_x1)
        fade = math.sin(t * math.pi)
        alpha = int(140 * fade)
        draw.line([(x, sep_y), (x, sep_y + 1)], fill=(245, 158, 11, alpha))

    # Center diamond accent on separator line
    draw.polygon([
        (sep_x1 + 45, sep_y - 4),
        (sep_x1 + 50, sep_y + 1),
        (sep_x1 + 45, sep_y + 6),
        (sep_x1 + 40, sep_y + 1)
    ], fill=(251, 191, 36, 200))

    # 2. Razor-Sharp Vector Leaf/Nest Emblem
    sharp_icon = create_sharp_brand_icon(size=32, scale=4)
    brand_row_y = sep_y + 45
    brand_icon_x = text_x + 50
    overlay.paste(sharp_icon, (brand_icon_x, brand_row_y - 8), sharp_icon)

    # 3. Clean Brand Row with Geometric Vector Diamond Separator (Zero Font Glitch)
    latin_font_path = resolve_font_path("latin")
    if latin_font_path:
        try:
            font_brand = ImageFont.truetype(latin_font_path, 19)
        except Exception:
            font_brand = ImageFont.load_default()
    else:
        font_brand = ImageFont.load_default()

    t_start_x = brand_icon_x + 42
    gold_text = (245, 158, 11, 170)
    gold_accent = (251, 191, 36, 220)

    draw.text((t_start_x, brand_row_y), "MINDNEST TALES", fill=gold_text, font=font_brand)
    bbox_t1 = font_brand.getbbox("MINDNEST TALES")
    w1 = bbox_t1[2] - bbox_t1[0]
    h1 = bbox_t1[3] - bbox_t1[1]

    # Geometric vector diamond separator (bullet replacement without tofu character bugs)
    sep_cx = t_start_x + w1 + 18
    sep_cy = brand_row_y + h1 // 2
    draw.polygon([
        (sep_cx, sep_cy - 4),
        (sep_cx + 4, sep_cy),
        (sep_cx, sep_cy + 4),
        (sep_cx - 4, sep_cy)
    ], fill=gold_accent)

    draw.text((sep_cx + 18, brand_row_y), "ORIGINAL", fill=gold_text, font=font_brand)

def generate_10min_master_thumbnail(
    hero_img_path,
    output_path,
    lang_code="en",
    badge_text=None,
    headline_l1=None,
    headline_l2=None
):
    """
    Renders the 16:9 Master Landscape Thumbnail:
    - Left ~52%: Hero character with huge sparkling eyes and warm gold rim light.
    - Soft feathered transition across the center to eliminate harsh split lines.
    - Right ~48%: Deep navy background (#080d1a) for maximum text contrast.
    - Top Right: High-visibility rounded pill badge (#f59e0b) with bold black text.
    - Center Right: Crisp two-line headline with drop shadow for mobile clarity.
    - Subtle Brand Touch: Glowing separator line & razor-sharp vector leaf/nest emblem.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    W, H = 1280, 720

    # Retrieve language config
    lang_data = LOCALIZED_THUMBNAIL_DATA.get(lang_code, LOCALIZED_THUMBNAIL_DATA["en"])
    badge_text = badge_text or lang_data["badge"]
    headline_l1 = headline_l1 or lang_data["l1"]
    headline_l2 = headline_l2 or lang_data["l2"]
    font_fam = lang_data.get("font_family", "latin")

    # Reshape RTL or Arabic text
    badge_text = shape_text(badge_text, font_fam)
    headline_l1 = shape_text(headline_l1, font_fam)
    headline_l2 = shape_text(headline_l2, font_fam)

    # 1. Base Canvas in Deep Midnight Navy (#080d1a)
    canvas = Image.new("RGB", (W, H), (8, 13, 26))

    # 2. Crop & Position Hero Character (Enlarge face to dominate left half)
    if os.path.exists(hero_img_path):
        src_img = Image.open(hero_img_path).convert("RGB")
        sw, sh = src_img.size

        # Zoom into face / upper body: eliminate feet / excess dirt / top sky
        # Chico's paw/head naturally breaches into the gradient boundary
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

    # RGBA Overlay Layer for smooth antialiasing and transparency effects
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    # 4. Typography Setup
    font_file = resolve_font_path(font_fam)

    # Dynamic sizing based on writing system
    h1_size = 72 if font_fam in ("latin", "vietnamese") else 64
    h2_size = 42 if font_fam in ("latin", "vietnamese") else 38
    badge_size = 28

    if font_file:
        try:
            font_badge = ImageFont.truetype(font_file, badge_size)
            font_h1 = ImageFont.truetype(font_file, h1_size)
            font_h2 = ImageFont.truetype(font_file, h2_size)
        except Exception:
            font_badge = font_h1 = font_h2 = ImageFont.load_default()
    else:
        font_badge = font_h1 = font_h2 = ImageFont.load_default()

    # 5. Top-Right "10 MIN" Badge (High-Contrast Amber-Gold Pill)
    badge_bbox = font_badge.getbbox(badge_text)
    calc_bw = badge_bbox[2] - badge_bbox[0]
    badge_w = max(140, calc_bw + 40)
    badge_h = 52
    badge_x = W - badge_w - 55
    badge_y = 50

    draw.rounded_rectangle(
        [badge_x, badge_y, badge_x + badge_w, badge_y + badge_h],
        radius=14,
        fill=(245, 158, 11, 255)
    )

    bw = badge_bbox[2] - badge_bbox[0]
    bh = badge_bbox[3] - badge_bbox[1]
    draw.text(
        (badge_x + (badge_w - bw) / 2, badge_y + (badge_h - bh) / 2 - 3),
        badge_text,
        fill=(0, 0, 0, 255),
        font=font_badge
    )

    # 6. Main Headline (High-Contrast White & Warm Gold)
    text_x = int(W * 0.48)
    text_y1 = 250
    text_y2 = 345

    # Line 1: Main Hook (Bold Pure White with heavy dark shadow)
    for dx, dy in [(-3, -3), (3, -3), (-3, 3), (3, 3), (0, 4), (0, -4), (4, 0), (-4, 0)]:
        draw.text((text_x + dx, text_y1 + dy), headline_l1, fill=(0, 0, 0, 230), font=font_h1)
    draw.text((text_x, text_y1), headline_l1, fill=(255, 255, 255, 255), font=font_h1)

    # Line 2: Moral / Emotional Promise (Warm Gold #FBBF24 with shadow)
    for dx, dy in [(-2, -2), (2, -2), (-2, 2), (2, 2), (0, 3), (0, -3), (3, 0), (-3, 0)]:
        draw.text((text_x + dx, text_y2 + dy), headline_l2, fill=(0, 0, 0, 230), font=font_h2)
    draw.text((text_x, text_y2), headline_l2, fill=(251, 191, 36, 255), font=font_h2)

    # 7. Subtle MindNest Tales Brand Touches (Separator + Sharp Vector Leaf/Nest Silhouette)
    sep_y = 430
    draw_mindnest_brand_elements(draw, overlay, text_x, sep_y, W=W, H=H)

    # Composite & Save Thumbnail
    final_canvas = Image.alpha_composite(canvas.convert("RGBA"), overlay).convert("RGB")
    final_canvas.save(output_path, "JPEG", quality=95)
    print(f"✅ Generated High-CTR 16:9 Thumbnail [{lang_code.upper()}]: {output_path} ({os.path.getsize(output_path)} bytes)")
    return output_path

def generate_all_language_thumbnails(hero_img_path, story_number=1, output_dir=None):
    """
    Renders unified high-CTR thumbnails for ALL configured MindNest Tales languages.
    Produces:
    - compilation_{story_number:02d}_thumbnail.jpg (Default / English master)
    - compilation_{story_number:02d}_thumbnail_{lang}.jpg (Language specific)
    """
    if not output_dir:
        output_dir = os.path.join(script_dir, "stories", "thumbnails")
    os.makedirs(output_dir, exist_ok=True)

    generated = {}
    print(f"\n=======================================================")
    print(f"🎨 GENERATING 16:9 MASTER THUMBNAILS FOR ALL 12 LANGUAGES")
    print(f"=======================================================")

    for lang in LOCALIZED_THUMBNAIL_DATA.keys():
        out_file = os.path.join(output_dir, f"compilation_{story_number:02d}_thumbnail_{lang}.jpg")
        generate_10min_master_thumbnail(hero_img_path, out_file, lang_code=lang)
        generated[lang] = out_file

    # Set English as the default un-suffixed master thumbnail
    master_default = os.path.join(output_dir, f"compilation_{story_number:02d}_thumbnail.jpg")
    if "en" in generated and os.path.exists(generated["en"]):
        img = Image.open(generated["en"])
        img.save(master_default, "JPEG", quality=95)
        print(f"🌟 Master default thumbnail linked: {master_default}")

    return generated

if __name__ == "__main__":
    hero_img = os.path.join(script_dir, "stories", "assets", "story_01", "scene_03_pride.jpg")
    generate_all_language_thumbnails(hero_img, story_number=1)
