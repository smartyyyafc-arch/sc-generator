# TLS Certificate Pinning for C2 Proxy Connections

## Overview

This implementation provides comprehensive TLS certificate pinning for C2 proxy connections to prevent Man-in-the-Middle (MITM) attacks during authorized pentesting operations. The system supports multiple pinning strategies, pin rotation, fallback mechanisms, and detailed audit logging.

## Architecture

### Core Components

1. **TLSPinningManager** - Central management of certificate pins
2. **CertificateExtractor** - Extract certificates from remote servers
3. **PinHashGenerator** - Generate hash-based pins
4. **TLSPinningValidator** - Validate certificates against pins
5. **HTTPSConnectionWithPinning** - HTTPS requests with pin validation
6. **C2ProxyPinningConnector** - Integration with C2 proxy connections
7. **C2ProxyFleet** - Manage multiple proxies with pinning

## Pinning Strategies

### 1. Certificate Pinning
- Pin the entire SSL/TLS certificate
- Most restrictive but ensures certificate hasn't changed
- Requires pin rotation when certificate renews

```python
strategy = PinningStrategy.CERTIFICATE
```

### 2. Public Key Pinning
- Pin only the public key component
- Survives certificate renewal if key remains same
- Recommended for long-term stability

```python
strategy = PinningStrategy.PUBLIC_KEY
```

### 3. SPKI Pinning
- Pin Subject Public Key Info structure
- Similar to public key pinning
- Industry standard approach

```python
strategy = PinningStrategy.SPKI
```

### 4. Certificate Chain Pinning
- Pin intermediate or root certificates
- Provides flexibility for certificate rotation
- Protects against rogue intermediate CAs

```python
strategy = PinningStrategy.CHAIN
```

## Hash Algorithms

- **SHA-256** (default) - Current industry standard
- **SHA-384** - Higher security margin
- **SHA-512** - Maximum security

## Usage Guide

### 1. Initialize Pinning Manager

```python
from tls_pinning_c2_proxy import TLSPinningManager, PinningStrategy, HashAlgorithm

# Create manager
manager = TLSPinningManager(config_dir='/tmp/sc-pins')
```

### 2. Add Pins from Remote Server

```python
# Add pin by connecting to server
success, message, pin_id = manager.add_pin_from_server(
    host='c2.example.com',
    port=443,
    strategy=PinningStrategy.PUBLIC_KEY,
    hash_algorithm=HashAlgorithm.SHA256,
    expiration_days=365,
    notes='C2 proxy primary handler'
)

if success:
    print(f"Pin added: {pin_id}")
else:
    print(f"Error: {message}")
```

### 3. Add Certificate Chain Pins

```python
# Pin entire certificate chain
success, message = manager.add_chain_pin_from_server(
    host='c2.example.com',
    port=443,
    hash_algorithm=HashAlgorithm.SHA256,
    expiration_days=365
)
```

### 4. Validate Connections

```python
# Validate connection to server
result = manager.validate_connection(
    host='c2.example.com',
    port=443,
    timeout=10.0
)

if result.is_valid:
    print(f"Pin validation passed: {result.matched_pin_id}")
    print(f"Strategy: {result.strategy_used.value}")
else:
    print(f"Pin validation failed: {result.error_message}")
```

### 5. Rotate Pins

```python
# Rotate pins (backup old, add new)
success, message = manager.rotate_pins(
    host='c2.example.com',
    port=443,
    strategy=PinningStrategy.PUBLIC_KEY,
    hash_algorithm=HashAlgorithm.SHA256,
    expiration_days=365
)
```

### 6. Make Pinned HTTPS Requests

```python
from tls_pinning_c2_proxy import HTTPSConnectionWithPinning

# Create connection handler
https_conn = HTTPSConnectionWithPinning(manager)

# Make request with pin validation
success, response, error = https_conn.make_pinned_request(
    url='https://c2.example.com/api/data',
    method='GET',
    headers={'User-Agent': 'C2Client/1.0'},
    verify_pins=True,
    timeout=10.0
)

if success:
    print(f"Response: {response}")
else:
    print(f"Error: {error}")
```

## C2 Proxy Integration

### Setup Pinned C2 Proxy Connection

