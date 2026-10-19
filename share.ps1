# JobNest - Instant Public Link Generator (PowerShell)
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "  JobNest - Public Internet Sharing Link" -ForegroundColor White
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "[*] Creating secure public tunnel for http://127.0.0.1:5000..." -ForegroundColor Yellow
Write-Host "[*] Copy the HTTPS link printed below to share with anyone." -ForegroundColor Green
Write-Host ""

ssh -T -o StrictHostKeyChecking=no -R 80:127.0.0.1:5000 nokey@localhost.run
