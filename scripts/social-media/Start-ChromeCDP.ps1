# Start Chrome with CDP
Write-Host "Stopping all Chrome processes..." -ForegroundColor Yellow
Stop-Process -Name chrome -Force -ErrorAction SilentlyContinue

Write-Host "Waiting 3 seconds..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

Write-Host "Starting Chrome with CDP on port 9222..." -ForegroundColor Green
Start-Process "C:\Program Files\Google\Chrome\Application\chrome.exe" -ArgumentList "--remote-debugging-port=9222","--user-data-dir=C:\Users\User\AppData\Local\Google\Chrome\User Data"

Write-Host "Waiting 5 seconds for Chrome to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

Write-Host "Checking if CDP is active..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:9222/json/version" -UseBasicParsing | ConvertFrom-Json
    Write-Host "SUCCESS! Chrome CDP is running!" -ForegroundColor Green
    Write-Host "Browser: $($response.'Browser')"
    Write-Host ""
    Write-Host "You can now run the social media posters!" -ForegroundColor Cyan
} catch {
    Write-Host "FAILED! CDP is not active." -ForegroundColor Red
    Write-Host "Error: $_" -ForegroundColor Red
}