```python
from c2_proxy_pinning_integration import (
    C2ProxyConfig,
    C2ProxyPinningConnector,
    FailoverMode,
    PinningStrategy,
    HashAlgorithm
)

# Create proxy configuration
config = C2ProxyConfig(
    proxy_host='c2-proxy.example.com',
    proxy_port=443,
    proxy_protocol='https',
    enable_pinning=True,
    pinning_strategy=PinningStrategy.PUBLIC_KEY,
    hash_algorithm=HashAlgorithm.SHA256,
    pin_expiration_days=365,
    failover_mode=FailoverMode.FALLBACK,
    fallback_proxies=[
        'c2-backup1.example.com:443',
        'c2-backup2.example.com:443'
    ],
    connection_timeout=10.0,
    enable_audit=True
)

# Create pinned connector
connector = C2ProxyPinningConnector(manager, config)

# Validate and connect through proxy
result = connector.validate_and_connect(
    target_url='https://command.example.com/beacon',
    method='POST',
    headers={'Content-Type': 'application/json'},
    data=b'{"beacon_id": "12345"}'
)

if result.success:
    print(f"Connected through: {result.proxy_host}:{result.proxy_port}")
    if result.fallback_used:
        print(f"Using fallback: {result.fallback_proxy}")
else:
    print(f"Connection failed: {result.error_message}")
```

### Manage Multiple Proxies (Fleet)

```python
from c2_proxy_pinning_integration import C2ProxyFleet

# Create fleet manager
fleet = C2ProxyFleet(manager)

# Add proxies
fleet.add_proxy('primary', primary_config)
fleet.add_proxy('secondary', secondary_config)
fleet.add_proxy('backup', backup_config)

# Initialize pins for all proxies
fleet.initialize_proxy_pins('primary')
fleet.initialize_proxy_pins('secondary')
fleet.initialize_proxy_pins('backup')

# Validate entire fleet
validation_results = fleet.validate_fleet()
for proxy_id, is_valid in validation_results.items():
    print(f"{proxy_id}: {'Valid' if is_valid else 'Invalid'}")

# Rotate all pins
rotation_results = fleet.rotate_all_pins()

# Get fleet status
status = fleet.get_fleet_status()
print(f"Fleet size: {len(status)}")

# Export comprehensive report
fleet.export_fleet_report('/tmp/fleet_report.json')
```

## Failover Modes

### STRICT Mode (Default)
- Rejects connection if pin validation fails
- No fallback allowed
- Most secure, prevents any MITM

```python
failover_mode=FailoverMode.STRICT
```

### GRACEFUL Mode
- Logs warning but allows connection
- Useful for development/testing
- Should not be used in production

```python
failover_mode=FailoverMode.GRACEFUL
```

### FALLBACK Mode
- Tries fallback proxies if primary fails
- Provides resilience without compromising security
- Recommended for production

```python
failover_mode=FailoverMode.FALLBACK
fallback_proxies=['backup1:443', 'backup2:443']
```

### ALERT Mode
- Alerts operator but waits for decision
- Requires manual intervention
- Useful for critical operations

```python
failover_mode=FailoverMode.ALERT
```

## Audit Logging

### Automatic Audit Events

```python
# View audit log
audit_log = manager.export_audit_log()

# Export to file
manager.export_audit_log('/tmp/audit.json')

# Search audit events
for event in audit_log:
    if event['event_type'] == 'validation_failed':
        print(f"Validation failure: {event['host']} - {event['details']}")
```

### Connection History

```python
# Get connection history
history = connector.get_connection_history()

# Export connection log
connector.export_connection_log('/tmp/connections.json')

# Analyze statistics
stats = connector.get_statistics()
print(f"Success rate: {stats['success_rate']:.2f}%")
```

## Security Best Practices

### 1. Pin Management
- Store pins in secure location with restricted permissions
- Regularly audit pins for expiration
- Maintain backup pins for key rotation

### 2. Certificate Rotation
- Plan pin rotation before certificate renewal
- Use SPKI or public key pinning for stability
- Maintain backup pins during transition

### 3. Fallback Configuration
- Configure fallback proxies on different infrastructure
- Use different certificate authorities for fallbacks
- Test fallback mechanisms regularly

### 4. Monitoring
- Monitor validation failures for potential attacks
- Alert on unexpected certificate changes
- Log all connection attempts for audit trail

### 5. Operational Security
- Restrict pin database access
- Use environment variables for sensitive data
- Implement principle of least privilege

## Pin Expiration and Rotation

### Automatic Expiration

```python
# Pins expire after specified days
add_pin_from_server(
    host='example.com',
    expiration_days=365
)

# Check expired pins
pins = manager.get_all_pins()
for host, pin_list in pins.items():
    for pin in pin_list:
        if pin.is_expired():
            print(f"Expired: {pin.pin_id}")
```

### Pin Rotation Workflow

