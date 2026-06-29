# Security Fix #4: Proxy Configuration with Actual Forwarding

## Problem Statement

The application had proxy configuration endpoints that stored proxy URLs but did not:
1. Encrypt proxy credentials before storage
2. Implement actual proxy forwarding in HTTP requests
3. Support SOCKS5 proxy protocol (RFC 1928/1929)
4. Properly handle authentication errors
5. Validate proxy connectivity

## Solution Overview

Complete proxy forwarding implementation with:
- **Credential Encryption**: Fernet (AES-128) encryption for proxy credentials
- **Multiple Proxy Types**: HTTP, HTTPS, and SOCKS5 support
- **Proper Forwarding**: Actual proxy usage in requests via `requests` library
- **Error Handling**: Comprehensive validation and error reporting
- **Testing**: Built-in proxy connectivity testing

## Implementation Details

### 1. Credential Encryption (`CredentialManager`)

Located in `fingerprint_manager.py`:

```python
class CredentialManager:
    """Manage credential encryption with Fernet (AES-128)"""
    
    def encrypt_credentials(self, username: str, password: str) -> str:
        """Encrypt username:password before storage"""
        
    def decrypt_credentials(self, encrypted_cred: str) -> Tuple[str, str]:
        """Decrypt credentials for proxy use"""
```

**Features:**
- Key stored with `0o600` permissions (read/write only for owner)
- Fernet provides authenticated encryption (AES-128 CBC + HMAC)
- Base64 encoding for safe storage and transmission
- Automatic key generation on first use

**File Location:** `/tmp/sc-fingerprints/.cred_key`

### 2. Proxy Authentication Encoding (`ProxyAuthEncoder`)

Three authentication methods supported:

#### HTTP Basic Auth
```python
@staticmethod
def encode_http_proxy_auth(username: str, password: str) -> str:
    """Base64-encoded Authorization header value"""
    credentials = f"{username}:{password}"
    encoded = base64.b64encode(credentials.encode()).decode()
    return f"Basic {encoded}"
```

#### SOCKS5 RFC 1929 Auth
```python
@staticmethod
def encode_socks5_auth(username: str, password: str) -> bytes:
    """
    SOCKS5 subnegotiation packet:
    [VER=1] [ULEN] [UNAME] [PLEN] [PASSWD]
    """
```

#### Proxy URL Authentication
```python
@staticmethod
def encode_proxy_url_auth(url: str, username: str, password: str, proxy_type: str) -> str:
    """Embed authentication in proxy URL: scheme://user:pass@host:port"""
```

### 3. SOCKS5 Handler (`SOCKS5Handler`)

Full RFC 1928/1929 implementation:

```python
class SOCKS5Handler:
    """RFC 1928/1929 SOCKS5 proxy implementation"""
    
    def connect(self) -> None:
        """Establish connection to SOCKS5 proxy"""
        
    def negotiate_auth(self, username: Optional[str] = None, 
                      password: Optional[str] = None) -> None:
        """Perform SOCKS5 authentication negotiation"""
        
    def send_connect_request(self, target_host: str, target_port: int) -> None:
        """Send CONNECT request through SOCKS5 proxy"""
```

**Features:**
- TCP connection establishment with timeouts
- Method negotiation (no auth or username/password)
- Proper error handling per SOCKS5 spec
- Complete disconnect/cleanup

### 4. Proxy Forwarder (`ProxyForwarder`)

New class in `app.py` that orchestrates proxy usage:

```python
class ProxyForwarder:
    """Manages proxy forwarding with credential encryption"""
    
    def get_proxies_dict(self, proxy_id: Optional[str] = None) -> Dict[str, str]:
        """Get proxy config in requests library format"""
        
    def create_session(self, proxy_id: Optional[str] = None, 
                      timeout: int = 30) -> requests.Session:
        """Create requests Session with proxy and retry logic"""
        
    def make_request(self, method: str, url: str, proxy_id: Optional[str] = None,
                    timeout: int = 30, **kwargs) -> requests.Response:
        """Make HTTP request with proxy forwarding"""
```

**Features:**
- Automatic retry strategy (exponential backoff, max 3 retries)
- Session pooling and connection reuse
- Proper timeout handling
- Credential decryption on-the-fly
- Comprehensive logging

## API Endpoints

### 1. Add Proxy Configuration

**POST** `/api/proxies`

Request:
```json
{
  "url": "http://proxy.example.com:8080",
  "type": "http",
  "username": "user",
  "password": "pass",
  "verify_ssl": true,
  "headers": {}
}
```

