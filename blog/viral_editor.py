"""
BuzzStormNow - Lead Editor AI & Viral Article Rewriting Engine
==============================================================
Role: Lead Editor for "BuzzStormNow".
Goal: Take standard/dry news updates and rewrite them into "MUST-READ" viral articles
with viralTitle, blogContentHtml, metaDescription, tags, and contextual imagery.
"""

import os
import sys
import re
import json
import urllib.parse
from datetime import datetime

# Ensure UTF-8 output across Windows and Linux
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

from config import EDITORIAL_SETTINGS, BLOG_NAME, BLOG_URL
from image_generator import generate_featured_image_url

VIRAL_HOOK_PATTERNS = [
    "{subject}: What Every Investor Must Know Before Tomorrow's Bell 🔔",
    "Dalal Street Shockwave: {subject} — Golden Opportunity or Red Flag? 🚨",
    "Revealed: The Real Story Behind {subject} & What Comes Next 📈",
    "Big Moves Ahead! {subject}: Key Numbers & Strategy Breakdown 💼",
    "{subject}: 4 Critical Takeaways That Could Impact Your Portfolio 🔥"
]

def clean_subject_line(title):
    """Extracts the core entity or subject from a raw press release or news title."""
    cleaned = title
    # Remove press release boilerplate
    cleaned = re.sub(r"(has informed the exchange regarding|intimation of|outcome of|proceedings of|notice of|circular regarding)", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"(annual general meeting|board meeting|extraordinary general meeting)", "Key Meeting", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"(\|.*|\-.*|\:.*)$", "", cleaned) # strip trailing source attribution
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned[:70]

def craft_viral_title(item):
    """
    Constructs an irresistible, high-CTR headline optimized for Google Discover & social buzz.
    Supports Markets, Tech & AI, Viral Trends, Entertainment, Sports, and Breaking News.
    """
    raw_title = item.get("title", "")
    category = item.get("category", "Trending")
    desc = item.get("description", "")
    combined = f"{raw_title} {desc}".lower()
    core = clean_subject_line(raw_title)
    if len(core) < 15:
        core = raw_title[:65]

    # 1. Technology & AI (strict word boundaries to avoid false positives on words like 'gaining', 'remains')
    if re.search(r"\b(ai|artificial intelligence|chatgpt|openai|nvidia|gemini|deepseek|robot|robotics|quantum|llm)\b", combined):
        return f"AI Shockwave: {core} — The Game-Changing Breakthrough That Changes Everything! 🤖⚡"

    # 2. Viral Content & Internet Sensations
    if any(k in combined for k in ["viral", "crazy", "unbelievable", "shocking", "internet", "social media", "storm"]):
        return f"The Internet Goes Wild: {core} — Why Everyone Is Talking About This! 🌪️🔥"

    # 3. Entertainment & Pop Culture
    if any(k in combined for k in ["movie", "cinema", "actor", "celebrity", "hollywood", "bollywood", "trailer", "box office"]):
        return f"Blockbuster Buzz: {core} — Big Revelations That Have Fans Stunned! 🎬✨"

    # 4. Sports & Athletic Milestones
    if any(k in combined for k in ["cricket", "match", "tournament", "ipl", "world cup", "champion", "sports"]):
        return f"Historic Milestone: {core} — The Masterclass That Left Fans Speechless! 🏆⚡"

    # 5. Financial Multibaggers & Rallies
    if "multibagger" in combined or "400%" in combined or "surge" in combined:
        return f"Multibagger Explosion: {core} — Is The Massive Rally Sustainable? 🚀"
    
    # 6. Corporate Mega Deals & Shakeups
    if "reliance" in combined or "ambani" in combined or "tata" in combined or "deal" in combined:
        return f"Mega Shakeup: {core} — Key Details & Massive Impact Revealed! 💥"
    
    # 7. Market Volatility & Warnings
    if "crash" in combined or "bleed" in combined or "falls" in combined or "plunge" in combined:
        return f"Market Alert: Dalal Street Shudders As Key Support Cracks — 4 Warning Signs To Watch! ⚠️📉"

    # 8. AGMs & Corporate Expansion
    if "agm" in combined or "expansion" in combined or "proceedings" in combined:
        return f"Big Expansion Ahead? {core} Reveals Strategic Masterplan! 💼"

    # 9. Regulatory & Exchange Directives
    if "circular" in combined or "limits" in combined or "sebi" in combined or "rbi" in combined:
        return f"Regulatory Bombshell: New Directives That Will Reshape The Rules! ⚡"

    # 10. IPOs & New Listings
    if "ipo" in combined or "listing" in combined:
        return f"IPO Frenzy: {core} Makes Waves — Key Allotment & Listing Breakdown! 🎯"

    # Default High-CTR Viral Hook
    return f"{core}: What You Need To Know Right Now Before It Goes Viral! 🔥"

