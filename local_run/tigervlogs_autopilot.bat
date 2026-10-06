@echo off
title Tiger Vlogs - 24/7 Continuous Autopilot
color 0A

echo ==============================================================================
echo   TIGER VLOGS (@TigerVlogs-2026) — 24/7 CONTINUOUS AUTOPILOT
echo   Channel: TigerVlogs-2026 (Food Investigation ^& Street Food Shorts)
echo   Mode:    Non-Stop Automated Daily 3-Video Scheduling Loop
echo ==============================================================================
echo.

cd /d "%~dp0.."

:loop
echo.
echo ==============================================================================
echo [%date% %time%] [TIGER VLOGS] Starting Autonomous Batch Cycle...
echo ==============================================================================
echo.

python channels/TigerVlogs-2026/scheduler.py

echo.
echo [%date% %time%] Batch completed. Resting for 60 minutes before next check...
echo (Press Ctrl+C at any time to safely exit)
echo.

timeout /t 3600 /nobreak >nul
goto loop
