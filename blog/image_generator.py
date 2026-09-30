"""
BuzzStormNow - Viral Featured Image & Thumbnail Generator
=========================================================
Generates 16:9 ultra-crisp financial & business visuals optimized for Google Discover,
Blogger post thumbnails, and in-article hero cards.
"""

import os
import re
import urllib.parse
from PIL import Image, ImageDraw, ImageFont

script_dir = os.path.dirname(os.path.abspath(__file__))

THEME_KEYWORDS_MAP = {
    "bull_rally": ["surge", "rally", "soar", "jump", "record", "high", "multibagger", "400%", "gain"],
    "bear_crash": ["crash", "fall", "plunge", "bleed", "slump", "loss", "tumble", "bleed", "down"],
    "corporate_deal": ["acquisition", "merger", "deal", "ambani", "tata", "reliance", "crore", "billion", "stake", "buyout"],
    "regulatory_sebi": ["sebi", "rbi", "penalty", "circular", "warning", "rules", "order", "board", "agm"],
    "ipo_market": ["ipo", "listing", "sme", "allotment", "subscription", "shares"],
    "macro_rates": ["inflation", "yields", "bond", "interest", "rate", "fed", "central bank"]
}

def determine_visual_theme(title, description):
    """Categorizes the news into visual motifs to generate context-matched imagery."""
    combined = f"{title} {description}".lower()
    for theme, keywords in THEME_KEYWORDS_MAP.items():
        if any(kw in combined for kw in keywords):
            return theme
    return "general_market"

def generate_featured_image_url(title, category="Market Analysis"):
    """
    Constructs an ultra-crisp 16:9 8K-styled financial banner URL using Flux/Pollinations CDN.
    Guaranteed high-speed, direct CDN URL that Blogger parses seamlessly for open-graph and thumbnails.
    """
    theme = determine_visual_theme(title, category)

    prompts = {
        "bull_rally": "hyper-realistic stock market bull charging forward, glowing neon green candlestick charts, 3D golden coins explosion, cinematic lighting, ultra-detailed 8k, bloom effect, octane render, financial news hero banner",
        "bear_crash": "dramatic stock market crash, glowing red candlestick charts plunging down, financial district in dark stormy atmosphere, digital market red numbers, 8k resolution, cinematic photorealistic lighting",
        "corporate_deal": "modern high-tech glass skyscraper boardroom overlooking financial district at sunset, golden handshake silhouettes, luxury corporate architecture, 8k photorealistic, Bloomberg style",
        "regulatory_sebi": "official financial regulatory modern headquarters, digital security shield, holographic stock market data streams, blue and gold corporate aesthetic, hyper-realistic 8k",
        "ipo_market": "massive stock exchange opening bell ceremony, glowing green ticker tape, IPO launch celebration, digital trading floor screens, cinematic lighting, 8k render",
        "macro_rates": "central bank gold vault with glowing digital treasury bond charts, global currency exchange holographic map, dramatic lighting, financial market masterpiece 8k",
        "general_market": "futuristic modern stock exchange trading desk, dual curved monitors displaying vibrant market charts, depth of field, 8k photorealism, editorial finance hero image"
    }

    base_prompt = prompts.get(theme, prompts["general_market"])
    # Clean title for clean URL seed
    clean_seed = abs(hash(title)) % 999999
    encoded_prompt = urllib.parse.quote(base_prompt)
    
    # Pollinations Flux endpoint (fast, high-resolution 1280x720 16:9, no watermark)
    image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1280&height=720&model=flux&seed={clean_seed}&nologo=true"
    return image_url

def create_local_fallback_banner(title, category, output_path):
    """Generates an elegant local 1280x720 fallback banner if needed."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    width, height = 1280, 720
    img = Image.new("RGB", (width, height), color=(15, 23, 42)) # Deep Slate Navy
    draw = ImageDraw.Draw(img)

    # Gradient highlight at top-left
    for r in range(400, 0, -10):
        alpha = int(25 * (r / 400))
        draw.ellipse([-100, -100, r * 2, r * 2], fill=(255, 69, 0, alpha)) # Brand orange accent

    # Category Pill
    draw.rounded_rectangle([80, 80, 320, 130], radius=12, fill=(255, 69, 0))
    draw.text((105, 92), f"⚡ {category.upper()}", fill=(255, 255, 255))

    # Site Branding
    draw.text((80, 620), "BUZZSTORMNOW", fill=(245, 158, 11))
    draw.text((250, 620), "| VIRAL MARKET INTELLIGENCE", fill=(148, 163, 184))

    # Gold separator line
    draw.line([(80, 150), (1200, 150)], fill=(245, 158, 11), width=3)

    # Title text (wrapped)
    words = title.split()
    lines = []
    curr = []
    for w in words:
        curr.append(w)
        if len(" ".join(curr)) > 38:
            lines.append(" ".join(curr[:-1]))
            curr = [w]
    if curr:
        lines.append(" ".join(curr))

    y = 220
    for line in lines[:4]:
        draw.text((80, y), line, fill=(255, 255, 255))
        y += 60

    img.save(output_path, "JPEG", quality=90)
    return output_path


if __name__ == "__main__":
    test_title = "Hero Motors AGM Announcement: Major Expansion & Investor Secrets Revealed!"
    url = generate_featured_image_url(test_title, "Official Announcements")
    print(f"Generated Featured Image URL:\n{url}")