def craft_meta_description(viral_title, item):
    """Produces a punchy 140-160 character snippet engineered for high click-through rates."""
    raw_desc = item.get("description", "")
    clean_snippet = re.sub(r"\s+", " ", raw_desc).strip()
    if clean_snippet and len(clean_snippet) > 40:
        snippet = clean_snippet[:110]
        meta = f"{snippet}... Get the complete breakdown and trending analysis on BuzzStormNow."
    else:
        meta = f"Breaking viral story: {viral_title[:90]}. Explore the full analysis, deep dive, and public reaction on BuzzStormNow."
    return meta[:160]

def extract_smart_tags(item):
    """Builds targeted SEO labels for Blogger across all BuzzStormNow niches."""
    raw = f"{item.get('title', '')} {item.get('description', '')}".lower()
    tags = list(EDITORIAL_SETTINGS["default_tags"])
    
    category = item.get("category")
    if category and category not in tags:
        tags.append(category)

    keywords_to_tags = {
        r"\b(ai|artificial intelligence)\b": "Artificial Intelligence",
        r"\b(chatgpt|openai)\b": "Tech & AI",
        r"\btech\b": "Technology",
        r"\bnifty\b": "Stock Market",
        r"\bsensex\b": "Dalal Street",
        r"\breliance\b": "Reliance",
        r"\btata\b": "Tata Group",
        r"\bhero\b": "Automobile",
        r"\bipo\b": "IPO News",
        r"\b(multibagger|rally|surge)\b": "Investing",
        r"\b(movie|cinema|actor)\b": "Entertainment",
        r"\b(cricket|match|ipl)\b": "Sports",
        r"\bcircular\b": "Official Announcements"
    }

    for pattern, tg in keywords_to_tags.items():
        if re.search(pattern, raw) and tg not in tags:
            tags.append(tg)

    return tags[:8]

