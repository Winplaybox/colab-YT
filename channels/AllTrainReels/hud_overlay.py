import os
import sys
import json
import re
import subprocess
from PIL import Image, ImageDraw, ImageFont, ImageOps
import static_ffmpeg

static_ffmpeg.add_paths()

script_dir = 'c:/Users/sagar/Desktop/Project/Colab/colab-YT/channels/AllTrainReels'
font_path = os.path.join(script_dir, 'fonts', 'Poppins-Bold.ttf')

w, h = 1080, 1920

font_brand = ImageFont.truetype(font_path, 34)
font_ep = ImageFont.truetype(font_path, 30)
font_title = ImageFont.truetype(font_path, 36)
font_subtitle = ImageFont.truetype(font_path, 22)
font_vs = ImageFont.truetype(font_path, 28)
font_spec_val = ImageFont.truetype(font_path, 28)
font_spec_lbl = ImageFont.truetype(font_path, 18)
font_sub_main = ImageFont.truetype(font_path, 42)
font_sub_sec = ImageFont.truetype(font_path, 36)
font_watermark = ImageFont.truetype(font_path, 22)

def extract_telemetry_for_story(story_data):
    fact = story_data.get("verified_fact", "")
    title = story_data.get("title", "")
    tagline = story_data.get("tagline", "")
    combined = f"{fact} {title} {tagline}".lower()

    badge1 = ("POWER MONSTER", "CATEGORY")
    badge2 = ("WORLD CLASS", "TRACTION")
    badge3 = ("EXTREME RAIL", "RECORD")

    hp_matches = [int(m.replace(',', '')) for m in re.findall(r'([\d,]+)\s*(?:hp|horsepower)', combined)]
    if hp_matches:
        badge1 = (f"{max(hp_matches):,} HP", "PEAK POWER")
    elif "steam" in combined:
        badge1 = ("~8% THERMAL", "EFFICIENCY")

    loco_match = re.search(r'(wag[-\s]?\d+[a-z]?|wdp[-\s]?\d+[a-z]?|tgv[-\s]?[a-z0-9]+|scmaglev|shinkansen|l0 series|v150)', combined)
    if loco_match:
        badge2 = (loco_match.group(1).upper().replace(" ", "-"), "LOCO CLASS")
    else:
        speed_match = re.search(r'([\d,.]+)\s*(?:km/h|kmph)', combined)
        if speed_match:
            badge2 = (f"{speed_match.group(1)} KM/H", "TOP SPEED")
        elif "electric" in combined:
            badge2 = ("25 kV AC", "CATENARY")

    haul_match = re.search(r'([\d,]+)\s*(?:ton|tonne)', combined)
    if haul_match:
        badge3 = (f"{haul_match.group(1)} TON", "MAX HAULAGE")
    else:
        len_match = re.search(r'([\d,.]+)\s*(?:km|wagon|car)', combined)
        if len_match:
            badge3 = (f"{len_match.group(0).upper()}", "SCALE")
        elif "wag-12" in combined:
            badge3 = ("TWIN-SECTION", "HEAVY FREIGHT")

    return [
        (badge1[0], badge1[1], (255, 195, 0, 255)),    # Gold
        (badge2[0], badge2[1], (56, 189, 248, 255)),   # Cyan
        (badge3[0], badge3[1], (74, 222, 128, 255))    # Green
    ]

def sanitize_subtitle(text):
    if not text:
        return "", ""
    t = text.replace("₹", "Rs ")
    t = re.sub(r'[\u0900-\u097F\U0001F000-\U0001FAFF\u2600-\u27BF]', '', t)
    t = t.replace("\r", "").replace("\t", " ").replace(":", " -")
    t = " ".join(t.split()).strip()
    words = t.split()
    if len(words) <= 5:
        return t, ""
    mid = len(words) // 2
    return " ".join(words[:mid]), " ".join(words[mid:])

