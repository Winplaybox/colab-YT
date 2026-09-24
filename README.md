# Colab YouTube Automation Pipeline

Google Colab pipeline to download YouTube videos, re-brand and enhance metadata (titles, descriptions, tags), and automatically upload them to YouTube with status tracking in Google Sheets.

## Notebooks

- `youtube_automation_pipeline.ipynb`: Main automation notebook.
- `Untitled0.ipynb`: Working copy of the notebook.

## Workflow Overview

1. **Google Sheets Integration:** Connects to Google Sheets via `gspread` to fetch video queues and track upload statuses.
2. **Video Downloader:** Downloads target videos using `yt-dlp`.
3. **Metadata Enhancement:** Cleans up titles, applies description templates, and optimizes tags/keywords.
4. **YouTube Data API Upload:** Uploads videos directly to YouTube using OAuth 2.0.
5. **Sheet Sync:** Updates the `IsUploaded` column in Google Sheets to `TRUE` after successful uploads and removes local temporary files.

## Setup & Authentication

1. **Google Sheets:** Authenticate via `google.colab.auth.authenticate_user()`.
2. **YouTube Uploads:** Requires a Google Cloud OAuth Client ID (Desktop App) with scope `https://www.googleapis.com/auth/youtube.upload`.
   - Place `youtube_client_secret.json` or generated `token.pickle` in the notebook root.
