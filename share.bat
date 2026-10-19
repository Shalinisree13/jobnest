@echo off
echo ========================================================
echo   JobNest - Instant Public Link Generator
echo ========================================================
echo.

cd /d "%~dp0"

echo [*] Launching secure public tunnel for port 5000...
echo [*] Anyone on the internet will be able to access your JobNest portal.
echo.

ssh -T -o StrictHostKeyChecking=no -R 80:127.0.0.1:5000 nokey@localhost.run

pause
