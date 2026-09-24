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
2. **YouTube Uploads:** Requires a Google Cloud OAuth Client ID (Desktop App / Installed) with scope `https://www.googleapis.com/auth/youtube.upload` (configured in GCP Project `n8n-client-483318`).

### How to Authenticate for YouTube:

#### Option A: 1-Click Local Token Generation (Recommended)
1. Run the local authentication helper:
   ```bash
   python authenticate_youtube.py
   ```
2. Your browser will open. Sign in to your YouTube channel's Google account and click **Allow**.
3. A `token.pickle` file will be generated in your project root.
4. Drag & drop `token.pickle` into the Colab Files panel (left sidebar).
5. Run the notebook cells; it will automatically authenticate using `token.pickle`.

#### Option B: Upload Client Secret to Colab
1. Drag & drop `youtube_client_secret.json` (or `client_secret_*.json`) directly into the Colab Files panel.
2. Run Step 6 cells in the notebook.
3. If running in Colab, click the authorization link printed in the output, accept permissions, and paste the redirected URL or code back into the cell prompt.

