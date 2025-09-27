@echo off
echo =========================================
echo   Rockfall Detection Server Startup
echo =========================================
echo.

cd /d "%~dp0"

echo Checking Python installation...
python --version
if errorlevel 1 (
    echo ERROR: Python not found! Please install Python 3.7+
    pause
    exit /b 1
)

echo.
echo Starting stable server (no auto-reload)...
python start_server.py

echo.
echo Server stopped. Press any key to exit...
pause >nul