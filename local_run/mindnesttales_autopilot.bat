@echo off
title MindNest Tales - 24/7 Continuous Autopilot
color 0A

echo ==============================================================================
echo   MINDNEST TALES (11-Language Network) — 24/7 CONTINUOUS AUTOPILOT
echo   Network: 11 Localized Global YouTube Channels (51 Stories)
echo   Mode:    Non-Stop Live YouTube Sync, 3D Pixar Animation ^& Multi-Channel Dubbing
echo ==============================================================================
echo.

cd /d "%~dp0.."

:loop
echo.
echo ==============================================================================
echo [%date% %time%] [MINDNEST TALES] Starting Autonomous Network Cycle...
echo ==============================================================================
echo.

python channels/MindNestTales/scheduler.py --story auto --mode short

echo.
echo [%date% %time%] Batch completed. Resting for 30 minutes before next check...
echo (Press Ctrl+C at any time to safely exit)
echo.

timeout /t 1800 /nobreak >nul
goto loop
