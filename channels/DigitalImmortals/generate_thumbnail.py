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

EPISODE_THUMBNAIL_CONFIG = {
    1: {
        "line1": "पहला श्लोक",
        "line2": "या भयंकर शाप?",
        "subhook": "वाल्मीकि रामायण रहस्य",
        "anchor_pref": ["valmiki_narada_dialogue_1790916626818.jpg", "valmiki_scene_test_1790916603573.jpg"]
    },
    2: {
        "line1": "यज्ञ से प्रकट हुआ",
        "line2": "दैवीय अमृत!",
        "subhook": "पुत्रकामेष्टि यज्ञ का सच",
        "anchor_pref": ["putrakameshti_purusha.jpg", "scene_23.jpg", "scene_01.jpg"]
    },
    3: {
        "line1": "१२ बजे प्रकट हुए",
        "line2": "साक्षात प्रभु राम!",
        "subhook": "अयोध्या महा-उत्सव",
        "anchor_pref": ["birth_of_princes_lacma.jpg", "birth_of_rama_keshava.webp", "dasharatha_celebrating_princes.jpg", "scene_06.jpg"]
    },
    4: {
        "line1": "१६ वर्ष के राम को",
        "line2": "राक्षस वध की चुनौती!",
        "subhook": "विश्वामित्र का भयंकर क्रोध",
        "anchor_pref": ["vishwamitra_arrival_court.jpg", "scene_29.jpg", "scene_01.jpg"]
    },
    5: {
        "line1": "सिद्धाश्रम महा-यज्ञ",
        "line2": "सुबाहु का महा-संहार!",
        "subhook": "श्री राम का पहला दिव्य बाण",
        "anchor_pref": ["scene_15.jpg", "scene_01.jpg"]
    },
    6: {
        "line1": "स्वर्ग से पृथ्वी पर",
        "line2": "गंगा का महा-अवतरण!",
        "subhook": "भगीरथ की अमर तपस्या",
        "anchor_pref": ["shiva_ganga_descent.jpg", "bhagiratha_tapasya.jpg", "ganga_descent.jpg", "scene_15.jpg", "scene_01.jpg"]
    },
    7: {
        "line1": "पत्थर बनी अहल्या",
        "line2": "प्रभु चरणों से उद्धार!",
        "subhook": "गौतम ऋषि का शाप",
        "anchor_pref": ["ahalya_uddhar.jpg", "scene_20.jpg", "scene_01.jpg"]
    },
    8: {
        "line1": "शिव धनुष भंग",
        "line2": "सीता-राम महाविवाह!",
        "subhook": "परशुराम का भयंकर क्रोध",
        "anchor_pref": ["shiva_dhanush_broken.jpg", "sita_ram_vivah.jpg", "scene_25.jpg"]
    }
}

