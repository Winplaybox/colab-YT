"""
BuzzStormNow - Google Blogger API v3 Publisher & Scheduler
==========================================================
Publishes and schedules high-CTR viral posts to https://buzzstormnow.blogspot.com
Blog ID: 7128783356419391680
"""

import os
import sys
import json
import re
from datetime import datetime, timezone

# Ensure UTF-8 output across Windows and Linux
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

from config import BLOG_ID, BLOG_NAME, BLOG_URL, CREDENTIALS_DIR, DRAFTS_DIR

try:
    from googleapiclient.discovery import build
    from google.oauth2.credentials import Credentials
    import google.auth.transport.requests
    HAS_GOOGLE_CLIENT = True
except ImportError:
    HAS_GOOGLE_CLIENT = False

SCOPES = ["https://www.googleapis.com/auth/blogger"]

def get_blogger_service():
    """
    Authenticates and builds Google Blogger API v3 client.
    Checks environment variables and local credentials directory.
    """
    if not HAS_GOOGLE_CLIENT:
        print("Notice: google-api-python-client not installed in this environment.")
        return None

    token_candidates = [
        os.path.join(CREDENTIALS_DIR, "blogger_token.json"),
        os.path.join(CREDENTIALS_DIR, "token.json"),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "token.json"),
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "token.json")
    ]

    token_path = None
    # 1. Check environment variable
    env_token = os.environ.get("BLOGGER_TOKEN_JSON", "").strip()
    if env_token:
        os.makedirs(CREDENTIALS_DIR, exist_ok=True)
        dest = os.path.join(CREDENTIALS_DIR, "blogger_token.json")
        with open(dest, "w", encoding="utf-8") as f:
            f.write(env_token)
        token_path = dest
    else:
        for cand in token_candidates:
            if os.path.exists(cand):
                token_path = cand
                break

    if not token_path or not os.path.exists(token_path):
        return None

    try:
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        # Refresh if expired
        if creds.expired and creds.refresh_token:
            creds.refresh(google.auth.transport.requests.Request())
            with open(token_path, "w", encoding="utf-8") as f:
                f.write(creds.to_json())
        
        service = build("blogger", "v3", credentials=creds)
        return service
    except Exception as e:
        print(f"Blogger authentication notice: {e}")
        return None

def slugify(text):
    """Converts a title into a clean filename slug."""
    text = re.sub(r"[^a-zA-Z0-9\s-]", "", text).strip().lower()
    return re.sub(r"[\s-]+", "_", text)[:60]

def save_local_draft(article_data):
    """Saves a rich JSON and standalone HTML copy of the post locally."""
    os.makedirs(DRAFTS_DIR, exist_ok=True)
    slug = slugify(article_data.get("viral_title", "article"))
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_name = f"{timestamp}_{slug}"

    json_path = os.path.join(DRAFTS_DIR, f"{base_name}.json")
    html_path = os.path.join(DRAFTS_DIR, f"{base_name}.html")

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(article_data, f, indent=2, ensure_ascii=False)

    # Standalone HTML for direct previewing in browser
    full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{article_data.get('viral_title')}</title>
  <meta name="description" content="{article_data.get('meta_description')}">
  <meta name="keywords" content="{', '.join(article_data.get('tags', []))}">
  <style>
    body {{ background: #f8fafc; margin: 0; padding: 24px; font-family: -apple-system, BlinkMacSystemFont, sans-serif; }}
    .preview-container {{ max-width: 840px; margin: 0 auto; background: #ffffff; padding: 36px 40px; border-radius: 16px; box-shadow: 0 4px 20px rgba(0,0,0,0.06); }}
    .admin-bar {{ background: #0f172a; color: #f8fafc; padding: 12px 18px; border-radius: 8px; margin-bottom: 24px; font-size: 13px; display: flex; justify-content: space-between; align-items: center; }}
  </style>
</head>
<body>
  <div class="preview-container">
    <div class="admin-bar">
      <span>⚡ <strong>BuzzStormNow Draft Preview</strong></span>
      <span>Target Blog: {BLOG_NAME} ({BLOG_ID})</span>
    </div>
    <h1 style="font-size: 32px; font-weight: 800; color: #0f172a; line-height: 1.25; margin-bottom: 20px;">
      {article_data.get('viral_title')}
    </h1>
    {article_data.get('content_html')}
  </div>
</body>
</html>"""

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(full_html)

    return html_path

def publish_article_to_blogger(article_data, is_draft=False, publish_date_iso=None):
    """
    Submits the viral article to Blogger API v3.
    Supports instant publish, draft creation, and scheduled releases.
    """
    service = get_blogger_service()

    if not service:
        # Save local draft fallback
        html_file = save_local_draft(article_data)
        print(f"ℹ️ Blogger API credentials not linked yet. Draft saved locally:")
        print(f"   -> {html_file}")
        return {
            "status": "LOCAL_DRAFT_SAVED",
            "post_id": None,
            "url": f"file:///{html_file.replace(os.sep, '/')}",
            "title": article_data.get("viral_title")
        }

    post_body = {
        "kind": "blogger#post",
        "blog": {"id": BLOG_ID},
        "title": article_data.get("viral_title"),
        "content": article_data.get("content_html"),
        "labels": article_data.get("tags", []),
        "customMetaData": article_data.get("meta_description")
    }

    if publish_date_iso:
        post_body["published"] = publish_date_iso

    try:
        print(f"🚀 Publishing to Blogger: '{article_data.get('viral_title')}'...")
        req = service.posts().insert(
            blogId=BLOG_ID,
            body=post_body,
            isDraft=is_draft
        )
        res = req.execute()
        post_id = res.get("id")
        post_url = res.get("url")
        status_label = "SCHEDULED" if publish_date_iso else ("DRAFT" if is_draft else "PUBLISHED")

        print(f"✅ SUCCESS: Post {status_label}! ID: {post_id}")
        print(f"🌐 URL: {post_url}")

        return {
            "status": status_label,
            "post_id": post_id,
            "url": post_url,
            "title": article_data.get("viral_title")
        }
    except Exception as e:
        print(f"❌ Blogger publish error: {e}")
        # Always preserve as local draft on any network error
        html_file = save_local_draft(article_data)
        return {
            "status": "ERROR_SAVED_LOCAL",
            "error": str(e),
            "post_id": None,
            "url": f"file:///{html_file.replace(os.sep, '/')}",
            "title": article_data.get("viral_title")
        }


if __name__ == "__main__":
    print("Testing Blogger publisher module...")
    svc = get_blogger_service()
    if svc:
        print("Connected to Google Blogger API v3!")
        try:
            blog_info = svc.blogs().get(blogId=BLOG_ID).execute()
            print(f"Blog Name: {blog_info.get('name')}")
            print(f"Blog URL: {blog_info.get('url')}")
            print(f"Total Posts: {blog_info.get('posts', {}).get('totalItems')}")
        except Exception as e:
            print(f"Blog query note: {e}")
    else:
        print("No Blogger OAuth token detected yet. Local fallback is ready.")
