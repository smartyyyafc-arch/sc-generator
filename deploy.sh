#!/bin/bash
set -euo pipefail

#############################################################
# SC-Generator VPS Deployment Script
# Run this on your VPS as root or with sudo
#
# Usage (one-liner from your VPS):
#   curl -fsSL https://raw.githubusercontent.com/smartyyyafc-arch/sc-generator/claude/codebase-audit-agents-es4ogc/deploy.sh | bash
#
# Or clone and run:
#   git clone https://github.com/smartyyyafc-arch/sc-generator.git
#   cd sc-generator
#   git checkout claude/codebase-audit-agents-es4ogc
#   chmod +x deploy.sh && sudo ./deploy.sh
#############################################################

RED='\033[0;31m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
NC='\033[0m'

log()  { echo -e "${GREEN}[+]${NC} $1"; }
warn() { echo -e "${YELLOW}[!]${NC} $1"; }
err()  { echo -e "${RED}[x]${NC} $1"; exit 1; }

INSTALL_DIR="/opt/sc-generator"
SERVICE_USER="scgen"
FLASK_PORT=5000
REPO_URL="https://github.com/smartyyyafc-arch/sc-generator.git"
BRANCH="claude/codebase-audit-agents-es4ogc"

echo -e "${CYAN}"
echo "============================================"
echo "  SC-Generator VPS Deployment"
echo "  Automated setup script"
echo "============================================"
echo -e "${NC}"

# Check root
if [ "$(id -u)" -ne 0 ]; then
    err "This script must be run as root (use sudo)"
fi

# Detect OS
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
    OS_VERSION=$VERSION_ID
    log "Detected OS: $PRETTY_NAME"
else
    err "Cannot detect OS. Supported: Ubuntu, Debian, CentOS/Rocky/Alma"
fi

#############################################################
# Step 1: Install system dependencies
#############################################################
log "Installing system dependencies..."

case "$OS" in
    ubuntu|debian)
        export DEBIAN_FRONTEND=noninteractive
        apt-get update -qq
        apt-get install -y -qq python3 python3-pip python3-venv git nginx curl ufw ca-certificates gnupg > /dev/null 2>&1
        # Install Node.js 18 LTS via NodeSource setup script
        if ! node --version 2>/dev/null | grep -qE '^v(1[89]|[2-9][0-9])\.'; then
            log "Installing Node.js 18 LTS..."
            # Remove any old nodejs/npm first
            apt-get remove -y nodejs npm > /dev/null 2>&1 || true
            # Use NodeSource setup script
            curl -fsSL https://deb.nodesource.com/setup_18.x -o /tmp/nodesource_setup.sh
            bash /tmp/nodesource_setup.sh
            apt-get install -y -qq nodejs > /dev/null 2>&1
            rm -f /tmp/nodesource_setup.sh
        fi
        log "Node.js version: $(node --version)"
        ;;
    centos|rocky|almalinux|rhel)
        dnf install -y python3 python3-pip git nginx curl firewalld > /dev/null 2>&1
        if ! node --version 2>/dev/null | grep -qE '^v(1[89]|[2-9][0-9])\.'; then
            log "Installing Node.js 18 LTS from NodeSource..."
            curl -fsSL https://rpm.nodesource.com/setup_18.x | bash - > /dev/null 2>&1
            dnf install -y nodejs > /dev/null 2>&1
        fi
        log "Node.js version: $(node --version)"
        ;;
    *)
        err "Unsupported OS: $OS. Supported: ubuntu, debian, centos, rocky, almalinux"
        ;;
esac

log "System dependencies installed"

#############################################################
# Step 2: Create service user
#############################################################
if ! id "$SERVICE_USER" &>/dev/null; then
    useradd -r -m -d "$INSTALL_DIR" -s /bin/false "$SERVICE_USER"
    log "Created service user: $SERVICE_USER"
else
    log "Service user $SERVICE_USER already exists"
fi

#############################################################
# Step 3: Clone/update repository
#############################################################
if [ -d "$INSTALL_DIR/.git" ]; then
    log "Updating existing installation..."
    cd "$INSTALL_DIR"
    git fetch origin "$BRANCH"
    git checkout "$BRANCH"
    git reset --hard "origin/$BRANCH"
