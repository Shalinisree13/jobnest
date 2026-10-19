# JobNest - One-click PowerShell Startup Script
$ErrorActionPreference = "Stop"

Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "  JobNest - Online Job Portal and Recruitment System" -ForegroundColor White
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host ""

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

# Check virtual environment
if (-not (Test-Path "venv\Scripts\Activate.ps1")) {
    Write-Host "[*] Creating virtual environment (venv)..." -ForegroundColor Yellow
    python -m venv venv
}

Write-Host "[*] Activating virtual environment..." -ForegroundColor Yellow
& "$ScriptDir\venv\Scripts\Activate.ps1"

Write-Host "[*] Checking and installing dependencies..." -ForegroundColor Yellow
python -m pip install -r requirements.txt --quiet

# Seed database if missing
if (-not (Test-Path "instance\jobnest.db")) {
    Write-Host "[*] Initializing SQLite database with seed data..." -ForegroundColor Yellow
    python seed.py
}

Write-Host ""
Write-Host "========================================================" -ForegroundColor Green
Write-Host "  JobNest is launching at http://127.0.0.1:5000" -ForegroundColor Green
Write-Host "  Press Ctrl+C to stop the server" -ForegroundColor Green
Write-Host "========================================================" -ForegroundColor Green
Write-Host ""

Start-Process "http://127.0.0.1:5000"
python app.py
