# Proxy Fallback Handler - API Reference

## Core Classes

### FallbackConfig

Configuration dataclass for the fallback handler.

```python
@dataclass
class FallbackConfig:
    primary_proxy_url: Optional[str] = None
    fallback_proxies: List[str] = field(default_factory=list)
    enable_fallback: bool = True
    enable_direct_fallback: bool = True
    
    # Retry configuration
    max_retries: int = 3
    initial_retry_delay: float = 1.0
    max_retry_delay: float = 30.0
    retry_backoff_factor: float = 2.0
    
    # Timeout configuration
    connection_timeout: float = 10.0
    read_timeout: float = 30.0
    health_check_timeout: float = 5.0
    
    # Circuit breaker
    circuit_break_threshold: int = 5
    circuit_break_recovery_time: float = 60.0
    
    # Health check
    health_check_enabled: bool = True
    health_check_interval: float = 30.0
    health_check_url: str = "http://www.google.com/generate_204"
    
    # Metrics
    enable_metrics: bool = True
    metrics_path: str = "/tmp/proxy_metrics"
    
    # SSL/TLS
    verify_ssl: bool = True
    ca_bundle: Optional[str] = None
    
    # User agent
    user_agent: str = "ProxyFallbackHandler/1.0"
```

### FallbackHandler

Main handler for executing requests with automatic fallback.

#### Constructor
```python
handler = FallbackHandler(config: FallbackConfig)
```

#### Methods

##### execute_request()
Execute HTTP request with automatic fallback.

```python
def execute_request(
    url: str,
    method: str = "GET",
    headers: Optional[Dict[str, str]] = None,
    timeout: Optional[float] = None
) -> Tuple[bool, Optional[Any], str]
```

**Parameters:**
- `url` (str): Target URL
- `method` (str): HTTP method (GET, POST, etc.)
- `headers` (dict): HTTP headers
- `timeout` (float): Request timeout in seconds

**Returns:**
- `success` (bool): True if successful
- `response`: Response object or None
- `info` (str): Information message

**Example:**
```python
success, response, info = handler.execute_request(
    url="https://api.example.com/data",
    method="GET",
    headers={"Authorization": "Bearer token"},
    timeout=30.0
)

if success:
    data = response.read()
else:
    print(f"Error: {info}")
```

##### get_metrics()
Get all recorded metrics.

```python
def get_metrics() -> List[Dict[str, Any]]
```

**Returns:**
List of metric dictionaries with fields:
- `timestamp`: When the request was made
- `proxy_used`: Proxy URL used (or None for direct)
- `is_direct`: True if direct connection was used
- `success`: Whether request was successful
- `response_time`: Time taken in seconds
- `status_code`: HTTP status code
- `error_message`: Error message if failed
- `retry_count`: Number of retries
- `fallback_triggered`: True if fallback was used

**Example:**
```python
metrics = handler.get_metrics()
for metric in metrics:
    print(f"{metric['timestamp']}: {metric['response_time']}s")
```

##### export_metrics()
Export metrics to file and return summary.

```python
def export_metrics(
    output_file: Optional[str] = None
) -> Dict[str, Any]
```

**Parameters:**
- `output_file` (str): Path to save JSON file (optional)

**Returns:**
Dictionary with:
- `summary`: Statistics summary
- `metrics`: List of all metrics

**Summary fields:**
- `total_requests`: Total number of requests
- `successful_requests`: Successful request count
- `failed_requests`: Failed request count
- `success_rate`: Percentage of successful requests
- `fallback_triggered_count`: Number of times fallback was used
- `average_response_time`: Average response time in seconds
- `generated_at`: Timestamp of export

**Example:**
```python
export = handler.export_metrics("/tmp/metrics.json")
print(f"Success Rate: {export['summary']['success_rate']}%")
```

##### get_health_status()
Get current health status.

```python
def get_health_status() -> Dict[str, Any]
```

**Returns:**
Dictionary with:
- `connection_state`: Current connection state
- `monitor_stats`: Proxy health statistics
- `metrics_summary`: Metrics summary

**Example:**
```python
status = handler.get_health_status()
print(f"State: {status['connection_state']}")
```

##### get_connection_state()
Get current connection state.

```python
def get_connection_state() -> ConnectionState
```