else
    log "Cloning repository..."
    rm -rf "$INSTALL_DIR"
    git clone -b "$BRANCH" "$REPO_URL" "$INSTALL_DIR"
fi

cd "$INSTALL_DIR"
chown -R "$SERVICE_USER:$SERVICE_USER" "$INSTALL_DIR"
log "Repository ready at $INSTALL_DIR"

#############################################################
# Step 4: Set up Python virtual environment
#############################################################
log "Setting up Python environment..."

python3 -m venv "$INSTALL_DIR/venv"
source "$INSTALL_DIR/venv/bin/activate"

pip install --upgrade pip -q
pip install -r requirements.txt -q
pip install gunicorn -q

log "Python dependencies installed"

#############################################################
# Step 5: Build React frontend
#############################################################
log "Building React frontend..."

cd "$INSTALL_DIR"
npm ci --silent 2>/dev/null || npm install --silent
npx react-scripts build 2>/dev/null

log "Frontend built successfully"

#############################################################
# Step 6: Create working directories
#############################################################
log "Creating working directories..."

mkdir -p /tmp/sc-uploads /tmp/sc-outputs /tmp/sc-fingerprints /tmp/sc-logs
chown -R "$SERVICE_USER:$SERVICE_USER" /tmp/sc-uploads /tmp/sc-outputs /tmp/sc-fingerprints /tmp/sc-logs
chmod 700 /tmp/sc-fingerprints

#############################################################
# Step 7: Create environment file
#############################################################
log "Creating environment configuration..."

cat > "$INSTALL_DIR/.env" << 'ENVEOF'
FLASK_ENV=production
FLASK_DEBUG=false
FLASK_HOST=127.0.0.1
FLASK_PORT=5000
CORS_ORIGINS=*
ENVEOF

chmod 600 "$INSTALL_DIR/.env"
chown "$SERVICE_USER:$SERVICE_USER" "$INSTALL_DIR/.env"

#############################################################
# Step 8: Create gunicorn config
#############################################################
log "Creating gunicorn configuration..."

cat > "$INSTALL_DIR/gunicorn.conf.py" << 'GUNIEOF'
import multiprocessing

bind = "127.0.0.1:5000"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
timeout = 120
keepalive = 5
max_requests = 1000
max_requests_jitter = 50
accesslog = "/tmp/sc-logs/access.log"
errorlog = "/tmp/sc-logs/error.log"
loglevel = "info"
GUNIEOF

chown "$SERVICE_USER:$SERVICE_USER" "$INSTALL_DIR/gunicorn.conf.py"

#############################################################
# Step 9: Create systemd service
#############################################################
log "Creating systemd service..."

cat > /etc/systemd/system/sc-generator.service << SVCEOF
[Unit]
Description=SC-Generator - VBS Payload Framework
After=network.target
Wants=network-online.target

[Service]
Type=exec
User=$SERVICE_USER
Group=$SERVICE_USER
WorkingDirectory=$INSTALL_DIR
Environment=PATH=$INSTALL_DIR/venv/bin:/usr/local/bin:/usr/bin:/bin
EnvironmentFile=$INSTALL_DIR/.env
ExecStart=$INSTALL_DIR/venv/bin/gunicorn -c gunicorn.conf.py app:app
ExecReload=/bin/kill -HUP \$MAINPID
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

# Security hardening
NoNewPrivileges=yes
ProtectSystem=strict
ProtectHome=yes
ReadWritePaths=/tmp/sc-uploads /tmp/sc-outputs /tmp/sc-fingerprints /tmp/sc-logs
PrivateTmp=no

[Install]
WantedBy=multi-user.target
SVCEOF

systemctl daemon-reload
systemctl enable sc-generator
log "Systemd service created and enabled"

#############################################################
# Step 10: Configure Nginx reverse proxy
#############################################################
log "Configuring Nginx..."

# Remove default site
rm -f /etc/nginx/sites-enabled/default 2>/dev/null || true

