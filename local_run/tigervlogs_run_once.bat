@echo off
title Tiger Vlogs - Single Daily Batch Run
color 0B

echo ==============================================================================
echo   TIGER VLOGS (@TigerVlogs-2026) — SINGLE DAILY BATCH RUNNER
echo   Channel: TigerVlogs-2026 (Food Investigation ^& Street Food Shorts)
echo   Mode:    Produce ^& Schedule Today's 3 Video Batch Once
echo ==============================================================================
echo.

cd /d "%~dp0.."
python channels/TigerVlogs-2026/scheduler.py

echo.
echo ==============================================================================
echo [%date% %time%] Batch complete.
echo ==============================================================================
pause