```python
# 1. Generate new pin with backup
success, msg = manager.rotate_pins(
    host='example.com',
    port=443,
    expiration_days=365
)

# 2. Verify new pin validates
result = manager.validate_connection('example.com', 443)
print(f"Validation: {result.is_valid}")

# 3. Monitor backup pin usage
for event in manager.audit_log:
    if 'backup' in event['details']:
        print(f"Backup pin used: {event['timestamp']}")

# 4. After verification, remove old pin
manager.remove_pin('example.com', old_pin_id)
```

## Reporting and Analytics

### Export Reports

```python
# Comprehensive pinning report
report = manager.export_report('/tmp/pinning_report.json')

# C2 proxy fleet report
fleet_report = fleet.export_fleet_report('/tmp/fleet_report.json')

# Connection statistics
conn_report = connector.export_connection_log('/tmp/conn_log.json')
```

### Statistics

```python
# Pinning statistics
stats = manager.get_statistics()
print(f"Total hosts: {stats['total_hosts']}")
print(f"Total pins: {stats['total_pins']}")
print(f"Active pins: {stats['active_pins']}")
print(f"Audit events: {stats['audit_events']}")

# Connection statistics
conn_stats = connector.get_statistics()
print(f"Success rate: {conn_stats['success_rate']:.2f}%")
print(f"Fallback used: {conn_stats['fallback_used_attempts']}")
```

## Troubleshooting

### Pin Validation Failures

```python
# Check if pins exist
pins = manager.get_pins('example.com')
if not pins:
    print("No pins configured for host")

# Validate certificate manually
cert = CertificateExtractor.get_server_certificate('example.com', 443)
if cert:
    cert_info = CertificateExtractor.get_certificate_info(cert)
    print(f"Subject: {cert_info['subject_name']}")
    print(f"Issuer: {cert_info['issuer_name']}")
```

### Expired Pins

```python
# Check for expired pins
for host, pin_list in manager.pins.items():
    for pin in pin_list:
        if pin.is_expired():
            print(f"Expired pin: {pin.pin_id}")
            # Remove or rotate
            manager.remove_pin(host, pin.pin_id)
```

### Certificate Chain Issues

```python
# Retrieve and inspect certificate chain
chain = CertificateExtractor.get_certificate_chain('example.com', 443)
for idx, cert in enumerate(chain):
    info = CertificateExtractor.get_certificate_info(cert)
    print(f"Certificate {idx}: {info['subject_name']}")
```

## Performance Considerations

### Connection Caching
```python
# Pins are validated once per connection
# Validation results can be cached for batch operations
validation_cache = {}

for host in hosts:
    if host not in validation_cache:
        result = manager.validate_connection(host)
        validation_cache[host] = result
```

### Async Operations
```python
import threading

# Validate multiple hosts concurrently
def validate_host(host, port):
    return manager.validate_connection(host, port)

threads = []
for host in hosts:
    t = threading.Thread(target=validate_host, args=(host, 443))
    threads.append(t)
    t.start()

for t in threads:
    t.join()
```

## Integration with Existing Systems

### With proxy_fallback_handler.py
```python
# Combine with fallback handler
handler = ProxyFallbackHandler(fallback_config)

# Add pinning validation
pinning_manager = TLSPinningManager()
result = pinning_manager.validate_connection(proxy_url)

if result.is_valid:
    response = handler.execute_request(url)
```

### With enhanced_proxy_system.py
```python
# Use with enhanced proxy manager
proxy_manager = EnhancedProxyManager()
pinning_manager = TLSPinningManager()

# Validate proxy before use
for proxy in proxy_manager.get_all_proxies():
    result = pinning_manager.validate_connection(proxy['host'], proxy['port'])
```

### With c2_fingerprint_router.py
```python
# Integrate pinning with C2 routing
router = C2FingerprintRouter()
connector = C2ProxyPinningConnector(pinning_manager, config)

# Route with pinning validation
decision = router.route_beacon(beacon_id)
if connector.validate_and_connect(decision.selected_server.address):
    # Proceed with routed connection
```

## Files Provided

1. **tls_pinning_c2_proxy.py** - Core TLS pinning implementation
2. **c2_proxy_pinning_integration.py** - C2 proxy integration
3. **TLS_PINNING_GUIDE.md** - This comprehensive guide
4. **test_tls_pinning.py** - Test suite and examples

## References

- RFC 7469: Public Key Pinning Extension for HTTP
- OWASP Certificate Pinning Guide
- RFC 5246: TLS Protocol 1.2
- RFC 8446: TLS Protocol 1.3

## Support and Troubleshooting

For issues, check:
1. Audit log: `manager.export_audit_log()`
2. Pin configuration: `manager.get_all_pins()`
3. Connection history: `connector.get_connection_history()`
4. Certificate chain: `CertificateExtractor.get_certificate_chain()`
