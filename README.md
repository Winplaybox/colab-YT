# 🚀 Multi-Channel YouTube Automation & Viral Engine (2026 - 2030)

Autonomous, multi-channel video production and scheduling platform designed for Google Colab and GitHub Actions. Built to scale brand-new YouTube channels into multi-million-view empires using mathematical SEO, psychological curiosity hooks, and high-retention 4K/8K rendering.

---

## 📂 Multi-Channel Architecture

Every channel operates as an independent, modular package inside the `channels/` directory:

```text
colab-YT/
├── channels/
│   ├── TigerVlogs-2026/             <-- https://www.youtube.com/@TigerVlogs-2026
│   │   ├── config.json              <-- Channel branding, slots, release times
│   │   ├── engine.py                <-- 4K/8K Long-form generator & 9:16 Short remixer
│   │   ├── scheduler.py             <-- Autonomous daily batch runner
│   │   ├── youtube_automation_pipeline.ipynb <-- Colab notebook for this channel
│   │   ├── token.json               <-- Channel OAuth credentials (gitignored)
│   │   └── youtube_client_secret.json <-- GCP OAuth secret (gitignored)
│   │
│   ├── [Next-Channel-2]/            <-- Add new channels in 2 minutes
│   └── [Next-Channel-3]/
│
├── .github/workflows/
│   └── daily_youtube_scheduler.yml  <-- 100% Zero-Touch Daily Cron Runner (2026 - 2030)
├── README.md
```

---

## ⚡ 100% Zero-Touch Autonomous Cron (GitHub Actions)

The repository includes a perpetual GitHub Actions Cron job (`.github/workflows/daily_youtube_scheduler.yml`) that runs **every single day at 00:00 UTC (5:30 AM IST)**:

1. **Wakes up autonomously** in GitHub's cloud environment.
2. **Generates the daily 3-video slate**:
   - **Slot 1 (1:00 PM IST / 07:30 UTC):** 100% Original 16:9 Food Investigation Video (4K UHD, real Wikipedia photography, natural Hinglish speech).
   - **Slot 2 (6:00 PM IST / 12:30 UTC):** 4K Ultra-Vertical Street Food Short (1.05x audio tempo/pitch, +20% saturation, kinetic banner).
   - **Slot 3 (8:45 PM IST / 15:15 UTC):** 100% Original 16:9 Food Science Video (4K UHD, Hinglish speech).
3. **Uploads and schedules** to YouTube Creator Studio with `privacyStatus='private'` and `publishAt`.
4. **Updates the queue** and commits state back to GitHub.

### Setting Up GitHub Secrets (One-Time Setup):
To let GitHub Actions upload on your behalf:
1. Go to your GitHub repository -> **Settings** -> **Secrets and variables** -> **Actions**.
2. Click **New repository secret**:
   - `YOUTUBE_TOKEN_JSON`: Paste the entire content of `channels/TigerVlogs-2026/token.json`.
   - `YOUTUBE_CLIENT_SECRET_JSON`: Paste the entire content of `channels/TigerVlogs-2026/youtube_client_secret.json`.

---

## 🎬 4K / 8K Master Visual Quality

To bypass YouTube's heavy AVC1 compression and force YouTube to assign the elite **VP09 / AV01 codec**:
- **Long-Form Videos:** Rendered at `3840x2160` (4K UHD) with Lanczos filtering and unsharp masking.
- **Shorts:** Rendered at `2160x3840` (4K Ultra-Vertical).
- **Encoding Profile:** `libx264 -crf 18 -preset fast -pix_fmt yuv420p` (Master broadcast visual fidelity).

---

## ➕ How to Add a New Channel in 2 Minutes

1. Duplicate `channels/TigerVlogs-2026/` to `channels/<YourNewChannelName>/`.
2. Edit `config.json` with the new channel's name, brand email, and release slots.
3. Place the new channel's `youtube_client_secret.json` in that folder and run `python authenticate_youtube.py` to generate `token.json`.
4. Done! The GitHub Actions scheduler and Colab notebooks will automatically detect and run the new channel.