def generate_shot_hud(story_data, shot_idx, subtitle_text, out_png_path):
    episode_num = story_data.get("episode_number", 13)
    title = story_data.get("title", "ALL TRAIN REELS")
    clean_title = re.sub(r'[\u0900-\u097F\U0001F000-\U0001FAFF\u2600-\u27BF]', '', title).strip()
    tagline = story_data.get("tagline", "High Speed Rail Marvels")
    clean_tagline = re.sub(r'[\u0900-\u097F\U0001F000-\U0001FAFF\u2600-\u27BF]', '', tagline).strip()

    is_vs = "vs" in clean_title.lower() or story_data.get("format") == "Vs / Comparison" or story_data.get("visual_theme") == "SPLIT_VS_ARENA"

    hud = Image.new('RGBA', (w, h), (10, 16, 30, 255))
    draw = ImageDraw.Draw(hud)

    # Grid
    for y in range(0, h, 60):
        draw.line([(0, y), (w, y)], fill=(16, 26, 46, 255), width=1)
    for x in range(0, w, 60):
        draw.line([(x, 0), (x, h)], fill=(16, 26, 46, 255), width=1)

    # Header Bar (y=0 to 110)
    draw.rectangle([(0, 0), (w, 110)], fill=(11, 31, 58, 255))
    draw.rectangle([(0, 110), (w, 114)], fill=(255, 195, 0, 255))
    draw.rectangle([(0, 114), (w, 118)], fill=(230, 57, 70, 255))
    draw.text((45, 36), 'ALL TRAIN REELS', font=font_brand, fill=(255, 195, 0, 255))
    draw.ellipse([(380, 48), (394, 62)], fill=(239, 68, 68, 255))
    draw.text((406, 44), 'LIVE ARCHIVE', font=font_subtitle, fill=(148, 163, 184, 255))
    draw.text((w - 260, 38), f'EPISODE #{episode_num:02d}', font=font_ep, fill=(241, 245, 249, 255))

    # Topic Banner (y=130 to 285)
    draw.rounded_rectangle([(40, 130), (w - 40, 285)], radius=18, fill=(15, 23, 42, 255), outline=(30, 58, 138, 255), width=2)
    draw.rounded_rectangle([(40, 130), (52, 285)], radius=6, fill=(255, 195, 0, 255))
    
    # Title display with dynamic font sizing to prevent truncation
    title_display = clean_title
    if len(title_display) > 36:
        t_font = ImageFont.truetype(font_path, 28)
    elif len(title_display) > 28:
        t_font = ImageFont.truetype(font_path, 32)
    else:
        t_font = font_title
    draw.text((70, 146), title_display, font=t_font, fill=(255, 255, 255, 255))
    draw.text((70, 194), clean_tagline[:45], font=font_subtitle, fill=(203, 213, 225, 255))

    if is_vs:
        draw.rounded_rectangle([(w - 170, 148), (w - 65, 204)], radius=12, fill=(220, 38, 38, 255), outline=(255, 195, 0, 255), width=2)
        draw.text((w - 138, 158), 'VS', font=font_vs, fill=(255, 255, 255, 255))

    # Category pill
    draw.rounded_rectangle([(70, 234), (320, 270)], radius=8, fill=(30, 41, 59, 255), outline=(56, 189, 248, 255), width=1)
    draw.polygon([(82, 256), (92, 242), (88, 252), (98, 252), (86, 266), (88, 256)], fill=(255, 195, 0, 255))
    draw.text((105, 240), 'LOCOMOTIVE CLASH' if is_vs else 'RAILWAY MARVEL', font=font_subtitle, fill=(56, 189, 248, 255))

    # Transparent Hero Screen Window (y=305 to 1175, x=40 to 1040)
    card_x1, card_y1 = 40, 305
    card_w, card_h = 1000, 870
    for py in range(card_y1, card_y1 + card_h):
        for px in range(card_x1, card_x1 + card_w):
            hud.putpixel((px, py), (0, 0, 0, 0))

    draw = ImageDraw.Draw(hud)
    draw.rounded_rectangle([(card_x1, card_y1), (card_x1 + card_w, card_y1 + card_h)], radius=18, outline=(56, 189, 248, 255), width=3)

    b_len = 40
    draw.line([(card_x1 + 10, card_y1 + 10), (card_x1 + 10 + b_len, card_y1 + 10)], fill=(255, 195, 0, 255), width=4)
    draw.line([(card_x1 + 10, card_y1 + 10), (card_x1 + 10, card_y1 + 10 + b_len)], fill=(255, 195, 0, 255), width=4)
    draw.line([(card_x1 + card_w - 10, card_y1 + 10), (card_x1 + card_w - 10 - b_len, card_y1 + 10)], fill=(255, 195, 0, 255), width=4)
    draw.line([(card_x1 + card_w - 10, card_y1 + 10), (card_x1 + card_w - 10, card_y1 + 10 + b_len)], fill=(255, 195, 0, 255), width=4)
    draw.line([(card_x1 + 10, card_y1 + card_h - 10), (card_x1 + 10 + b_len, card_y1 + card_h - 10)], fill=(255, 195, 0, 255), width=4)
    draw.line([(card_x1 + 10, card_y1 + card_h - 10), (card_x1 + 10, card_y1 + card_h - 10 - b_len)], fill=(255, 195, 0, 255), width=4)
    draw.line([(card_x1 + card_w - 10, card_y1 + card_h - 10), (card_x1 + card_w - 10 - b_len, card_y1 + card_h - 10)], fill=(255, 195, 0, 255), width=4)
    draw.line([(card_x1 + card_w - 10, card_y1 + card_h - 10), (card_x1 + card_w - 10, card_y1 + card_h - 10 - b_len)], fill=(255, 195, 0, 255), width=4)

    # Telemetry Strip (y=1195 to 1295)
    telemetry = extract_telemetry_for_story(story_data)
    badge_w = (w - 80 - 30) // 3
    for i, (val, lbl, color) in enumerate(telemetry):
        bx1 = 40 + i * (badge_w + 15)
        bx2 = bx1 + badge_w
        by1, by2 = 1195, 1295
        draw.rounded_rectangle([(bx1, by1), (bx2, by2)], radius=14, fill=(15, 23, 42, 255), outline=(30, 41, 59, 255), width=2)
        draw.rounded_rectangle([(bx1 + 12, by1 + 6), (bx1 + badge_w - 12, by1 + 9)], radius=2, fill=color)
        draw.text((bx1 + 16, by1 + 18), val, font=font_spec_val, fill=color)
        draw.text((bx1 + 16, by1 + 58), lbl, font=font_spec_lbl, fill=(148, 163, 184, 255))

    # Kinetic Subtitle Pill (y=1320 to 1530)
    sub_x1, sub_y1 = 40, 1320
    sub_x2, sub_y2 = w - 40, 1530
    draw.rounded_rectangle([(sub_x1, sub_y1), (sub_x2, sub_y2)], radius=24, fill=(11, 23, 42, 255), outline=(255, 195, 0, 255), width=2)

    line1, line2 = sanitize_subtitle(subtitle_text)
    if line1:
        bb1 = draw.textbbox((0, 0), line1, font=font_sub_main)
        tw1 = bb1[2] - bb1[0]
        pos_y_line1 = sub_y1 + 25 if line2 else sub_y1 + 60
        draw.text(((w - tw1) // 2, pos_y_line1), line1, font=font_sub_main, fill=(255, 215, 0, 255))
    if line2:
        bb2 = draw.textbbox((0, 0), line2, font=font_sub_sec)
        tw2 = bb2[2] - bb2[0]
        draw.text(((w - tw2) // 2, sub_y1 + 95), line2, font=font_sub_sec, fill=(255, 255, 255, 255))

    # Watermark
    draw.rounded_rectangle([(70, 1560), (w - 70, 1615)], radius=14, fill=(15, 23, 42, 255), outline=(30, 41, 59, 255), width=1)
    draw.ellipse([(95, 1581), (107, 1593)], fill=(239, 68, 68, 255))
    draw.text((122, 1575), '@AllTrainReels • Subscribe for Daily World Rail Records', font=font_watermark, fill=(203, 213, 225, 255))

    hud.save(out_png_path, 'PNG')
    return out_png_path

print("HUD helper ready!")
