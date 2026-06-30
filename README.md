# SC-Generator

Advanced VBS payload encryption, obfuscation, and deployment pipeline for authorized security testing, penetration testing education, and CTF exercises.

> **Disclaimer:** This tool is intended exclusively for authorized security research, penetration testing with proper authorization, CTF competitions, and educational purposes. Unauthorized use against systems you do not own or have explicit permission to test is illegal.

## Features

### Four Deployment Modes

| Mode | Description |
|------|-------------|
| **Standard** | Encode and obfuscate payloads with 12 encoding techniques |
| **One-Click** | Self-extracting installer payloads with anti-analysis capabilities |
| **Persistent** | Payloads that survive reboots via registry, WMI, scheduled tasks, and more |
| **Combined** | Composable pipeline merging encoding + installer + persistence into a single payload |

### Encoding Techniques

| Technique | Detection Resistance | Description |
|-----------|---------------------|-------------|
| `base64` | Medium | Base64 encoding with MSXML decoder |
| `hex` | Medium-High | Hexadecimal encoding with Chr() decoder |
| `array` | Medium-High | Array concatenation with chunk-based encoding |
| `wmi` | Medium-High | WMI object-based command execution |
| `registry` | High | Registry-stored payload fragments |
| `environment` | High | Environment variable-based storage |
| `com` | Medium-High | COM object method invocation chains |
| `obfuscated_calls` | High | String-built function name resolution |
| `filewriter` | Medium | Temp file execution pattern |
| `multi_encoding` | Very High | Multiple encoding layers chained together |
| `hidden_execution` | Very High | Polymorphic WScript hidden wrapper |
| `polymorphic` | Very High | Signature-varying output on each generation |

### Installer Types

| Type | Description |
|------|-------------|
| Silent | Zero-visibility execution, no user interaction |
| Multi-Stage | Staged deployment with configurable delays |
| Polymorphic | 5 randomly selected execution templates |
| Anti-Analysis | VM/sandbox/debugger detection before execution |

### Persistence Mechanisms

| Method | Windows Support | Survival Rate |
|--------|-----------------|---------------|
| Registry (HKCU/HKLM Run) | All versions | High |
| Startup Folder | All versions | High |
| Scheduled Tasks | Vista+ | High |
| WMI Event Subscriptions | Vista+ | Very High |
| Windows Service | All versions (admin) | Very High |
| Defender Exclusions | Windows 8+ | Medium |
| Multi-Method (all combined) | All versions | 99%+ |

### Combined Pipeline Presets

| Preset | Encoding | Installer | Persistence | Size | Success Rate |
|--------|----------|-----------|-------------|------|-------------|
| `stealth_pro` | Multi-Encoding | Anti-Analysis | WMI | 8-15 KB | 94% |
| `reliable_max` | Base64 | Silent | Registry | 4-8 KB | 98% |
| `quick_deploy` | Hex | None | None | 2-4 KB | 99% |
| `full_arsenal` | Polymorphic | Polymorphic | Scheduled Task | 12-20 KB | 91% |
| `silent_persistent` | Environment | Multi-Stage | Startup Folder | 6-10 KB | 96% |

### Additional Features

- **PE Fingerprint Spoofing** -- Modify PE metadata to match known legitimate software (Windows Update, Adobe Reader, Chrome, etc.)
- **Proxy Configuration** -- Route traffic through SOCKS5 and HTTP/HTTPS proxies
- **Batch Generation** -- Generate multiple payload variants across techniques in one operation
- **Polymorphic Output** -- Each generation produces unique signatures that defeat static analysis
- **Recommendations Engine** -- Mode-specific best-practice guidance with expected performance metrics

## Architecture

