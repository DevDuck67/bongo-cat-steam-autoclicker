@echo off
:: Check if already running as Administrator
net session >nul 2>&1
if %errorLevel% == 0 (
    goto :admin_ok
) else (
    echo Requesting Administrator privileges to interact with Steam...
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

:admin_ok
title Bongo Cat AutoPlayer (ADMINISTRATOR)
cd /d "%~dp0"
echo ========================================================
echo   Bongo Cat AutoPlayer - ADMINISTRATOR MODE ACTIVE
echo ========================================================
python bongo_autoclicker.py
pause
