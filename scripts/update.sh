#!/usr/bin/env bash
# Update script — pulls latest code and restarts services
# Run on the server after pushing new commits to main
# Usage: bash scripts/update.sh

set -euo pipefail

APP_DIR="/var/www/prokar-agency-website"
VENV_DIR="$APP_DIR/venv"
SERVICE_NAME="prokar"

GREEN='\033[0;32m'; NC='\033[0m'
info() { echo -e "${GREEN}[INFO]${NC}  $*"; }

info "Pulling latest code..."
git -C "$APP_DIR" pull origin main

source "$VENV_DIR/bin/activate"
cd "$APP_DIR"

info "Installing/updating dependencies..."
pip install -r requirements.txt -q

info "Running migrations..."
python manage.py migrate --noinput

info "Collecting static files..."
python manage.py collectstatic --noinput --clear

info "Compiling messages..."
python manage.py compilemessages 2>/dev/null || true

info "Restarting Gunicorn..."
sudo systemctl restart $SERVICE_NAME

info "Reloading Nginx..."
sudo systemctl reload nginx

echo ""
echo -e "${GREEN}✓ Update complete!${NC}"
echo "  Logs: sudo journalctl -u $SERVICE_NAME -f"
