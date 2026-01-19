@echo off
REM###############################################################################
REM Git Sync Pull - Local Machine
REM
REM Pulls vault changes (drafts, updates) from Git repository.
REM Runs every 5 minutes via cron/PM2.
REM
REM SECRETS NEVER SYNC: .env, *_token.json, whatsapp_session/
REM###############################################################################

setlocal enabledelayedexpansion

echo [%DATE% %TIME%] Git Sync Pull: Starting...

cd /d "%~dp0.."
set REPO_DIR=%CD%

echo [%DATE% %TIME%] Repository: %REPO_DIR%

REM Fetch from remote
echo [%DATE% %TIME%] Fetching from remote...
git fetch origin

REM Check if there are changes to pull
for /f %%i in ('git rev-list HEAD..@{u} --count') do set COMMITS=%%i

if "%COMMITS%"=="0" (
    echo [%DATE% %TIME%] No new changes to pull.
    goto :end
)

echo [%DATE% %TIME%] New commits detected: %COMMITS%

REM Pull changes (Local wins for conflicts)
echo [%DATE% %TIME%] Pulling from remote...
git pull origin main --no-recurse-submodules

REM Show what changed
echo [%DATE% %TIME%] Changes pulled:
git status --short

echo [%DATE% %TIME%] Git Sync Pull: Complete ✅

:end
echo [%DATE% %TIME%] Git Sync Pull: Done.
