# Proxy Failure Detection and Automatic Fallback Handler

## Overview

The Proxy Fallback Handler provides intelligent proxy failure detection with automatic fallback to direct connections. It implements:

- **Real-time Proxy Health Monitoring**: Tracks proxy health and detects failures
- **Automatic Fallback**: Seamlessly switches to direct connection or fallback proxies on failure
- **Circuit Breaker Pattern**: Temporarily suspends failing proxies and attempts recovery
- **Retry Logic**: Configurable exponential backoff retry strategies
- **Metrics Collection**: Detailed tracking of connection attempts and performance
- **Thread-Safe Operations**: Safe for concurrent usage

## Architecture

### Components

#### 1. **FallbackConfig**
Configuration dataclass for the handler with all customizable options.

```python
config = FallbackConfig(
    primary_proxy_url="http://proxy.example.com:8080",
    fallback_proxies=[
        "http://fallback1.example.com:8080",
        "http://fallback2.example.com:8080"
    ],
    enable_fallback=True,
    enable_direct_fallback=True,
    max_retries=3,
    circuit_break_threshold=5,
    circuit_break_recovery_time=60.0
)
```

#### 2. **ProxyHealthMonitor**
Monitors proxy health and manages state transitions.

```python
monitor = ProxyHealthMonitor(config)

# Record failure
monitor.record_failure(proxy_url)

# Record success
monitor.record_success(proxy_url)

# Check availability
is_available = monitor.is_proxy_available(proxy_url)

# Get health statistics
stats = monitor.get_stats()
```

#### 3. **FallbackHandler**
Main handler for executing requests with automatic fallback.

```python
handler = FallbackHandler(config)

# Execute request with automatic fallback
success, response, info = handler.execute_request(
    url="https://api.example.com/data",
    method="GET",
    headers={"Authorization": "Bearer token"}
)

# Check health status
status = handler.get_health_status()

# Get metrics
metrics = handler.get_metrics()

# Export metrics
handler.export_metrics("/tmp/proxy_metrics.json")
```

## Connection Flow

### Standard Flow (with fallback enabled)

```
1. Primary Proxy
   ├─ Success → Return response
   └─ Failure (with retries)
        ├─ All retries failed → Mark proxy unhealthy
        └─ Retry with backoff

2. Fallback Proxies (in order)
   ├─ Success → Return response
   └─ Failure (with retries)
        ├─ All retries failed → Mark proxy unhealthy
        └─ Retry with backoff

3. Direct Connection (if enabled)
   ├─ Success → Return response (fallback triggered)
   └─ Failure (with retries)
        └─ All methods exhausted → Return error
```

## Configuration Options

### Basic Settings

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `primary_proxy_url` | str | None | Primary proxy URL |
| `fallback_proxies` | List[str] | [] | List of fallback proxy URLs |
| `enable_fallback` | bool | True | Enable fallback mechanism |
| `enable_direct_fallback` | bool | True | Allow fallback to direct connection |

### Retry Configuration

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `max_retries` | int | 3 | Maximum retry attempts per proxy |
| `initial_retry_delay` | float | 1.0 | Initial retry delay (seconds) |
| `max_retry_delay` | float | 30.0 | Maximum retry delay (seconds) |
| `retry_backoff_factor` | float | 2.0 | Exponential backoff multiplier |

### Circuit Breaker Configuration

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `circuit_break_threshold` | int | 5 | Failures before circuit break |
| `circuit_break_recovery_time` | float | 60.0 | Recovery time (seconds) |

### Timeout Configuration

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `connection_timeout` | float | 10.0 | Connection timeout (seconds) |
| `read_timeout` | float | 30.0 | Read timeout (seconds) |
| `health_check_timeout` | float | 5.0 | Health check timeout (seconds) |

### Health Check Configuration

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `health_check_enabled` | bool | True | Enable health checks |
| `health_check_interval` | float | 30.0 | Check interval (seconds) |
| `health_check_url` | str | http://www.google.com/generate_204 | Health check target |

