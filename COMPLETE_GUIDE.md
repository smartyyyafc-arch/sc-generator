# SC-Generator: Complete Installation & Usage Guide

**Advanced VBS Encryption Tool with One-Click Installer Payloads**

---

## 🚀 QUICK START (One-Click Installation)

### Option 1: Automated Setup

```bash
bash install.sh
./start-all.sh
```

**That's it!** Open http://localhost:3000 in your browser.

### Option 2: Interactive Launcher

```bash
bash run.sh
```

Select option 2 to start everything.

### Option 3: Docker (One Command)

```bash
docker-compose up -d
```

Access at http://localhost:3000

---

## 🎯 TWO MODES: Standard vs One-Click

### Mode 1: Standard Payload Generation

**Use for:** Advanced obfuscation with custom fingerprints and proxies

**Steps:**
1. Upload MSI/EXE file
2. Select encoding technique (12 options)
3. Choose obfuscation level (Low/Medium/High)
4. Select fingerprint (optional)
5. Add proxy (optional)
6. Click "Generate Payload"
7. Download or copy VBS code

**Output:** Raw VBS code ready for customization

**Techniques Available:**
- Base64 (standard)
- Hex (good evasion)
- Array (chunk-based)
- WMI (Shell avoidance)
- Registry (registry-stored)
- Environment (env vars)
- COM (object variation)
- Obfuscated Calls (string concat)
- File Writer (temp files)
- Multi-Encoding (multi-layer)
- Hidden Execution (polymorphic)

### Mode 2: One-Click Installer (NEW!)

**Use for:** Completely invisible, one-click installation

**Steps:**
1. Upload EXE/MSI file
2. Select obfuscation style
3. Choose output format (VBS or BAT)
4. Click "Generate One-Click Installer"
5. Send to user
6. User double-clicks = silent installation

**User Experience:**
- Double-click the file
- Installation completes silently
- No visible output
- Completely invisible to user
- Takes 2-5 seconds
- Done!

**Obfuscation Styles:**
- **Polymorphic** - Different code each generation
- **Anti-Analysis** - Detects analysis tools
- **Multi-Stage** - Staged execution
- **Silent** - No output whatsoever

---

## 📋 INSTALLATION WALKTHROUGH

### First-Time Setup

```bash
# 1. Clone the repository
git clone <repo-url>
cd sc-generator

# 2. Run automated installer
bash install.sh

# 3. Start everything
./start-all.sh

# 4. Open browser
# http://localhost:3000
```

**Installation takes 5-10 minutes**

### What Gets Installed

- ✓ Python 3.8+ with all dependencies
- ✓ Node.js 18+ with all packages
- ✓ React frontend application
- ✓ Flask REST API backend
- ✓ VBS encoding engines
- ✓ Fingerprinting system
- ✓ Proxy management
- ✓ One-click installer generator
- ✓ Startup scripts
- ✓ Docker containers (optional)

---

## 🖥️ USAGE EXAMPLES

### Example 1: Generate Standard Payload

**Scenario:** Need a powershell command executed on target

**Steps:**
1. Upload dummy file (any format)
2. Mode: Standard
3. Technique: WMI
4. Obfuscation: High
5. Fingerprint: Windows Update
6. Generate
7. Download payload.vbs
8. Execute on target: `cscript payload.vbs`

**Result:** Powershell command runs silently

### Example 2: Create One-Click Installer

**Scenario:** Need user to install without suspicion

**Steps:**
1. Upload malware.exe (or legit binary)
2. Mode: One-Click
3. Style: Polymorphic
4. Format: BAT
5. Generate
6. Download "Windows Update.bat"
7. Send to user
8. User double-clicks
9. Silent installation complete

**Result:** Installation happens in 3 seconds, zero visible output

### Example 3: Advanced Fingerprinting

**Scenario:** Target has behavioral detection

**Steps:**
1. Upload payload.exe
2. Mode: Standard
3. Fingerprint: Custom "Office 365"
4. Proxy: Add HTTP proxy
5. Obfuscation: High with Multi-Encoding
6. Enable: Add Comments + Add Noise
7. Generate payload
8. Deploy through proxy

**Result:** Bypasses fingerprint-based detection

### Example 4: Batch Testing

**Scenario:** Don't know which technique works best

**Steps:**
1. Upload test_payload.exe
2. Generate payloads with multiple techniques
3. Test each on target environment
4. Find which works
5. Use that technique for real deployment

**Result:** Data-driven selection of best technique

---

