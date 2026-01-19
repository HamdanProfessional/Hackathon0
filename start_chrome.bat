@echo off
echo ============================================================
echo Starting Chrome CDP with YOUR Main Profile
echo ============================================================
echo.

echo Killing Chrome...
taskkill /F /IM chrome.exe /T >nul 2>&1

echo Waiting for Chrome to close...
timeout /t 3 /nobreak >nul

echo Starting Chrome CDP...
start "" "C:\Program Files\Google\Chrome\Application\chrome.exe" "--user-data-dir=C:\Users\User\AppData\Local\Google\Chrome\User Data" --remote-debugging-port=9222

echo.
echo Waiting 5 seconds for Chrome to initialize...
timeout /t 5 /nobreak >nul

echo.
echo Checking CDP status...
curl -s http://localhost:9222/json/version >nul 2>&1
if %errorlevel% equ 0 (
    echo ============================================================
    echo SUCCESS! Chrome CDP is RUNNING!
    echo.
    echo Profile: C:\Users\User\AppData\Local\Google\Chrome\User Data
    echo CDP Port: 9222
    echo.
    echo You can now test the MCP wrappers:
    cd mcp-servers\linkedin-mcp
    set LINKEDIN_DRY_RUN=true
    node call_post_tool.js "Test"
    echo ============================================================
) else (
    echo Chrome is starting but CDP not ready yet...
    echo Please wait a few more seconds and check manually.
)

echo.
pause
