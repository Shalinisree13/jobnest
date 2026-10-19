@echo off
echo ========================================================
echo   JobNest - Online Job Portal and Recruitment System
echo ========================================================
echo.

cd /d "%~dp0"

REM Check for virtual environment
if not exist "venv\Scripts\activate.bat" (
    echo [*] Creating Python virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo [!] Error creating virtual environment. Ensure Python is installed.
        pause
        exit /b 1
    )
)

echo [*] Activating virtual environment...
call venv\Scripts\activate.bat

echo [*] Installing / verifying dependencies...
python -m pip install -r requirements.txt --quiet

REM Initialize database if not already present
if not exist "instance\jobnest.db" (
    echo [*] First-time setup: Seeding database with demo users, jobs and resumes...
    python seed.py
)

echo.
echo ========================================================
echo   JobNest is starting on http://127.0.0.1:5000
echo   Press Ctrl+C to stop the server
echo ========================================================
echo.

start "" http://127.0.0.1:5000
python app.py

pause
