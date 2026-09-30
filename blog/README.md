# ⚡ BuzzStormNow — Autonomous Viral Blog Automation Engine

Automated news intelligence, Lead Editor AI transformation, and multi-post publishing engine for **[BuzzStormNow](https://buzzstormnow.blogspot.com)** (`Blog ID: 7128783356419391680`).

---

## 🎯 High-Engagement Strategy: 3 Optimal Daily Posts

To maximize viral traffic, Google Discover impressions, and user engagement on Dalal Street / Indian business news, the engine publishes across **3 high-intent daily windows**:

| Slot | Target Time (IST) | Target Time (UTC) | Focus & Audience Persona |
| :--- | :---: | :---: | :--- |
| **1. Morning Bell & Pre-Market Setup** | **08:15 AM** | 02:45 UTC | Overnight cues, Gift Nifty, global cues, key stocks in radar. Read by traders and commuters before 09:15 AM opening bell. |
| **2. Mid-Day Movers & Board Actions** | **01:00 PM** | 07:30 UTC | Breaking board meeting outcomes, AGM revelations, massive volume surges. Read during lunch breaks (12:30 - 01:30 PM). |
| **3. Closing Bell Wrap & Tomorrow's Radar** | **05:30 PM** | 12:00 UTC | Day's market scorecard, NSE/SEBI circulars, FII/DII action, tomorrow's watch list. Read during evening commutes and portfolio checks. |

---

## 📡 Live Ingestion Feeds Monitored

1. **Economic Times Markets**: `https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms`
2. **NSE Online Announcements**: `https://nsearchives.nseindia.com/content/RSS/Online_announcements.xml`
3. **NSE Board Meetings**: `https://nsearchives.nseindia.com/content/RSS/Board_Meetings.xml`
4. **NSE Circulars**: `https://nsearchives.nseindia.com/content/RSS/Circulars.xml`
5. **Livemint Markets & Corporate News**: `https://www.livemint.com/rss/markets`
6. **Economic Times Top Stories**: `https://economictimes.indiatimes.com/rssfeedstopstories.cms`

---

## ✍️ The Lead Editor AI Transformation

Every raw news update passes through the **Lead Editor Engine** (`blog/viral_editor.py`), which constructs:
- **`viralTitle`**: Punchy, curiosity-inducing, SEO-rich title with high-CTR power words (e.g. *"Multibagger Explosion: SME IPO Multibaggers — Is The Massive Rally Sustainable? 🚀"*).
- **`metaDescription`**: 150-160 character snippet engineered for Google Discover / SERP mobile CTR.
- **`tags`**: Targeted categories matching Blogger labels (`Stock Market`, `Market Analysis`, `NSE`, `IPO News`, `BuzzStormNow`).
- **`imageUrl`**: Instant 16:9 ultra-HD financial illustration (glowing candlesticks, bull vs bear, modern corporate skylines) rendered via high-speed CDN.
- **`blogContentHtml`**: Responsive, mobile-first article with:
  - 60-Second Executive Summary callout box
  - 16:9 Featured Hero Banner
  - Section 1: The Big Picture (What Just Happened)
  - Section 2: Deep Dive Breakdown (Key Numbers & Highlights)
  - Section 3: Why This Matters (Bull Case vs Caution Zone)
  - Section 4: BuzzStormNow Verdict & Tomorrow's Radar
  - Direct Source Attribution Link
  - Interactive Reader Poll / Discussion CTA
  - Statutory SEBI/Educational Disclaimer

---

## 📁 Project Architecture

```text
blog/
├── config.py                 # Feeds list, posting times, blog ID, editorial tone, categories
├── rss_parser.py             # Feed ingestion with deduplication & BuzzScore ranking
├── viral_editor.py           # Lead Editor rewriting engine (viralTitle, HTML, metaDesc, tags)
├── image_generator.py        # 16:9 ultra-HD featured imagery & thumbnail generator
├── blogger_publisher.py      # Google Blogger API v3 client (Publish, Schedule, Drafts)
├── authenticate_blogger.py   # One-click OAuth authorization for Blogger API
├── scheduler.py              # Master runner (auto slot detection, batch, preview, post_now)
├── data/
│   ├── published_archive.json # Deduplication archive (prevents repeating stories)
│   └── drafts/               # Local HTML previews & JSON bundles
└── credentials/
    └── blogger_token.json    # OAuth credentials for Blogger API
```

---

## 🚀 Quick Start & Usage

### 1. Preview a Post Locally (Dry Run)
Test how the engine ingests fresh news and generates an article preview:
```bash
python blog/scheduler.py preview
```
Open the generated `.html` file inside `blog/data/drafts/` in any browser to inspect the layout!

### 2. Authenticate Blogger API (One-Time Setup)
Run the authenticator locally:
```bash
python blog/authenticate_blogger.py
```
This opens your browser. Log in with the Google account managing `buzzstormnow.blogspot.com`. It will generate `blog/credentials/blogger_token.json`.

### 3. Publish an Instant Post
```bash
python blog/scheduler.py post_now
```

### 4. Run Daily 3-Post Batch
```bash
python blog/scheduler.py batch 3
```

---

## 🤖 Autonomous GitHub Actions CI/CD

The workflow `.github/workflows/buzzstorm_blog_scheduler.yml` runs automatically 3 times a day:
- **02:45 UTC (08:15 AM IST)**: Morning Bell Post
- **07:30 UTC (01:00 PM IST)**: Mid-Day Movers Post
- **12:00 UTC (05:30 PM IST)**: Closing Wrap Post

### Setting Up GitHub Repository Secrets:
1. Go to **Settings > Secrets and variables > Actions**.
2. Add `BLOGGER_TOKEN_JSON`: Paste the JSON content of your `blog/credentials/blogger_token.json`.
3. (Optional) Add `BLOGGER_CLIENT_SECRET_JSON`: If you want to customize the OAuth client secret.
