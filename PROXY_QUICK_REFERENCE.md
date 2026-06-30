# Enhanced Proxy System - Quick Reference

## URL Format Cheat Sheet

### HTTP Proxy
```
http://host:port
http://user:pass@host:port
http://proxy.example.com:8080
http://john:secret@proxy.example.com:8080
```

### HTTPS Proxy
```
https://host:port
https://user:pass@host:port
https://secure.example.com:8443
https://john:secret@secure.example.com:8443
```

### SOCKS4 Proxy
```
socks4://host:port
socks4://socks.example.com:1080
Note: No authentication support
```

### SOCKS5 Proxy
```
socks5://host:port
socks5://user:pass@host:port
socks5://socks.example.com:1080
socks5://john:secret@socks.example.com:1080
```

## Common Ports

| Protocol | Default | Alternative |
|----------|---------|-------------|
| HTTP | 80 | 8080, 3128, 8000 |
| HTTPS | 443 | 8443, 8080 |
| SOCKS4 | 1080 | 1080, 9090 |
| SOCKS5 | 1080 | 1080, 9090 |

## Python Quick Start

```python
from enhanced_proxy_system import EnhancedProxyManager

# Initialize
manager = EnhancedProxyManager()

# Add proxy
success, msg, proxy_id = manager.add_proxy(
    "socks5://user:pass@proxy.example.com:1080",
    tags=["vpn", "secure"],
    notes="My VPN proxy"
)

# Test proxy
success, msg = manager.test_proxy(proxy_id)
print(f"Test: {msg}")

# List all proxies
proxies = manager.get_all_proxies()
for p in proxies:
    print(f"{p['id']}: {p['url']}")

# Get by type
socks5_proxies = manager.get_proxies_by_type(ProxyType.SOCKS5)

# Get by tag
vpn_proxies = manager.get_proxies_by_tag("vpn")

# Delete
manager.remove_proxy(proxy_id)
```

## API Endpoints Quick Reference

### Proxy Management
```
GET  /api/proxies                    - List all proxies
POST /api/proxies                    - Add proxy
GET  /api/proxies/<id>               - Get proxy details
DELETE /api/proxies/<id>             - Delete proxy
PUT  /api/proxies/<id>/toggle        - Enable/disable
```

### Testing & Validation
```
POST /api/proxies/<id>/test          - Test single proxy
POST /api/proxies/test-all           - Test all proxies
```

### Filtering & Organization
```
GET  /api/proxies/by-type/<type>     - Get proxies by type
GET  /api/proxies/by-tag/<tag>       - Get proxies by tag
POST /api/proxies/<id>/tags          - Add tag to proxy
```

### Reports
```
GET  /api/proxies/report             - Export full report
```

## cURL Examples

### Add HTTP Proxy
```bash
curl -X POST http://localhost:5000/api/proxies \
  -H "Content-Type: application/json" \
  -d '{
    "url": "http://proxy.example.com:8080",
    "tags": ["http"],
    "notes": "Corporate proxy"
  }'
```

### Add SOCKS5 with Auth
```bash
curl -X POST http://localhost:5000/api/proxies \
  -H "Content-Type: application/json" \
  -d '{
    "url": "socks5://user:password@socks.example.com:1080",
    "tags": ["socks5", "vpn"],
    "notes": "SOCKS5 with authentication"
  }'
```

### Test Proxy
```bash
curl -X POST http://localhost:5000/api/proxies/{proxy_id}/test \
  -H "Content-Type: application/json" \
  -d '{"timeout": 10}'
```

### List All Proxies
```bash
curl http://localhost:5000/api/proxies
```

### Get by Type
```bash
curl http://localhost:5000/api/proxies/by-type/socks5
```

### Get by Tag
```bash
curl http://localhost:5000/api/proxies/by-tag/vpn
```

## JavaScript/Frontend Usage

### Fetch All Proxies
```javascript
const response = await fetch('/api/proxies');
const { proxies, statistics } = await response.json();
console.log(`Total: ${statistics.total_proxies}`);
console.log(`Active: ${statistics.active_proxies}`);
```

### Add Proxy
```javascript
const response = await fetch('/api/proxies', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    url: 'socks5://user:pass@socks.example.com:1080',
    tags: ['vpn', 'secure'],
    notes: 'Production SOCKS5'
  })
});
const { success, id } = await response.json();
```

### Test Proxy
```javascript
const response = await fetch(`/api/proxies/${proxyId}/test`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ timeout: 10 })
});
const { success, message } = await response.json();
alert(`Test: ${message}`);
```

### Get Statistics
```javascript
const response = await fetch('/api/proxies');
const { statistics } = await response.json();

console.log(`Total: ${statistics.total_proxies}`);
console.log(`HTTP: ${statistics.by_type.http}`);
console.log(`HTTPS: ${statistics.by_type.https}`);
console.log(`SOCKS4: ${statistics.by_type.socks4}`);
console.log(`SOCKS5: ${statistics.by_type.socks5}`);
```

