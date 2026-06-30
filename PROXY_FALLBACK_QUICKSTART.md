# Proxy Fallback Handler - Quick Start Guide

## Installation

```bash
# Copy the handler to your project
cp proxy_fallback_handler.py your_project/
```

## 5-Minute Setup

### 1. Basic Usage

```python
from proxy_fallback_handler import FallbackConfig, FallbackHandler

# Create configuration
config = FallbackConfig(
    primary_proxy_url="http://proxy.example.com:8080",
    fallback_proxies=["http://backup-proxy.example.com:8080"],
    enable_direct_fallback=True
)

# Create handler
handler = FallbackHandler(config)

# Use it
success, response, info = handler.execute_request("https://api.example.com/data")

if success:
    print(f"Success: {info}")
else:
    print(f"Failed: {info}")
```

### 2. With Custom Configuration

```python
config = FallbackConfig(
    primary_proxy_url="http://proxy.example.com:8080",
    fallback_proxies=["http://fallback1.example.com:8080", "http://fallback2.example.com:8080"],
    max_retries=3,
    circuit_break_threshold=5,
    connection_timeout=15.0,
    enable_metrics=True
)

handler = FallbackHandler(config)
```

### 3. Execute Requests

```python
# Simple GET request
success, response, info = handler.execute_request(
    url="https://api.example.com/data",
    method="GET"
)

# POST request with headers
success, response, info = handler.execute_request(
    url="https://api.example.com/submit",
    method="POST",
    headers={"Authorization": "Bearer token123"}
)
```

### 4. Check Health

```python
# Get connection status
status = handler.get_health_status()
print(f"Connection state: {status['connection_state']}")

# Get proxy states
stats = status['monitor_stats']
for proxy_url, state in stats['proxy_states'].items():
    print(f"{proxy_url}: {state}")
```

### 5. Export Metrics

```python
# Export to file
handler.export_metrics("/tmp/proxy_metrics.json")

# Get metrics in memory
metrics = handler.get_metrics()
print(f"Total requests: {len(metrics)}")

# Get summary
export = handler.export_metrics()
print(f"Success rate: {export['summary']['success_rate']}%")
```

## Common Scenarios

### Scenario 1: Simple HTTP Proxy with Fallback

```python
config = FallbackConfig(
    primary_proxy_url="http://corporate-proxy:8080",
    fallback_proxies=["http://backup-proxy:8080"],
    enable_direct_fallback=True
)
handler = FallbackHandler(config)
```

### Scenario 2: Multiple Fallback Proxies

```python
config = FallbackConfig(
    primary_proxy_url="http://proxy1:8080",
    fallback_proxies=[
        "http://proxy2:8080",
        "http://proxy3:8080",
        "http://proxy4:8080"
    ],
    enable_direct_fallback=True
)
handler = FallbackHandler(config)
```

### Scenario 3: Aggressive Retry with Circuit Breaker

```python
config = FallbackConfig(
    primary_proxy_url="http://proxy:8080",
    max_retries=5,
    initial_retry_delay=0.5,
    max_retry_delay=20.0,
    circuit_break_threshold=3,  # Trip after 3 failures
    circuit_break_recovery_time=30.0  # Try again after 30s
)
handler = FallbackHandler(config)
```

### Scenario 4: Direct Connection Only with Metrics

```python
config = FallbackConfig(
    enable_fallback=False,  # Disable proxy fallback
    enable_direct_fallback=True,
    enable_metrics=True,
    metrics_path="/var/log/proxy_metrics"
)
handler = FallbackHandler(config)
```

### Scenario 5: High Security with SSL Verification

```python
config = FallbackConfig(
    primary_proxy_url="https://secure-proxy:8443",
    verify_ssl=True,
    ca_bundle="/etc/ssl/certs/ca-bundle.crt"
)
handler = FallbackHandler(config)
```

## Configuration Presets

### Development/Testing
```python
config = FallbackConfig(
    primary_proxy_url="http://localhost:8080",
    enable_direct_fallback=True,
    verify_ssl=False,  # For testing
    connection_timeout=5.0
)
```

### Production
```python
config = FallbackConfig(
    primary_proxy_url="http://proxy.example.com:8080",
    fallback_proxies=["http://proxy-backup.example.com:8080"],
    enable_direct_fallback=True,
    max_retries=3,
    circuit_break_threshold=5,
    verify_ssl=True,
    ca_bundle="/etc/ssl/certs/ca-bundle.crt",
    enable_metrics=True
)
```

