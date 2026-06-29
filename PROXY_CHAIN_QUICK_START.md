# Proxy Chain Configuration - Quick Start Guide

## 5-Minute Start

### Installation

```bash
# No external dependencies required - uses Python stdlib only
python3 -c "from proxy_chain_builder import ProxyChainBuilder"
```

### Basic Usage

```python
from proxy_chain_builder import ProxyChainBuilder
from proxy_chain_executor import ProxyChainExecutor

# Step 1: Create builder
builder = ProxyChainBuilder("my-chain")

# Step 2: Add proxy hops
builder.add_hop("proxy1.example.com", 8080)
builder.add_hop("proxy2.example.com", 3128)

# Step 3: Build chain
chain = builder.build()

# Step 4: Execute request
executor = ProxyChainExecutor(chain)
success, response, info = executor.execute("https://api.example.com/data")

print(f"Result: {info}")
```

## Common Patterns

### Pattern 1: Authentication on Each Hop

```python
builder = ProxyChainBuilder("auth-chain")

# Hop 1: Corporate proxy
builder.add_hop(
    "corp-proxy.example.com", 8080,
    auth_type="basic",
    username="corp_user",
    password="corp_pass"
)

# Hop 2: ISP proxy
builder.add_hop(
    "isp-proxy.example.com", 3128,
    auth_type="basic",
    username="isp_user",
    password="isp_pass"
)

chain = builder.build()
```

### Pattern 2: Multiple Protocols

```python
builder = ProxyChainBuilder("multi-proto")

# HTTP proxy
builder.add_hop("proxy1.example.com", 8080, protocol="http")

# SOCKS5 proxy
builder.add_hop("proxy2.example.com", 1080, protocol="socks5")

# HTTPS with certificate
builder.add_hop(
    "proxy3.example.com", 8443,
    protocol="https",
    auth_type="certificate",
    cert_path="/path/to/cert.pem",
    key_path="/path/to/key.pem"
)

chain = builder.build()
```

### Pattern 3: Metrics Tracking

```python
builder = ProxyChainBuilder("tracked-chain")
builder.add_hop("proxy1.example.com", 8080)
builder.add_hop("proxy2.example.com", 3128)
builder.enable_metrics(True)

chain = builder.build()
executor = ProxyChainExecutor(chain)

# Execute multiple requests
for i in range(10):
    executor.execute(f"https://api.example.com/request/{i}")

# Get statistics
stats = executor.get_executor_stats()
print(f"Success rate: {stats['success_rate']:.1f}%")
print(f"Avg time: {stats['average_duration']:.2f}s")
```

### Pattern 4: Configuration from File

```json
{
  "chain_name": "prod-chain",
  "hops": [
    {
      "hostname": "proxy1.example.com",
      "port": 8080,
      "auth_type": "basic"
    },
    {
      "hostname": "proxy2.example.com",
      "port": 3128,
      "protocol": "https"
    }
  ],
  "total_timeout": 120
}
```

```python
from proxy_chain_builder import ProxyChainConfig, ProxyChainBuilder

# Load from file
config = ProxyChainConfig.from_file("chain.json")
chain = ProxyChainBuilder.from_config(config).build()
```

### Pattern 5: Error Handling

```python
executor = ProxyChainExecutor(chain)

success, response, info = executor.execute(
    url="https://api.example.com/data",
    max_retries=3,  # Retry up to 3 times
    timeout=30      # 30 second timeout
)

if success:
    print(f"Success: {info}")
    # Process response...
else:
    print(f"Failed: {info}")
    # Handle error...
```

## API Cheat Sheet

### Builder Methods

```python
builder = ProxyChainBuilder("name")

# Add hops
builder.add_hop(hostname, port, protocol="http", auth_type="none", **kwargs)
builder.add_hop_from_url("http://proxy:8080")

# Configuration
builder.set_chain_name("name")
builder.set_description("description")
builder.set_total_timeout(120)
builder.set_max_hops(10)
builder.set_allow_direct_fallback(True)
builder.enable_load_balancing(True)
builder.enable_metrics(True)

# Build
chain = builder.build()
```

### Chain Methods

```python
chain = builder.build()

# Get configuration
chain.get_all_hops()
chain.get_enabled_hops()
chain.get_hop_config(index)

# Metrics
chain.get_hop_metrics(index)
chain.get_all_metrics()

# State
chain.get_chain_state()
chain.get_chain_health()
chain.record_hop_success(index, response_time)
chain.record_hop_failure(index)
```

### Executor Methods

```python
executor = ProxyChainExecutor(chain)

# Execute
executor.execute(url, method="GET", headers=None, max_retries=1)

# History
executor.get_execution_history(limit=100)
executor.get_last_execution_trace()
executor.clear_history()

# Stats
executor.get_executor_stats()
executor.export_execution_report(file_path)
```

