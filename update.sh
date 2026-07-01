#!/bin/bash
set -euo pipefail

#############################################################
# SC-Generator Quick Update Script
# Run on VPS as root after code changes are pushed
#
# Usage:
#   sudo bash update.sh
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
BRANCH="claude/codebase-audit-agents-es4ogc"

echo -e "${CYAN}"
echo "============================================"
echo "  SC-Generator Update"
echo "============================================"
echo -e "${NC}"

if [ "$(id -u)" -ne 0 ]; then
    err "Run as root (sudo bash update.sh)"
fi

cd "$INSTALL_DIR" || err "Install dir $INSTALL_DIR not found. Run deploy.sh first."

# Step 1: Pull latest code
log "Pulling latest code from $BRANCH..."
git fetch origin "$BRANCH"
git checkout "$BRANCH"
git reset --hard "origin/$BRANCH"
log "Code updated"

# Step 2: Update Python dependencies
log "Updating Python dependencies..."
"$INSTALL_DIR/venv/bin/pip" install -r requirements.txt -q 2>/dev/null
log "Python deps OK"

# Step 3: Rebuild React frontend
log "Rebuilding React frontend..."
npm ci --silent 2>/dev/null || npm install --silent 2>/dev/null
npx react-scripts build 2>/dev/null
log "Frontend built"

# Step 4: Fix ownership
log "Fixing file ownership..."
chown -R scgen:scgen "$INSTALL_DIR"

# Step 5: Restart services
log "Restarting services..."
systemctl restart sc-generator
systemctl restart nginx

sleep 3

# Step 6: Verify
if systemctl is-active --quiet sc-generator; then
    log "SC-Generator service: RUNNING"
else
    warn "SC-Generator service failed!"
    journalctl -u sc-generator -n 20 --no-pager
fi

if systemctl is-active --quiet nginx; then
    log "Nginx: RUNNING"
else
    warn "Nginx failed!"
fi

HEALTH_OK=false
for i in 1 2 3; do
    sleep 2
    if curl -sf http://127.0.0.1:5000/api/health > /dev/null 2>&1; then
        HEALTH_OK=true
        break
    fi
done

if [ "$HEALTH_OK" = true ]; then
    log "API health check: PASSED"
else
    warn "API health check failed"
    warn "Check: journalctl -u sc-generator -n 30 --no-pager"
fi

SERVER_IP=$(curl -sf https://ifconfig.me 2>/dev/null || hostname -I | awk '{print $1}')

echo ""
echo -e "${GREEN}Update complete!${NC}"
echo -e "  ${CYAN}Web UI:${NC}  http://$SERVER_IP"
echo -e "  ${CYAN}API:${NC}     http://$SERVER_IP/api/health"
echo -e "  ${CYAN}Logs:${NC}    journalctl -u sc-generator -f"
echo ""

# Step 7: Quick smoke test
echo -e "${CYAN}--- Smoke Test ---${NC}"

# Test API health
HEALTH=$(curl -sf http://127.0.0.1:5000/api/health 2>/dev/null || echo "FAIL")
echo -e "  Health:      ${GREEN}${HEALTH}${NC}"

# Test techniques endpoint
TECHS=$(curl -sf http://127.0.0.1:5000/api/techniques 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); print(len(d.get('techniques',[])),' techniques')" 2>/dev/null || echo "FAIL")
echo -e "  Techniques:  ${GREEN}${TECHS}${NC}"

# Test persistence methods
PERSIST=$(curl -sf http://127.0.0.1:5000/api/persistence-methods 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); print(', '.join(d.get('methods',{}).keys()))" 2>/dev/null || echo "FAIL")
echo -e "  Persistence: ${GREEN}${PERSIST}${NC}"

# Test combined options
COMBINED=$(curl -sf http://127.0.0.1:5000/api/combined-options 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); print(len(d.get('presets',{})),' presets')" 2>/dev/null || echo "FAIL")
echo -e "  Combined:    ${GREEN}${COMBINED}${NC}"

# Test one-click styles
STYLES=$(curl -sf http://127.0.0.1:5000/api/one-click-styles 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); print(', '.join(d.get('styles',{}).keys()))" 2>/dev/null || echo "FAIL")
echo -e "  Styles:      ${GREEN}${STYLES}${NC}"

# Check frontend build exists
if [ -f "$INSTALL_DIR/build/index.html" ]; then
    FSIZE=$(du -sh "$INSTALL_DIR/build/" | cut -f1)
    echo -e "  Frontend:    ${GREEN}Built (${FSIZE})${NC}"
else
    echo -e "  Frontend:    ${RED}MISSING build/index.html${NC}"
fi

echo ""
echo -e "${GREEN}All checks complete. Open http://$SERVER_IP in your browser.${NC}"
echo ""
