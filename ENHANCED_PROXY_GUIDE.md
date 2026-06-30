# Enhanced Proxy System Documentation

## Overview

The Enhanced Proxy System provides comprehensive support for multiple proxy protocols with advanced configuration, validation, and management capabilities. It supports HTTP, HTTPS, SOCKS4, and SOCKS5 proxies with optional authentication.

## Supported Proxy Types

### 1. HTTP (Port 80)
- **Protocol**: `http://`
- **Standard Port**: 80
- **Use Cases**:
  - Most common proxy type
  - Good for unencrypted connections
  - High compatibility
  - Network traffic is not encrypted
- **Example**: `http://proxy.example.com:8080`
- **With Auth**: `http://user:password@proxy.example.com:8080`

### 2. HTTPS (Port 443)
- **Protocol**: `https://`
- **Standard Port**: 443
- **Use Cases**:
  - Encrypted proxy connections
  - Sensitive network environments
  - SSL/TLS protected traffic
  - Better security for credentials
- **Example**: `https://secure-proxy.example.com:8443`
- **With Auth**: `https://user:password@secure-proxy.example.com:8443`

### 3. SOCKS4 (Port 1080)
- **Protocol**: `socks4://`
- **Standard Port**: 1080
- **Use Cases**:
  - Legacy systems
  - Universal protocol support
  - Non-HTTP traffic routing
  - IPv4 only
- **Example**: `socks4://socks.example.com:1080`
- **Limitations**:
  - No authentication support
  - IPv4 only
  - Limited feature set
  - Mostly for backward compatibility

### 4. SOCKS5 (Port 1080)
- **Protocol**: `socks5://`
- **Standard Port**: 1080
- **Use Cases**:
  - Any traffic type (UDP, TCP, etc.)
  - Advanced applications
  - Full feature support
  - IPv6 compatible
  - Maximum flexibility
- **Example**: `socks5://user:password@socks.example.com:1080`
- **With Auth**: `socks5://username:password@socks.example.com:1080`
- **Features**:
  - Username/password authentication
  - IPv4 and IPv6 support
  - UDP association
  - Most flexible option

## API Endpoints

### Get All Proxies
```
GET /api/proxies
```
Returns all configured proxies with statistics.

**Response**:
```json
{
  "proxies": [
    {
      "id": "proxy123456",
      "url": "http://proxy.example.com:8080",
      "proxy_type": "http",
      "host": "proxy.example.com",
      "port": 8080,
      "is_active": true,
      "tags": ["corporate", "test"],
      "created_at": "2024-06-29T10:00:00",
      "last_tested": "2024-06-29T10:15:00",
      "test_status": "passed"
    }
  ],
  "statistics": {
    "total_proxies": 4,
    "active_proxies": 3,
    "tested_proxies": 2,
    "passed_tests": 2,
    "by_type": {
      "http": 1,
      "https": 1,
      "socks5": 2
    }
  }
}
```

### Add Proxy
```
POST /api/proxies
Content-Type: application/json

{
  "url": "socks5://user:pass@socks.example.com:1080",
  "tags": ["secure", "production"],
  "notes": "Production SOCKS5 proxy with authentication"
}
```

**Response**:
```json
{
  "success": true,
  "id": "proxy123456",
  "message": "Proxy added successfully"
}
```

### Test Proxy
```
POST /api/proxies/{proxy_id}/test
Content-Type: application/json

{
  "timeout": 10
}
```

**Response**:
```json
{
  "proxy_id": "proxy123456",
  "success": true,
  "message": "SOCKS5 proxy is functional",
  "timestamp": "2024-06-29T10:15:00"
}
```

### Test All Proxies
```
POST /api/proxies/test-all
Content-Type: application/json

{
  "timeout": 10
}
```

**Response**:
```json
{
  "results": {
    "proxy123456": {
      "success": true,
      "message": "HTTP proxy is reachable"
    },
    "proxy789012": {
      "success": false,
      "message": "SOCKS5 proxy connection timed out"
    }
  },
  "summary": {
    "total": 2,
    "passed": 1,
    "failed": 1
  },
  "timestamp": "2024-06-29T10:15:00"
}
```

### Get Proxies by Type
```
GET /api/proxies/by-type/socks5
```

**Response**:
```json
{
  "type": "socks5",
  "proxies": [
    {
      "id": "proxy123456",
      "url": "socks5://user:pass@socks.example.com:1080",
      "proxy_type": "socks5",
      ...
    }
  ],
  "count": 1
}
```

### Get Proxies by Tag
```
GET /api/proxies/by-tag/production
```

**Response**:
```json
{
  "tag": "production",
  "proxies": [
    {
      "id": "proxy123456",
      ...
    }
  ],
  "count": 1
}
```

### Delete Proxy
```
DELETE /api/proxies/{proxy_id}
```