## Authentication Types

| Type | Setup | Notes |
|------|-------|-------|
| none | No auth required | Default |
| basic | `username`, `password` | HTTP Basic Auth |
| digest | `username`, `password` | HTTP Digest Auth |
| ntlm | `username`, `password`, `domain` | Windows NTLM |
| certificate | `cert_path`, `key_path`, `ca_bundle` | mTLS/Client certs |

## Troubleshooting

### Chain Won't Build

```python
chain = builder.build()  # Raises ValueError if invalid
```

Check validation:
```python
is_valid, errors = chain.config.validate()
if not is_valid:
    for error in errors:
        print(error)
```

### Request Fails Through Chain

```python
# Check chain health
health = chain.get_chain_health()
for hop_idx, hop in health['hops'].items():
    print(f"Hop {hop_idx}: {hop['state']}")
```

### See What's Happening

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Now run with detailed logging
executor.execute(url)
```

## Performance Tips

1. **Timeouts**: Set per-hop timeouts to prevent hanging
2. **Retries**: Use backoff-based retries (exponential by default)
3. **Metrics**: Disable if not needed (`enable_metrics=False`)
4. **Connection**: Reuse executor for multiple requests
5. **Hops**: Keep chains under 5 hops for best performance

## Security Best Practices

1. **Credentials**: Don't hardcode passwords
   ```python
   import os
   password = os.environ.get('PROXY_PASSWORD')
   builder.add_hop(..., password=password)
   ```

2. **SSL Verification**: Keep enabled by default
   ```python
   hop = ProxyHopConfig(..., verify_ssl=True)
   ```

3. **Certificate Validation**: Use CA bundles for self-signed certs
   ```python
   builder.add_hop(..., ca_bundle="/path/to/ca-bundle.pem")
   ```

4. **Audit Logging**: Check execution history
   ```python
   history = executor.get_execution_history()
   ```

## Examples

### Example 1: Simple 2-Hop

```python
builder = ProxyChainBuilder("simple")
builder.add_hop("proxy1.com", 8080)
builder.add_hop("proxy2.com", 3128)
chain = builder.build()
executor = ProxyChainExecutor(chain)
success, _, info = executor.execute("https://api.com/data")
```

### Example 2: With Auth

```python
builder = ProxyChainBuilder("with-auth")
builder.add_hop("proxy1.com", 8080, auth_type="basic", 
                username="u1", password="p1")
builder.add_hop("proxy2.com", 3128, auth_type="basic",
                username="u2", password="p2")
chain = builder.build()
```

### Example 3: Mixed Protocols

```python
builder = ProxyChainBuilder("mixed")
builder.add_hop("proxy1.com", 8080, protocol="http")
builder.add_hop("proxy2.com", 1080, protocol="socks5")
builder.add_hop("proxy3.com", 8443, protocol="https")
chain = builder.build()
```

### Example 4: With Fallback

```python
builder = ProxyChainBuilder("fallback")
builder.add_hop("primary.com", 8080)
builder.add_hop("secondary.com", 3128)
builder.set_allow_direct_fallback(True)
chain = builder.build()
```

### Example 5: Post Request

```python
executor = ProxyChainExecutor(chain)
success, response, info = executor.execute(
    url="https://api.com/submit",
    method="POST",
    headers={"Content-Type": "application/json"},
    body=b'{"key": "value"}',
    max_retries=2
)
```

## Testing Your Chain

```bash
# Run test suite
python3 test_proxy_chain.py

# Output should show:
# RESULTS: 20 passed, 0 failed
```

## File Reference

| File | Purpose |
|------|---------|
| `proxy_chain_builder.py` | Chain building and configuration |
| `proxy_chain_executor.py` | Request execution through chain |
| `test_proxy_chain.py` | Test suite (20 tests) |
| `PROXY_CHAIN_CONFIGURATION.md` | Full documentation |
| `PROXY_CHAIN_SUMMARY.md` | Implementation details |
| `PROXY_CHAIN_QUICK_START.md` | This file |

## Next Steps

1. **Read**: `PROXY_CHAIN_CONFIGURATION.md` for full API
2. **Explore**: Try the examples in this guide
3. **Integrate**: Add to your proxy infrastructure
4. **Monitor**: Use metrics to track performance
5. **Extend**: Customize for your needs

## Support

For issues or questions:
1. Check `PROXY_CHAIN_CONFIGURATION.md` troubleshooting section
2. Review test cases in `test_proxy_chain.py`
3. Enable debug logging with `logging.basicConfig(level=logging.DEBUG)`
4. Verify chain health with `chain.get_chain_health()`
