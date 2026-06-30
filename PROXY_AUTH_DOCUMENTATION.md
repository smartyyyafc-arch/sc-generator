# Proxy Authentication Handler - Complete Documentation

## Overview

The Proxy Authentication Handler is a comprehensive Python library that provides authentication support for HTTP/HTTPS proxy connections. It supports multiple authentication schemes including Basic, Digest, NTLM, and certificate-based authentication (mTLS).

**Version**: 1.0  
**Status**: Production Ready  
**Python**: 3.7+

## Key Features

- **Multiple Authentication Methods**
  - Basic Authentication (RFC 7617)
  - Digest Authentication (RFC 7616)
  - NTLM Authentication (NT LAN Manager)
  - Certificate-Based Authentication (mTLS)

- **Robust Error Handling**
  - Configuration validation
  - File existence checks for certificates
  - Graceful error messages

- **Easy Integration**
  - Simple API design
  - Convenience functions
  - Flexible configuration
  - JSON export capability

- **Security-Focused**
  - No credential logging
  - Safe JSON export (credentials excluded)
  - Support for custom headers
  - SSL/TLS verification options

## Installation

### No external dependencies required for core functionality

```bash
# Copy the module to your project
cp proxy_auth_handler.py /path/to/your/project/
```

### Optional dependencies (for specific use cases)

```bash
# For certificate handling enhancements
pip install cryptography

# For NTLM support (alternative)
pip install python-ntlm
```

## Quick Start

### Basic Authentication

```python
from proxy_auth_handler import ProxyAuthHandler, ProxyConfig

config = ProxyConfig(
    proxy_url="http://proxy.example.com:8080",
    auth_type="basic",
    username="john_doe",
    password="secure_password"
)

handler = ProxyAuthHandler(config)
headers = handler.get_auth_headers()

# Use headers in HTTP requests
print(headers)
# Output: {'Proxy-Authorization': 'Basic am9obl9kb2U6c2VjdXJlX3Bhc3N3b3Jk'}
```

### Certificate-Based Authentication

```python
config = ProxyConfig(
    proxy_url="https://secure-proxy.example.com:8443",
    auth_type="certificate",
    cert_path="/path/to/client-cert.pem",
    key_path="/path/to/client-key.pem",
    ca_bundle="/path/to/ca-bundle.pem"
)

handler = ProxyAuthHandler(config)
conn_config = handler.get_connection_config()

# Use in requests library
import requests
session = requests.Session()
session.cert = (conn_config['client_cert'], conn_config['client_key'])
session.verify = conn_config['ca_bundle']
```

### Using Convenience Function

```python
from proxy_auth_handler import create_auth_handler

handler = create_auth_handler(
    proxy_url="http://proxy.example.com:8080",
    auth_type="basic",
    username="user",
    password="pass",
    timeout=30
)

headers = handler.get_auth_headers()
```

## Configuration

### ProxyConfig Class

The `ProxyConfig` dataclass contains all proxy authentication settings.

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `proxy_url` | str | Yes | - | Proxy server URL (http/https) |
| `auth_type` | AuthType | No | BASIC | Authentication method |
| `username` | str | No | None | Username for auth |
| `password` | str | No | None | Password for auth |
| `cert_path` | str | No | None | Path to client certificate |
| `key_path` | str | No | None | Path to private key |
| `ca_bundle` | str | No | None | Path to CA bundle for verification |
| `domain` | str | No | None | Domain (for NTLM) |
| `workstation` | str | No | None | Workstation name (for NTLM) |
| `timeout` | int | No | 30 | Connection timeout in seconds |
| `verify_ssl` | bool | No | True | Verify SSL certificates |
| `custom_headers` | dict | No | {} | Custom HTTP headers |
| `ntlm_flags` | int | No | 0x00000017 | NTLM negotiation flags |

#### Example Configurations