## 🔑 FINGERPRINTING SYSTEM

### Built-in Templates

1. **Windows Update**
   - Appears as legitimate Windows Update process
   - Modifies PE sections
   - Adds system metadata

2. **Adobe Reader**
   - Mimics Adobe Reader signature
   - Uses Adobe version strings
   - Spoofs company metadata

3. **Google Chrome**
   - Matches Chrome executable structure
   - Uses Chrome version info
   - Randomizes section names

4. **System Process**
   - Generic system process fingerprint
   - Looks like native Windows binary
   - Minimal detection risk

5. **Random Variation**
   - Each generation is unique
   - Randomizes everything possible
   - Best for unknown defenses

### Custom Fingerprints

**Create your own:**
1. Click "Custom Fingerprint"
2. Enter name (e.g., "Excel 2019")
3. Configure modifications:
   - PE section modifications
   - Metadata injection
   - String encryption
   - Random junk addition
4. Save and use

### How Fingerprinting Works

1. **PE Modification** - Adds junk, randomizes names
2. **Metadata Spoofing** - Fakes version strings
3. **Section Randomization** - Changes section names
4. **Import Obfuscation** - Hides imports

---

## 🌐 PROXY SUPPORT

### Adding Proxies

**In UI:**
1. Click "Add Proxy" in Proxy Settings
2. Enter proxy URL (e.g., `http://proxy.example.com:8080`)
3. Select type: HTTP, HTTPS, or SOCKS5
4. Click "Add Proxy"

**Proxy Types:**
- **HTTP** - Standard HTTP proxy
- **HTTPS** - Encrypted proxy connection
- **SOCKS5** - SOCKS5 protocol proxy

### Why Use Proxies

- Modify fingerprints based on proxy characteristics
- Evade proxy-based detection
- Test through corporate proxies
- Split detection signatures

### Example: Using Proxies

1. Add proxy: `http://192.168.1.1:3128`
2. Generate payload
3. Execute through proxy
4. Payload looks different to proxy analysis tools
5. Evades proxy-based detection

---

## 📊 AVAILABLE TECHNIQUES COMPARISON

| Technique | Detection | Speed | Size | Best For |
|-----------|-----------|-------|------|----------|
| base64 | Medium | Fast | Medium | Standard evasion |
| hex | Medium-High | Fast | Medium | Good stealth |
| wmi | Medium-High | Medium | Medium | Avoid Shell.Run |
| registry | High | Medium | Large | Persistent storage |
| env | High | Fast | Small | Variable hiding |
| multi_encoding | Very High | Slow | Large | Maximum stealth |
| polymorphic | Very High | Medium | Medium | Signature defeat |

---

## 🛡️ SECURITY CONSIDERATIONS

### Authorized Use ONLY

✅ **Authorized Scenarios:**
- Internal security testing
- Penetration testing (with written authorization)
- Red team exercises (authorized)
- CTF competitions
- Security research on own systems
- Defensive testing

❌ **NOT Authorized:**
- Unauthorized system access
- Malware distribution
- Unauthorized testing
- Any illegal activity

### Best Practices

1. **Always get written authorization** before testing
2. **Document your testing** - keep records
3. **Use isolated environments** when possible
4. **Clean up after testing** - remove all payloads
5. **Follow legal guidelines** in your jurisdiction
6. **Report findings properly** to system owner

---

## 🐛 TROUBLESHOOTING

### Installation Issues

**"Python not found"**
```bash
# Install Python 3.8+
sudo apt-get install python3  # Linux
brew install python3          # macOS
# Windows: python.org
```

**"Node not found"**
```bash
# Install Node.js 16+
# Visit: nodejs.org
```

**"Port 5000 in use"**
```bash
# Change port in app.py
app.run(port=5001)
```

### Runtime Issues

**"Cannot upload file"**
- Check backend is running: `curl http://localhost:5000/api/health`
- Verify file size < 100MB
- Check file type is supported

**"Frontend won't load"**
- Wait 30 seconds for backend to start
- Clear browser cache (Ctrl+Shift+Del)
- Check browser console (F12) for errors

**"Payload generation fails"**
- Check error message in UI
- Verify file was uploaded successfully
- Try smaller test file first
- Check backend logs: `/tmp/sc-logs/backend.log`

---

## 📦 SYSTEM REQUIREMENTS

### Minimum
- Python 3.8+
- Node.js 16+
- 2 GB RAM
- 500 MB disk
- Internet (for dependencies)

