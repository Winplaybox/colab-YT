@echo off
title BuzzStormNow Blog - Single Post Run
color 0B

echo ==============================================================================
echo   BUZZSTORMNOW BLOG — SINGLE ARTICLE PUBLISHER
echo   Target: https://buzzstormnow.blogspot.com
echo   Mode:   Scrape Live News, Write Viral Article ^& Publish to Blogger Once
echo ==============================================================================
echo.

cd /d "%~dp0.."
python blog/scheduler.py post_now

echo.
echo ==============================================================================
echo [%date% %time%] Publishing complete.
echo ==============================================================================
pause
