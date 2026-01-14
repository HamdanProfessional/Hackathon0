@echo off
echo ============================================================
echo STARTING AUTOMATION CHROME (SEPARATE PROFILE)
echo ============================================================
echo.
echo This creates a NEW Chrome profile specifically for automation
echo Your main Chrome profile stays separate
echo.
echo Profile: C:\Users\User\ChromeAutomationProfile
echo CDP Port: 9222
echo.

REM Create profile directory if it doesn't exist
if not exist "C:\Users\User\ChromeAutomationProfile" mkdir "C:\Users\User\ChromeAutomationProfile"

echo Starting Chrome with CDP...
start "" "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="C:\Users\User\ChromeAutomationProfile"

echo.
echo Waiting 5 seconds...
timeout /t 5 /nobreak > nul

echo.
echo Checking CDP status...
powershell -Command "try { $r = Invoke-WebRequest -Uri 'http://localhost:9222/json/version' -UseBasicParsing -TimeoutSec 3; $c = $r.Content | ConvertFrom-Json; Write-Host 'SUCCESS!' -ForegroundColor Green; Write-Host 'Browser:' $c.Browser; Write-Host 'CDP Endpoint: http://localhost:9222' } catch { Write-Host 'FAILED - CDP not active' -ForegroundColor Red }"

echo.
echo ============================================================
echo.
echo If you see SUCCESS above:
echo 1. Log in to LinkedIn, Twitter, and Meta in THIS Chrome window
echo 2. Keep this window open
echo 3. Run the automation scripts
echo.
pause
