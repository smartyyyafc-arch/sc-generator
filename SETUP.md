# SC-Generator: Full Stack Setup Guide

Complete web-based VBS encryption and obfuscation tool with advanced fingerprinting and proxy support.

## 🚀 Quick Start

### Prerequisites
- **Python 3.8+** - Backend engine
- **Node.js 16+** - Frontend development
- **Git** - Version control

### Automated Setup (Linux/macOS)

```bash
# Clone and navigate to repo
git clone <repo-url>
cd sc-generator

# Run setup script
chmod +x setup.sh
./setup.sh
```

### Manual Setup

#### 1. Python Backend Setup

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

#### 2. Frontend Setup

```bash
# Install Node dependencies
npm install
```

#### 3. Create Directories

```bash
mkdir -p /tmp/sc-uploads
mkdir -p /tmp/sc-outputs
mkdir -p /tmp/sc-fingerprints
```

## 🎯 Running the Application

### Terminal 1: Start Backend Server

```bash
# Activate Python environment
source venv/bin/activate

# Start Flask server
python3 app.py
```

Server will run on: `http://localhost:5000`

### Terminal 2: Start Frontend Dev Server

```bash
# Start React development server
npm start
```

Frontend will open on: `http://localhost:3000`

## 📚 Project Structure

```
sc-generator/
├── app.py                          # Flask backend server
├── fingerprint_manager.py          # Fingerprint & proxy handling
├── payload_generator.py            # Unified payload API
├── vbs_encoder.py                 # Base VBS encoding
├── vbs_advanced_obfuscation.py    # Advanced obfuscation techniques
│
├── src/                            # React frontend
│   ├── App.jsx                    # Main app component
│   ├── App.css                    # Styling
│   ├── index.jsx                  # Entry point
│   └── components/
│       ├── FileUpload.jsx         # File upload component
│       ├── PayloadGenerator.jsx   # Technique selector
│       ├── FingerprintSelector.jsx # Fingerprint manager
│       ├── ProxyManager.jsx       # Proxy configuration
│       └── OutputDisplay.jsx      # Results display
│
├── public/
│   └── index.html                 # HTML entry point
│
├── requirements.txt               # Python dependencies
└── package.json                   # Node dependencies
```

## 🎨 Features

### File Upload
- **Drag & Drop** - Easy file upload
- **Supported Formats** - MSI, EXE, DLL, BAT, CMD, VBS
- **File Validation** - Automatic format checking
- **Progress Display** - Upload status and file info

### Encoding Techniques (12 Options)

| Technique | Detection Resistance | Best Use Case |
|-----------|----------------------|---------------|
| **base64** | Medium | Standard obfuscation |
| **hex** | Medium-High | Good evasion |
| **array** | Medium-High | Chunk-based encoding |
| **wmi** | Medium-High | Avoids Shell detection |
| **registry** | High | Registry-based payload |
| **env** | High | Environment variable hiding |
| **com** | Medium-High | COM object variation |
| **obfuscated_calls** | High | String-concatenated names |
| **filewriter** | Medium | Temp file execution |
| **multi_encoding** | Very High | Multiple layers |
| **hidden_execution** | Very High | Polymorphic wrapper |

### Obfuscation Levels
- **Low** - Minimal obfuscation, fast execution
- **Medium** - Balanced stealth and performance
- **High** - Maximum obfuscation (default)

### Fingerprinting System

**Built-in Templates:**
- 🪟 Windows Update
- 🔴 Adobe Reader
- 🌐 Google Chrome
- 💻 System Process
- 🎲 Random Variation

**Custom Fingerprints:**
- Create custom signatures
- Modify PE sections
- Inject metadata
- Add random junk
- Randomize names

### Proxy Support

**Proxy Types:**
- HTTP
- HTTPS
- SOCKS5

**Features:**
- Modify fingerprints based on proxy characteristics
- Validate payloads through proxies
- Multiple proxy configurations
- Persist proxy settings

### Advanced Options
- **Add Comments** - Insert legitimate-looking comments
- **Add Noise** - Add obfuscation code
- **Batch Generation** - Generate with multiple techniques
- **Real-time Preview** - See payload before download