**Response**:
```json
{
  "success": true,
  "message": "Proxy removed successfully"
}
```

### Toggle Proxy Status
```
PUT /api/proxies/{proxy_id}/toggle
Content-Type: application/json

{
  "is_active": false
}
```

**Response**:
```json
{
  "success": true,
  "message": "Proxy deactivated successfully"
}
```

### Add Tag to Proxy
```
POST /api/proxies/{proxy_id}/tags
Content-Type: application/json

{
  "tag": "backup"
}
```

**Response**:
```json
{
  "success": true,
  "message": "Tag 'backup' added"
}
```

### Export Report
```
GET /api/proxies/report
```

**Response**:
```json
{
  "generated_at": "2024-06-29T10:15:00",
  "statistics": {
    "total_proxies": 4,
    "active_proxies": 3,
    "tested_proxies": 2,
    "passed_tests": 2,
    "by_type": {...}
  },
  "proxies": [...],
  "summary": {
    "total": 4,
    "active": 3,
    "success_rate": 100.0
  }
}
```

## Python Usage

### Basic Usage
```python
from enhanced_proxy_system import EnhancedProxyManager

# Initialize manager
manager = EnhancedProxyManager()

# Add proxies
success, message, proxy_id = manager.add_proxy(
    "http://proxy.example.com:8080",
    tags=["corporate", "http"],
    notes="Corporate HTTP proxy"
)

# Test proxy
success, message = manager.test_proxy(proxy_id)
print(f"Test result: {message}")

# Get all proxies
proxies = manager.get_all_proxies()

# Get proxies by type
socks5_proxies = manager.get_proxies_by_type(ProxyType.SOCKS5)

# Get proxies by tag
secure_proxies = manager.get_proxies_by_tag("secure")

# Export report
report = manager.export_report('/tmp/proxy_report.json')
```

### Advanced Validation
```python
from enhanced_proxy_system import ProxyParserValidator

# Parse proxy URL
success, parsed, message = ProxyParserValidator.parse_proxy_url(
    "socks5://user:pass@socks.example.com:1080"
)

if success:
    print(f"Protocol: {parsed['protocol']}")
    print(f"Host: {parsed['host']}")
    print(f"Port: {parsed['port']}")
    if parsed['credentials']:
        print(f"Username: {parsed['credentials']['username']}")
```

### Proxy Statistics
```python
# Get statistics
stats = manager.get_statistics()
print(f"Total: {stats['total_proxies']}")
print(f"Active: {stats['active_proxies']}")
print(f"By Type: {stats['by_type']}")

# Calculate success rate
success_rate = manager._calculate_success_rate()
print(f"Success Rate: {success_rate}%")
```

## URL Format Specifications

### HTTP/HTTPS Format
```
[protocol]://[username:password@]host:port
http://proxy.example.com:8080
https://user:password@secure-proxy.example.com:8443
```

### SOCKS Format
```
[protocol]://[username:password@]host:port
socks4://socks.example.com:1080
socks5://user:password@socks.example.com:1080
```

## Authentication Types

### Basic Authentication
Used for HTTP/HTTPS and SOCKS5 proxies.
```
http://username:password@proxy.example.com:8080
```

**Encoding**: Credentials are Base64 encoded in HTTP headers.

### SOCKS5 Authentication
```
socks5://username:password@socks.example.com:1080
```

**Method**: Username/password authentication as per RFC 1929.

## Configuration File

Proxies are stored in JSON format at `/tmp/sc-proxies/proxies.json`:

```json
[
  {
    "id": "proxy123456",
    "url": "http://proxy.example.com:8080",
    "proxy_type": "http",
    "host": "proxy.example.com",
    "port": 8080,
    "credentials": null,
    "timeout": 10,
    "retry_count": 3,
    "tags": ["corporate"],
    "is_active": true,
    "created_at": "2024-06-29T10:00:00",
    "last_tested": "2024-06-29T10:15:00",
    "test_status": "passed",
    "notes": "Corporate proxy"
  }
]
```

## Proxy Validation

### HTTP/HTTPS Validation
- Attempts TCP connection to proxy host/port
- Verifies connectivity
- Timeout handling

### SOCKS4 Validation
- Establishes SOCKS4 handshake
- Sends CONNECT request to localhost:80
- Verifies response code (90 = granted)

### SOCKS5 Validation
- Initiates SOCKS5 greeting
- Handles authentication methods
- Sends CONNECT request to localhost:80
- Verifies successful connection

## Use Cases

### Corporate Environment
- **Setup**: HTTP proxy with authentication
- **Configuration**:
  ```
  http://user:pass@corp-proxy.company.com:8080
  ```
- **Tags**: `corporate`, `http`, `authenticated`

### Secure Remote Access
- **Setup**: HTTPS proxy with authentication
- **Configuration**:
  ```
  https://user:pass@vpn-gateway.company.com:8443
  ```