```python
# Minimal basic auth
config = ProxyConfig(
    proxy_url="http://proxy:8080",
    auth_type="basic",
    username="user",
    password="pass"
)

# Full digest auth with custom headers
config = ProxyConfig(
    proxy_url="http://proxy:8080",
    auth_type="digest",
    username="user",
    password="pass",
    timeout=60,
    custom_headers={
        "User-Agent": "MyApp/1.0",
        "X-Correlation-ID": "req-123"
    }
)

# NTLM with domain
config = ProxyConfig(
    proxy_url="http://proxy:8080",
    auth_type="ntlm",
    username="username",
    password="pass",
    domain="CORP",
    workstation="MYPC"
)

# Certificate-based
config = ProxyConfig(
    proxy_url="https://proxy:8443",
    auth_type="certificate",
    cert_path="/etc/ssl/certs/client.pem",
    key_path="/etc/ssl/private/client-key.pem",
    ca_bundle="/etc/ssl/certs/ca-bundle.crt",
    verify_ssl=True
)
```

## Authentication Methods

### 1. Basic Authentication (RFC 7617)

Simplest authentication method. Username and password are base64-encoded.

**Characteristics:**
- Simple and widely supported
- Should only be used over HTTPS
- No challenge-response mechanism

**Example:**

```python
handler = create_auth_handler(
    proxy_url="http://proxy:8080",
    auth_type="basic",
    username="user",
    password="pass"
)

headers = handler.get_auth_headers()
# {'Proxy-Authorization': 'Basic dXNlcjpwYXNz'}
```

**Security Note:** Always use HTTPS when transmitting Basic auth credentials.

### 2. Digest Authentication (RFC 7616)

Challenge-response mechanism. More secure than Basic.

**Characteristics:**
- Requires server challenge
- Supports MD5 and SHA-256
- Client nonce and nonce count
- QOP (Quality of Protection) support

**Example:**

```python
handler = create_auth_handler(
    proxy_url="http://proxy:8080",
    auth_type="digest",
    username="user",
    password="pass"
)

# Initially empty, must handle challenge
initial_headers = handler.get_auth_headers()

# Server sends challenge
challenge = 'Digest realm="Proxy", nonce="...", qop="auth"'

# Generate response
response_headers = handler.handle_challenge(challenge)
```

**Challenge Format:**

```
Digest realm="Proxy Realm",
       nonce="dcd98b7102dd2f0e8b11d0f600bfb0c093",
       qop="auth",
       opaque="5ccc069c403ebaf9f0171986f2c632e5",
       algorithm=MD5
```

### 3. NTLM Authentication

Microsoft's NT LAN Manager protocol. Three-way handshake.

**Characteristics:**
- Type 1 Message: Client initiates with capabilities
- Type 2 Message: Server sends challenge
- Type 3 Message: Client responds with hash
- Supports domain and workstation
- Complex but widely used in corporate environments

**Example:**

```python
handler = create_auth_handler(
    proxy_url="http://proxy:8080",
    auth_type="ntlm",
    username="domain\\username",
    password="pass",
    domain="CORP",
    workstation="MYPC"
)

# Step 1: Send Type 1 message
type1_headers = handler.get_auth_headers()

# Step 2: Receive Type 2 challenge
type2_challenge = "NTLM TlRMTVNTUAA..."

# Step 3: Send Type 3 response
type3_headers = handler.handle_challenge(type2_challenge)
```

**NTLM Flow:**

```
Client                          Proxy Server
  |                              |
  |------ Type 1 (Negotiate) --->|
  |                              |
  |<----- Type 2 (Challenge) ----|
  |                              |
  |------ Type 3 (Authenticate)->|
  |                              |
  |<----- 407 / Auth Success ----|
```

### 4. Certificate-Based Authentication (mTLS)

Mutual TLS authentication using client certificates.

**Characteristics:**
- Client presents certificate and key
- Server verifies certificate
- No password required
- Suitable for service-to-service authentication
- Highest security level

**Example:**

```python
handler = create_auth_handler(
    proxy_url="https://proxy:8443",
    auth_type="certificate",
    cert_path="/path/to/client-cert.pem",
    key_path="/path/to/client-key.pem",
    ca_bundle="/path/to/ca.pem",
    verify_ssl=True
)

config = handler.get_connection_config()

# Use with requests
import requests
session = requests.Session()
session.cert = (config['client_cert'], config['client_key'])
session.verify = config['ca_bundle']
response = session.get('http://api.example.com', proxies={'http': config['proxy_url']})
```

**Certificate Generation:**

