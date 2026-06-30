#!/usr/bin/env python3
"""
Proxy Failure Detection and Automatic Fallback Handler

Provides intelligent failure detection with automatic fallback to direct connection,
retry logic, circuit breaker pattern, and connection state management.

Features:
- Real-time proxy health monitoring
- Automatic fallback to direct connection on proxy failure
- Circuit breaker pattern for failing proxies
- Configurable retry strategies
- Connection state tracking
- Fallback handler for seamless connection switching
- Logging and metrics collection

Usage:
    from proxy_fallback_handler import ProxyFallbackHandler, FallbackConfig

    config = FallbackConfig(
        primary_proxy_url="http://proxy.example.com:8080",
        enable_fallback=True,
        max_retries=3,
        circuit_break_threshold=5
    )

    handler = ProxyFallbackHandler(config)

    # Execute request with automatic fallback
    response = handler.execute_request(
        url="https://api.example.com/data",
        method="GET"
    )
"""

import logging
import time
import socket
import json
import os
from typing import Dict, Optional, Tuple, Any, Callable, List
from dataclasses import dataclass, field, asdict
from enum import Enum
from datetime import datetime, timedelta
from abc import ABC, abstractmethod
import urllib.request
import urllib.error
import ssl
import threading
from queue import Queue
from urllib.parse import urlparse


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ConnectionState(Enum):
    """Connection state enumeration"""
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    DEGRADED = "degraded"
    RECOVERING = "recovering"


class ProxyState(Enum):
    """Proxy state enumeration"""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    SUSPENDED = "suspended"
    RECOVERING = "recovering"


class FallbackStrategy(Enum):
    """Fallback strategy options"""
    IMMEDIATE = "immediate"
    RETRY_THEN_FALLBACK = "retry_then_fallback"
    CIRCUIT_BREAKER = "circuit_breaker"
    GRADUATED = "graduated"


@dataclass
class FallbackConfig:
    """Configuration for proxy fallback handler"""

    primary_proxy_url: Optional[str] = None
    fallback_proxies: List[str] = field(default_factory=list)
    enable_direct_fallback: bool = True
    enable_fallback: bool = True

    # Retry configuration
    max_retries: int = 3
    initial_retry_delay: float = 1.0
    max_retry_delay: float = 30.0
    retry_backoff_factor: float = 2.0

    # Timeout configuration
    connection_timeout: float = 10.0
    read_timeout: float = 30.0
    health_check_timeout: float = 5.0

    # Circuit breaker configuration
    circuit_break_threshold: int = 5
    circuit_break_recovery_time: float = 60.0

    # Health check configuration
    health_check_interval: float = 30.0
    health_check_enabled: bool = True
    health_check_url: str = "http://www.google.com/generate_204"

    # Fallback strategy
    fallback_strategy: FallbackStrategy = FallbackStrategy.CIRCUIT_BREAKER

    # Metrics configuration
    enable_metrics: bool = True
    metrics_path: str = "/tmp/proxy_metrics"

    # SSL/TLS configuration
    verify_ssl: bool = True
    ca_bundle: Optional[str] = None

    # User agent
    user_agent: str = "ProxyFallbackHandler/1.0"


@dataclass
class ConnectionMetrics:
    """Metrics for connection attempt"""
    timestamp: str
    proxy_used: Optional[str]
    is_direct: bool
    success: bool
    response_time: float
    status_code: Optional[int] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    fallback_triggered: bool = False


