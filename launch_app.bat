@echo off
cd /d %~dp0\src

REM Activate venv from root folder
IF EXIST "..\.venv\Scripts\activate.bat" (
    call "..\.venv\Scripts\activate.bat"
)

REM Open in default browser
start http://localhost:5000

REM Run the Flask app using waitress
python InstaWebDownload.py