### Other Settings

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `enable_metrics` | bool | True | Enable metrics collection |
| `metrics_path` | str | /tmp/proxy_metrics | Metrics storage directory |
| `verify_ssl` | bool | True | Verify SSL certificates |
| `ca_bundle` | str | None | Path to CA bundle file |
| `user_agent` | str | ProxyFallbackHandler/1.0 | HTTP User-Agent header |

## Usage Examples

### Basic Usage

```python
from proxy_fallback_handler import FallbackConfig, FallbackHandler

# Create configuration
config = FallbackConfig(
    primary_proxy_url="http://proxy.example.com:8080",
    fallback_proxies=["http://fallback.example.com:8080"],
    enable_direct_fallback=True
)

# Create handler
handler = FallbackHandler(config)

# Execute request
success, response, info = handler.execute_request(
    url="https://api.example.com/data",
    method="GET"
)

if success:
    print(f"Success: {info}")
    print(f"Data: {response.read()}")
else:
    print(f"Failed: {info}")
```

### Advanced Configuration

```python
config = FallbackConfig(
    primary_proxy_url="http://proxy.example.com:8080",
    fallback_proxies=[
        "http://fallback1.example.com:8080",
        "http://fallback2.example.com:8080"
    ],
    enable_direct_fallback=True,
    max_retries=5,
    initial_retry_delay=0.5,
    max_retry_delay=20.0,
    circuit_break_threshold=3,
    circuit_break_recovery_time=120.0,
    connection_timeout=15.0,
    enable_metrics=True,
    verify_ssl=False  # For testing only
)

handler = FallbackHandler(config)
```

### Health Monitoring

```python
# Get health status
status = handler.get_health_status()
print(f"Connection State: {status['connection_state']}")
print(f"Monitor Stats: {status['monitor_stats']}")

# Record manual failure
handler.health_monitor.record_failure(proxy_url)

# Check proxy availability
is_available = handler.health_monitor.is_proxy_available(proxy_url)
```

### Metrics Collection

```python
# Get all metrics
metrics = handler.get_metrics()

# Export metrics to file
export_data = handler.export_metrics("/tmp/metrics.json")

# Access summary
print(f"Total Requests: {export_data['summary']['total_requests']}")
print(f"Success Rate: {export_data['summary']['success_rate']}%")
print(f"Fallback Triggered: {export_data['summary']['fallback_triggered_count']} times")

# Analyze metrics
for metric in metrics:
    if metric['fallback_triggered']:
        print(f"Fallback used: {metric['timestamp']}")
```

### Retry Strategy

```python
# Configure retry strategy
config = FallbackConfig(
    primary_proxy_url=proxy_url,
    max_retries=4,
    initial_retry_delay=0.5,
    max_retry_delay=30.0,
    retry_backoff_factor=2.0
)

handler = FallbackHandler(config)

# Retry delays will be:
# Attempt 0: no delay
# Attempt 1: 0.5s
# Attempt 2: 1.0s
# Attempt 3: 2.0s
# Attempt 4: 4.0s (capped at max_retry_delay)
```

## Connection States

| State | Description |
|-------|-------------|
| `CONNECTED` | Successfully connected via proxy or direct |
| `DISCONNECTED` | No active connection |
| `DEGRADED` | Connection operational but with issues |
| `RECOVERING` | Attempting to recover from failure |

## Proxy States

| State | Description |
|-------|-------------|
| `HEALTHY` | Proxy working normally |
| `UNHEALTHY` | Proxy has experienced failures |
| `SUSPENDED` | Circuit breaker active, proxy temporarily disabled |
| `RECOVERING` | Attempting to recover after suspension |

## Circuit Breaker Pattern

The circuit breaker prevents repeated attempts to failing proxies:

