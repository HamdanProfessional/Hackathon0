@echo off
REM Setup Git Sync Scheduled Task for AI Employee
REM Runs git_sync_pull.bat every 5 minutes

set TASK_NAME=AI Employee Git Sync
set SCRIPT_PATH=C:\Users\User\Desktop\AI_EMPLOYEE_APP\scripts\git_sync_pull.bat

echo Creating scheduled task: %TASK_NAME%

REM Delete existing task if present
schtasks /Delete /TN "%TASK_NAME%" /F >nul 2>&1

REM Create new task - runs every 5 minutes
schtasks /Create /TN "%TASK_NAME%" /TR "cmd.exe /c %SCRIPT_PATH%" /SC MINUTE /MO 5 /RU SYSTEM /RL HIGHEST /F

if %ERRORLEVEL% EQU 0 (
    echo Scheduled task created successfully!
    echo Task will run every 5 minutes.
    echo.
    echo Task details:
    schtasks /Query /TN "%TASK_NAME%" /FO LIST /V
) else (
    echo Failed to create scheduled task. Error: %ERRORLEVEL%
)
