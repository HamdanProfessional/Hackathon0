@echo off
REM Start Chrome with Remote Debugging (CDP) on port 9222
REM This allows Playwright scripts to connect to your existing Chrome session

echo ============================================================
echo Starting Chrome with CDP (Chrome DevTools Protocol)
echo ============================================================
echo.

REM Check if Chrome is already running
tasklist /FI "IMAGENAME eq chrome.exe" 2>NUL | find /I /N "chrome.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo WARNING: Chrome is already running!
    echo Please close all Chrome windows first, or the CDP port may be in use.
    echo.
    echo Press Ctrl+C to cancel, or
    pause
)

REM Use known Chrome path
set CHROME_PATH=C:\Program Files\Google\Chrome\Application\chrome.exe

REM Use your existing Chrome profile
set CHROME_USER_DATA=C:\Users\User\AppData\Local\Google\Chrome\User Data

echo Using Chrome at: %CHROME_PATH%
echo Profile directory: %CHROME_USER_DATA%
echo.
echo Starting Chrome with remote debugging on port 9222...
echo.

REM Start Chrome with CDP using your existing profile
"%CHROME_PATH%" --remote-debugging-port=9222 --user-data-dir="%CHROME_USER_DATA%"

echo.
echo ============================================================
echo Chrome started with CDP on port 9222
echo ============================================================
echo.
echo IMPORTANT:
echo - This Chrome window is now controlled by CDP
echo - Keep this window OPEN while running social media scripts
echo - Log in to LinkedIn, Twitter, and Meta in THIS window
echo.
echo DO NOT close this window, or the connection will be lost!
echo.
