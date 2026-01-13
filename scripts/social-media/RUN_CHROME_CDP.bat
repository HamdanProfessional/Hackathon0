@echo off
echo ============================================================
echo STARTING CHROME WITH CDP (Chrome DevTools Protocol)
echo ============================================================
echo.
echo This will start Chrome with remote debugging on port 9222
echo.
echo IMPORTANT: Close ALL other Chrome windows first!
echo.
pause

echo.
echo Starting Chrome...
start "" "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="C:\Users\User\AppData\Local\Google\Chrome\User Data"

echo.
echo Waiting 5 seconds for Chrome to start...
timeout /t 5 /nobreak > nul

echo.
echo Checking if CDP is active...
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://localhost:9222/json/version' -UseBasicParsing -TimeoutSec 2; Write-Host 'SUCCESS! Chrome CDP is running on port 9222' -ForegroundColor Green; $content = $response.Content | ConvertFrom-Json; Write-Host 'Browser:' $content.Browser } catch { Write-Host 'FAILED! CDP is not active.' -ForegroundColor Red; Write-Host 'Make sure all Chrome windows are closed before running this script.' -ForegroundColor Yellow }"

echo.
echo ============================================================
echo.
echo If you see SUCCESS above, Chrome is ready!
echo You can now log in to LinkedIn, Twitter, and Meta.
echo.
pause
