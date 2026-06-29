#!/bin/bash

#############################################################################
# SC-Generator: One-Click Automated Installation
# Complete setup for VBS encryption tool with web UI
#############################################################################

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ASCII Banner
echo -e "${BLUE}"
cat << "EOF"
 ___  _____         ___                       _           _
/ __||_   _|       / _ \  ___  _ __   ___  __| | __ _  __|_  _   _  __
\__ \  | |        | | | |/ _ \| '_ \ / _ \/ _` |/ _` |/ _ \ | | | |/ _ \
|___/  |_|        | |_| | (_) | | | |  __/ (_| | (_| |  __/ | |_| | __/
                   \__\_\\___/|_| |_|\___|\__,_|\__,_|\___| |_|__, |\___|
                                                              |___/
EOF
echo -e "${NC}"

echo -e "${GREEN}[+] SC-Generator Installation${NC}"
echo -e "${BLUE}════════════════════════════════════════════${NC}"
echo ""

# Check OS
OS="Unknown"
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="Linux"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macOS"
elif [[ "$OSTYPE" == "msys" ]]; then
    OS="Windows (Git Bash)"
fi

echo -e "${BLUE}[*] Detected OS: ${OS}${NC}"
echo ""

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
echo -e "${YELLOW}[*] Checking prerequisites...${NC}"

if ! command_exists python3; then
    echo -e "${RED}[!] Python 3 not found. Please install Python 3.8+${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo -e "${GREEN}[+] Python ${PYTHON_VERSION} found${NC}"

if ! command_exists node; then
    echo -e "${RED}[!] Node.js not found. Please install Node.js 16+${NC}"
    exit 1
fi

NODE_VERSION=$(node --version)
echo -e "${GREEN}[+] Node.js ${NODE_VERSION} found${NC}"

if ! command_exists npm; then
    echo -e "${RED}[!] npm not found. Please install npm${NC}"
    exit 1
fi

NPM_VERSION=$(npm --version)
echo -e "${GREEN}[+] npm ${NPM_VERSION} found${NC}"

echo ""

# Create virtual environment
echo -e "${YELLOW}[*] Setting up Python virtual environment...${NC}"
python3 -m venv venv
source venv/bin/activate
echo -e "${GREEN}[+] Virtual environment created${NC}"

# Upgrade pip
echo -e "${YELLOW}[*] Upgrading pip...${NC}"
pip install --upgrade pip >/dev/null 2>&1
echo -e "${GREEN}[+] pip upgraded${NC}"

# Install Python dependencies
echo -e "${YELLOW}[*] Installing Python dependencies...${NC}"
pip install -q -r requirements.txt
if [ $? -eq 0 ]; then
    echo -e "${GREEN}[+] Python dependencies installed${NC}"
else
    echo -e "${RED}[!] Failed to install Python dependencies${NC}"
    exit 1
fi

# Install Node dependencies
echo -e "${YELLOW}[*] Installing Node.js dependencies...${NC}"
npm install -q
if [ $? -eq 0 ]; then
    echo -e "${GREEN}[+] Node.js dependencies installed${NC}"
else
    echo -e "${RED}[!] Failed to install Node.js dependencies${NC}"
    exit 1
fi

# Create necessary directories
echo -e "${YELLOW}[*] Creating directories...${NC}"
mkdir -p /tmp/sc-uploads
mkdir -p /tmp/sc-outputs
mkdir -p /tmp/sc-fingerprints
mkdir -p /tmp/sc-logs
chmod 755 /tmp/sc-*
echo -e "${GREEN}[+] Directories created${NC}"

# Create config file
echo -e "${YELLOW}[*] Creating configuration...${NC}"
cat > .env << 'ENVEOF'
FLASK_ENV=production
FLASK_DEBUG=False
REACT_APP_API_URL=http://localhost:5000/api
NODE_ENV=production
ENVEOF
echo -e "${GREEN}[+] Configuration created${NC}"

