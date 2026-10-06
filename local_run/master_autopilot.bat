@echo off
title Master Dual-Channel 24/7 Autopilot
color 0A

echo ==============================================================================
echo   MASTER DUAL-CHANNEL 24/7 AUTOPILOT ENGINE
echo   Channels: @DigitalImmortals (Ramayana) + @MindNestTales (11 Languages)
echo ==============================================================================
echo.

cd /d "%~dp0.."
python master_dual_autopilot.py --status
echo.
echo Starting 24/7 Continuous Loop...
echo (Press Ctrl+C at any time to pause or exit safely)
echo.

python master_dual_autopilot.py --continuous

pause
