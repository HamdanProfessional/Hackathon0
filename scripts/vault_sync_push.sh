#!/bin/bash
#
# Vault Sync Push Script for Local Machine (Platinum Tier)
#
# Pushes vault changes to remote repository for cloud to pull.
# Local pushes, cloud pulls (single writer rule for Dashboard.md)
#

set -e

VAULT_PATH="${VAULT_PATH:-AI_Employee_Vault}"
REPO_URL="${VAULT_REPO_URL:-}"
BRANCH="${VAULT_BRANCH:-main}"
LOG_FILE="logs/vault_sync_push.log"

# Create logs directory
mkdir -p "$(dirname "$LOG_FILE")"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

log "Starting vault sync push..."

# Check if vault path exists
if [ ! -d "$VAULT_PATH" ]; then
    log "ERROR: Vault path not found: $VAULT_PATH"
    exit 1
fi

cd "$VAULT_PATH"

# Initialize git if not already done
if [ ! -d ".git" ]; then
    log "Initializing git repository..."
    git init
    if [ -n "$REPO_URL" ]; then
        git remote add origin "$REPO_URL"
    fi
fi

# Check if remote is configured
if [ -n "$REPO_URL" ] && ! git remote | grep -q origin; then
    git remote add origin "$REPO_URL"
fi

# Check for changes
if ! git diff --quiet || ! git diff --cached --quiet; then
    log "Changes detected, adding to git..."

    # Add all changes
    git add . 2>&1 | tee -a "$LOG_FILE"

    # Commit changes
    COMMIT_MESSAGE="Update from local - $(date -Iseconds)"
    git commit -m "$COMMIT_MESSAGE" 2>&1 | tee -a "$LOG_FILE"

    # Push to remote
    if [ -n "$REPO_URL" ]; then
        log "Pushing to remote: $REPO_URL"
        git push origin "$BRANCH" 2>&1 | tee -a "$LOG_FILE"
        log "Push completed successfully"
    else
        log "No remote configured, skipping push"
    fi
else
    log "No changes to push"
fi

# Update timestamp
echo "$(date -Iseconds)" > .last_sync_push

log "Vault sync push completed"

exit 0