```
HEALTHY (normal operation)
   ↓ (failures accumulate)
SUSPENDED (circuit open, proxy disabled)
   ↓ (after recovery_time)
RECOVERING (testing if proxy is back up)
   ↓
HEALTHY (success) or SUSPENDED (still failing)
```

Example:
```python
config = FallbackConfig(
    primary_proxy_url=proxy_url,
    circuit_break_threshold=5,  # Trip after 5 failures
    circuit_break_recovery_time=60.0  # Try again after 60 seconds
)
```

## Retry Logic with Exponential Backoff

Retry strategy with exponential backoff prevents overwhelming failing proxies:

```python
# Configuration
config = FallbackConfig(
    max_retries=4,
    initial_retry_delay=1.0,
    retry_backoff_factor=2.0,
    max_retry_delay=30.0
)

# Resulting delays:
# Retry 0: immediate
# Retry 1: 1.0 * 2^0 = 1.0s
# Retry 2: 1.0 * 2^1 = 2.0s
# Retry 3: 1.0 * 2^2 = 4.0s
# Retry 4: min(1.0 * 2^3, 30.0) = 8.0s
```

## Metrics Format

Exported metrics follow this structure:

```json
{
  "summary": {
    "total_requests": 100,
    "successful_requests": 95,
    "failed_requests": 5,
    "success_rate": 95.0,
    "fallback_triggered_count": 3,
    "average_response_time": 0.45,
    "generated_at": "2024-01-15T10:30:00.000000"
  },
  "metrics": [
    {
      "timestamp": "2024-01-15T10:30:00.000000",
      "proxy_used": "http://proxy.example.com:8080",
      "is_direct": false,
      "success": true,
      "response_time": 0.35,
      "status_code": 200,
      "error_message": null,
      "retry_count": 0,
      "fallback_triggered": false
    },
    ...
  ]
}
```

## Error Handling

### Common Error Scenarios

1. **All proxies down, direct connection fails**
   ```python
   success, response, info = handler.execute_request(url)
   # success = False
   # info = "All connection methods failed"
   ```

2. **Primary proxy fails, fallback succeeds**
   ```python
   success, response, info = handler.execute_request(url)
   # success = True
   # info = "Connected via http://fallback.example.com:8080"
   ```

3. **Circuit breaker active**
   ```python
   success, response, info = handler.execute_request(url)
   # Proxy is temporarily suspended, tries fallback
   ```

## SSL/TLS Configuration

### With Certificate Verification

```python
config = FallbackConfig(
    primary_proxy_url=proxy_url,
    verify_ssl=True,
    ca_bundle="/path/to/ca-bundle.crt"
)
handler = FallbackHandler(config)
```

### Without Certificate Verification (testing only)

```python
config = FallbackConfig(
    primary_proxy_url=proxy_url,
    verify_ssl=False
)
handler = FallbackHandler(config)
```

## Thread Safety

The handler is thread-safe for concurrent operations:

```python
import threading

config = FallbackConfig(primary_proxy_url=proxy_url)
handler = FallbackHandler(config)

def make_requests():
    for i in range(10):
        success, response, info = handler.execute_request(url)

threads = [threading.Thread(target=make_requests) for _ in range(5)]

for thread in threads:
    thread.start()

for thread in threads:
    thread.join()

# Safe to access metrics from any thread
metrics = handler.get_metrics()
```

## Integration with Existing Code

### With requests library

```python
import requests
from proxy_fallback_handler import FallbackConfig, FallbackHandler

class RequestsWithFallback:
    def __init__(self, proxy_url, fallback_proxies=None):
        config = FallbackConfig(
            primary_proxy_url=proxy_url,
            fallback_proxies=fallback_proxies or []
        )
        self.handler = FallbackHandler(config)

    def get(self, url, **kwargs):
        success, response, info = self.handler.execute_request(
            url=url,
            method="GET"
        )
        
        if success:
            return response
        raise Exception(info)

# Usage
client = RequestsWithFallback("http://proxy.example.com:8080")
response = client.get("https://api.example.com/data")
```

