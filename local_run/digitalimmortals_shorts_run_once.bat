@echo off
title Digital Immortals - Daily Short (run once)
color 0A

echo ==============================================================================
echo   DIGITAL IMMORTALS - DAILY SHORT
echo   Script (Claude) - Voice (Edge TTS) - Scenes (Gemini) - Amar + Captions
echo   Upload: PRIVATE on YouTube. Review in YouTube Studio app, then publish.
echo.
echo   Keys go in: channels\DigitalImmortals\shorts\.env  (see .env.example)
echo   Render only, no upload:  digitalimmortals_shorts_run_once.bat --no-upload
echo ==============================================================================
echo.

cd /d "%~dp0..\channels\DigitalImmortals\shorts"

if not exist ".env" (
  echo [!] .env file missing. Copy .env.example to .env and add your API keys.
  pause
  exit /b 1
)

python -m pip install -q -r requirements.txt
python -m pipeline.main %*

echo.
echo Video folder: %cd%\out
pause
