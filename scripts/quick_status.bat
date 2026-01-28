@echo off
REM Quick System Status Check for Windows
REM Shows essential AI Employee system status at a glance

echo ==================================
echo AI EMPLOYEE SYSTEM STATUS
echo ==================================
echo.

echo [LOCAL MACHINE]
pm2 status 2>nul | findstr /C:"online" | find /C /V "" > nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo   PM2 is running
) else (
    echo   [!] PM2 is not running
)

echo.
echo [CLOUD VM]
ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=no root@143.244.143.143 "cd /root/AI_EMPLOYEE_APP && pm2 status" 2>nul | findstr /C:"online" > nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo   Cloud is online
) else (
    echo   [!] Could not connect to Cloud
)

echo.
echo [GIT SYNC]
for /f %%i in ('git status --short ^| find /C /V ""') do set UNCOMMITTED=%%i
echo   Uncommitted changes: %UNCOMMITTED%

echo.
echo ==================================
echo Run 'python scripts/system_health_report.py' for detailed report
echo ==================================
