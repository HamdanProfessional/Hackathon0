@echo off
echo Starting Chrome with CDP...
"C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="C:\Users\User\AppData\Local\Google\Chrome\User Data"
echo.
echo Chrome should now be running with CDP on port 9222
echo.
