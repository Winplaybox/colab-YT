@echo off
title Digital Immortals - Single Production Run
color 0B

echo ==============================================================================
echo   DIGITAL IMMORTALS (@DigitalImmortals) — SINGLE PRODUCTION RUNNER
echo   Series: Valmiki Ramayana Definitive Saga (54 Episodes)
echo   Mode:   Produce ^& Schedule Next Episode Once
echo ==============================================================================
echo.

cd /d "%~dp0.."
python channels/DigitalImmortals/channel_autopilot.py --next

echo.
echo ==============================================================================
echo [%date% %time%] Production complete.
echo ==============================================================================
pause
