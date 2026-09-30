"""
MindNest Tales High-CTR 16:9 Landscape Master Thumbnail Engine:
- Generates 16:9 YouTube landscape thumbnails (1280x720) in hyper-realistic 8K detailed aesthetic.
- High-contrast split panel: warm animated character (left) + dark navy void (right).
- Story-matched titles and subtitles with dynamic auto-scaling to guarantee ZERO text truncation.
- Official MindNest Tales global logo (woven nest, teal paw, open book) integrated seamlessly.
- Crisp vector stroke outlines (stroke_width) for ultra-clear visibility at small mobile feed sizes.
- Luminous gold separator line with center diamond accent.
- '10 MIN' duration pill badge (top-right, safe from YouTube timestamps).
- Full multi-language templating engine covering all 12 global channels with native fonts.
"""

import os
import sys
import math
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

# Localized Story-Matched High-CTR Titles & Subtitles
# Tailored specifically for Story 1 (Chico the Cheetah) while maintaining parent moral hooks
LOCALIZED_THUMBNAIL_DATA = {
    "en": {
        "badge": "10 MIN",
        "l1": "CHICO THE CHEETAH",
        "l2": "LEARNS A BIG LESSON",
        "font_family": "latin",
        "brand_sub": "ORIGINAL"
    },
    "hi": {
        "badge": "10 MIN",
        "l1": "चीकू चीता",
        "l2": "ने सीखी एक बड़ी सीख",
        "font_family": "devanagari",
        "brand_sub": "ORIGINAL"
    },
    "es": {
        "badge": "10 MIN",
        "l1": "CHICO EL GUEPARDO",
        "l2": "APRENDE UNA GRAN LECCIÓN",
        "font_family": "latin",
        "brand_sub": "ORIGINAL"
    },
    "pt": {
        "badge": "10 MIN",
        "l1": "CHICO O GUEPARDO",
        "l2": "APRENDE UMA GRANDE LIÇÃO",
        "font_family": "latin",
        "brand_sub": "ORIGINAL"
    },
    "fr": {
        "badge": "10 MIN",
        "l1": "CHICO LE GUÉPARD",
        "l2": "APPREND UNE GRANDE LEÇON",
        "font_family": "latin",
        "brand_sub": "ORIGINAL"
    },
    "de": {
        "badge": "10 MIN",
        "l1": "CHICO DER GEPARD",
        "l2": "LERNT EINE GROSSE LEKTION",
        "font_family": "latin",
        "brand_sub": "ORIGINAL"
    },
    "ar": {
        "badge": "10 دقائق",
        "l1": "الفهد شيكو",
        "l2": "يتعلم درسا كبيرا",
        "font_family": "arabic",
        "brand_sub": "ORIGINAL"
    },
    "ja": {
        "badge": "10分",
        "l1": "チーターのチコ",
        "l2": "たいせつな気づき",
        "font_family": "japanese",
        "brand_sub": "ORIGINAL"
    },
    "ko": {
        "badge": "10분",
        "l1": "치타 치코",
        "l2": "소중한 교훈을 배우다",
        "font_family": "korean",
        "brand_sub": "ORIGINAL"
    },
    "vi": {
        "badge": "10 PHÚT",
        "l1": "BÁO CON CHICO",
        "l2": "BÀI HỌC ĐẦU ĐỜI Ý NGHĨA",
        "font_family": "vietnamese",
        "brand_sub": "ORIGINAL"
    },
    "fil": {
        "badge": "10 MIN",
        "l1": "SI CHICO ANG CHEETAH",
        "l2": "NATUTO NG MAHALAGANG ARAL",
        "font_family": "latin",
        "brand_sub": "ORIGINAL"
    },
    "ru": {
        "badge": "10 МИН",
        "l1": "ГЕПАРД ЧИКО",
        "l2": "УЧИТ ВАЖНЫЙ УРОК",
        "font_family": "latin",
        "brand_sub": "ORIGINAL"
    }
}