```
sc-generator/
+-- app.py                          # Flask API server (20 endpoints)
+-- combined_pipeline.py            # Combined deployment pipeline with 5 presets
+-- payload_generator.py            # Unified payload generation engine with caching
+-- vbs_encoder.py                  # Base encoding/obfuscation (12 techniques)
+-- vbs_advanced_obfuscation.py     # Advanced stealth techniques (WMI, registry, COM)
+-- payload_installer.py            # Self-extracting installer generation
+-- persistence_manager.py          # Multi-method persistence (7 mechanisms)
+-- fingerprint_manager.py          # PE fingerprint spoofing & proxy management
+-- examples.py                     # Usage examples
+-- test_vbs_encoder.py             # Unit tests
+-- src/
|   +-- App.jsx                     # Main React app with 4 deployment modes
|   +-- App.css                     # Dark cyberpunk theme styles
|   +-- config.js                   # Shared configuration (API_BASE)
|   +-- index.jsx                   # React entry point
|   +-- components/
|       +-- FileUpload.jsx          # Drag-and-drop file upload (.exe/.msi)
|       +-- PayloadGenerator.jsx    # Encoding technique & obfuscation selector
|       +-- CombinedMode.jsx        # Combined pipeline UI with preset cards
|       +-- OneClickInstaller.jsx   # One-click installer configuration
|       +-- PersistencePayload.jsx  # Persistence method selector
|       +-- OutputDisplay.jsx       # Code preview, copy, and download
|       +-- FingerprintSelector.jsx # PE fingerprint profile manager
|       +-- ProxyManager.jsx        # Proxy configuration UI
|       +-- RecommendationCard.jsx  # Mode-specific best-practice tips
+-- Dockerfile                      # Multi-stage build, non-root user
+-- docker-compose.yml              # Production deployment
+-- .dockerignore                   # Build context exclusions
+-- requirements.txt                # Python dependencies
+-- requirements_secure.txt         # Enhanced security dependencies
```

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- npm 9+

### Local Development

```bash
# Clone the repository
git clone https://github.com/smartyyyafc-arch/sc-generator.git
cd sc-generator

# Install Python dependencies
pip install -r requirements.txt

# Install frontend dependencies
npm install

# Start the Flask backend (port 5000)
python app.py

# In a separate terminal, start the React frontend (port 3000)
npm start
```

### Docker Deployment

```bash
# Build and run with Docker Compose
docker compose up --build

# Or build the image directly
docker build -t sc-generator .
docker run -p 5000:5000 sc-generator
```

The Docker image uses a multi-stage build (build tools excluded from production), runs as a non-root user, and includes a health check on `/api/health`.

### CLI Usage

```bash
# List available techniques
python3 payload_generator.py --list-techniques

# Generate a base64-encoded payload
python3 payload_generator.py -c "powershell.exe -Command 'Write-Host test'" --technique base64

# Generate with advanced technique and save to file
python3 payload_generator.py -c "cmd /c echo test" --technique multi_encoding -f payload.vbs

# Get technique details
python3 payload_generator.py --technique-info wmi
```

## Programmatic Usage

### Standard Payload Generation

```python
from payload_generator import PayloadGenerator

gen = PayloadGenerator()
payload = gen.generate(
    "powershell.exe -Command 'Write-Host test'",
    technique="base64",
    obfuscation_level="high"
)
```

### Combined Pipeline

```python
from combined_pipeline import CombinedPipeline

pipeline = CombinedPipeline()

# Use a preset
result = pipeline.generate("powershell.exe test", preset="stealth_pro")

# Or customize individual stages
result = pipeline.generate(
    "powershell.exe test",
    encoding="multi_encoding",
    installer="anti_analysis",
    persistence="wmi"
)

print(result['combined_payload'])
print(result['metadata'])  # sizes, stages applied, techniques used
```

### One-Click Installer

```python
from payload_installer import create_one_click_payload

result = create_one_click_payload(
    "powershell.exe test",
    obfuscation_style="polymorphic"  # or anti_analysis, multi_stage, silent
)
print(result['vbs_payload'])
```

### Persistent Payload

```python
from persistence_manager import create_persistent_payload

result = create_persistent_payload(
    "powershell.exe test",
    persistence_method="multi"  # registry, startup, task, wmi, service, multi
)
print(result['vbs_code'])
print(f"Survival rate: {result['survival_rate']}")
```

### Direct Encoder Access

```python
from vbs_encoder import VBSEncoder, generate_clean_vbs_payload
from vbs_advanced_obfuscation import create_stealthy_payload

# Using the encoder directly
encoder = VBSEncoder()
payload = encoder.create_full_obfuscated_payload("cmd /c echo test", "base64")

# Using advanced techniques
stealthy = create_stealthy_payload("powershell.exe test", technique="wmi")
```

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `FLASK_DEBUG` | `false` | Enable Flask debug mode |
| `FLASK_HOST` | `0.0.0.0` | Server bind address |
| `FLASK_PORT` | `5000` | Server port |
| `CORS_ORIGINS` | `http://localhost:3000` | Allowed CORS origins (comma-separated) |
| `REACT_APP_API_URL` | `http://localhost:5000/api` | Backend API URL for frontend |
| `FLASK_ENV` | `production` | Flask environment mode |

