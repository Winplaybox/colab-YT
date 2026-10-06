@echo off
title Epic Bharat Saga - Single Production Run
color 0B

echo ==============================================================================
echo   EPIC BHARAT SAGA — SINGLE PRODUCTION RUNNER
echo   Channel: EpicBharatSaga (Vedic Mythology Shorts)
echo   Mode:    Produce ^& Schedule Next Episode Once
echo ==============================================================================
echo.

cd /d "%~dp0.."
python channels/EpicBharatSaga/scheduler.py --mode scheduled --quality 1080p

echo.
echo ==============================================================================
echo [%date% %time%] Production complete.
echo ==============================================================================
pause