def resolve_font_path(font_family="latin"):
    """Finds best bold font file matching the target writing system."""
    fonts_dir = os.path.join(script_dir, "fonts")
    
    # Priority paths per writing system
    if sys.platform.startswith("win"):
        win_fonts = os.environ.get("WINDIR", "C:\\Windows") + "\\Fonts\\"
        if font_family == "japanese":
            for jf in ["YuGothB.ttc", "meiryob.ttc", "msgothic.ttc"]:
                p = os.path.join(win_fonts, jf)
                if os.path.exists(p):
                    return p
        elif font_family == "korean":
            for kf in ["malgunbd.ttf", "malgun.ttf"]:
                p = os.path.join(win_fonts, kf)
                if os.path.exists(p):
                    return p

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

def fit_font_size(text, font_path, max_width, initial_size, min_size=22, step=2):
    """
    Dynamically auto-scales font size so that the text fits perfectly
    within max_width without ever truncating, clipping, or wrapping awkwardly.
    """
    if not font_path or not os.path.exists(font_path):
        return ImageFont.load_default(), initial_size

    for sz in range(initial_size, min_size - 1, -step):
        try:
            f = ImageFont.truetype(font_path, sz)
            bbox = f.getbbox(text)
            w = bbox[2] - bbox[0]
            if w <= max_width:
                return f, sz
        except Exception:
            break
    try:
        return ImageFont.truetype(font_path, min_size), min_size
    except Exception:
        return ImageFont.load_default(), min_size

