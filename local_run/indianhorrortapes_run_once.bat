@echo off
title Indian Horror Tapes - Single Production Run
color 0B

echo ==============================================================================
echo   INDIAN HORROR TAPES — SINGLE PRODUCTION RUNNER
echo   Channel: IndianHorrorTapes (Cinematic Horror Shorts)
echo   Mode:    Produce ^& Schedule Next Episode Once
echo ==============================================================================
echo.

cd /d "%~dp0.."
python channels/IndianHorrorTapes/scheduler.py --quality 1080p

echo.
echo ==============================================================================
echo [%date% %time%] Production complete.
echo ==============================================================================
pause
