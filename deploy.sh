#!/usr/bin/env bash
set -euo pipefail

APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BOT_NAME="storonsky-bot"
WEBHOOK_NAME="storonsky-webhook"

echo "[deploy] Pulling latest code..."
cd "$APP_DIR"
git fetch origin main
git reset --hard origin/main

echo "[deploy] Installing/updating dependencies..."
pip install -q -r requirements.txt

echo "[deploy] Restarting bot via PM2..."
if pm2 describe "$BOT_NAME" > /dev/null 2>&1; then
    pm2 reload "$BOT_NAME" --update-env
else
    pm2 start ecosystem.config.js --only "$BOT_NAME"
fi

pm2 save
echo "[deploy] Done."