cat > /etc/nginx/sites-available/sc-generator << 'NGINXEOF'
server {
    listen 80 default_server;
    listen [::]:80 default_server;
    server_name _;

    # Serve React frontend
    root /opt/sc-generator/build;
    index index.html;

    # Frontend routes - serve index.html for SPA
    location / {
        try_files $uri $uri/ /index.html;
    }

    # Proxy API requests to Flask/Gunicorn
    location /api/ {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # File upload size
        client_max_body_size 100M;

        # Timeouts for payload generation
        proxy_read_timeout 120s;
        proxy_connect_timeout 10s;
    }

    # Cache static assets
    location /static/ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Security headers
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
}
NGINXEOF

# Enable site
ln -sf /etc/nginx/sites-available/sc-generator /etc/nginx/sites-enabled/sc-generator 2>/dev/null || \
    cp /etc/nginx/sites-available/sc-generator /etc/nginx/conf.d/sc-generator.conf

# Test nginx config
nginx -t 2>/dev/null || err "Nginx configuration test failed"

log "Nginx configured"

#############################################################
# Step 11: Configure firewall
#############################################################
log "Configuring firewall..."

case "$OS" in
    ubuntu|debian)
        if command -v ufw &>/dev/null; then
            ufw --force enable > /dev/null 2>&1 || true
            ufw allow 22/tcp > /dev/null 2>&1
            ufw allow 80/tcp > /dev/null 2>&1
            ufw allow 443/tcp > /dev/null 2>&1
            log "UFW firewall configured (ports 22, 80, 443)"
        fi
        ;;
    centos|rocky|almalinux|rhel)
        if command -v firewall-cmd &>/dev/null; then
            systemctl enable --now firewalld > /dev/null 2>&1 || true
            firewall-cmd --permanent --add-service=http > /dev/null 2>&1
            firewall-cmd --permanent --add-service=https > /dev/null 2>&1
            firewall-cmd --permanent --add-service=ssh > /dev/null 2>&1
            firewall-cmd --reload > /dev/null 2>&1
            log "firewalld configured (ssh, http, https)"
        fi
        ;;
esac

#############################################################
# Step 12: Start services
#############################################################
log "Starting services..."

systemctl restart sc-generator
systemctl restart nginx

sleep 2

# Verify services are running
if systemctl is-active --quiet sc-generator; then
    log "SC-Generator service: RUNNING"
else
    warn "SC-Generator service failed to start. Check: journalctl -u sc-generator -n 50"
fi

if systemctl is-active --quiet nginx; then
    log "Nginx service: RUNNING"
else
    warn "Nginx failed to start. Check: journalctl -u nginx -n 50"
fi

# Health check
sleep 1
if curl -sf http://127.0.0.1:5000/api/health > /dev/null 2>&1; then
    log "API health check: PASSED"
else
    warn "API health check failed - service may still be starting"
fi

#############################################################
# Done!
#############################################################
SERVER_IP=$(curl -sf https://ifconfig.me 2>/dev/null || hostname -I | awk '{print $1}')

echo ""
echo -e "${CYAN}============================================${NC}"
echo -e "${GREEN}  SC-Generator deployed successfully!${NC}"
echo -e "${CYAN}============================================${NC}"
echo ""
echo -e "  ${CYAN}Web UI:${NC}     http://$SERVER_IP"
echo -e "  ${CYAN}API:${NC}        http://$SERVER_IP/api/health"
echo ""
echo -e "  ${CYAN}Service:${NC}    systemctl status sc-generator"
echo -e "  ${CYAN}Logs:${NC}       journalctl -u sc-generator -f"
echo -e "  ${CYAN}Restart:${NC}    systemctl restart sc-generator"
echo -e "  ${CYAN}Nginx:${NC}      systemctl status nginx"
echo ""
echo -e "  ${CYAN}Install dir:${NC} $INSTALL_DIR"
echo -e "  ${CYAN}Config:${NC}      $INSTALL_DIR/.env"
echo ""
echo -e "${YELLOW}  For authorized security research only.${NC}"
echo ""