- **Tags**: `secure`, `vpn`, `encrypted`

### Universal Proxy
- **Setup**: SOCKS5 with authentication
- **Configuration**:
  ```
  socks5://user:pass@socks-gateway.company.com:1080
  ```
- **Tags**: `socks5`, `universal`, `flexible`

### Legacy System Support
- **Setup**: SOCKS4 without authentication
- **Configuration**:
  ```
  socks4://legacy-proxy.company.com:1080
  ```
- **Tags**: `legacy`, `socks4`

## Error Handling

### Common Errors

1. **Invalid URL Format**
   ```
   Error: Invalid proxy URL format
   Solution: Check URL syntax, ensure protocol is specified
   ```

2. **Connection Timeout**
   ```
   Error: SOCKS5 proxy connection timed out
   Solution: Increase timeout, check proxy availability
   ```

3. **Authentication Failed**
   ```
   Error: No acceptable SOCKS5 authentication method
   Solution: Verify credentials, check proxy auth requirements
   ```

4. **Port Out of Range**
   ```
   Error: Port must be between 1 and 65535
   Solution: Use valid port number
   ```

## Performance Considerations

- **Timeout**: Default 10 seconds per proxy test
- **Retry Count**: Default 3 retries for failed connections
- **Batch Testing**: Test all proxies in parallel (recommended)
- **Caching**: Proxies loaded from disk on startup

## Security Best Practices

1. **Credentials Storage**
   - Store in configuration files with restricted permissions
   - Use environment variables for sensitive data
   - Never log credentials in debug output

2. **Connection Security**
   - Use HTTPS for encrypted proxy connections
   - Use SOCKS5 for maximum flexibility
   - Enable authentication when available

3. **Testing**
   - Test proxies before deployment
   - Monitor proxy health regularly
   - Rotate proxies based on usage patterns

4. **Access Control**
   - Restrict API access to authorized users
   - Log all proxy operations
   - Audit proxy configurations

## Migration Guide

### From Legacy System
```python
# Old system
proxy_id = fingerprint_mgr.add_proxy("http://proxy.example.com:8080", "http")

# New system
success, message, proxy_id = proxy_mgr.add_proxy(
    "http://proxy.example.com:8080",
    tags=["legacy"],
    notes="Migrated from old system"
)
```

### Bulk Import
```python
import json

with open('legacy_proxies.json', 'r') as f:
    proxies = json.load(f)
    for proxy in proxies:
        proxy_mgr.add_proxy(
            proxy['url'],
            tags=proxy.get('tags', []),
            notes=proxy.get('notes', '')
        )
```

## Troubleshooting

### Proxy Not Responding
1. Check proxy address and port
2. Verify network connectivity
3. Check firewall rules
4. Test with external tools (curl, telnet)

### Authentication Issues
1. Verify username and password
2. Check authentication method supported
3. Test credentials separately
4. Review proxy logs

### Performance Issues
1. Increase timeout values
2. Reduce number of simultaneous tests
3. Check network latency
4. Review proxy server logs

## Examples

### Example 1: Setting up Corporate Proxy
```python
manager = EnhancedProxyManager()

# Add corporate HTTP proxy
success, msg, proxy_id = manager.add_proxy(
    "http://john.doe:password123@corp-proxy.company.com:8080",
    tags=["corporate", "http", "production"],
    notes="Main corporate proxy for all outbound traffic"
)

# Test the proxy
success, message = manager.test_proxy(proxy_id)

# Get statistics
stats = manager.get_statistics()
print(f"Total active proxies: {stats['active_proxies']}")
```

### Example 2: Managing Multiple Proxy Types
```python
# Add various proxy types
proxies_config = [
    ("http://proxy1.example.com:8080", ["http", "backup"]),
    ("https://proxy2.example.com:8443", ["https", "secure"]),
    ("socks5://user:pass@socks.example.com:1080", ["socks5", "vpn"]),
]

for url, tags in proxies_config:
    success, msg, proxy_id = manager.add_proxy(url, tags=tags)
    print(f"Added: {proxy_id}")

# Test all
results = manager.test_all_proxies()

# Get report
report = manager.export_report()
print(f"Success rate: {report['summary']['success_rate']}%")
```

### Example 3: Filtering and Searching
```python
# Get all SOCKS5 proxies
socks5_proxies = manager.get_proxies_by_type(ProxyType.SOCKS5)

# Get production proxies
prod_proxies = manager.get_proxies_by_tag("production")

# Get active proxies only
active = [p for p in manager.get_all_proxies(active_only=True)]

# Filter by test status
passed_proxies = [p for p in manager.get_all_proxies() if p['test_status'] == 'passed']
```

## Version History

- **v2.0**: Enhanced proxy system with HTTPS/SOCKS support
- **v1.0**: Basic proxy support (HTTP only)

## Support

For issues or questions, refer to the main project documentation or contact support.
