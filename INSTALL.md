# SC-Generator: Installation Guide

Complete guide for installing SC-Generator in multiple environments.

## ⚡ Quick Install (One Click)

### Linux/macOS

```bash
curl -sSL https://your-repo-url/install.sh | bash
./start-all.sh
```

Open browser to: **http://localhost:3000**

### Windows (PowerShell)

```powershell
python setup.py
npm start
```

## 🎯 Installation Methods

### Method 1: Automated Script (Recommended)

```bash
# Download and run installer
bash install.sh

# Start application
./start-all.sh
```

**What it does:**
- ✓ Checks Python 3.8+ and Node.js 16+
- ✓ Creates Python virtual environment
- ✓ Installs all dependencies
- ✓ Creates required directories
- ✓ Builds frontend application
- ✓ Creates startup scripts

**Time required:** 5-10 minutes

### Method 2: Manual Installation

**Step 1: Python Setup**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**Step 2: Node Setup**
```bash
npm install
npm run build
```

**Step 3: Create Directories**
```bash
mkdir -p /tmp/sc-{uploads,outputs,fingerprints,logs}
```

**Step 4: Run Application**
```bash
# Terminal 1
source venv/bin/activate
python3 app.py

# Terminal 2
npm start
```

### Method 3: Docker (Container)

**Prerequisites:** Docker and Docker Compose

**Step 1: Build Image**
```bash
docker build -t sc-generator:latest .
```

**Step 2: Run Container**
```bash
docker-compose up -d
```

**Step 3: Access Application**
```bash
http://localhost:3000
```

**Useful Docker Commands:**
```bash
# View logs
docker-compose logs -f

# Stop container
docker-compose down

# Rebuild
docker-compose build --no-cache
```

### Method 4: Production Deployment

**Using Gunicorn + Nginx**

```bash
# Install gunicorn
pip install gunicorn

# Start backend
gunicorn -w 4 -b 0.0.0.0:5000 app:app

# Build and serve frontend (static)
npm run build
# Serve build/ directory with nginx
```

## 📋 System Requirements

### Minimum
- Python 3.8+
- Node.js 16+
- 2 GB RAM
- 500 MB disk space
- Internet connection (for dependencies)

### Recommended
- Python 3.10+
- Node.js 18+
- 4 GB RAM
- 2 GB disk space
- Stable internet connection

## 🔧 Configuration

### Environment Variables

Create `.env` file:

```env
# Flask
FLASK_ENV=production
FLASK_DEBUG=False

# React
REACT_APP_API_URL=http://localhost:5000/api

# Node
NODE_ENV=production

# File Limits
MAX_FILE_SIZE=104857600  # 100MB
```

### Python Configuration (app.py)

```python
UPLOAD_FOLDER = '/tmp/sc-uploads'
OUTPUT_FOLDER = '/tmp/sc-outputs'
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
app.config['JSON_SORT_KEYS'] = False
app.config['PROPAGATE_EXCEPTIONS'] = True
```

## 🚀 Starting the Application

### Option 1: All-in-One Script
```bash
./start-all.sh
```

### Option 2: Separate Terminals
```bash
# Terminal 1 - Backend
source venv/bin/activate
python3 app.py

# Terminal 2 - Frontend
npm start
```

### Option 3: Interactive Launcher
```bash
./run.sh
```

## 🌐 Accessing the Application

After installation, access via:

| Component | URL | Purpose |
|-----------|-----|---------|
| Frontend | http://localhost:3000 | Web UI |
| Backend | http://localhost:5000 | API Server |
| API Docs | http://localhost:5000/api | API Endpoints |
| Health | http://localhost:5000/api/health | Server Status |

## ✅ Verification

### Check Backend
```bash
curl http://localhost:5000/api/health
# Should return: {"status":"ok","version":"1.0.0"}
```

### Check Frontend
```bash
curl http://localhost:3000
# Should return HTML
```

### Check File Upload
```bash
curl -X POST -F "file=@test.msi" http://localhost:5000/api/upload
```

## 🐛 Troubleshooting

### Port Already in Use

**Error:** `Address already in use`

**Solution:**
```bash
# Find process using port
lsof -i :5000
lsof -i :3000

# Kill process
kill -9 <PID>

# Or change port in app.py
app.run(port=5001)
```

### Python Virtual Environment Issues

**Error:** `command not found: python3`

**Solution:**
```bash
# Install Python
# Ubuntu/Debian
sudo apt-get install python3 python3-venv

# macOS
brew install python3

# Windows
# Download from python.org
```

### Node Dependencies Fail

**Error:** `npm ERR! code ERESOLVE`

**Solution:**
```bash
# Clear npm cache
npm cache clean --force

# Reinstall
rm -rf node_modules package-lock.json
npm install
```

### Permission Denied on Scripts

**Error:** `bash: ./install.sh: Permission denied`

**Solution:**
```bash
chmod +x install.sh
chmod +x start-*.sh
chmod +x run.sh
```

### Backend Won't Start

**Error:** `ModuleNotFoundError`

**Solution:**
```bash
# Activate venv
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt

# Check Python version
python3 --version  # Should be 3.8+
```

### Frontend Won't Load

**Error:** `Cannot GET /` or blank page

**Solution:**
```bash
# Kill any running process
pkill -f "npm start"

# Clear cache
rm -rf node_modules/.cache

# Reinstall
npm install

# Start again
npm start
```

## 📦 Uninstall

### Complete Removal

```bash
# Deactivate venv
deactivate

# Remove installation
rm -rf venv node_modules .env *.log

# Clean up temp files
rm -rf /tmp/sc-*

# Remove startup scripts (optional)
rm -f start-*.sh run.sh
```

## 🔒 Security After Installation

1. **Change default permissions:**
```bash
chmod 700 /tmp/sc-*
```

2. **Use HTTPS in production:**
- Install SSL certificate
- Update API_URL in frontend to use https://

3. **Set environment to production:**
```bash
export FLASK_ENV=production
export NODE_ENV=production
```

## 📊 Installation Verification Checklist

- [ ] Python 3.8+ installed
- [ ] Node.js 16+ installed
- [ ] Virtual environment created
- [ ] Dependencies installed
- [ ] Directories created
- [ ] Frontend built
- [ ] Backend starts without errors
- [ ] Frontend accessible at localhost:3000
- [ ] API responds to /api/health
- [ ] File upload works
- [ ] Payload generation works

## 🆘 Getting Help

If installation fails:

1. **Check logs:**
   - Backend: `/tmp/sc-logs/backend.log`
   - Frontend: Browser console (F12)

2. **Verify requirements:**
   ```bash
   python3 --version
   node --version
   npm --version
   ```

3. **Try clean install:**
   ```bash
   bash uninstall.sh  # If available
   bash install.sh    # Fresh install
   ```

4. **Check documentation:**
   - SETUP.md - Detailed setup
   - README.md - Feature guide
   - QUICKSTART.md - Quick reference

## 📈 Post-Installation

After successful installation:

1. **Read QUICKSTART.md** for first-time usage
2. **Configure fingerprints** for your target
3. **Add proxies** if needed
4. **Test with sample file** before production
5. **Review logs** for any warnings

---

**Installation Complete!** 🎉

Next steps: Read QUICKSTART.md or visit http://localhost:3000