### With urllib3

```python
from urllib3 import PoolManager
from proxy_fallback_handler import FallbackConfig, FallbackHandler

class PoolManagerWithFallback:
    def __init__(self, proxy_url):
        config = FallbackConfig(primary_proxy_url=proxy_url)
        self.handler = FallbackHandler(config)

    def request(self, method, url, **kwargs):
        success, response, info = self.handler.execute_request(
            url=url,
            method=method
        )
        
        return response if success else None
```

## Monitoring and Alerting

### Health Check Integration

```python
from proxy_fallback_handler import FallbackConfig, FallbackHandler

config = FallbackConfig(
    primary_proxy_url=proxy_url,
    health_check_enabled=True,
    health_check_interval=30.0
)

handler = FallbackHandler(config)

# Periodically check health
import time

def monitor_health():
    while True:
        status = handler.get_health_status()
        
        if status['connection_state'] == 'disconnected':
            # Alert: connection down
            print("ALERT: Connection is down")
        
        time.sleep(30)
```

### Metrics Export for Analysis

```python
import json
from datetime import datetime

def generate_report(handler):
    export_data = handler.export_metrics()
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "success_rate": export_data["summary"]["success_rate"],
        "total_requests": export_data["summary"]["total_requests"],
        "fallback_count": export_data["summary"]["fallback_triggered_count"],
        "avg_response_time": export_data["summary"]["average_response_time"]
    }
    
    with open("/tmp/proxy_report.json", "w") as f:
        json.dump(report, f, indent=2)
```

## Best Practices

### 1. **Configure Appropriate Timeouts**
```python
config = FallbackConfig(
    connection_timeout=15.0,  # For slow networks
    read_timeout=30.0,
    health_check_timeout=5.0
)
```

### 2. **Set Reasonable Circuit Breaker Thresholds**
```python
config = FallbackConfig(
    circuit_break_threshold=3,  # Not too low
    circuit_break_recovery_time=60.0  # Allow recovery
)
```

### 3. **Enable Metrics for Analysis**
```python
config = FallbackConfig(
    enable_metrics=True,
    metrics_path="/var/log/proxy_metrics"
)
```

### 4. **Use Graduated Retries**
```python
config = FallbackConfig(
    max_retries=3,
    initial_retry_delay=0.5,
    retry_backoff_factor=2.0
)
```

### 5. **Monitor Health Regularly**
```python
status = handler.get_health_status()

if status['connection_state'] == 'disconnected':
    # Take appropriate action
    pass
```

## Troubleshooting

### Issue: All requests failing
```python
# Check proxy availability
for proxy_url in [config.primary_proxy_url] + config.fallback_proxies:
    is_available = handler.health_monitor.is_proxy_available(proxy_url)
    state = handler.health_monitor.get_proxy_state(proxy_url)
    print(f"{proxy_url}: {state.value}")
```

### Issue: Excessive fallback usage
```python
# Check metrics
export_data = handler.export_metrics()
fallback_rate = (
    export_data["summary"]["fallback_triggered_count"] / 
    export_data["summary"]["total_requests"]
)
print(f"Fallback rate: {fallback_rate * 100:.1f}%")
```

### Issue: Slow response times
```python
# Analyze response times
metrics = handler.get_metrics()
avg_time = sum(m['response_time'] for m in metrics) / len(metrics)
print(f"Average response time: {avg_time:.2f}s")
```

## Performance Considerations

1. **Metrics Collection Overhead**: Minimal impact on request performance
2. **Health Checks**: Run asynchronously, can be disabled if needed
3. **Memory Usage**: Metrics stored in memory, export regularly for cleanup
4. **Thread Safety**: Uses locks for thread-safe operations, minimal contention

## License

This proxy fallback handler is provided as part of the sc-generator project.

## Support

For issues, feature requests, or contributions, please refer to the project repository.