### High Availability
```python
config = FallbackConfig(
    primary_proxy_url="http://proxy1.example.com:8080",
    fallback_proxies=[
        "http://proxy2.example.com:8080",
        "http://proxy3.example.com:8080",
        "http://proxy4.example.com:8080"
    ],
    enable_direct_fallback=True,
    max_retries=4,
    circuit_break_threshold=2,  # Aggressive
    circuit_break_recovery_time=30.0,
    enable_metrics=True
)
```

## Key Methods

### Execute Request
```python
success, response, info = handler.execute_request(
    url="https://example.com",
    method="GET",
    headers={"User-Agent": "MyApp/1.0"},
    timeout=30.0
)
```

### Get Metrics
```python
metrics = handler.get_metrics()  # List of metric dicts
export = handler.export_metrics()  # Summary + metrics
handler.export_metrics("/tmp/metrics.json")  # Save to file
```

### Get Health Status
```python
status = handler.get_health_status()
# Returns:
# {
#   "connection_state": "connected|disconnected|degraded|recovering",
#   "monitor_stats": {...},
#   "metrics_summary": {...}
# }
```

### Check Connection State
```python
state = handler.get_connection_state()  # ConnectionState enum
```

## Monitoring

### Track Success Rate
```python
export = handler.export_metrics()
success_rate = export['summary']['success_rate']
print(f"Success rate: {success_rate}%")
```

### Check Fallback Usage
```python
export = handler.export_metrics()
fallback_count = export['summary']['fallback_triggered_count']
print(f"Fallback used {fallback_count} times")
```

### Monitor Response Times
```python
export = handler.export_metrics()
avg_time = export['summary']['average_response_time']
print(f"Average response: {avg_time:.2f}s")
```

### Check Proxy States
```python
status = handler.get_health_status()
for proxy, state in status['monitor_stats']['proxy_states'].items():
    print(f"{proxy}: {state}")
```

## Error Handling

### All Proxies Down
```python
success, response, info = handler.execute_request(url)
if not success:
    if "All connection methods failed" in info:
        # All proxies and direct connection down
        print("Critical: No connectivity available")
```

### Proxy Temporarily Unavailable
```python
# Circuit breaker will skip this proxy temporarily
# Handler will try fallback proxies automatically
success, response, info = handler.execute_request(url)
print(f"Info: {info}")  # Will show which proxy/method was used
```

## Thread-Safe Usage

```python
import threading

config = FallbackConfig(primary_proxy_url="http://proxy:8080")
handler = FallbackHandler(config)

def worker():
    success, response, info = handler.execute_request("https://example.com")
    print(f"Thread result: {info}")

threads = [threading.Thread(target=worker) for _ in range(5)]
for t in threads:
    t.start()
for t in threads:
    t.join()
```

## Performance Tips

1. **Reuse Handler**: Create once, use for multiple requests
2. **Set Appropriate Timeouts**: Based on your network conditions
3. **Export Metrics Periodically**: To keep memory usage low
4. **Disable Health Checks**: If you don't need them

```python
# Good
handler = FallbackHandler(config)
for url in urls:
    handler.execute_request(url)  # Reuse

# Avoid
for url in urls:
    handler = FallbackHandler(config)  # Don't recreate
```

## Testing Locally

```python
# Test without actual proxies
config = FallbackConfig(
    enable_fallback=False,
    enable_direct_fallback=True,
    verify_ssl=False  # For testing self-signed certs
)
handler = FallbackHandler(config)

# Make direct requests
success, response, info = handler.execute_request("http://httpbin.org/get")
print(f"Direct connection test: {info}")
```

## Logging

Enable debug logging to see detailed information:

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('proxy_fallback_handler')
logger.setLevel(logging.DEBUG)

# Now run handler
success, response, info = handler.execute_request(url)
```

## Factory Functions

### Quick Creation
```python
from proxy_fallback_handler import create_default_handler

handler = create_default_handler(
    primary_proxy_url="http://proxy:8080",
    fallback_proxies=["http://fallback:8080"]
)
```

## Troubleshooting

### Handler not using fallback
1. Check if `enable_fallback=True`
2. Check if `enable_direct_fallback=True` for direct connection fallback
3. Verify proxy URLs are correct

### Metrics not being recorded
1. Check if `enable_metrics=True`
2. Verify metrics directory exists
3. Check write permissions

### Proxies marked as suspended
1. Failures exceeded `circuit_break_threshold`
2. Will recover after `circuit_break_recovery_time`
3. Monitor with `get_health_status()`

## Next Steps

- Read full guide: `PROXY_FALLBACK_GUIDE.md`
- Run tests: `python test_proxy_fallback_handler.py`
- Check examples: Look for example scripts in project
- Monitor logs: Enable logging and trace execution
