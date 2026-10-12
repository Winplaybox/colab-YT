@echo off
title All Train Reels - Manual Production Run
color 0B

echo ==============================================================================
echo   ALL TRAIN REELS — MANUAL PRODUCTION RUNNER
echo   Channel: @AllTrainReels (High-Speed ^& Extreme Locomotives)
echo   Mode:    Produce ^& Schedule Specific Episode
echo ==============================================================================
echo.

cd /d "%~dp0.."

for /f "tokens=*" %%i in ('python -c "import json; print(json.load(open('channels/AllTrainReels/state.json', encoding='utf-8')).get('current_story_number', 13))"') do set CURRENT_EP=%%i
if "%CURRENT_EP%"=="" set CURRENT_EP=13

set /p EPISODE_NUM="Enter episode number to generate [default: %CURRENT_EP%, or press Enter]: "
if "%EPISODE_NUM%"=="" set EPISODE_NUM=%CURRENT_EP%

echo.
set /p FORCE_FLAG="Force re-upload if already detected on YouTube? (y/n) [default: n]: "
set FORCE_ARG=
if /i "%FORCE_FLAG%"=="y" set FORCE_ARG=--force

echo.
echo ==============================================================================
echo [START] Generating Episode #%EPISODE_NUM% for AllTrainReels...
echo ==============================================================================
echo.

python channels/AllTrainReels/scheduler.py --episode %EPISODE_NUM% --mode scheduled --quality 1080p %FORCE_ARG%

echo.
echo ==============================================================================
echo [%date% %time%] Production finished for Episode #%EPISODE_NUM%.
echo ==============================================================================
pause
