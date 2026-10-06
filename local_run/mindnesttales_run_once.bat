@echo off
title MindNest Tales - Single Production Run
color 0B

echo ==============================================================================
echo   MINDNEST TALES (11-Language Network) — SINGLE PRODUCTION RUNNER
echo   Network: 11 Localized Global YouTube Channels (51 Stories)
echo   Mode:    Per-Channel YouTube Ground Truth Sync ^& Single Story Production
echo ==============================================================================
echo.

cd /d "%~dp0.."
python channels/MindNestTales/scheduler.py --story auto --mode short

echo.
echo ==============================================================================
echo [%date% %time%] Production complete.
echo ==============================================================================
pause
