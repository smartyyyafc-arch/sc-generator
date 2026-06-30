# Proxy Authentication Handler - Quick Start Guide

## Installation

```python
# Copy proxy_auth_handler.py to your project
# No external dependencies required
```

## 60-Second Setup

### Basic Auth

```python
from proxy_auth_handler import create_auth_handler

handler = create_auth_handler(
    proxy_url="http://proxy.example.com:8080",
    auth_type="basic",
    username="user",
    password="pass"
)

headers = handler.get_auth_headers()
# Use in requests: session.headers.update(headers)
```

### Digest Auth

```python
handler = create_auth_handler(
    proxy_url="http://proxy:8080",
    auth_type="digest",
    username="user",
    password="pass"
)

# Handle server challenge
challenge = "Digest realm=..."
response_headers = handler.handle_challenge(challenge)
```

### Certificate Auth

```python
handler = create_auth_handler(
    proxy_url="https://proxy:8443",
    auth_type="certificate",
    cert_path="/path/to/cert.pem",
    key_path="/path/to/key.pem"
)

config = handler.get_connection_config()
# Use in requests: session.cert = (config['client_cert'], config['client_key'])
```

### NTLM Auth

```python
handler = create_auth_handler(
    proxy_url="http://proxy:8080",
    auth_type="ntlm",
    username="domain\\user",
    password="pass",
    domain="DOMAIN"
)

# Send Type 1: handler.get_auth_headers()
# Receive Type 2: challenge = "NTLM ..."
# Send Type 3: handler.handle_challenge(challenge)
```

## Common Patterns

### With requests library

```python
import requests
from proxy_auth_handler import create_auth_handler

handler = create_auth_handler(
    proxy_url="http://proxy:8080",
    auth_type="basic",
    username="user",
    password="pass"
)

session = requests.Session()
session.proxies = {'http': handler.get_proxy_url()}
session.headers.update(handler.get_auth_headers())

response = session.get('http://api.example.com')
```

### With urllib

```python
import urllib.request
from proxy_auth_handler import create_auth_handler

handler = create_auth_handler(
    proxy_url="http://proxy:8080",
    auth_type="basic",
    username="user",
    password="pass"
)

proxy_handler = urllib.request.ProxyHandler({
    'http': handler.get_proxy_url(),
    'https': handler.get_proxy_url()
})

# Add auth headers separately based on auth type
opener = urllib.request.build_opener(proxy_handler)
response = opener.open('http://api.example.com')
```

### Environment Variables

```python
import os
from proxy_auth_handler import create_auth_handler

handler = create_auth_handler(
    proxy_url=os.environ.get('PROXY_URL'),
    auth_type=os.environ.get('PROXY_AUTH_TYPE', 'basic'),
    username=os.environ.get('PROXY_USER'),
    password=os.environ.get('PROXY_PASS')
)
```

### With Custom Headers

```python
handler = create_auth_handler(
    proxy_url="http://proxy:8080",
    auth_type="basic",
    username="user",
    password="pass",
    custom_headers={
        "User-Agent": "MyApp/1.0",
        "X-Request-ID": "req-123"
    }
)

headers = handler.get_auth_headers()
# All headers ready to use
```

## Authentication Types Cheat Sheet

| Type | Use Case | Complexity | Security |
|------|----------|-----------|----------|
| **basic** | Simple, development | Low | Low* |
| **digest** | Better than basic | Medium | Medium |
| **ntlm** | Corporate/Windows | High | Medium |
| **certificate** | Service-to-service | High | High |

*Basic: Always use over HTTPS

## API Quick Reference

```python
# Create handler
handler = create_auth_handler(proxy_url, auth_type="basic", **kwargs)

# Get headers
headers = handler.get_auth_headers()

# Get proxy URL (no credentials)
url = handler.get_proxy_url()

# Handle challenge
response = handler.handle_challenge(challenge_header)

# Get connection config (safe to export)
config = handler.get_connection_config()

# Export as JSON (credentials excluded)
json_str = handler.to_json()
```

## Configuration Options

```python
create_auth_handler(
    proxy_url="http://proxy:8080",      # Required
    auth_type="basic",                  # basic|digest|ntlm|certificate
    username="user",                    # For basic/digest/ntlm
    password="pass",                    # For basic/digest/ntlm
    cert_path="/path/cert.pem",        # For certificate
    key_path="/path/key.pem",          # For certificate
    ca_bundle="/path/ca.pem",          # Optional
    domain="CORP",                      # For NTLM
    workstation="PC",                   # For NTLM
    timeout=30,                         # Timeout in seconds
    verify_ssl=True,                    # SSL verification
    custom_headers={...}                # Custom headers
)
```

## Error Handling

```python
from proxy_auth_handler import ProxyConfig, ProxyAuthHandler

try:
    config = ProxyConfig(
        proxy_url="http://proxy:8080",
        auth_type="basic",
        username="user",
        password="pass"
    )
    handler = ProxyAuthHandler(config)
except ValueError as e:
    print(f"Config error: {e}")
except FileNotFoundError as e:
    print(f"File error: {e}")
```

## Testing

```bash
# Run all tests
python -m unittest test_proxy_auth_handler.py

# Run examples
python proxy_auth_examples.py

# Verbose
python -m unittest test_proxy_auth_handler.py -v
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| 407 Proxy Auth Required | Verify credentials, try different auth type |
| NTLM fails | Use domain\username format |
| Certificate validation fails | Check cert/key paths, verify SSL settings |
| "username and password required" | Auth type requires those parameters |

## Security Tips

1. **Never hardcode credentials**
   ```python
   import os
   password = os.environ.get('PROXY_PASSWORD')
   ```

2. **Use HTTPS for Basic Auth**
   ```python
   proxy_url="https://proxy:8443"  # Not http://
   ```

3. **Use Certificate Auth for services**
   ```python
   auth_type="certificate"  # Most secure for service-to-service
   ```

4. **Verify exports don't contain credentials**
   ```python
   json_str = handler.to_json()  # Safe - no credentials
   # NOT: str(handler.config)  # Unsafe - contains credentials
   ```

## Real-World Examples

### Corporate Environment

```python
handler = create_auth_handler(
    proxy_url="http://corporate-proxy.example.com:3128",
    auth_type="ntlm",
    username="DOMAIN\\john.doe",
    password=os.environ.get('PASSWORD'),
    domain="DOMAIN",
    workstation="WORKSTATION01"
)
```

### Cloud Service

```python
handler = create_auth_handler(
    proxy_url="https://proxy.internal.example.com:8443",
    auth_type="certificate",
    cert_path="/etc/certs/service-cert.pem",
    key_path="/etc/certs/service-key.pem",
    ca_bundle="/etc/certs/ca-bundle.crt",
    verify_ssl=True
)
```

### Development

```python
handler = create_auth_handler(
    proxy_url="http://localhost:8080",
    auth_type="basic",
    username="dev",
    password="devpass"
)
```

## Next Steps

- See `PROXY_AUTH_DOCUMENTATION.md` for complete documentation
- Run `proxy_auth_examples.py` for detailed examples
- Check `test_proxy_auth_handler.py` for test patterns
- Review `proxy_auth_handler.py` source code

---

**For full documentation**: See `PROXY_AUTH_DOCUMENTATION.md`