```bash
# Generate self-signed certificate
openssl req -x509 -newkey rsa:4096 -keyout client-key.pem -out client-cert.pem -days 365 -nodes

# Or generate CSR for signing
openssl req -new -newkey rsa:4096 -keyout client-key.pem -out client.csr
openssl x509 -req -in client.csr -CA ca-cert.pem -CAkey ca-key.pem -CAcreateserial -out client-cert.pem -days 365 -sha256
```

## API Reference

### ProxyAuthHandler Class

Main class for handling proxy authentication.

#### Methods

**`__init__(config: ProxyConfig)`**

Initialize the authentication handler.

```python
handler = ProxyAuthHandler(config)
```

**`get_auth_headers() -> Dict[str, str]`**

Get authentication headers for the initial request.

```python
headers = handler.get_auth_headers()
# Returns: {'Proxy-Authorization': '...'}
```

**`handle_challenge(challenge: str) -> Dict[str, str]`**

Handle authentication challenge from proxy server.

```python
response_headers = handler.handle_challenge(challenge_header)
```

**`get_proxy_url() -> str`**

Get proxy URL without embedded credentials.

```python
url = handler.get_proxy_url()
# Returns: 'http://proxy.example.com:8080'
```

**`get_connection_config() -> Dict[str, Any]`**

Get complete connection configuration (safe to export).

```python
config = handler.get_connection_config()
# Returns: {
#     'proxy_url': '...',
#     'auth_type': 'basic',
#     'timeout': 30,
#     'verify_ssl': True,
#     ...
# }
```

**`to_json() -> str`**

Export configuration as JSON (credentials excluded).

```python
json_str = handler.to_json()
print(json_str)
```

### Authentication Scheme Classes

#### BasicAuth

HTTP Basic Authentication (RFC 7617).

```python
auth = BasicAuth(config)
headers = auth.get_auth_header()
```

#### DigestAuth

HTTP Digest Authentication (RFC 7616).

```python
auth = DigestAuth(config)
headers = auth.get_auth_header()
response = auth.handle_auth_challenge(challenge)
```

#### NTLMAuth

NTLM Authentication.

```python
auth = NTLMAuth(config)
type1_msg = auth.get_auth_header()
type3_msg = auth.handle_auth_challenge(type2_challenge)
```

#### CertificateAuth

Certificate-based (mTLS) Authentication.

```python
auth = CertificateAuth(config)
headers = auth.get_auth_header()
auth.validate_certificate()
```

### Convenience Function

**`create_auth_handler(proxy_url: str, auth_type: str = "basic", **kwargs) -> ProxyAuthHandler`**

Create authentication handler with convenient syntax.

```python
handler = create_auth_handler(
    proxy_url="http://proxy:8080",
    auth_type="basic",
    username="user",
    password="pass"
)
```

## Usage Patterns

### Pattern 1: Simple Proxy with Basic Auth

```python
from proxy_auth_handler import create_auth_handler
import requests

handler = create_auth_handler(
    proxy_url="http://proxy.corp.com:8080",
    auth_type="basic",
    username="employee",
    password="password"
)

session = requests.Session()
session.proxies = {'http': handler.get_proxy_url()}
session.headers.update(handler.get_auth_headers())

response = session.get('http://api.example.com/data')
```

### Pattern 2: HTTPS Proxy with Digest Auth

```python
handler = create_auth_handler(
    proxy_url="https://secure-proxy.corp.com:8443",
    auth_type="digest",
    username="user",
    password="pass",
    verify_ssl=True
)

# Initial request
headers = handler.get_auth_headers()

# If challenged:
# challenge = response.headers.get('Proxy-Authenticate')
# headers = handler.handle_challenge(challenge)
```

### Pattern 3: Enterprise Environment with NTLM

```python
handler = create_auth_handler(
    proxy_url="http://corporate-proxy.example.com:3128",
    auth_type="ntlm",
    username="domain\\username",
    password="password",
    domain="CORPORATE",
    workstation="WORKSTATION01"
)

# Use with urllib
import urllib.request

proxy_handler = urllib.request.ProxyHandler({
    'http': handler.get_proxy_url(),
    'https': handler.get_proxy_url()
})

# Add authentication
auth_handler = urllib.request.HTTPBasicAuthHandler()
# For NTLM, use additional handler...

opener = urllib.request.build_opener(proxy_handler)
response = opener.open('http://api.example.com')
```

