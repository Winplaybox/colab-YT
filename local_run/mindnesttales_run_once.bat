@echo off
title MindNest Tales - Manual Production Run
color 0B

echo ==============================================================================
echo   MINDNEST TALES (11-Language Network) — MANUAL PRODUCTION RUNNER
echo   Network: 11 Localized Global YouTube Channels (51 Stories)
echo ==============================================================================
echo.

set /p STORY_NUM="Enter story number to generate [default: 2, or press Enter]: "
if "%STORY_NUM%"=="" set STORY_NUM=2

echo.
set /p FORCE_FLAG="Force re-upload if already detected on YouTube? (y/n) [default: n]: "
set FORCE_ARG=
if /i "%FORCE_FLAG%"=="y" set FORCE_ARG=--force

echo.
echo ==============================================================================
echo [START] Generating Story #%STORY_NUM% across all 11 language channels...
echo ==============================================================================
echo.

cd /d "%~dp0.."
python channels/MindNestTales/scheduler.py --story %STORY_NUM% --mode short %FORCE_ARG%

echo.
echo ==============================================================================
echo [%date% %time%] Production finished for Story #%STORY_NUM%.
echo ==============================================================================
pause
