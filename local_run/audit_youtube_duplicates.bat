@echo off
title YouTube Duplicate Video Audit - All Channels
color 0B

echo ==============================================================================
echo   LIVE YOUTUBE DUPLICATE CONTENT AUDIT ^& STATE SYNCHRONIZATION
echo ==============================================================================
echo.

cd /d "%~dp0.."
python channels/common/audit_all_channels.py

echo.
echo ==============================================================================
echo   Audit Complete. Duplicate check is actively protecting all channels.
echo ==============================================================================
echo.
pause