### Pattern 4: Service-to-Service with Certificate Auth

```python
handler = create_auth_handler(
    proxy_url="https://proxy.internal.example.com:8443",
    auth_type="certificate",
    cert_path="/etc/certs/service-cert.pem",
    key_path="/etc/certs/service-key.pem",
    ca_bundle="/etc/certs/ca.pem"
)

import requests
config = handler.get_connection_config()

session = requests.Session()
session.cert = (config['client_cert'], config['client_key'])
session.verify = config['ca_bundle']
session.proxies = {'https': config['proxy_url']}

response = session.get('https://api.internal.example.com/data')
```

### Pattern 5: Custom Headers with Retry Logic

```python
handler = create_auth_handler(
    proxy_url="http://proxy:8080",
    auth_type="basic",
    username="user",
    password="pass",
    timeout=30,
    custom_headers={
        "User-Agent": "MyApp/1.0",
        "X-Request-ID": "req-123"
    }
)

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

session = requests.Session()
session.proxies = {'http': handler.get_proxy_url()}
session.headers.update(handler.get_auth_headers())

# Add retry strategy
retry_strategy = Retry(
    total=3,
    backoff_factor=1,
    status_forcelist=[407, 429, 500, 502, 503, 504]
)
adapter = HTTPAdapter(max_retries=retry_strategy)
session.mount("http://", adapter)

response = session.get('http://api.example.com')
```

## Error Handling

### Configuration Validation Errors

```python
from proxy_auth_handler import ProxyConfig, AuthType

# Missing password for basic auth
try:
    config = ProxyConfig(
        proxy_url="http://proxy:8080",
        auth_type=AuthType.BASIC,
        username="user"
        # password missing
    )
except ValueError as e:
    print(f"Config error: {e}")
    # Output: Config error: basic auth requires username and password
```

### File Not Found Errors

```python
# Missing certificate file
try:
    config = ProxyConfig(
        proxy_url="https://proxy:8443",
        auth_type=AuthType.CERTIFICATE,
        cert_path="/nonexistent/cert.pem",
        key_path="/nonexistent/key.pem"
    )
except FileNotFoundError as e:
    print(f"File error: {e}")
    # Output: File error: [Errno 2] No such file or directory: '/nonexistent/cert.pem'
```

### Authentication Challenge Handling

```python
handler = create_auth_handler(
    proxy_url="http://proxy:8080",
    auth_type="digest",
    username="user",
    password="pass"
)

# Handle challenge
challenge = response.headers.get('Proxy-Authenticate')
if challenge:
    response_headers = handler.handle_challenge(challenge)
    # Retry request with response headers
```

## Testing

### Running Tests

```bash
# Run all tests
python -m unittest test_proxy_auth_handler.py

# Run specific test class
python -m unittest test_proxy_auth_handler.TestBasicAuth

# Run specific test
python -m unittest test_proxy_auth_handler.TestBasicAuth.test_auth_header_encoding

# Verbose output
python -m unittest test_proxy_auth_handler.py -v
```

### Test Coverage

Run the examples to verify functionality:

```bash
python proxy_auth_examples.py
```

## Security Considerations

### 1. Credential Storage

- Never store passwords in plaintext in configuration files
- Use environment variables or secure vaults for credentials
- Always exclude credentials from logs and exports

```python
import os

password = os.environ.get('PROXY_PASSWORD')
config = ProxyConfig(
    proxy_url="http://proxy:8080",
    auth_type="basic",
    username=os.environ.get('PROXY_USER'),
    password=password
)
```

### 2. HTTPS for Basic Auth

- Always use HTTPS when using Basic authentication
- Basic auth credentials are only base64-encoded, not encrypted

```python
# Good: HTTPS
config = ProxyConfig(
    proxy_url="https://proxy:8443",  # HTTPS
    auth_type="basic",
    username="user",
    password="pass"
)

# Risky: HTTP with Basic Auth
# Not recommended for production
```

### 3. Certificate Management

- Keep private keys secure and protected
- Use proper file permissions (e.g., 0600 for key files)
- Rotate certificates periodically
- Verify certificate chains

