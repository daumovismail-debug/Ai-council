#!/usr/bin/env bash
# Run once on the server: bash setup_server.sh
set -euo pipefail

APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=== [1/5] Installing system packages ==="
apt-get update -qq
apt-get install -y -qq python3 python3-pip python3-venv git curl

echo "=== [2/5] Installing Node.js + PM2 ==="
if ! command -v node &>/dev/null; then
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
    apt-get install -y nodejs
fi
npm install -g pm2 --silent
pm2 startup systemd -u root --hp /root | tail -1 | bash || true

echo "=== [3/5] Installing Python dependencies ==="
cd "$APP_DIR"
pip install -q -r requirements.txt

echo "=== [4/5] Creating logs directory ==="
mkdir -p "$APP_DIR/logs"

echo "=== [5/5] Starting PM2 processes ==="
pm2 start ecosystem.config.js
pm2 save

echo ""
echo "✓ Setup complete."
echo ""
echo "NEXT STEPS:"
echo "  1. Add .env file with TELEGRAM_TOKEN, GEMINI_API_KEY, WEBHOOK_SECRET"
echo "  2. In GitHub repo → Settings → Webhooks → Add webhook:"
echo "       Payload URL:  http://139.59.153.139:9000/webhook"
echo "       Content type: application/json"
echo "       Secret:       <same as WEBHOOK_SECRET in .env>"
echo "       Events:       Just the push event"
echo "  3. pm2 logs storonsky-bot   — check bot logs"
echo "  4. pm2 logs storonsky-webhook — check webhook logs"