def generate_master_thumbnail(episode_num=1, line1=None, line2=None):
    """
    Renders the high-CTR 16:9 Landscape thumbnail.
    """
    width, height = 1280, 720
    out_path = os.path.join(thumbnails_dir, f"thumbnail_ep{episode_num:02d}.jpg")

    cfg = EPISODE_THUMBNAIL_CONFIG.get(episode_num, {
        "line1": f"महा-रहस्य Ep {episode_num:02d}",
        "line2": "वाल्मीकि रामायण",
        "subhook": "प्रामाणिक इतिहास",
        "anchor_pref": []
    })

    if line1 is None:
        line1 = cfg["line1"]
    if line2 is None:
        line2 = cfg["line2"]
    subhook_text = cfg.get("subhook", "वाल्मीकि रामायण")

    ep_dir = os.path.join(script_dir, "episodes", f"episode_{episode_num:02d}")
    candidate_arts = [
        os.path.join(ep_dir, "assets", "anchors", pref) for pref in cfg.get("anchor_pref", [])
    ] + [
        os.path.join(ep_dir, "assets", pref) for pref in cfg.get("anchor_pref", [])
    ] + [
        os.path.join(ep_dir, "assets", "scene_23.jpg"),
        os.path.join(ep_dir, "assets", "scene_01.jpg")
    ]

    base_img = None
    for art in candidate_arts:
        if os.path.exists(art):
            try:
                raw = Image.open(art).convert("RGB")
                # If image is very wide, crop to focal area
                rw, rh = raw.size
                if rw > rh * 1.5:
                    crop_box = (0, 0, int(rh * 1.777), rh)
                    raw = raw.crop(crop_box)
                base_img = raw.resize((width, height), Image.Resampling.LANCZOS)
                print(f"[THUMBNAIL] Using base artwork: {os.path.basename(art)}")
                break
            except Exception:
                continue

    if base_img is None:
        base_img = Image.new("RGB", (width, height), color=(20, 12, 10))

    # Apply right-hand dark gradient overlay (Right 45% dark void safe-zone for crisp readability)
    gradient = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    g_draw = ImageDraw.Draw(gradient)

    split_x = int(width * 0.46)
    for x in range(split_x, width):
        alpha = int(248 * ((x - split_x) / (width - split_x)) ** 0.8)
        g_draw.line([(x, 0), (x, height)], fill=(8, 5, 12, alpha))

    base_img = Image.alpha_composite(base_img.convert("RGBA"), gradient).convert("RGB")
    draw = ImageDraw.Draw(base_img)

    font_path = find_devanagari_font()
    print(f"[THUMBNAIL] Loaded Devanagari font: {font_path}")
    try:
        title_font = ImageFont.truetype(font_path, 72) if font_path else ImageFont.load_default()
        sub_font = ImageFont.truetype(font_path, 66) if font_path else ImageFont.load_default()
        badge_font = ImageFont.truetype(font_path, 34) if font_path else ImageFont.load_default()
    except Exception as e:
        print(f"[WARN] Font load issue: {e}")
        title_font = sub_font = badge_font = ImageFont.load_default()

    # Draw Corner Pill Badge: 'EPISODE 02'
    badge_x, badge_y = int(width * 0.56), 60
    badge_w, badge_h = 240, 54
    draw.rounded_rectangle([badge_x, badge_y, badge_x + badge_w, badge_y + badge_h], radius=14, fill=(185, 28, 28))
    badge_text = f"EPISODE {episode_num:02d}"
    draw.text((badge_x + 30, badge_y + 8), badge_text, fill=(255, 255, 255), font=badge_font)

    # Draw Line 1 (Golden Glow): 'यज्ञ से प्रकट हुआ'
    text_x = int(width * 0.52)
    y1 = 195
    draw.text((text_x + 4, y1 + 4), line1, fill=(0, 0, 0), font=title_font)
    draw.text((text_x, y1), line1, fill=(255, 215, 0), font=title_font)

    # Draw Line 2 (Crisp Blood Red / Diamond White): 'दैवीय अमृत!'
    y2 = 315
    draw.text((text_x + 4, y2 + 4), line2, fill=(0, 0, 0), font=sub_font)
    draw.text((text_x, y2), line2, fill=(255, 255, 255), font=sub_font)

    # Sub-hook
    try:
        subhook_font = ImageFont.truetype(font_path, 38)
        draw.text((text_x + 2, 442), subhook_text, fill=(0, 0, 0), font=subhook_font)
        draw.text((text_x, 440), subhook_text, fill=(255, 180, 50), font=subhook_font)
    except Exception:
        pass

    # Channel Tagline / Branding: DIGITAL IMMORTALS
    draw.text((text_x, 555), "DIGITAL IMMORTALS", fill=(218, 165, 32), font=badge_font)

    base_img.save(out_path, "JPEG", quality=98)
    print(f"[OK] Generated High-CTR Master Thumbnail: {out_path} ({width}x{height})")
    return out_path

if __name__ == "__main__":
    ep = 1
    if len(sys.argv) > 2 and sys.argv[1] == "--episode":
        ep = int(sys.argv[2])
    generate_master_thumbnail(ep)