### Recommended
- Python 3.10+
- Node.js 18+
- 4 GB RAM
- 2 GB disk
- Stable internet

### Supported OS
- Linux (Ubuntu, Debian, Fedora, etc.)
- macOS
- Windows (with WSL or Git Bash)
- Docker (any OS with Docker installed)

---

## 🔧 CONFIGURATION

### Environment Variables

Create `.env`:
```env
FLASK_ENV=production
FLASK_DEBUG=False
REACT_APP_API_URL=http://localhost:5000/api
MAX_FILE_SIZE=104857600
```

### Flask Settings (app.py)

```python
UPLOAD_FOLDER = '/tmp/sc-uploads'      # Upload dir
OUTPUT_FOLDER = '/tmp/sc-outputs'      # Output dir
MAX_FILE_SIZE = 100 * 1024 * 1024      # 100MB limit
```

### Backend Port

Change in `app.py`:
```python
app.run(port=5001)  # Change from 5000
```

### Frontend Port

Change in package.json:
```json
"scripts": {
  "start": "PORT=3001 react-scripts start"
}
```

---

## 📚 ADDITIONAL DOCUMENTATION

- **SETUP.md** - Detailed setup instructions
- **INSTALL.md** - Installation guide for all platforms
- **QUICKSTART.md** - Quick reference guide
- **README.md** - Feature documentation

---

## 🎓 LEARNING RESOURCES

### Understanding VBS
- Microsoft VBS documentation
- WScript.Shell object reference
- VBS error handling patterns

### Understanding Evasion
- MITRE ATT&CK framework
- Evasion technique databases
- Obfuscation methodologies

### Understanding Detection
- Windows Event Log analysis
- AV/EDR detection mechanisms
- Behavioral analysis techniques

---

## 🚀 PRODUCTION DEPLOYMENT

### Using Gunicorn + Nginx

```bash
# Install gunicorn
pip install gunicorn

# Start backend
gunicorn -w 4 -b 0.0.0.0:5000 app:app

# Configure Nginx to reverse proxy
# Point /api to localhost:5000
# Serve static build/ directory
```

### Using Docker

```bash
# Build image
docker build -t sc-generator:latest .

# Run container
docker run -p 5000:5000 -p 3000:3000 sc-generator

# Or use docker-compose
docker-compose up -d
```

### Using Systemd (Linux)

Create `/etc/systemd/system/sc-generator.service`:
```ini
[Unit]
Description=SC-Generator
After=network.target

[Service]
Type=simple
User=appuser
WorkingDirectory=/opt/sc-generator
ExecStart=/opt/sc-generator/venv/bin/python3 app.py

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable sc-generator
sudo systemctl start sc-generator
```

---

## 📞 GETTING HELP

### Logs

**Backend logs:**
```bash
tail -f /tmp/sc-logs/backend.log
```

**Frontend logs:**
- Open browser console: F12
- Check Network tab for API errors

### Debugging

**Enable debug mode:**
```bash
export FLASK_DEBUG=True
export FLASK_ENV=development
python3 app.py
```

**API health check:**
```bash
curl http://localhost:5000/api/health
```

**Test file upload:**
```bash
curl -X POST -F "file=@test.exe" http://localhost:5000/api/upload
```

---

## 📋 CHECKLIST: Ready to Deploy?

- [ ] Installation completed successfully
- [ ] Backend running without errors
- [ ] Frontend accessible at localhost:3000
- [ ] File upload working
- [ ] Payload generation working
- [ ] Download functionality working
- [ ] All techniques tested
- [ ] Fingerprints configured
- [ ] Proxies configured (if needed)
- [ ] One-click installer tested
- [ ] Authorization obtained (if applicable)
- [ ] Test environment isolated
- [ ] Logging configured
- [ ] Security considerations reviewed

---

## ⚖️ LEGAL DISCLAIMER

SC-Generator is provided for authorized security testing, pentesting, and security research only. Users are responsible for:

1. **Obtaining proper authorization** before testing
2. **Following applicable laws** in their jurisdiction
3. **Using ethically and legally**
4. **Not using for malicious purposes**
5. **Properly disclosing findings**

Unauthorized access to computer systems is illegal in most jurisdictions.

---

## 🎉 Ready to Launch!

```bash
# One-click installation
bash install.sh

# Start everything
./start-all.sh

# Access at
http://localhost:3000
```

**Happy testing!**

---

**Version:** 1.0.0  
**Last Updated:** 2026-06-29  
**Status:** Production Ready ✓

For updates, visit: [repository URL]