# Create startup script
echo -e "${YELLOW}[*] Creating startup scripts...${NC}"

cat > start-backend.sh << 'STARTEOF'
#!/bin/bash
source venv/bin/activate
python3 app.py
STARTEOF

cat > start-frontend.sh << 'STARTEOF'
#!/bin/bash
npm start
STARTEOF

cat > start-all.sh << 'STARTEOF'
#!/bin/bash

# Start backend in background
echo "[+] Starting backend server..."
source venv/bin/activate
python3 app.py > /tmp/sc-logs/backend.log 2>&1 &
BACKEND_PID=$!
echo "[+] Backend started (PID: $BACKEND_PID)"

# Wait for backend to start
sleep 3

# Start frontend
echo "[+] Starting frontend..."
npm start
STARTEOF

chmod +x start-backend.sh start-frontend.sh start-all.sh
echo -e "${GREEN}[+] Startup scripts created${NC}"

# Build frontend (optional)
echo ""
echo -e "${YELLOW}[*] Building frontend (this may take a moment)...${NC}"
npm run build >/dev/null 2>&1
echo -e "${GREEN}[+] Frontend built${NC}"

# Create quick start guide
echo -e "${YELLOW}[*] Creating quick start guide...${NC}"

cat > QUICKSTART.md << 'QUICKEOF'
# SC-Generator Quick Start

## Starting the Application

### Option 1: Start Everything (Recommended)
```bash
./start-all.sh
```

### Option 2: Start Services Separately

**Terminal 1 - Start Backend:**
```bash
source venv/bin/activate
python3 app.py
```
Backend runs on: http://localhost:5000

**Terminal 2 - Start Frontend:**
```bash
npm start
```
Frontend opens on: http://localhost:3000

## First Time Usage

1. The UI will open automatically at http://localhost:3000
2. Upload an MSI/EXE file
3. Select an encoding technique
4. Configure fingerprint (optional)
5. Add proxy (optional)
6. Click "Generate Payload"
7. Download or copy the generated VBS

## Stopping

- Press Ctrl+C in each terminal
- Or run: `pkill -f "python3 app.py"` and `pkill -f "npm start"`

## Troubleshooting

**Port already in use:**
```bash
# Change port in app.py
app.run(port=5001)
```

**Frontend won't load:**
- Wait 30 seconds for backend to start
- Check http://localhost:5000/api/health

**File upload fails:**
- Check browser console for errors
- Verify backend is running

## Uninstall

```bash
rm -rf venv node_modules /tmp/sc-*
```

More help: See SETUP.md and README.md
QUICKEOF

echo -e "${GREEN}[+] Quick start guide created${NC}"

# Final summary
echo ""
echo -e "${BLUE}════════════════════════════════════════════${NC}"
echo -e "${GREEN}[✓] Installation Complete!${NC}"
echo -e "${BLUE}════════════════════════════════════════════${NC}"
echo ""
echo -e "${YELLOW}Ready to launch:${NC}"
echo -e "  ${GREEN}./start-all.sh${NC}          - Start everything automatically"
echo -e "  ${GREEN}./start-backend.sh${NC}      - Start backend only"
echo -e "  ${GREEN}./start-frontend.sh${NC}     - Start frontend only"
echo ""
echo -e "${YELLOW}Access the application:${NC}"
echo -e "  Frontend:  ${GREEN}http://localhost:3000${NC}"
echo -e "  Backend:   ${GREEN}http://localhost:5000${NC}"
echo -e "  API:       ${GREEN}http://localhost:5000/api${NC}"
echo ""
echo -e "${YELLOW}Documentation:${NC}"
echo -e "  Quick Start:  QUICKSTART.md"
echo -e "  Setup Guide:  SETUP.md"
echo -e "  Full README:  README.md"
echo ""
echo -e "${GREEN}[+] To get started, run:${NC}"
echo -e "    ${YELLOW}./start-all.sh${NC}"
echo ""