## Configuration File Structure

Location: `/tmp/sc-proxies/proxies.json`

```json
[
  {
    "id": "proxy123456",
    "url": "socks5://user:pass@socks.example.com:1080",
    "proxy_type": "socks5",
    "host": "socks.example.com",
    "port": 1080,
    "credentials": {
      "username": "user",
      "password": "pass",
      "auth_type": "basic"
    },
    "timeout": 10,
    "retry_count": 3,
    "tags": ["vpn", "secure"],
    "is_active": true,
    "created_at": "2024-06-29T10:00:00",
    "last_tested": "2024-06-29T10:15:00",
    "test_status": "passed",
    "notes": "Production proxy"
  }
]
```

## Proxy Selection Guide

### Choose HTTP if:
- Corporate environment
- Unencrypted traffic OK
- Wide compatibility needed
- Simple setup preferred

### Choose HTTPS if:
- Sensitive data transit
- Encrypted connection required
- Corporate approved
- Performance acceptable

### Choose SOCKS4 if:
- Legacy system support
- No authentication needed
- Simple protocol required
- IPv4 only sufficient

### Choose SOCKS5 if:
- Maximum flexibility needed
- Authentication required
- Any traffic type
- IPv6 support needed
- Universal compatibility required

## Troubleshooting Quick Tips

**Proxy not connecting?**
1. Check URL format: `protocol://[user:pass@]host:port`
2. Verify port number (1-65535)
3. Test connectivity: `ping host`
4. Check firewall rules

**Authentication failing?**
1. Verify credentials (username:password)
2. Check auth method (Basic, SOCKS5 RFC 1929)
3. Test with SOCKS5 only (no auth for SOCKS4)
4. Review proxy documentation

**Validation timeout?**
1. Increase timeout value
2. Check network latency
3. Verify proxy responsiveness
4. Try different proxy

**Adding proxy fails?**
1. Check URL format
2. Validate protocol spelling
3. Ensure port in range 1-65535
4. Check for reserved characters

## Performance Tips

- Test proxies during off-peak hours
- Use appropriate timeout values (10-30 seconds)
- Batch test multiple proxies
- Monitor success rates regularly
- Rotate proxies for load distribution

## Security Reminders

- Store credentials securely
- Use HTTPS/SOCKS5 for sensitive data
- Validate proxy before deployment
- Monitor proxy usage
- Audit configurations regularly
- Restrict API access
- Rotate credentials periodically

## Common Scenarios

### Scenario 1: Corporate HTTP Proxy
```
URL: http://user:password@proxy.company.com:8080
Tags: corporate, http, authenticated
Use: General corporate traffic
```

### Scenario 2: SOCKS5 VPN
```
URL: socks5://user:password@vpn.company.com:1080
Tags: vpn, socks5, secure
Use: Secure remote access, any traffic type
```

### Scenario 3: HTTPS Secure Proxy
```
URL: https://user:password@secure-proxy.company.com:8443
Tags: https, secure, production
Use: Sensitive data, encrypted channels
```

### Scenario 4: Legacy SOCKS4
```
URL: socks4://legacy-proxy.company.com:1080
Tags: legacy, socks4, old-systems
Use: Legacy system support, no auth needed
```

## Environment Variables (Optional)

```bash
# Set default timeout
export PROXY_TIMEOUT=15

# Set config directory
export PROXY_CONFIG_DIR=/custom/path/proxies

# Enable debug logging
export PROXY_DEBUG=1
```

## Statistics Interpretation

```
Total Proxies: All configured proxies
Active Proxies: Currently enabled proxies
Tested Proxies: Proxies that have been tested
Passed Tests: Proxies with successful last test
Success Rate: (Passed Tests / Tested Proxies) * 100%
By Type: Count of each proxy type
```

## File Locations

| Item | Path |
|------|------|
| Proxies Config | `/tmp/sc-proxies/proxies.json` |
| Reports | `/tmp/sc-proxies/proxy_report.json` |
| Logs | Application logs (see framework) |
| Legacy Config | `/tmp/sc-fingerprints/proxies.json` |

## Version Info

- **Current Version**: 2.0
- **Release Date**: 2024-06-29
- **Supported Protocols**: HTTP, HTTPS, SOCKS4, SOCKS5
- **Status**: Production Ready

## Need More Help?

1. Check `ENHANCED_PROXY_GUIDE.md` for detailed documentation
2. Review `PROXY_SYSTEM_INTEGRATION.md` for architecture
3. Run `python test_enhanced_proxy_system.py` for examples
4. Check API responses for error messages

---

**Quick Reference Version**: 2.0 | **Last Updated**: 2024-06-29
