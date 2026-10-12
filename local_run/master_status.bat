@echo off
title Multi-Channel Status Dashboard
color 0E

echo ==============================================================================
echo   ALL-CHANNELS STATUS ^& YOUTUBE GROUND TRUTH AUDIT
echo ==============================================================================
echo.

cd /d "%~dp0.."
python master_dual_autopilot.py --status
echo.
echo Checking Live YouTube Duplicate Ground Truth across all channels...
python channels/common/audit_all_channels.py

echo.
echo ==============================================================================
echo   To launch a channel, run the corresponding .bat file in this folder:
echo     - alltrainreels_run_once.bat     ^| alltrainreels_autopilot.bat
echo     - digitalimmortals_run_once.bat  ^| digitalimmortals_autopilot.bat
echo     - mindnesttales_run_once.bat     ^| mindnesttales_autopilot.bat
echo     - epicbharatsaga_run_once.bat    ^| epicbharatsaga_autopilot.bat
echo     - indianhorrortapes_run_once.bat ^| indianhorrortapes_autopilot.bat
echo     - tigervlogs_run_once.bat        ^| tigervlogs_autopilot.bat
echo     - blog_run_once.bat              ^| blog_autopilot.bat
echo     - master_autopilot.bat (Continuous 24/7 Digital Immortals + MindNest)
echo ==============================================================================
echo.
pause