def build_rich_html_content(viral_title, item, image_url, meta_desc, tags):
    """
    Constructs an ultra-clean, mobile-first, high-converting HTML layout
    matching modern financial publications (Bloomberg/Economic Times style).
    """
    source = item.get("source_name", "Market Feed")
    raw_desc = item.get("description", "Details emerging from exchange disclosures.")
    category = item.get("category", "Market Analysis")
    original_link = item.get("link", "#")
    timestamp_str = datetime.now().strftime("%B %d, %Y")

    # Key highlight bullet points extracted from description
    sentences = [s.strip() for s in re.split(r"[.\n]", raw_desc) if len(s.strip()) > 20]
    if len(sentences) < 3:
        sentences.append(f"Official filing submitted to exchange archives for public review.")
        sentences.append(f"Institutional analysts and retail participants are closely monitoring volatility.")
        sentences.append(f"Key financial ratios and management commentary will dictate market direction.")

    bullets_html = "".join([f"<li style='margin-bottom: 10px; line-height: 1.6;'><strong>{s}</strong></li>" for s in sentences[:4]])

    html_content = f"""<!-- BuzzStormNow Viral Financial Article -->
<div class="buzzstorm-article" style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color: #1e293b; max-width: 800px; margin: 0 auto; line-height: 1.7; font-size: 17px;">

  <!-- Category & Reading Time Header -->
  <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 16px; flex-wrap: wrap;">
    <span style="background: linear-gradient(135deg, #ff4500, #ea580c); color: #ffffff; padding: 4px 12px; border-radius: 9999px; font-size: 12px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px;">
      ⚡ {category}
    </span>
    <span style="color: #64748b; font-size: 14px;">⏱️ 3 Min Read</span>
    <span style="color: #64748b; font-size: 14px;">• Updated: {timestamp_str}</span>
  </div>

  <!-- Lead Viral Hook / Quick Takeaway Box -->
  <div style="background: #fff7ed; border-left: 5px solid #ff4500; border-radius: 8px; padding: 18px 20px; margin-bottom: 24px; box-shadow: 0 2px 10px rgba(255, 69, 0, 0.05);">
    <div style="font-weight: 700; color: #c2410c; margin-bottom: 6px; font-size: 15px; text-transform: uppercase; letter-spacing: 0.5px;">
      🔥 The 60-Second Executive Summary:
    </div>
    <div style="color: #431407; font-size: 16px; font-weight: 500;">
      {meta_desc}
    </div>
  </div>

  <!-- Featured 16:9 Hero Image -->
  <div style="position: relative; margin: 24px 0 32px 0;">
    <img src="{image_url}" alt="{viral_title}" style="width: 100%; height: auto; max-height: 480px; object-fit: cover; border-radius: 12px; box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1); display: block;" />
    <div style="font-size: 12px; color: #94a3b8; text-align: right; margin-top: 6px; font-style: italic;">
      Illustration / Market Visual via BuzzStormNow Creative Studio
    </div>
  </div>

  <!-- Section 1: The Big Picture -->
  <h2 style="font-size: 24px; font-weight: 800; color: #0f172a; margin-top: 36px; margin-bottom: 16px; border-bottom: 2px solid #f1f5f9; padding-bottom: 8px;">
    📊 The Big Picture: What Just Happened?
  </h2>
  <p style="margin-bottom: 20px;">
    In a significant development reported by <strong>{source}</strong>, the Indian financial landscape witnessed key disclosures regarding <em>{item.get('title', 'market developments')}</em>. As trading desks react and order books adjust, retail investors and market observers are scrambling to evaluate the immediate ripple effects across relevant sectors.
  </p>
  <p style="margin-bottom: 20px;">
    With broader indices showing heightened volatility and institutional participants realigning their positions, understanding the fine print of this announcement is paramount for anyone looking to navigate the upcoming trading sessions.
  </p>

  <!-- Section 2: Deep Dive Breakdown -->
  <h2 style="font-size: 24px; font-weight: 800; color: #0f172a; margin-top: 36px; margin-bottom: 16px; border-bottom: 2px solid #f1f5f9; padding-bottom: 8px;">
    🔍 Key Highlights & Numbers You Need to Know
  </h2>
  <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; padding: 22px 26px; margin-bottom: 24px;">
    <ul style="margin: 0; padding-left: 20px; color: #334155;">
      {bullets_html}
    </ul>
  </div>

  <!-- Section 3: Why This Matters For Your Portfolio -->
  <h2 style="font-size: 24px; font-weight: 800; color: #0f172a; margin-top: 36px; margin-bottom: 16px; border-bottom: 2px solid #f1f5f9; padding-bottom: 8px;">
    💡 Why This Matters For Retail Investors & Traders
  </h2>
  <p style="margin-bottom: 20px;">
    Whenever developments of this magnitude surface on Dalal Street, they rarely stay confined to a single stock. Here is how seasoned market participants are dissecting the real impact:
  </p>
  <div style="display: grid; grid-gap: 16px; margin-bottom: 24px;">
    <div style="background: #ffffff; border: 1px solid #e2e8f0; border-left: 4px solid #10b981; border-radius: 8px; padding: 16px;">
      <strong style="color: #065f46; display: block; margin-bottom: 4px;">📈 The Bullish Case:</strong>
      <span style="color: #1e293b; font-size: 15px;">Clear corporate visibility, resolution of pending overhangs, and potential upside triggers if volume accumulation confirms institutional backing.</span>
    </div>
    <div style="background: #ffffff; border: 1px solid #e2e8f0; border-left: 4px solid #ef4444; border-radius: 8px; padding: 16px;">
      <strong style="color: #991b1b; display: block; margin-bottom: 4px;">⚠️ The Caution Zone:</strong>
      <span style="color: #1e293b; font-size: 15px;">Near-term momentum chasing without strict stop-losses can trap retail traders in event of sudden profit booking or broader index headwinds.</span>
    </div>
  </div>

  <!-- Section 4: BuzzStormNow Verdict -->
  <h2 style="font-size: 24px; font-weight: 800; color: #0f172a; margin-top: 36px; margin-bottom: 16px; border-bottom: 2px solid #f1f5f9; padding-bottom: 8px;">
    🎯 The BuzzStormNow Verdict: Tomorrow's Radar
  </h2>
  <p style="margin-bottom: 20px;">
    Keep this counter on your active watchlist for the opening 30 minutes of tomorrow's session. Watch how delivery percentages compare with 10-day moving averages. If key technical pivots hold, this story could continue driving market chatter throughout the week.
  </p>
  <p style="margin-bottom: 24px;">
    <a href="{original_link}" target="_blank" rel="nofollow noopener" style="display: inline-flex; align-items: center; gap: 6px; color: #ff4500; font-weight: 700; text-decoration: none;">
      🔗 Read Official Source Disclosure on {source} &rarr;
    </a>
  </p>

  <!-- Interactive Call to Action & BuzzStormNow Mission -->
  <div style="background: linear-gradient(135deg, #0f172a, #1e293b); color: #f8fafc; border-radius: 12px; padding: 26px 28px; margin: 36px 0; text-align: center; box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.2);">
    <h3 style="margin-top: 0; color: #ffffff; font-size: 21px; font-weight: 800;">💬 Join The Conversation!</h3>
    <p style="color: #cbd5e1; font-size: 15px; margin-bottom: 18px; line-height: 1.6;">
      What is your perspective on this development? Are you seeing this as an unprecedented opportunity or a sign of things to come? Share your thoughts below!
    </p>
    <div style="background: rgba(255, 69, 0, 0.15); border: 1px solid rgba(255, 69, 0, 0.4); border-radius: 8px; padding: 12px 16px; margin-bottom: 14px;">
      <div style="color: #ffedd5; font-size: 13px; line-height: 1.5;">
        🎯 <strong>BuzzStormNow Mission:</strong> Curating viral stories, breaking updates, and cutting-edge insights from around the globe — 24/7.
      </div>
    </div>
    <div style="color: #f59e0b; font-weight: 700; font-size: 14px; letter-spacing: 0.3px;">
      ⚡ Stay ahead of the curve with BuzzStormNow
    </div>
  </div>

  <!-- Regulatory Disclaimer -->
  <div style="background: #f1f5f9; border-radius: 8px; padding: 14px 18px; margin-top: 32px; font-size: 12px; color: #64748b; line-height: 1.5;">
    <strong>Notice:</strong> {EDITORIAL_SETTINGS['disclaimer']}
  </div>

</div>
"""
    return html_content