## 🔌 API Endpoints

### Core Endpoints

```
GET  /api/health               # Health check
GET  /api/techniques           # List available techniques
GET  /api/settings             # Get app settings
```

### File Operations

```
POST /api/upload               # Upload MSI/EXE file
POST /api/generate-payload     # Generate VBS payload
GET  /api/download/<id>        # Download payload
GET  /api/preview/<id>         # Preview payload
POST /api/batch-generate       # Batch generation
```

### Fingerprints

```
GET  /api/fingerprints         # List fingerprints
POST /api/fingerprints         # Create custom fingerprint
```

### Proxies

```
GET  /api/proxies              # List configured proxies
POST /api/proxies              # Add proxy configuration
```

## 🔧 Configuration

### Backend Configuration (app.py)

```python
UPLOAD_FOLDER = '/tmp/sc-uploads'      # Upload directory
OUTPUT_FOLDER = '/tmp/sc-outputs'      # Output directory
MAX_FILE_SIZE = 100 * 1024 * 1024      # 100MB limit
```

### Environment Variables

Create `.env` file in root:

```
FLASK_ENV=development
FLASK_DEBUG=True
REACT_APP_API_URL=http://localhost:5000/api
```

## 🛡️ Security Considerations

### For Authorized Testing ONLY

✅ **Authorized Uses:**
- Penetration testing (with client authorization)
- Internal security testing
- Security research on your own systems
- CTF competitions
- Red team exercises

❌ **Unauthorized Uses:**
- Unauthorized system access
- Malware distribution
- Unauthorized testing
- Reverse shells on non-owned systems

### Best Practices

1. **Always get written authorization** before testing
2. **Document your testing** - keep records of work
3. **Use isolated test environments** where possible
4. **Clean up after testing** - remove payloads
5. **Follow legal guidelines** in your jurisdiction

## 📋 Example Workflows

### Workflow 1: Basic MSI Encryption

1. Upload MSI file
2. Select "WMI" technique
3. Set obfuscation to "High"
4. Click "Generate Payload"
5. Download VBS file
6. Execute in target environment

### Workflow 2: Advanced Fingerprinting

1. Upload EXE file
2. Select "Windows Update" fingerprint
3. Add HTTP proxy
4. Use "multi_encoding" technique
5. Enable "Add Comments" and "Add Noise"
6. Generate and test

### Workflow 3: Batch Testing

1. Upload file
2. Select multiple techniques
3. Generate payloads for each
4. Compare sizes and characteristics
5. Choose best for target environment

## 🐛 Troubleshooting

### Backend Issues

**Port already in use:**
```bash
# Change port in app.py
app.run(host='0.0.0.0', port=5001)
```

**CORS errors:**
- Check Flask-CORS is installed
- Verify frontend URL matches `CORS(app)` settings

**File upload fails:**
- Check `/tmp/sc-uploads` permissions
- Verify file size < 100MB
- Check allowed file types

### Frontend Issues

**Blank page:**
- Check browser console for errors
- Verify API server is running
- Check API_BASE URL in App.jsx

**Cannot upload file:**
- Check backend is running
- Verify CORS is enabled
- Check file format is supported

## 📦 Building for Production

### Backend

```bash
# Use production WSGI server
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Frontend

```bash
# Build production bundle
npm run build

# Output in build/ directory
# Deploy to web server (nginx, Apache, etc.)
```

## 🤝 Component Communication

```
React Frontend (port 3000)
         ↓
    axios HTTP
         ↓
Flask Backend (port 5000)
         ↓
   VBS Encoder
   Fingerprint Manager
   Payload Generator
```

## 📊 File Upload Process

```
User selects file
         ↓
Validation (type, size)
         ↓
FormData sent to /api/upload
         ↓
Backend saves to /tmp/sc-uploads
         ↓
Returns file_id
         ↓
Frontend stores for payload generation
```

## 📜 License

For internal use in authorized security testing scenarios only.

---

**Version:** 1.0.0  
**Last Updated:** 2026-06-29  
**Status:** Production Ready
