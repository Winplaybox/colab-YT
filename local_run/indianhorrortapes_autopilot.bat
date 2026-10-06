@echo off
title Indian Horror Tapes - 24/7 Continuous Autopilot
color 0A

echo ==============================================================================
echo   INDIAN HORROR TAPES — 24/7 CONTINUOUS AUTOPILOT
echo   Channel: IndianHorrorTapes (Cinematic Horror Shorts)
echo   Mode:    Non-Stop Production, Community Polls ^& Wed/Sun 21:00 IST Scheduling
echo ==============================================================================
echo.

cd /d "%~dp0.."

:loop
echo.
echo ==============================================================================
echo [%date% %time%] [INDIAN HORROR TAPES] Starting Autonomous Episode Cycle...
echo ==============================================================================
echo.

python channels/IndianHorrorTapes/scheduler.py --quality 1080p

echo.
echo [%date% %time%] Cycle completed. Resting for 60 minutes before next check...
echo (Press Ctrl+C at any time to safely exit)
echo.

timeout /t 3600 /nobreak >nul
goto loop
