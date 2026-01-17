#!/bin/bash
#
# Vault Sync Pull Script for Cloud VM (Platinum Tier)
#
# Pulls latest vault changes from local machine via Git.
# Cloud pulls, never pushes (local is single writer for Dashboard.md)
#

set -e

VAULT_PATH="${VAULT_PATH:-AI_Employee_Vault}"
REPO_URL="${VAULT_REPO_URL:-}"
BRANCH="${VAULT_BRANCH:-main}"
LOG_FILE="logs/vault_sync_pull.log"

# Create logs directory
mkdir -p "$(dirname "$LOG_FILE")"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

log "Starting vault sync pull..."

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

# Fetch latest changes
if [ -n "$REPO_URL" ]; then
    log "Fetching from remote: $REPO_URL"
    git fetch origin "$BRANCH" 2>&1 | tee -a "$LOG_FILE" || true

    # Check if there are changes to pull
    LOCAL_COMMIT=$(git rev-parse HEAD)
    REMOTE_COMMIT=$(git rev-parse origin/"$BRANCH" 2>/dev/null || echo "none")

    if [ "$LOCAL_COMMIT" != "$REMOTE_COMMIT" ]; then
        log "Changes detected, pulling..."
        git pull origin "$BRANCH" 2>&1 | tee -a "$LOG_FILE"
        log "Pull completed successfully"
    else
        log "No changes to pull"
    fi
else
    log "No remote configured, skipping pull"
fi

# Update timestamp
echo "$(date -Iseconds)" > .last_sync_pull

log "Vault sync pull completed"

# Optional: Run dashboard merger if it exists
if [ -f "../scripts/merge_dashboard_updates.py" ]; then
    log "Running dashboard update merger..."
    python3 ../scripts/merge_dashboard_updates.py --vault "$VAULT_PATH" 2>&1 | tee -a "$LOG_FILE"
fi

exit 0
