#!/usr/bin/env bash
# First-time deployment script for prokar.uz
# Run as a non-root user with sudo privileges on Ubuntu 22.04 / Debian 12
# Usage: bash scripts/deploy.sh

set -euo pipefail

# ── Config ────────────────────────────────────────────────────────────────────
REPO_URL="https://github.com/ulugbek101/prokar-agency-website.git"
APP_DIR="/var/www/prokar-agency-website"
DOMAIN="prokar.uz"
PYTHON="python3"
VENV_DIR="$APP_DIR/venv"
WSGI_MODULE="prokar_site.wsgi:application"
SERVICE_NAME="prokar"
NGINX_CONF="/etc/nginx/sites-available/$DOMAIN"
GUNICORN_SOCKET="/run/$SERVICE_NAME.sock"

# ── Colors ────────────────────────────────────────────────────────────────────
GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; NC='\033[0m'
info()    { echo -e "${GREEN}[INFO]${NC}  $*"; }
warn()    { echo -e "${YELLOW}[WARN]${NC}  $*"; }
error()   { echo -e "${RED}[ERROR]${NC} $*"; exit 1; }

# ── 1. System packages ────────────────────────────────────────────────────────
info "Removing stale cdrom apt source if present..."
sudo sed -i '/^deb cdrom:/d' /etc/apt/sources.list

info "Installing system packages..."
sudo apt-get update -q
sudo apt-get install -y -q \
    python3 python3-pip python3-venv \
    postgresql postgresql-contrib \
    nginx \
    git \
    certbot python3-certbot-nginx \
    gettext \
    libpq-dev

# ── 2. Clone repository ───────────────────────────────────────────────────────
info "Cloning repository..."
sudo mkdir -p /var/www
sudo chown "$USER:$USER" /var/www

if [ -d "$APP_DIR/.git" ]; then
    warn "Repository already exists at $APP_DIR. Pulling latest..."
    git -C "$APP_DIR" pull origin main
else
    git clone "$REPO_URL" "$APP_DIR"
fi

# ── 3. .env file ─────────────────────────────────────────────────────────────
[ ! -f "$APP_DIR/.env" ] && error ".env not found at $APP_DIR/.env — place it there before running this script. See .env.example for the required variables."
info ".env found — using it."
chmod 640 "$APP_DIR/.env"

# Read DB credentials from .env to create the PostgreSQL user/database
DB_NAME=$(grep -E '^DB_NAME=' "$APP_DIR/.env" | cut -d= -f2)
DB_USER=$(grep -E '^DB_USER=' "$APP_DIR/.env" | cut -d= -f2)
DB_PASSWORD=$(grep -E '^DB_PASSWORD=' "$APP_DIR/.env" | cut -d= -f2)

[ -z "$DB_NAME" ]     && error "DB_NAME is not set in .env"
[ -z "$DB_USER" ]     && error "DB_USER is not set in .env"
[ -z "$DB_PASSWORD" ] && error "DB_PASSWORD is not set in .env"

# ── 4. PostgreSQL ─────────────────────────────────────────────────────────────
info "Setting up PostgreSQL..."
sudo -u postgres psql -tc "SELECT 1 FROM pg_roles WHERE rolname='$DB_USER'" | grep -q 1 || \
    sudo -u postgres psql -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';"

sudo -u postgres psql -tc "SELECT 1 FROM pg_database WHERE datname='$DB_NAME'" | grep -q 1 || \
    sudo -u postgres psql -c "CREATE DATABASE $DB_NAME OWNER $DB_USER;"

sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;"

# ── 5. Python virtual environment & dependencies ──────────────────────────────
info "Creating virtual environment..."
$PYTHON -m venv "$VENV_DIR"
source "$VENV_DIR/bin/activate"

info "Installing Python dependencies..."
pip install --upgrade pip -q
pip install -r "$APP_DIR/requirements.txt" -q
pip install gunicorn -q

# ── 6. Django setup ───────────────────────────────────────────────────────────
info "Running Django setup..."
cd "$APP_DIR"

python manage.py migrate --noinput
python manage.py collectstatic --noinput --clear
python manage.py compilemessages 2>/dev/null || warn "compilemessages skipped (gettext may not be installed)"

# ── 7. Gunicorn systemd service ───────────────────────────────────────────────
info "Creating Gunicorn systemd service..."
sudo tee /etc/systemd/system/$SERVICE_NAME.socket > /dev/null <<EOF
[Unit]
Description=Gunicorn socket for $DOMAIN

[Socket]
ListenStream=$GUNICORN_SOCKET
SocketUser=www-data

[Install]
WantedBy=sockets.target
EOF

sudo tee /etc/systemd/system/$SERVICE_NAME.service > /dev/null <<EOF
[Unit]
Description=Gunicorn daemon for $DOMAIN
Requires=$SERVICE_NAME.socket
After=network.target

[Service]
User=$USER
Group=www-data
WorkingDirectory=$APP_DIR
EnvironmentFile=$APP_DIR/.env
ExecStart=$VENV_DIR/bin/gunicorn \\
    --access-logfile - \\
    --workers 3 \\
    --bind unix:$GUNICORN_SOCKET \\
    $WSGI_MODULE

Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable --now $SERVICE_NAME.socket
sudo systemctl restart $SERVICE_NAME

# ── 8. Nginx ──────────────────────────────────────────────────────────────────
info "Configuring Nginx..."
sudo tee "$NGINX_CONF" > /dev/null <<EOF
server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN;

    client_max_body_size 20M;

    location = /favicon.ico { access_log off; log_not_found off; }

    location /static/ {
        alias $APP_DIR/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location /media/ {
        alias $APP_DIR/media/;
        expires 30d;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:$GUNICORN_SOCKET;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

sudo ln -sf "$NGINX_CONF" /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx

# ── 9. SSL certificate ────────────────────────────────────────────────────────
info "Obtaining SSL certificate with Certbot..."
sudo certbot --nginx -d "$DOMAIN" -d "www.$DOMAIN" --non-interactive --agree-tos -m thedevu101@gmail.com

sudo systemctl reload nginx

# ── 10. Fix permissions ───────────────────────────────────────────────────────
info "Setting file permissions..."
sudo chown -R "$USER:www-data" "$APP_DIR"
sudo chmod -R 755 "$APP_DIR"
sudo chmod -R 775 "$APP_DIR/media"
sudo chmod 640 "$APP_DIR/.env"

# ── Done ──────────────────────────────────────────────────────────────────────
echo ""
echo -e "${GREEN}✓ Deployment complete!${NC}"
echo "  Site:    https://$DOMAIN"
echo "  Admin:   https://$DOMAIN/admin"
echo "  Logs:    sudo journalctl -u $SERVICE_NAME -f"
echo ""
echo "  Next: create a superuser with:"
echo "    source $VENV_DIR/bin/activate && cd $APP_DIR && python manage.py createsuperuser"
