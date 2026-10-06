@echo off
title Epic Bharat Saga - 24/7 Continuous Autopilot
color 0A

echo ==============================================================================
echo   EPIC BHARAT SAGA — 24/7 CONTINUOUS AUTOPILOT
echo   Channel: EpicBharatSaga (Vedic Mythology Shorts)
echo   Mode:    Non-Stop Daily Mythology Shorts Production ^& 19:00 IST Scheduling
echo ==============================================================================
echo.

cd /d "%~dp0.."

:loop
echo.
echo ==============================================================================
echo [%date% %time%] [EPIC BHARAT SAGA] Starting Autonomous Episode Cycle...
echo ==============================================================================
echo.

python channels/EpicBharatSaga/scheduler.py --mode scheduled --quality 1080p

echo.
echo [%date% %time%] Cycle completed. Resting for 60 minutes before next check...
echo (Press Ctrl+C at any time to safely exit)
echo.

timeout /t 3600 /nobreak >nul
goto loop
