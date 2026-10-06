@echo off
title BuzzStormNow Blog - 24/7 Continuous Autopilot
color 0A

echo ==============================================================================
echo   BUZZSTORMNOW BLOG — 24/7 CONTINUOUS AUTOPILOT
echo   Target: https://buzzstormnow.blogspot.com
echo   Mode:   Non-Stop Financial Feeds Monitoring ^& 3-Slot Daily Publishing
echo ==============================================================================
echo.

cd /d "%~dp0.."

:loop
echo.
echo ==============================================================================
echo [%date% %time%] [BUZZSTORMNOW BLOG] Checking Market News Feeds...
echo ==============================================================================
echo.

python blog/scheduler.py auto

echo.
echo [%date% %time%] Check completed. Resting for 30 minutes before next market check...
echo (Press Ctrl+C at any time to safely exit)
echo.

timeout /t 1800 /nobreak >nul
goto loop
