@echo off
title MindNest Tales - 24/7 Continuous Autopilot
color 0A

echo ==============================================================================
echo   MINDNEST TALES (11-Language Network) — 24/7 CONTINUOUS AUTOPILOT
echo   Network: 11 Localized Global YouTube Channels (51 Stories)
echo   Mode:    Autonomous Multi-Channel Production ^& YouTube Scheduling
echo ==============================================================================
echo.

set /p STORY_NUM="Enter story number to generate [default: 2, or press Enter]: "
if "%STORY_NUM%"=="" set STORY_NUM=2

echo.
set /p AUTO_ADV="Auto-advance to next story after completion? (y/n) [default: n]: "
if /i "%AUTO_ADV%"=="" set AUTO_ADV=n

echo.
set /p FORCE_FLAG="Force re-upload if already detected on YouTube? (y/n) [default: n]: "
set FORCE_ARG=
if /i "%FORCE_FLAG%"=="y" set FORCE_ARG=--force

echo.
echo ==============================================================================
echo Starting MindNest Tales Autopilot for Story #%STORY_NUM%...
if /i "%AUTO_ADV%"=="y" (
    echo Mode: Auto-advancing (Story #%STORY_NUM% -^> next stories)
) else (
    echo Mode: Fixed (Proceeding with Story #%STORY_NUM% only)
)
echo ==============================================================================
echo.

cd /d "%~dp0.."

:loop
echo.
echo ==============================================================================
echo [%date% %time%] [MINDNEST TALES] Starting Production Cycle for Story #%STORY_NUM%...
echo ==============================================================================
echo.

python channels/MindNestTales/scheduler.py --story %STORY_NUM% --mode short %FORCE_ARG%

if /i "%AUTO_ADV%"=="y" (
    set /a STORY_NUM=STORY_NUM+1
    echo.
    echo Next autopilot cycle will proceed with Story #%STORY_NUM%.
)

echo.
echo [%date% %time%] Batch completed. Resting for 30 minutes before next check...
echo (Press Ctrl+C at any time to safely exit)
echo.

timeout /t 1800 /nobreak >nul
goto loop
