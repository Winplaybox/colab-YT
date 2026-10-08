@echo off
title Set Redundant Duplicate Videos to PRIVATE
color 0E

echo ==============================================================================
echo   MAKE DUPLICATE VIDEOS PRIVATE (All YouTube Channels)
echo ==============================================================================
echo   This tool will safely find all redundant copies of duplicate videos
echo   across your channels and change their status to PRIVATE.
echo.
echo   - Canonical (oldest original) videos will remain PUBLIC and untouched.
echo   - Redundant copies will be hidden from public YouTube feeds.
echo ==============================================================================
echo.

cd /d "%~dp0.."
python channels/common/cleanup_duplicates.py --private

echo.
echo ==============================================================================
echo   Process complete. Redundant duplicate videos have been set to PRIVATE.
echo ==============================================================================
echo.
pause