Response (200):
```json
{
  "success": true,
  "id": "a1b2c3d4",
  "url": "http://proxy.example.com:8080",
  "type": "http",
  "has_auth": true,
  "verify_ssl": true,
  "timeout": 30,
  "message": "Proxy configuration added. Credentials are encrypted for security."
}
```

**Security Notes:**
- Credentials are encrypted before storage
- Only username and ID are returned (never plaintext password)
- Supports HTTP, HTTPS, and SOCKS5 proxies
- Optional SSL verification control

### 2. Test Proxy Connectivity

**POST** `/api/proxies/{proxy_id}/test`

Response (200):
```json
{
  "success": true,
  "message": "Proxy connectivity test passed",
  "proxy_id": "a1b2c3d4",
  "proxy_type": "http",
  "test_url": "http://httpbin.org/ip"
}
```

Response (503 on failure):
```json
{
  "success": false,
  "error": "Proxy test failed",
  "message": "Connection timeout through proxy",
  "proxy_id": "a1b2c3d4",
  "proxy_type": "http",
  "suggestions": [
    "Verify proxy URL is correct",
    "Verify proxy credentials if required",
    "Check proxy server is reachable",
    "Verify firewall allows connection",
    "For SOCKS5, ensure RFC 1928/1929 compliance"
  ]
}
```

**Features:**
- Automatic retries (2 attempts with backoff)
- Detailed error messages and suggestions
- Tests actual proxy connectivity
- Non-blocking (timeout: 10s)

### 3. Get Proxy Information

**GET** `/api/proxy-info`

Response (200):
```json
{
  "proxies": [
    {
      "id": "a1b2c3d4",
      "type": "http",
      "url": "http://proxy.example.com:8080",
      "has_auth": true,
      "timeout": 30,
      "verify_ssl": true
    }
  ],
  "count": 1
}
```

**Security Notes:**
- Credentials are never returned
- Only metadata exposed
- Safe for logging and debugging

### 4. Generate Payload with Proxy

**POST** `/api/generate-payload`

Request:
```json
{
  "file_id": "abc123",
  "technique": "polymorphic",
  "obfuscation": "high",
  "fingerprint_id": "fp1",
  "proxy_id": "a1b2c3d4",
  "options": {
    "add_comments": false,
    "add_noise": true
  }
}
```

Response (200):
```json
{
  "success": true,
  "output_id": "xyz789",
  "payload": "...",
  "size": 8192,
  "technique": "polymorphic",
  "obfuscation": "high",
  "fingerprint_applied": true,
  "proxy_used": true,
  "timestamp": "2025-06-29T12:34:56"
}
```

**Proxy Integration:**
- Fingerprint application uses proxy for network operations
- Proxy credentials automatically decrypted
- Connection pooling for efficiency
- Automatic retries with backoff

## Configuration

### Environment Variables

```bash
# Credential key storage location
CRED_KEY_FILE=/tmp/sc-fingerprints/.cred_key

# Proxy timeout (seconds)
PROXY_TIMEOUT_SECONDS=30

# SSL verification (true/false)
PROXY_VERIFY_SSL=true
```

### File Permissions

Encryption key file is created with secure permissions:
```
-rw------- 1 root root 0 Jun 29 12:00 /tmp/sc-fingerprints/.cred_key
```

Permissions breakdown:
- `6` (rw-): Owner can read and write
- `0` (---): Group cannot access
- `0` (---): Others cannot access

## Security Considerations

### 1. Credential Storage

**Before (VULNERABLE):**
```python
proxy_config = {
    'username': 'user',
    'password': 'plaintext_password'  # EXPOSED
}
```

**After (SECURE):**
```python
# Credentials encrypted with Fernet (AES-128)
proxy_config = {
    'username': 'user',
    'password_encrypted': 'gAAAAAB...'  # Encrypted
}
# Decrypted only when creating sessions
username, password = credential_manager.decrypt_credentials(encrypted)
```

### 2. Proxy Forwarding

**Before (NOT IMPLEMENTED):**
```python
# Proxy endpoints existed but weren't used
def add_proxy():
    # Stored proxy but never used it in requests
    return jsonify({'id': proxy_id})

@app.route('/api/generate-payload', methods=['POST'])
def generate_payload():
    # Made requests WITHOUT proxy
    response = requests.get(url)  # No proxy forwarding!
```

**After (IMPLEMENTED):**
```python
# Proxy forwarder orchestrates all proxy operations
proxy_forwarder = ProxyForwarder()

def generate_payload():
    # Uses proxy when specified
    response = proxy_forwarder.make_request(
        'GET', url, 
        proxy_id=proxy_id,  # Actual proxy forwarding
        timeout=30
    )
```

