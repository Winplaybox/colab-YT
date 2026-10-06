@echo off
title Digital Immortals - 24/7 Continuous Autopilot
color 0A

echo ==============================================================================
echo   DIGITAL IMMORTALS (@DigitalImmortals) — 24/7 CONTINUOUS AUTOPILOT
echo   Series: Valmiki Ramayana Definitive Saga (54 Episodes)
echo   Mode:   Non-Stop Production, NVENC Rendering ^& YouTube Scheduling
echo ==============================================================================
echo.

cd /d "%~dp0.."

:loop
echo.
echo ==============================================================================
echo [%date% %time%] [DIGITAL IMMORTALS] Starting Autonomous Cycle...
echo ==============================================================================
echo.

python channels/DigitalImmortals/channel_autopilot.py --next

echo.
echo [%date% %time%] Cycle completed. Resting for 30 minutes before next check...
echo (Press Ctrl+C at any time to safely exit)
echo.

timeout /t 1800 /nobreak >nul
goto loop