class ProxyHealthMonitor:
    """Monitor proxy health and detect failures"""

    def __init__(self, config: FallbackConfig):
        self.config = config
        self.proxy_states: Dict[str, ProxyState] = {}
        self.failure_counts: Dict[str, int] = {}
        self.last_failure_time: Dict[str, float] = {}
        self.last_health_check: Dict[str, float] = {}
        self.lock = threading.Lock()

        # Initialize proxy states
        if config.primary_proxy_url:
            self.proxy_states[config.primary_proxy_url] = ProxyState.HEALTHY
            self.failure_counts[config.primary_proxy_url] = 0

        for proxy_url in config.fallback_proxies:
            self.proxy_states[proxy_url] = ProxyState.HEALTHY
            self.failure_counts[proxy_url] = 0

    def record_failure(self, proxy_url: str) -> None:
        """Record a proxy failure"""
        with self.lock:
            if proxy_url not in self.failure_counts:
                self.failure_counts[proxy_url] = 0
                self.proxy_states[proxy_url] = ProxyState.HEALTHY

            self.failure_counts[proxy_url] += 1
            self.last_failure_time[proxy_url] = time.time()

            # Check if circuit breaker should trip
            if (self.failure_counts[proxy_url] >=
                self.config.circuit_break_threshold):
                self.proxy_states[proxy_url] = ProxyState.SUSPENDED
                logger.warning(
                    f"Circuit breaker tripped for proxy {proxy_url} "
                    f"({self.failure_counts[proxy_url]} failures)"
                )

    def record_success(self, proxy_url: str) -> None:
        """Record a successful proxy connection"""
        with self.lock:
            if proxy_url not in self.failure_counts:
                self.failure_counts[proxy_url] = 0

            # Reset failure count on success
            self.failure_counts[proxy_url] = max(0,
                self.failure_counts[proxy_url] - 1)

            if self.proxy_states.get(proxy_url) != ProxyState.SUSPENDED:
                self.proxy_states[proxy_url] = ProxyState.HEALTHY
                logger.info(f"Proxy {proxy_url} marked as healthy")

    def is_proxy_available(self, proxy_url: str) -> bool:
        """Check if proxy is available"""
        with self.lock:
            state = self.proxy_states.get(proxy_url, ProxyState.HEALTHY)

            if state == ProxyState.SUSPENDED:
                # Check if recovery time has passed
                last_failure = self.last_failure_time.get(proxy_url, 0)
                recovery_time = (time.time() - last_failure)

                if recovery_time > self.config.circuit_break_recovery_time:
                    self.proxy_states[proxy_url] = ProxyState.RECOVERING
                    self.failure_counts[proxy_url] = 0
                    logger.info(
                        f"Attempting to recover proxy {proxy_url}"
                    )
                    return True
                return False

            return state in (ProxyState.HEALTHY, ProxyState.RECOVERING)

    def get_proxy_state(self, proxy_url: str) -> ProxyState:
        """Get current proxy state"""
        with self.lock:
            return self.proxy_states.get(proxy_url, ProxyState.HEALTHY)

    def check_proxy_health(self, proxy_url: str) -> Tuple[bool, str]:
        """Check proxy health via test request"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.config.health_check_timeout)

            parsed = urlparse(proxy_url)
            host = parsed.hostname or "127.0.0.1"
            port = parsed.port or 80

            sock.connect((host, port))
            sock.close()

            with self.lock:
                self.last_health_check[proxy_url] = time.time()

            return True, "Proxy is reachable"

        except socket.timeout:
            return False, "Proxy connection timed out"
        except socket.error as e:
            return False, f"Proxy connection failed: {str(e)}"
        except Exception as e:
            return False, f"Health check error: {str(e)}"

    def get_stats(self) -> Dict[str, Any]:
        """Get health monitor statistics"""
        with self.lock:
            return {
                "proxy_states": {
                    proxy: state.value
                    for proxy, state in self.proxy_states.items()
                },
                "failure_counts": self.failure_counts.copy(),
                "last_failure_times": self.last_failure_time.copy()
            }


class FallbackHandler:
    """Handle fallback connection logic"""

    def __init__(self, config: FallbackConfig):
        self.config = config
        self.health_monitor = ProxyHealthMonitor(config)
        self.metrics: List[ConnectionMetrics] = []
        self.connection_state = ConnectionState.DISCONNECTED
        self.lock = threading.Lock()
        self.retry_queue: Queue = Queue()

        # Ensure metrics directory exists
        if config.enable_metrics:
            os.makedirs(config.metrics_path, exist_ok=True)

    def _create_ssl_context(self) -> ssl.SSLContext:
        """Create SSL context for secure connections"""
        context = ssl.create_default_context()

        if not self.config.verify_ssl:
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE

        if self.config.ca_bundle and os.path.exists(self.config.ca_bundle):
            context.load_verify_locations(self.config.ca_bundle)

        return context

    def _make_request_with_proxy(
        self,
        url: str,
        proxy_url: str,
        method: str = "GET",
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None
    ) -> Tuple[bool, Optional[Any], Optional[str], float]:
        """Make HTTP request via proxy"""
        start_time = time.time()

        try:
            if timeout is None:
                timeout = self.config.connection_timeout

            headers = headers or {}
            headers['User-Agent'] = self.config.user_agent

            # Parse proxy URL
            parsed_proxy = urlparse(proxy_url)
            proxy_host = f"{parsed_proxy.hostname}:{parsed_proxy.port or 80}"

            # Create proxy handler
            proxy_handler = urllib.request.ProxyHandler({
                'http': proxy_url,
                'https': proxy_url
            })

            # Create request
            req = urllib.request.Request(
                url,
                headers=headers,
                method=method
            )

            # Create opener with proxy
            opener = urllib.request.build_opener(proxy_handler)

            # Execute request
            response = opener.open(req, timeout=timeout)
            response_time = time.time() - start_time

            self.health_monitor.record_success(proxy_url)
            logger.info(
                f"Request successful via proxy {proxy_host} "
                f"({response_time:.2f}s)"
            )

            return True, response, None, response_time

        except urllib.error.HTTPError as e:
            response_time = time.time() - start_time
            error_msg = f"HTTP Error {e.code}: {e.reason}"
            logger.warning(f"HTTP error via proxy: {error_msg}")
            return False, None, error_msg, response_time

        except (urllib.error.URLError, socket.timeout) as e:
            response_time = time.time() - start_time
            error_msg = f"Connection error: {str(e)}"
            self.health_monitor.record_failure(proxy_url)
            logger.warning(f"Proxy connection error: {error_msg}")
            return False, None, error_msg, response_time

        except Exception as e:
            response_time = time.time() - start_time
            error_msg = f"Request error: {str(e)}"
            self.health_monitor.record_failure(proxy_url)
            logger.error(f"Unexpected error with proxy: {error_msg}")
            return False, None, error_msg, response_time

    def _make_direct_request(
        self,
        url: str,
        method: str = "GET",
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None
    ) -> Tuple[bool, Optional[Any], Optional[str], float]:
        """Make HTTP request directly (no proxy)"""
        start_time = time.time()

        try:
            if timeout is None:
                timeout = self.config.connection_timeout

            headers = headers or {}
            headers['User-Agent'] = self.config.user_agent

            # Create request
            req = urllib.request.Request(url, headers=headers, method=method)

            # Create opener without proxy
            opener = urllib.request.build_opener()

            # Execute request
            response = opener.open(req, timeout=timeout)
            response_time = time.time() - start_time

            logger.info(f"Request successful via direct connection ({response_time:.2f}s)")

            return True, response, None, response_time

        except urllib.error.HTTPError as e:
            response_time = time.time() - start_time
            error_msg = f"HTTP Error {e.code}: {e.reason}"
            logger.warning(f"HTTP error on direct connection: {error_msg}")
            return False, None, error_msg, response_time

        except (urllib.error.URLError, socket.timeout) as e:
            response_time = time.time() - start_time
            error_msg = f"Connection error: {str(e)}"
            logger.error(f"Direct connection failed: {error_msg}")
            return False, None, error_msg, response_time

        except Exception as e:
            response_time = time.time() - start_time
            error_msg = f"Request error: {str(e)}"
            logger.error(f"Unexpected error: {error_msg}")
            return False, None, error_msg, response_time

    def _get_retry_delay(self, retry_count: int) -> float:
        """Calculate retry delay with exponential backoff"""
        delay = self.config.initial_retry_delay * (
            self.config.retry_backoff_factor ** retry_count
        )
        return min(delay, self.config.max_retry_delay)

    def execute_request(
        self,
        url: str,
        method: str = "GET",
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None
    ) -> Tuple[bool, Optional[Any], str]:
        """
        Execute request with automatic fallback

        Returns:
            Tuple of (success, response, info_message)
        """

        if not self.config.enable_fallback:
            # Use primary proxy only
            if self.config.primary_proxy_url:
                success, response, error, response_time = self._make_request_with_proxy(
                    url, self.config.primary_proxy_url, method, headers, timeout
                )

                info = (
                    f"Connected via proxy "
                    f"({response_time:.2f}s)" if success
                    else f"Proxy failed: {error}"
                )

                return success, response, info
            else:
                success, response, error, response_time = self._make_direct_request(
                    url, method, headers, timeout
                )

                return success, response, error or "Direct connection"

        # Execute with fallback logic
        return self._execute_with_fallback(url, method, headers, timeout)

    def _execute_with_fallback(
        self,
        url: str,
        method: str,
        headers: Optional[Dict[str, str]],
        timeout: Optional[float]
    ) -> Tuple[bool, Optional[Any], str]:
        """Execute request with automatic fallback"""

        proxies_to_try = []

        # Add primary proxy if available
        if (self.config.primary_proxy_url and
            self.health_monitor.is_proxy_available(self.config.primary_proxy_url)):
            proxies_to_try.append(self.config.primary_proxy_url)

        # Add fallback proxies if available
        for proxy_url in self.config.fallback_proxies:
            if self.health_monitor.is_proxy_available(proxy_url):
                proxies_to_try.append(proxy_url)

        # Try each proxy with retries
        for proxy_url in proxies_to_try:
            for retry_attempt in range(self.config.max_retries):
                if retry_attempt > 0:
                    delay = self._get_retry_delay(retry_attempt - 1)
                    logger.info(
                        f"Retrying via {proxy_url} after {delay:.1f}s "
                        f"(attempt {retry_attempt + 1}/{self.config.max_retries})"
                    )
                    time.sleep(delay)

                success, response, error, response_time = (
                    self._make_request_with_proxy(
                        url, proxy_url, method, headers, timeout
                    )
                )

                if success:
                    # Record success metric
                    self._record_metric(
                        proxy_used=proxy_url,
                        is_direct=False,
                        success=True,
                        response_time=response_time,
                        status_code=response.getcode() if response else None,
                        retry_count=retry_attempt
                    )

                    with self.lock:
                        self.connection_state = ConnectionState.CONNECTED

                    return True, response, f"Connected via {proxy_url}"

        # All proxies failed, try direct connection
        if self.config.enable_direct_fallback:
            logger.info("All proxies failed, attempting direct connection")

            for retry_attempt in range(self.config.max_retries):
                if retry_attempt > 0:
                    delay = self._get_retry_delay(retry_attempt - 1)
                    logger.info(
                        f"Retrying direct connection after {delay:.1f}s "
                        f"(attempt {retry_attempt + 1}/{self.config.max_retries})"
                    )
                    time.sleep(delay)

                success, response, error, response_time = (
                    self._make_direct_request(url, method, headers, timeout)
                )

                if success:
                    # Record success metric
                    self._record_metric(
                        proxy_used=None,
                        is_direct=True,
                        success=True,
                        response_time=response_time,
                        status_code=response.getcode() if response else None,
                        retry_count=retry_attempt,
                        fallback_triggered=True
                    )

                    with self.lock:
                        self.connection_state = ConnectionState.CONNECTED

                    return True, response, "Connected via direct connection (fallback)"

            # Direct connection also failed
            self._record_metric(
                proxy_used=None,
                is_direct=True,
                success=False,
                response_time=0.0,
                error_message="All connection methods failed",
                fallback_triggered=True
            )

            with self.lock:
                self.connection_state = ConnectionState.DISCONNECTED

            return False, None, "All connection methods failed"

        # Fallback disabled
        with self.lock:
            self.connection_state = ConnectionState.DISCONNECTED

        return False, None, "All proxies failed and fallback is disabled"

    def _record_metric(
        self,
        proxy_used: Optional[str],
        is_direct: bool,
        success: bool,
        response_time: float,
        status_code: Optional[int] = None,
        error_message: Optional[str] = None,
        retry_count: int = 0,
        fallback_triggered: bool = False
    ) -> None:
        """Record connection metric"""
        if not self.config.enable_metrics:
            return

        metric = ConnectionMetrics(
            timestamp=datetime.now().isoformat(),
            proxy_used=proxy_used,
            is_direct=is_direct,
            success=success,
            response_time=response_time,
            status_code=status_code,
            error_message=error_message,
            retry_count=retry_count,
            fallback_triggered=fallback_triggered
        )

        with self.lock:
            self.metrics.append(metric)

        logger.debug(f"Recorded metric: {metric}")

    def get_metrics(self) -> List[Dict[str, Any]]:
        """Get all recorded metrics"""
        with self.lock:
            return [asdict(m) for m in self.metrics]

    def export_metrics(self, output_file: Optional[str] = None) -> Dict[str, Any]:
        """Export metrics to file and return summary"""
        with self.lock:
            metrics_data = [asdict(m) for m in self.metrics]

        # Calculate summary
        total_requests = len(metrics_data)
        successful_requests = sum(
            1 for m in metrics_data if m['success']
        )
        fallback_triggered_count = sum(
            1 for m in metrics_data if m['fallback_triggered']
        )

        avg_response_time = (
            sum(m['response_time'] for m in metrics_data) / total_requests
            if total_requests > 0 else 0
        )

        summary = {
            "total_requests": total_requests,
            "successful_requests": successful_requests,
            "failed_requests": total_requests - successful_requests,
            "success_rate": (
                (successful_requests / total_requests * 100)
                if total_requests > 0 else 0
            ),
            "fallback_triggered_count": fallback_triggered_count,
            "average_response_time": avg_response_time,
            "generated_at": datetime.now().isoformat()
        }

        export_data = {
            "summary": summary,
            "metrics": metrics_data
        }

        if output_file:
            with open(output_file, 'w') as f:
                json.dump(export_data, f, indent=2)
            logger.info(f"Metrics exported to {output_file}")

        return export_data

    def get_connection_state(self) -> ConnectionState:
        """Get current connection state"""
        with self.lock:
            return self.connection_state

    def get_health_status(self) -> Dict[str, Any]:
        """Get overall health status"""
        return {
            "connection_state": self.connection_state.value,
            "monitor_stats": self.health_monitor.get_stats(),
            "metrics_summary": self._get_metrics_summary()
        }

    def _get_metrics_summary(self) -> Dict[str, Any]:
        """Get metrics summary"""
        with self.lock:
            if not self.metrics:
                return {
                    "total_requests": 0,
                    "successful_requests": 0,
                    "success_rate": 0
                }

            total = len(self.metrics)
            successful = sum(1 for m in self.metrics if m.success)

            return {
                "total_requests": total,
                "successful_requests": successful,
                "success_rate": (successful / total * 100) if total > 0 else 0
            }


def create_fallback_handler(config: FallbackConfig) -> FallbackHandler:
    """Factory function to create fallback handler"""
    return FallbackHandler(config)


def create_default_handler(
    primary_proxy_url: Optional[str] = None,
    fallback_proxies: Optional[List[str]] = None
) -> FallbackHandler:
    """Create handler with default configuration"""
    config = FallbackConfig(
        primary_proxy_url=primary_proxy_url,
        fallback_proxies=fallback_proxies or []
    )
    return FallbackHandler(config)


# Example usage and testing
if __name__ == "__main__":
    print("=" * 80)
    print("PROXY FALLBACK HANDLER - DEMONSTRATION")
    print("=" * 80)

    # Create configuration
    config = FallbackConfig(
        primary_proxy_url="http://proxy.example.com:8080",
        fallback_proxies=[
            "http://fallback1.example.com:8080",
            "http://fallback2.example.com:8080"
        ],
        enable_direct_fallback=True,
        max_retries=2,
        circuit_break_threshold=3
    )

    # Create handler
    handler = create_fallback_handler(config)

    print("\n1. Handler Configuration")
    print("-" * 80)
    print(f"  Primary Proxy: {config.primary_proxy_url}")
    print(f"  Fallback Proxies: {config.fallback_proxies}")
    print(f"  Direct Fallback Enabled: {config.enable_direct_fallback}")
    print(f"  Max Retries: {config.max_retries}")

    print("\n2. Health Status")
    print("-" * 80)
    status = handler.get_health_status()
    print(f"  Connection State: {status['connection_state']}")
    print(f"  Monitor Stats: {json.dumps(status['monitor_stats'], indent=2)}")

    print("\n3. Example Request Execution")
    print("-" * 80)
    print("  (Note: This is a demonstration of the handler interface)")
    print("  To test with real requests, provide valid proxy URLs")

    # Show how to use the handler
    print("\n4. Usage Example")
    print("-" * 80)
    print("""
    # Simple usage
    success, response, info = handler.execute_request(
        url="https://api.example.com/data",
        method="GET"
    )

    # Get metrics
    metrics = handler.get_metrics()

    # Export metrics to file
    handler.export_metrics("/tmp/proxy_metrics.json")

    # Check health status
    status = handler.get_health_status()
    """)

    print("\n" + "=" * 80)
    print("PROXY FALLBACK HANDLER - DEMONSTRATION COMPLETE")
    print("=" * 80)
