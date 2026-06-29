# Proxy Chain Configuration for Multi-Hop Routing

Complete guide for building and managing multi-hop proxy chains with automatic routing, authentication, and failure handling.

## Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Chain Builder](#chain-builder)
4. [Configuration](#configuration)
5. [Execution](#execution)
6. [Authentication](#authentication)
7. [Advanced Features](#advanced-features)
8. [Examples](#examples)
9. [API Reference](#api-reference)

## Overview

The proxy chain configuration system enables sophisticated multi-hop proxy routing scenarios:

- **Sequential Routing**: Route requests through multiple proxies in sequence
- **Per-Hop Authentication**: Each proxy hop can use different authentication methods
- **Protocol Support**: HTTP, HTTPS, SOCKS4, SOCKS5 protocols per hop
- **Failure Handling**: Automatic retry and fallback mechanisms
- **Metrics Collection**: Track performance metrics per hop
- **Chain Validation**: Detect circular dependencies and configuration errors

### Architecture

```
Client Request
    ↓
Chain Builder (configuration)
    ↓
ProxyChain (active chain instance)
    ↓
ProxyChainExecutor (request execution)
    ↓
Sequential Hop Execution
    Hop 1 (Proxy 1) → Hop 2 (Proxy 2) → Hop 3 (Proxy 3)
    ↓
Target Server
```

## Quick Start

### Basic 2-Hop Chain

```python
from proxy_chain_builder import ProxyChainBuilder

# Create builder
builder = ProxyChainBuilder("my-chain")

# Add hops
builder.add_hop(
    "proxy1.example.com", 8080,
    auth_type="basic",
    username="user1",
    password="pass1"
)
builder.add_hop(
    "proxy2.example.com", 3128,
    auth_type="basic",
    username="user2",
    password="pass2"
)

# Build chain
chain = builder.build()

# Execute request
from proxy_chain_executor import ProxyChainExecutor

executor = ProxyChainExecutor(chain)
success, response, info = executor.execute("https://api.example.com/data")

print(f"Success: {success}")
print(f"Info: {info}")
```

### From Configuration File

```python
from proxy_chain_builder import ProxyChainConfig, ProxyChainBuilder

# Load configuration
config = ProxyChainConfig.from_file("chain_config.json")

# Build chain
builder = ProxyChainBuilder.from_config(config)
chain = builder.build()
```

## Chain Builder

### Creating a Builder

```python
from proxy_chain_builder import ProxyChainBuilder

# Empty builder
builder = ProxyChainBuilder()

# With name and description
builder = ProxyChainBuilder(
    chain_name="enterprise-proxy-chain",
    description="Production proxy chain for API requests"
)
```

### Adding Hops

#### Simple HTTP Proxy

```python
builder.add_hop("proxy.example.com", 8080)
```

#### With Authentication

```python
builder.add_hop(
    "proxy.example.com", 8080,
    auth_type="basic",
    username="user",
    password="pass",
    label="Corporate Proxy"
)
```

#### SOCKS5 Proxy

```python
builder.add_hop(
    "socks.example.com", 1080,
    protocol="socks5",
    auth_type="basic",
    username="socks_user",
    password="socks_pass"
)
```

#### From URL

```python
builder.add_hop_from_url(
    "http://user:pass@proxy.example.com:8080",
    label="Proxy from URL"
)
```

### Chain Configuration Options

```python
builder
    .set_chain_name("production-chain")
    .set_description("Multi-hop production chain")
    .set_total_timeout(60)           # Total chain timeout
    .set_max_hops(10)                # Maximum hops allowed
    .set_allow_direct_fallback(True) # Allow direct connection fallback
    .enable_load_balancing(True)     # Load balance across hops
    .enable_metrics(True)            # Collect metrics

chain = builder.build()
```

## Configuration

### ProxyChainConfig Structure

```python
from proxy_chain_builder import ProxyChainConfig, ProxyHopConfig

# Create configuration programmatically
config = ProxyChainConfig(
    chain_name="my-chain",
    description="Multi-hop chain",
    hops=[
        ProxyHopConfig(
            hostname="proxy1.example.com",
            port=8080,
            auth_type="basic",
            username="user1",
            password="pass1"
        ),
        ProxyHopConfig(
            hostname="proxy2.example.com",
            port=3128,
            auth_type="basic",
            username="user2",
            password="pass2"
        )
    ],
    allow_direct_fallback=False,
    max_chain_hops=10,
    total_timeout=120
)

# Validate
is_valid, errors = config.validate()
if not is_valid:
    print("Configuration errors:", errors)
```

### JSON Configuration File

```json
{
  "chain_name": "production-chain",
  "description": "Multi-hop routing for APIs",
  "hops": [
    {
      "hostname": "proxy1.example.com",
      "port": 8080,
      "protocol": "http",
      "auth_type": "basic",
      "timeout": 30,
      "verify_ssl": true,
      "label": "First Proxy",
      "priority": 0,
      "enabled": true
    },
    {
      "hostname": "proxy2.example.com",
      "port": 3128,
      "protocol": "http",
      "auth_type": "basic",
      "timeout": 30,
      "verify_ssl": true,
      "label": "Second Proxy",
      "priority": 0,
      "enabled": true
    }
  ],
  "allow_direct_fallback": false,
  "enable_load_balancing": false,
  "max_chain_hops": 10,
  "total_timeout": 120,
  "max_retries_per_hop": 2,
  "enable_metrics": true
}
```

## Execution

### Basic Execution

```python
from proxy_chain_executor import ProxyChainExecutor

executor = ProxyChainExecutor(chain)

# GET request
success, response, info = executor.execute("https://api.example.com/data")

# POST request with body
success, response, info = executor.execute(
    url="https://api.example.com/submit",
    method="POST",
    body=b'{"key": "value"}',
    headers={"Content-Type": "application/json"}
)
```

### With Retries

```python
success, response, info = executor.execute(
    url="https://api.example.com/data",
    max_retries=3,
    timeout=30
)
```

### Execution Tracing

```python
# Execute and record trace
success, response, info = executor.execute(
    url="https://api.example.com/data",
    record_trace=True
)

# Get execution history
history = executor.get_execution_history(limit=10)

for trace in history:
    print(f"Request {trace['request_id']}: {trace['final_status']}")
    print(f"Duration: {trace['total_duration']:.2f}s")
    for hop in trace['hop_traces']:
        print(f"  Hop {hop['hop_index']}: {hop['status']}")
```

## Authentication

### Authentication Types

#### None (No Authentication)

```python
builder.add_hop("proxy.example.com", 8080, auth_type="none")
```

#### Basic Authentication

```python
builder.add_hop(
    "proxy.example.com", 8080,
    auth_type="basic",
    username="user",
    password="pass"
)
```

#### Digest Authentication

```python
builder.add_hop(
    "proxy.example.com", 8080,
    auth_type="digest",
    username="user",
    password="pass"
)
```

#### NTLM Authentication

```python
builder.add_hop(
    "proxy.example.com", 8080,
    auth_type="ntlm",
    username="domain\\user",
    password="pass",
    domain="example.com"
)
```

#### Certificate Authentication (mTLS)

```python
builder.add_hop(
    "proxy.example.com", 8443,
    protocol="https",
    auth_type="certificate",
    cert_path="/path/to/cert.pem",
    key_path="/path/to/key.pem",
    ca_bundle="/path/to/ca-bundle.pem"
)
```

## Advanced Features

### Chain Validation

```python
# Automatic validation on build
chain = builder.build()  # Validates automatically

# Manual validation
is_valid, errors = chain.validate()
if not is_valid:
    for error in errors:
        print(f"Error: {error}")
```

### Metrics Collection

```python
# Get metrics for specific hop
hop_metrics = chain.get_hop_metrics(hop_index=0)
print(f"Hop 0 success rate: {hop_metrics.get_success_rate():.1f}%")
print(f"Avg response time: {hop_metrics.get_average_response_time():.2f}s")

# Get all metrics
all_metrics = chain.get_all_metrics()
for hop_idx, metrics in all_metrics.items():
    print(f"Hop {hop_idx}: {metrics.successful_requests}/{metrics.total_requests}")
```

### Chain Health Status

```python
# Get comprehensive health information
health = chain.get_chain_health()

print(f"Chain state: {health['chain_state']}")
print(f"Enabled hops: {health['enabled_hops']}/{health['total_hops']}")

for hop_idx, hop_info in health['hops'].items():
    print(f"Hop {hop_idx}: {hop_info['state']}")
    if hop_info['metrics']:
        metrics = hop_info['metrics']
        print(f"  Requests: {metrics['total_requests']}")
```

### Executor Statistics

```python
# Get executor statistics
stats = executor.get_executor_stats()

print(f"Total requests: {stats['total_requests']}")
print(f"Success rate: {stats['success_rate']:.1f}%")
print(f"Avg duration: {stats['average_duration']:.2f}s")

# Export report
executor.export_execution_report("/tmp/chain_report.json")
```

### Configuration Export/Import

```python
# Export to JSON
json_config = chain.config.to_json()

with open("chain_backup.json", "w") as f:
    f.write(json_config)

# Import from JSON
from proxy_chain_builder import ProxyChainConfig

loaded_config = ProxyChainConfig.from_file("chain_backup.json")
new_chain = ProxyChainBuilder.from_config(loaded_config).build()
```

## Examples

### Example 1: Simple 2-Hop Chain

```python
from proxy_chain_builder import ProxyChainBuilder
from proxy_chain_executor import ProxyChainExecutor

builder = ProxyChainBuilder("simple-chain")
builder.add_hop("proxy1.example.com", 8080)
builder.add_hop("proxy2.example.com", 3128)

chain = builder.build()
executor = ProxyChainExecutor(chain)

success, response, info = executor.execute("https://api.example.com/data")
print(f"Result: {info}")
```

### Example 2: Enterprise Chain with Auth

```python
builder = ProxyChainBuilder("enterprise-chain")

# Corporate proxy with NTLM
builder.add_hop(
    "corp-proxy.internal.com", 8080,
    auth_type="basic",
    username="corp_user",
    password="corp_pass",
    label="Corporate Proxy"
)

# ISP proxy with authentication
builder.add_hop(
    "isp-proxy.example.com", 3128,
    auth_type="basic",
    username="isp_user",
    password="isp_pass",
    label="ISP Proxy"
)

builder.set_total_timeout(60)
chain = builder.build()
```

### Example 3: Mixed Protocol Chain

```python
builder = ProxyChainBuilder("mixed-protocol-chain")

# First hop: HTTP
builder.add_hop(
    "proxy1.example.com", 8080,
    protocol="http"
)

# Second hop: SOCKS5
builder.add_hop(
    "proxy2.example.com", 1080,
    protocol="socks5",
    auth_type="basic",
    username="socks_user",
    password="socks_pass"
)

# Third hop: HTTPS with certificate
builder.add_hop(
    "proxy3.example.com", 8443,
    protocol="https",
    auth_type="certificate",
    cert_path="/path/to/cert.pem",
    key_path="/path/to/key.pem"
)

chain = builder.build()
```

### Example 4: Load Balancing Chain

```python
builder = ProxyChainBuilder("load-balanced-chain")
builder.set_description("Chain with load balancing")
builder.enable_load_balancing(True)

# Add multiple hops with different priorities
for i in range(3):
    builder.add_hop(
        f"proxy{i+1}.example.com", 8080,
        label=f"Proxy {i+1}",
        priority=i
    )

chain = builder.build()
executor = ProxyChainExecutor(chain)

# Execute multiple requests
for i in range(10):
    success, response, info = executor.execute(
        f"https://api.example.com/request/{i}"
    )
```

### Example 5: Metrics and Monitoring

```python
import json

builder = ProxyChainBuilder("monitored-chain")
builder.add_hop("proxy1.example.com", 8080)
builder.add_hop("proxy2.example.com", 3128)
builder.enable_metrics(True)

chain = builder.build()
executor = ProxyChainExecutor(chain)

# Execute multiple requests
for i in range(5):
    success, response, info = executor.execute("https://api.example.com/data")

# Export metrics
report = executor.export_execution_report("/tmp/chain_report.json")

print(json.dumps(report['executor_stats'], indent=2))
```

## API Reference

### ProxyChainBuilder

**Methods:**

- `add_hop(hostname, port, auth_type, protocol, label, **kwargs)` - Add proxy hop
- `add_hop_from_url(proxy_url, auth_type, label, **kwargs)` - Add hop from URL
- `set_chain_name(name)` - Set chain name
- `set_description(description)` - Set description
- `set_allow_direct_fallback(allow)` - Allow direct fallback
- `set_max_hops(max_hops)` - Set maximum hops
- `set_total_timeout(timeout)` - Set total timeout
- `enable_load_balancing(enable)` - Enable load balancing
- `enable_metrics(enable)` - Enable metrics
- `build()` - Build chain
- `from_config(config)` - Create from config
- `from_file(file_path)` - Create from file

### ProxyChain

**Methods:**

- `get_chain_id()` - Get unique chain ID
- `validate()` - Validate chain
- `get_hop_config(hop_index)` - Get hop config
- `get_all_hops()` - Get all hops
- `get_enabled_hops()` - Get enabled hops
- `record_hop_success(hop_index, response_time)` - Record success
- `record_hop_failure(hop_index)` - Record failure
- `get_hop_metrics(hop_index)` - Get hop metrics
- `get_all_metrics()` - Get all metrics
- `get_hop_state(hop_index)` - Get hop state
- `get_chain_state()` - Get chain state
- `update_chain_state(state)` - Update state
- `get_chain_health()` - Get health info

### ProxyChainExecutor

**Methods:**

- `execute(url, method, headers, timeout, body, max_retries, record_trace)` - Execute request
- `get_execution_history(limit)` - Get history
- `get_last_execution_trace()` - Get last trace
- `clear_history()` - Clear history
- `get_executor_stats()` - Get statistics
- `export_execution_report(output_file)` - Export report

## Troubleshooting

### Chain Validation Errors

```python
is_valid, errors = chain.validate()
if not is_valid:
    for error in errors:
        print(f"Validation error: {error}")
```

### Circular Dependency Detection

```python
# Disable if needed
config = ProxyChainConfig(
    chain_name="chain",
    circular_hop_detection=False
)
```

### Debugging

```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

# Check chain health
health = chain.get_chain_health()
print(f"Chain health: {json.dumps(health, indent=2)}")

# Check hop states
for hop_idx, state in chain.get_all_hop_states().items():
    print(f"Hop {hop_idx}: {state}")
```

## Performance Considerations

1. **Sequential Execution**: Each hop is executed in sequence; total time = sum of all hop times
2. **Timeout Settings**: Set per-hop timeouts to prevent hanging
3. **Retry Logic**: Exponential backoff reduces load on failed proxies
4. **Metrics Overhead**: Minimal impact; can be disabled if not needed
5. **Connection Pooling**: Reuse connections when possible

## Security Considerations

1. **Credential Storage**: Never commit passwords to version control
2. **SSL Verification**: Enable by default; disable only if necessary
3. **Certificate Validation**: Use CA bundles for self-signed certificates
4. **Audit Logging**: All requests are logged with chain ID
5. **Sensitive Data**: Passwords masked in logs and exports
