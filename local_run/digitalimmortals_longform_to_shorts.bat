@echo off
title Digital Immortals - Long episode to Shorts
color 0A
cd /d "%~dp0.."
set /p EP=Episode number (e.g. 7): 
python channels/DigitalImmortals/longform_to_shorts.py %EP% %*
echo.
echo Shorts are in channels\DigitalImmortals\output (uploaded as PRIVATE)
pause