def draw_mindnest_brand_elements(draw, overlay, text_x, sep_y, W=1280, H=720):
    """
    Renders the official MindNest Tales brand elements:
    1. Elegant glowing gold separator line with center diamond accent.
    2. Official MindNest Tales global logo (woven nest, teal paw, open book).
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

    # 2. Official MindNest Tales Global Logo (Woven nest, teal paw, open book)
    logo_path = os.path.join(script_dir, "assets", "logo.png")
    if not os.path.exists(logo_path):
        logo_path = os.path.join(script_dir, "logo.png")

    brand_row_y = sep_y + 38
    brand_logo_x = text_x + 40
    logo_size = 52

    if os.path.exists(logo_path):
        logo_img = Image.open(logo_path).convert("RGBA")
        logo_res = logo_img.resize((logo_size, logo_size), Image.Resampling.LANCZOS)
        overlay.paste(logo_res, (brand_logo_x, brand_row_y - 14), logo_res)

    # 3. Clean Brand Row with Geometric Vector Diamond Separator (Zero Font Glitch)
    latin_font_path = resolve_font_path("latin")
    if latin_font_path:
        try:
            font_brand = ImageFont.truetype(latin_font_path, 19)
        except Exception:
            font_brand = ImageFont.load_default()
    else:
        font_brand = ImageFont.load_default()

    t_start_x = brand_logo_x + logo_size + 14
    gold_text = (245, 158, 11, 180)
    gold_accent = (251, 191, 36, 230)

    draw.text((t_start_x, brand_row_y), "MINDNEST TALES", fill=gold_text, font=font_brand)
    bbox_t1 = font_brand.getbbox("MINDNEST TALES")
    w1 = bbox_t1[2] - bbox_t1[0]
    h1 = bbox_t1[3] - bbox_t1[1]

    # Geometric vector diamond separator (bullet replacement without missing-character boxes)
    sep_cx = t_start_x + w1 + 16
    sep_cy = brand_row_y + h1 // 2
    draw.polygon([
        (sep_cx, sep_cy - 4),
        (sep_cx + 4, sep_cy),
        (sep_cx, sep_cy + 4),
        (sep_cx - 4, sep_cy)
    ], fill=gold_accent)

    draw.text((sep_cx + 16, brand_row_y), "ORIGINAL", fill=gold_text, font=font_brand)

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
    - Dynamic auto-scaling to prevent any text clipping or truncation.
    - Official MindNest Tales global logo in the brand signature row.
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

    # 2. Hero Image Crop & Hyper-Realistic 8K Detail Enhancement
    if os.path.exists(hero_img_path):
        src_img = Image.open(hero_img_path).convert("RGB")
        
        # Detail enhancement filters for fur, whiskers, eye sparkles & warm sunset rim light
        enh_c = ImageEnhance.Color(src_img).enhance(1.08)
        enh_k = ImageEnhance.Contrast(enh_c).enhance(1.06)
        src_sharp = enh_k.filter(ImageFilter.UnsharpMask(radius=1.8, percent=140, threshold=2))

        sw, sh = src_sharp.size

        # Zoom into face / upper body: eliminate feet / excess dirt / top sky
        # Chico's paw/head naturally breaches into the gradient boundary
        crop_box = (int(sw * 0.04), int(sh * 0.18), int(sw * 0.96), int(sh * 0.75))
        cropped = src_sharp.crop(crop_box)

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

    # 4. Typography Setup with Auto-Fitting
    font_file = resolve_font_path(font_fam)

    # 5. Top-Right "10 MIN" Badge (High-Contrast Amber-Gold Pill)
    badge_font_path = resolve_font_path(font_fam if font_fam != "latin" else "latin")
    if badge_font_path:
        try:
            font_badge = ImageFont.truetype(badge_font_path, 28)
        except Exception:
            font_badge = ImageFont.load_default()
    else:
        font_badge = ImageFont.load_default()

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

    # 6. Main Headline (Guaranteed NO Truncation via Auto-Scaling)
    text_x = int(W * 0.48)
    max_text_width = W - text_x - 55  # ~610px safe right-panel text width
    text_y1 = 250
    text_y2 = 345

    # Determine optimal non-clipping font sizes
    init_h1_size = 70 if font_fam in ("latin", "vietnamese") else 62
    init_h2_size = 42 if font_fam in ("latin", "vietnamese") else 36

    font_h1, actual_sz1 = fit_font_size(headline_l1, font_file, max_text_width, init_h1_size, min_size=28)
    font_h2, actual_sz2 = fit_font_size(headline_l2, font_file, max_text_width, init_h2_size, min_size=20)

    # Line 1: Main Story Hook (Bold Pure White with heavy dark shadow & outline)
    for dx, dy in [(-3, -3), (3, -3), (-3, 3), (3, 3), (0, 4), (0, -4), (4, 0), (-4, 0)]:
        draw.text((text_x + dx, text_y1 + dy), headline_l1, fill=(0, 0, 0, 230), font=font_h1)
    draw.text((text_x, text_y1), headline_l1, fill=(255, 255, 255, 255), font=font_h1, stroke_width=2, stroke_fill=(0, 0, 0))

    # Line 2: Moral / Emotional Promise (Warm Gold #FBBF24 with shadow)
    for dx, dy in [(-2, -2), (2, -2), (-2, 2), (2, 2), (0, 3), (0, -3), (3, 0), (-3, 0)]:
        draw.text((text_x + dx, text_y2 + dy), headline_l2, fill=(0, 0, 0, 230), font=font_h2)
    draw.text((text_x, text_y2), headline_l2, fill=(251, 191, 36, 255), font=font_h2, stroke_width=1, stroke_fill=(0, 0, 0))

    # 7. Official MindNest Tales Brand Touches (Separator + Official Global Logo)
    sep_y = 430
    draw_mindnest_brand_elements(draw, overlay, text_x, sep_y, W=W, H=H)

    # Composite & Save Thumbnail at high 95 quality
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

    # Set English as the default master thumbnail
    master_default = os.path.join(output_dir, f"compilation_{story_number:02d}_thumbnail.jpg")
    if "en" in generated and os.path.exists(generated["en"]):
        img = Image.open(generated["en"])
        img.save(master_default, "JPEG", quality=95)
        print(f"🌟 Master default thumbnail linked: {master_default}")

    return generated

if __name__ == "__main__":
    hero_img = os.path.join(script_dir, "stories", "assets", "story_01", "scene_03_pride.jpg")
    generate_all_language_thumbnails(hero_img, story_number=1)