**Returns:**
- `ConnectionState.CONNECTED`: Connected
- `ConnectionState.DISCONNECTED`: Disconnected
- `ConnectionState.DEGRADED`: Degraded performance
- `ConnectionState.RECOVERING`: Attempting recovery

**Example:**
```python
state = handler.get_connection_state()
if state == ConnectionState.CONNECTED:
    print("Connected")
```

### ProxyHealthMonitor

Monitor proxy health and manage state.

```python
monitor = handler.health_monitor
```

#### Methods

##### record_failure()
Record a proxy failure.

```python
def record_failure(proxy_url: str) -> None
```

**Example:**
```python
monitor.record_failure("http://proxy.example.com:8080")
```

##### record_success()
Record a successful proxy connection.

```python
def record_success(proxy_url: str) -> None
```

**Example:**
```python
monitor.record_success("http://proxy.example.com:8080")
```

##### is_proxy_available()
Check if proxy is available for use.

```python
def is_proxy_available(proxy_url: str) -> bool
```

**Returns:**
- `True`: Proxy is available
- `False`: Proxy is suspended/unavailable

**Example:**
```python
if monitor.is_proxy_available(proxy_url):
    # Use proxy
    pass
```

##### get_proxy_state()
Get current state of proxy.

```python
def get_proxy_state(proxy_url: str) -> ProxyState
```

**Returns:**
- `ProxyState.HEALTHY`: Proxy is working
- `ProxyState.UNHEALTHY`: Proxy has issues
- `ProxyState.SUSPENDED`: Circuit breaker active
- `ProxyState.RECOVERING`: Attempting recovery

**Example:**
```python
state = monitor.get_proxy_state(proxy_url)
print(f"Proxy state: {state.value}")
```

##### check_proxy_health()
Check proxy connectivity via socket test.

```python
def check_proxy_health(proxy_url: str) -> Tuple[bool, str]
```

**Returns:**
- `success` (bool): True if reachable
- `message` (str): Status message

**Example:**
```python
success, msg = monitor.check_proxy_health(proxy_url)
if success:
    print(f"Proxy is healthy: {msg}")
```

##### get_stats()
Get health monitor statistics.

```python
def get_stats() -> Dict[str, Any]
```

**Returns:**
Dictionary with:
- `proxy_states`: Current state of each proxy
- `failure_counts`: Failure count for each proxy
- `last_failure_times`: Last failure timestamps

**Example:**
```python
stats = monitor.get_stats()
print(f"Failures: {stats['failure_counts']}")
```

## Enumerations

### ConnectionState

```python
class ConnectionState(Enum):
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    DEGRADED = "degraded"
    RECOVERING = "recovering"
```

### ProxyState

```python
class ProxyState(Enum):
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    SUSPENDED = "suspended"
    RECOVERING = "recovering"
```

### FallbackStrategy

```python
class FallbackStrategy(Enum):
    IMMEDIATE = "immediate"
    RETRY_THEN_FALLBACK = "retry_then_fallback"
    CIRCUIT_BREAKER = "circuit_breaker"
    GRADUATED = "graduated"
```

## Factory Functions

### create_fallback_handler()

Create handler with custom configuration.

```python
def create_fallback_handler(config: FallbackConfig) -> FallbackHandler
```

**Example:**
```python
config = FallbackConfig(primary_proxy_url="http://proxy:8080")
handler = create_fallback_handler(config)
```

### create_default_handler()

Create handler with minimal configuration.

```python
def create_default_handler(
    primary_proxy_url: Optional[str] = None,
    fallback_proxies: Optional[List[str]] = None
) -> FallbackHandler
```

**Example:**
```python
handler = create_default_handler(
    primary_proxy_url="http://proxy:8080",
    fallback_proxies=["http://fallback:8080"]
)
```

## Data Classes

### ConnectionMetrics

Represents a single request attempt.

```python
@dataclass
class ConnectionMetrics:
    timestamp: str              # ISO format timestamp
    proxy_used: Optional[str]   # Proxy URL or None
    is_direct: bool             # True if direct connection
    success: bool               # Request successful
    response_time: float        # Time in seconds
    status_code: Optional[int]  # HTTP status
    error_message: Optional[str] # Error if failed
    retry_count: int            # Number of retries
    fallback_triggered: bool    # Fallback was used
```