### 3. Error Handling

Comprehensive error handling at multiple levels:

```python
try:
    # Credential decryption
    _, password = credential_manager.decrypt_credentials(encrypted)
except CredentialEncryptionError as e:
    logger.error(f"Decryption failed: {e}")
    raise

try:
    # SOCKS5 connection
    socks5.connect()
    socks5.negotiate_auth(username, password)
except SOCKS5ConnectionError as e:
    logger.error(f"SOCKS5 connection failed: {e}")
    raise

try:
    # HTTP request with proxy
    response = session.request(method, url, timeout=timeout)
except requests.Timeout:
    logger.error(f"Request timeout: {url}")
except requests.ConnectionError:
    logger.error(f"Connection failed: {url}")
```

### 4. Timeout Protection

All proxy operations have timeouts:

```python
# SOCKS5 socket timeout
sock = socket.socket()
sock.settimeout(30)  # 30 seconds

# HTTP request timeout
response = session.request(..., timeout=10)  # 10 seconds for tests

# Flask request timeout
@request_timeout(DEFAULT_REQUEST_TIMEOUT)  # 30 seconds default
```

## Testing

### Test Proxy Connectivity

```bash
curl -X POST http://localhost:5000/api/proxies/a1b2c3d4/test
```

### Add HTTP Proxy with Authentication

```bash
curl -X POST http://localhost:5000/api/proxies \
  -H "Content-Type: application/json" \
  -d '{
    "url": "http://proxy.example.com:8080",
    "type": "http",
    "username": "user",
    "password": "pass"
  }'
```

### Add SOCKS5 Proxy

```bash
curl -X POST http://localhost:5000/api/proxies \
  -H "Content-Type: application/json" \
  -d '{
    "url": "socks5://proxy.example.com:1080",
    "type": "socks5",
    "username": "user",
    "password": "pass"
  }'
```

### Generate Payload with Proxy

```bash
curl -X POST http://localhost:5000/api/generate-payload \
  -H "Content-Type: application/json" \
  -d '{
    "file_id": "abc123",
    "proxy_id": "a1b2c3d4",
    "technique": "polymorphic",
    "obfuscation": "high"
  }'
```

## Logging

All proxy operations are logged with appropriate levels:

```
INFO: Proxy added successfully: a1b2c3d4 (type=http)
INFO: Session configured with proxy: a1b2c3d4
INFO: Making GET request to http://httpbin.org/ip (proxy=a1b2c3d4, timeout=30s)
INFO: Request successful: GET http://httpbin.org/ip (200)
INFO: Proxy test successful: a1b2c3d4

WARNING: Proxy test timeout: a1b2c3d4
WARNING: Proxy not found: invalid_id

ERROR: Failed to encrypt proxy credentials: [reason]
ERROR: Connection failed: http://proxy.example.com:8080 - [reason]
```

## Dependencies

Required packages:
- `requests` - HTTP library with proxy support
- `urllib3` - Retry logic and connection pooling
- `cryptography` - Fernet encryption

Install:
```bash
pip install requests urllib3 cryptography
```

## Migration Guide

If you have existing proxy configurations without encryption:

```python
# Before: Plaintext credentials in storage
old_config = {
    'url': 'http://proxy.example.com:8080',
    'username': 'user',
    'password': 'plaintext'  # VULNERABLE
}

# After: Encrypt credentials
credential_mgr = CredentialManager()
encrypted = credential_mgr.encrypt_credentials('user', 'plaintext')

new_config = {
    'url': 'http://proxy.example.com:8080',
    'username': 'user',
    'password_encrypted': encrypted
}
```

## Compliance & Standards

- **RFC 1928**: SOCKS5 Protocol
- **RFC 1929**: SOCKS5 Authentication
- **FIPS 197**: AES (via cryptography library)
- **HTTP/1.1 Proxy Specification**: RFC 7230-7235

## Future Enhancements

1. **Proxy Pooling**: Multiple proxies with load balancing
2. **Proxy Rotation**: Automatic rotation between proxies
3. **Proxy Validation**: Periodic health checks
4. **Custom Protocols**: Additional proxy types (HTTP/2, QUIC)
5. **Metrics**: Proxy usage statistics and performance monitoring

## References

- Fernet (cryptography): https://cryptography.io/en/latest/fernet/
- SOCKS5: https://tools.ietf.org/html/rfc1928
- SOCKS5 Auth: https://tools.ietf.org/html/rfc1929
- Requests Library: https://requests.readthedocs.io/
- urllib3 Retries: https://urllib3.readthedocs.io/en/latest/advanced-usage.html#retrying-requests
