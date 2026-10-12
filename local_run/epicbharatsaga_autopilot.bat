@echo off
title Epic Bharat Saga - 24/7 Continuous Autopilot
color 0A

echo ==============================================================================
echo   EPIC BHARAT SAGA — 24/7 CONTINUOUS AUTOPILOT
echo   Channel: EpicBharatSaga (Vedic Mythology Shorts)
echo   Mode:    Autonomous Daily Mythology Shorts Production ^& 19:00 IST Scheduling
echo ==============================================================================
echo.

cd /d "%~dp0.."

for /f "tokens=*" %%i in ('python -c "import json; print(json.load(open('channels/EpicBharatSaga/state.json', encoding='utf-8')).get('current_episode', 36))"') do set CURRENT_EP=%%i
if "%CURRENT_EP%"=="" set CURRENT_EP=36

set /p EPISODE_NUM="Enter starting episode number [default: %CURRENT_EP%, or press Enter]: "
if "%EPISODE_NUM%"=="" set EPISODE_NUM=%CURRENT_EP%

echo.
set /p AUTO_ADV="Auto-advance to next episode after completion? (y/n) [default: y]: "
if /i "%AUTO_ADV%"=="" set AUTO_ADV=y

echo.
set /p FORCE_FLAG="Force re-upload if already detected on YouTube? (y/n) [default: n]: "
set FORCE_ARG=
if /i "%FORCE_FLAG%"=="y" set FORCE_ARG=--force

echo.
echo ==============================================================================
echo Starting EpicBharatSaga Autopilot for Episode #%EPISODE_NUM%...
if /i "%AUTO_ADV%"=="y" (
    echo Mode: Auto-advancing (Episode #%EPISODE_NUM% -^> next episodes)
) else (
    echo Mode: Fixed (Proceeding with Episode #%EPISODE_NUM% only)
)
echo ==============================================================================
echo.

:loop
echo.
echo ==============================================================================
echo [%date% %time%] [EPIC BHARAT SAGA] Starting Production Cycle for Episode #%EPISODE_NUM%...
echo ==============================================================================
echo.

python channels/EpicBharatSaga/scheduler.py --episode %EPISODE_NUM% --mode scheduled --quality 1080p %FORCE_ARG%

if /i "%AUTO_ADV%"=="y" (
    set /a EPISODE_NUM=EPISODE_NUM+1
    echo.
    echo Next autopilot cycle will proceed with Episode #%EPISODE_NUM%.
)

echo.
echo [%date% %time%] Cycle completed. Resting for 60 minutes before next check...
echo (Press Ctrl+C at any time to safely exit)
echo.

timeout /t 3600 /nobreak >nul
goto loop
