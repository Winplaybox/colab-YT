"""BuzzStormNow - Telegram Channel Auto-Broadcaster
==================================================
Broadcasts newly published Blogger articles (headline, summary, image, and clickable link)
to the @buzzstormnow Telegram channel right after publication.
"""
from __future__ import annotations

import html
import os
import re
import requests


def _strip_html(raw: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", raw or ""))).strip()


def broadcast_post(
    title: str,
    url: str,
    summary: str = "",
    image_url: str = "",
    category: str = "",
    *,
    bot_token: str | None = None,
    chat_id: str | None = None,
) -> bool:
    """Post a newly published article to Telegram. Returns True on success, False if skipped/failed."""
    token = (bot_token or os.environ.get("TELEGRAM_BOT_TOKEN", "")).strip()
    channel = (chat_id or os.environ.get("TELEGRAM_CHAT_ID", "")).strip()
    if not token or not channel or not url:
        return False

    clean_title = html.escape(_strip_html(title))
    clean_summary = html.escape(_strip_html(summary)[:260])
    tag = re.sub(r"[^A-Za-z0-9]", "", category or "")
    hashtags = f"#{tag} #BuzzStormNow #IndiaNews" if tag else "#BuzzStormNow #IndiaNews"

    caption_parts = [f"<b>{clean_title}</b>"]
    if clean_summary:
        caption_parts.append(clean_summary)
    caption_parts.append(f'Read full story: <a href="{html.escape(url)}">{html.escape(url)}</a>')
    caption_parts.append(hashtags)
    caption = "\n\n".join(caption_parts)

    base = f"https://api.telegram.org/bot{token}"
    try:
        if image_url and image_url.startswith("http"):
            resp = requests.post(
                f"{base}/sendPhoto",
                json={
                    "chat_id": channel,
                    "photo": image_url,
                    "caption": caption[:1024],
                    "parse_mode": "HTML",
                },
                timeout=15,
            )
            if resp.ok and resp.json().get("ok"):
                return True

        resp = requests.post(
            f"{base}/sendMessage",
            json={
                "chat_id": channel,
                "text": caption[:4096],
                "parse_mode": "HTML",
                "disable_web_page_preview": False,
            },
            timeout=15,
        )
        return bool(resp.ok and resp.json().get("ok"))
    except Exception as exc:
        print(f"⚠️ Telegram broadcast skipped due to error: {exc}")
        return False