## Common Usage Patterns

### Pattern 1: Simple Request with Fallback

```python
config = FallbackConfig(
    primary_proxy_url="http://proxy:8080",
    fallback_proxies=["http://fallback:8080"],
    enable_direct_fallback=True
)

handler = FallbackHandler(config)
success, response, info = handler.execute_request(url)
```

### Pattern 2: Request with Error Handling

```python
try:
    success, response, info = handler.execute_request(url)
    if success:
        data = response.read()
    else:
        print(f"Request failed: {info}")
except Exception as e:
    print(f"Exception: {e}")
```

### Pattern 3: Monitoring and Metrics

```python
# Execute requests
for url in urls:
    handler.execute_request(url)

# Get metrics
export = handler.export_metrics("/tmp/metrics.json")
print(f"Success rate: {export['summary']['success_rate']}%")

# Check health
status = handler.get_health_status()
print(f"Connection state: {status['connection_state']}")
```

### Pattern 4: Custom Configuration

```python
config = FallbackConfig(
    primary_proxy_url="http://proxy:8080",
    fallback_proxies=["http://fallback1:8080", "http://fallback2:8080"],
    max_retries=5,
    initial_retry_delay=0.5,
    max_retry_delay=20.0,
    circuit_break_threshold=3,
    circuit_break_recovery_time=60.0,
    connection_timeout=15.0,
    verify_ssl=True,
    ca_bundle="/etc/ssl/certs/ca-bundle.crt"
)

handler = FallbackHandler(config)
```

### Pattern 5: Manual Health Check

```python
proxy_url = "http://proxy.example.com:8080"

# Check if available
if handler.health_monitor.is_proxy_available(proxy_url):
    # Use proxy
    pass

# Check connectivity
success, msg = handler.health_monitor.check_proxy_health(proxy_url)
print(f"Health: {msg}")

# Get state
state = handler.health_monitor.get_proxy_state(proxy_url)
print(f"State: {state.value}")
```

## Exception Handling

The handler may raise:
- `ValueError`: Invalid configuration
- `FileNotFoundError`: Certificate or CA bundle not found
- `urllib.error.HTTPError`: HTTP protocol errors
- `urllib.error.URLError`: Network errors
- `socket.timeout`: Connection timeouts
- `ssl.SSLError`: SSL/TLS errors

## Configuration Presets

### Development

```python
config = FallbackConfig(
    primary_proxy_url="http://localhost:8080",
    enable_direct_fallback=True,
    verify_ssl=False,
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
    primary_proxy_url="http://proxy1:8080",
    fallback_proxies=[
        "http://proxy2:8080",
        "http://proxy3:8080",
        "http://proxy4:8080"
    ],
    enable_direct_fallback=True,
    max_retries=4,
    circuit_break_threshold=2,
    circuit_break_recovery_time=30.0
)
```

## Thread Safety

All methods are thread-safe. Safe to use from multiple threads:

```python
import threading

handler = FallbackHandler(config)

def worker():
    success, response, info = handler.execute_request(url)

threads = [threading.Thread(target=worker) for _ in range(10)]
for t in threads:
    t.start()
for t in threads:
    t.join()

# Safe to access metrics from any thread
metrics = handler.get_metrics()
```

## Performance Metrics

Access performance statistics:

```python
export = handler.export_metrics()
summary = export['summary']

print(f"Total Requests: {summary['total_requests']}")
print(f"Success Rate: {summary['success_rate']}%")
print(f"Avg Response: {summary['average_response_time']:.2f}s")
print(f"Fallback Used: {summary['fallback_triggered_count']} times")
```

## Logging

Enable detailed logging:

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('proxy_fallback_handler')
logger.setLevel(logging.DEBUG)
```

Log levels used:
- `DEBUG`: Detailed operation information
- `INFO`: Normal operations and state changes
- `WARNING`: Proxy failures and circuit breaks
- `ERROR`: Unexpected errors

## Version & Compatibility

- **Python**: 3.7+
- **Dependencies**: Standard library only (urllib, socket, ssl, json, logging, threading, time)
- **License**: Part of sc-generator project

---

**Last Updated**: 2026-06-29
**API Version**: 1.0
**Status**: Production Ready
