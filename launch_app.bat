@echo off
cd /d "%~dp0src"

set "VENV=..\Scripts\activate"
set "VENV_FOLDER=..\"

echo [INFO] Starting InstaDownloader...

:: Check Python
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed. Please install it first from https://www.python.org/downloads/
    pause
    exit /b
)

:: Check virtualenv
if not exist "%VENV_FOLDER%\.venv" (
    echo [INFO] Creating virtual environment...
    python -m venv %VENV_FOLDER%\.venv
)

:: Activate venv
call %VENV_FOLDER%\.venv\Scripts\activate

:: Install dependencies
echo [INFO] Installing required packages...
pip install --upgrade pip
pip install -r %VENV_FOLDER%requirements.txt

:: Check ffmpeg
where ffmpeg >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] ffmpeg is not installed or not in PATH. Install it from https://ffmpeg.org/download.html
    pause
    exit /b
)
echo [OK] ffmpeg is installed.

:: Create videos dir if needed
if not exist "%VENV_FOLDER%videos" (
    mkdir "%VENV_FOLDER%videos"
)

:: Launch App
start "" http://localhost:5000
python InstaWebDownload.py