```bash
# Secure key file permissions
chmod 600 /path/to/client-key.pem

# Verify certificate
openssl x509 -in /path/to/client-cert.pem -text -noout
```

### 4. Proxy Configuration Export

- The `to_json()` method never includes credentials
- Always verify exported configurations before sharing
- Use `get_connection_config()` for safe configuration passing

```python
# Safe to share or log
config_dict = handler.get_connection_config()
json_str = handler.to_json()

# Not safe to share
# config_dict = handler.config.__dict__  # Contains credentials
```

## Troubleshooting

### Issue: 407 Proxy Authentication Required

**Problem:** Proxy returns 407 even with correct credentials.

**Solutions:**
1. Verify credentials are correct
2. Check proxy URL format
3. Try different auth type
4. Verify proxy server supports chosen auth method

```python
# Debug: Check what headers are being sent
headers = handler.get_auth_headers()
print("Sending headers:", headers)

# Try alternative auth type
handler2 = create_auth_handler(
    proxy_url=handler.config.proxy_url,
    auth_type="digest",  # Try digest instead of basic
    username=handler.config.username,
    password=handler.config.password
)
```

### Issue: NTLM Authentication Fails

**Problem:** NTLM authentication doesn't work.

**Solutions:**
1. Ensure domain and workstation are correct
2. Verify proxy supports NTLM
3. Check username format (domain\username)
4. Try alternative NTLM implementation

```python
# Correct format
handler = create_auth_handler(
    proxy_url="http://proxy:8080",
    auth_type="ntlm",
    username="DOMAIN\\username",  # Use domain\username format
    password="pass",
    domain="DOMAIN",
    workstation="WORKSTATION"
)
```

### Issue: Certificate Validation Fails

**Problem:** SSL certificate verification errors.

**Solutions:**
1. Verify certificate path is correct
2. Check certificate validity period
3. Ensure CA bundle is correct
4. Try disabling verification (development only)

```python
# Check certificate
config = ProxyConfig(
    proxy_url="https://proxy:8443",
    auth_type="certificate",
    cert_path="/path/to/cert.pem",
    key_path="/path/to/key.pem",
    verify_ssl=True  # Strict verification
)

try:
    handler = ProxyAuthHandler(config)
    auth = handler.auth_scheme
    if hasattr(auth, 'validate_certificate'):
        auth.validate_certificate()
except Exception as e:
    print(f"Certificate error: {e}")
```

## Performance Characteristics

| Operation | Time | Notes |
|-----------|------|-------|
| Create handler | <1ms | Fast initialization |
| Generate Basic auth | <1ms | Simple base64 encoding |
| Generate Digest auth | 5-10ms | Includes hashing |
| Handle NTLM Type 1 | 1-2ms | Message generation |
| Handle NTLM Type 3 | 5-10ms | Includes HMAC |
| Certificate validation | 10-50ms | File I/O dependent |

## Limitations

1. **Proxy Server Requirements**
   - Proxy must support chosen authentication method
   - Some proxies may not support all methods

2. **NTLM Specifics**
   - Requires three-way handshake
   - May not work with some HTTP client libraries
   - Performance impact due to complex calculations

3. **Certificate Authentication**
   - Requires valid certificate/key pair
   - Certificate must be trusted by proxy server
   - Higher setup complexity

4. **Authentication Challenges**
   - Some clients require manual challenge handling
   - Automatic retry may not be supported by all HTTP libraries

## Contributing

To add new authentication methods:

1. Extend `AuthenticationScheme` class
2. Implement `get_auth_header()` method
3. Implement `handle_auth_challenge()` method
4. Add to `scheme_map` in `ProxyAuthHandler`
5. Add tests to `test_proxy_auth_handler.py`
6. Document in this file

## License & Disclaimer

This library is provided for authorized use only. Ensure you have explicit permission before using proxy authentication in any environment.

## Support & Resources

- **Examples**: See `proxy_auth_examples.py`
- **Tests**: Run `python -m unittest test_proxy_auth_handler.py`
- **Source Code**: `proxy_auth_handler.py`
- **This Documentation**: `PROXY_AUTH_DOCUMENTATION.md`

---

**Version**: 1.0  
**Last Updated**: June 2026  
**Status**: Production Ready