def transform_news_into_viral_article(item):
    """
    Master function: Takes a raw candidate news item and transforms it
    into a production-ready, viral article bundle.
    """
    viral_title = craft_viral_title(item)
    meta_desc = craft_meta_description(viral_title, item)
    tags = extract_smart_tags(item)
    image_url = generate_featured_image_url(viral_title, item.get("category", "Market Analysis"))
    content_html = build_rich_html_content(viral_title, item, image_url, meta_desc, tags)

    return {
        "viral_title": viral_title,
        "original_title": item.get("title", ""),
        "meta_description": meta_desc,
        "tags": tags,
        "image_url": image_url,
        "content_html": content_html,
        "source_name": item.get("source_name", ""),
        "source_link": item.get("link", ""),
        "category": item.get("category", ""),
        "published_at": item.get("published_at", ""),
        "buzz_score": item.get("buzz_score", 0)
    }


if __name__ == "__main__":
    sample_item = {
        "title": "Hero Motors Limited has informed the Exchange regarding Proceedings of Annual General Meeting held on 30-Sep-2026",
        "description": "Hero Motors Limited has informed the Exchange regarding Proceedings of Annual General Meeting held on 30-Sep-2026. The shareholders approved major capital expenditure, EV expansion roadmap, and record export targets for FY27.",
        "source_name": "NSE Online announcements",
        "category": "Official Announcements",
        "link": "https://nsearchives.nseindia.com/corporate/HML_AGM.pdf"
    }
    art = transform_news_into_viral_article(sample_item)
    print("=== VIRAL ARTICLE CRAFTED ===")
    print(f"Title: {art['viral_title']}")
    print(f"Meta Description: {art['meta_description']}")
    print(f"Tags: {art['tags']}")
    print(f"Image URL: {art['image_url']}")
    print(f"HTML Content Preview: {art['content_html'][:300]}...")