### Storage Paths

| Path | Purpose |
|------|---------|
| `/tmp/sc-uploads/` | Uploaded MSI/EXE files (100 MB max) |
| `/tmp/sc-outputs/` | Generated payload files |
| `~/.sc-fingerprints/` | Fingerprint/proxy configs (mode 0700) |

## API Reference

### Core

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/health` | Health check |
| `GET` | `/api/techniques` | List encoding techniques with metadata |
| `GET` | `/api/settings` | Get server settings |
| `POST` | `/api/upload` | Upload MSI/EXE file |
| `POST` | `/api/generate-payload` | Generate standard encoded payload |
| `POST` | `/api/batch-generate` | Generate multiple technique variants |
| `GET` | `/api/download/:id` | Download generated payload |
| `GET` | `/api/preview/:id` | Preview payload content |
| `GET` | `/api/recommendations` | Mode-specific best-practice tips |

### One-Click Installer

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/generate-one-click` | Generate self-extracting installer |
| `GET` | `/api/one-click-styles` | List installer styles |

### Persistence

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/generate-persistent` | Generate persistent payload |
| `GET` | `/api/persistence-methods` | List persistence methods |

### Combined Pipeline

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/generate-combined` | Generate combined multi-stage payload |
| `GET` | `/api/combined-options` | List presets and available options |

### Fingerprinting & Proxies

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/fingerprints` | List PE fingerprint profiles |
| `POST` | `/api/fingerprints` | Create custom fingerprint profile |
| `GET` | `/api/proxies` | List configured proxies |
| `POST` | `/api/proxies` | Add proxy configuration |

## Security

### Built-in Protections

- Path traversal protection on all file operations
- CORS origin restrictions (configurable via environment)
- Security headers: `X-Content-Type-Options`, `X-Frame-Options`, `X-XSS-Protection`, `Content-Security-Policy`, `Referrer-Policy`
- Non-root Docker execution with restricted permissions
- Sanitized error messages (no internal path leakage)
- Secure credential storage with `0o600` file permissions
- Client-side file validation (.exe/.msi only)

### Detection & Response Guidance

For defenders monitoring for these techniques:

- Monitor VBScript execution via process auditing
- Alert on WMI process creation (`Win32_Process.Create`)
- Watch registry writes to `HKCU\...\Run` and `HKLM\...\Run`
- Monitor environment variable creation by script processes
- Track file creation in `%TEMP%` directories
- Watch for WMI event subscriptions in `root\subscription`
- Monitor scheduled task creation via `schtasks`

## Generated Payload Characteristics

- **Legitimate Windows Objects**: Uses built-in COM objects (`WScript.Shell`, `MSXML2.DOMDocument`, `Scripting.FileSystemObject`, etc.)
- **No External Dependencies**: Pure VBScript using native Windows APIs
- **Error Resilient**: `On Error Resume Next` with proper `Err.Clear`
- **Hidden Execution**: Window style 0 for invisible operation
- **Variable Obfuscation**: Random variable and function names on each generation
- **Polymorphic**: Structure changes on every generation to defeat signatures
- **Cross-Version**: Compatible with Windows XP SP3 through Windows 11

## Legal Use

- Authorized penetration testing engagements
- Testing your own infrastructure
- Security research on systems you own or control
- CTF challenges and authorized competitions
- Security training and education

## Tech Stack

- **Backend**: Flask 3.0, Werkzeug 3.0, Flask-CORS 4.0, python-dotenv
- **Frontend**: React 18, Axios, Create React App
- **Deployment**: Docker (multi-stage build), Docker Compose
- **Languages**: Python 3.11, JavaScript/JSX

## Performance

- **Generation**: < 100ms per payload
- **Payload Size**: 0.5 KB (quick_deploy) to 20 KB (full_arsenal)
- **Batch Generation**: Parallel via ThreadPoolExecutor
- **Caching**: LRU cache for non-polymorphic techniques (1000-item max)

## License

For authorized security research and education only.

---

**Version**: 2.0.0
**Last Updated**: 2026-06-30
