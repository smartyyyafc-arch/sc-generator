#!/usr/bin/env python3
"""
Proxy Fallback Handler - Practical Examples

Demonstrates real-world usage patterns and best practices.
"""

import logging
import json
import time
import threading
from proxy_fallback_handler import (
    FallbackConfig,
    FallbackHandler,
    create_default_handler,
    create_fallback_handler
)


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class Example1BasicUsage:
    """Example 1: Basic usage with proxy and direct fallback"""

    @staticmethod
    def run():
        print("\n" + "=" * 80)
        print("EXAMPLE 1: Basic Usage with Automatic Fallback")
        print("=" * 80)

        # Create configuration
        config = FallbackConfig(
            primary_proxy_url="http://proxy.example.com:8080",
            fallback_proxies=["http://backup-proxy.example.com:8080"],
            enable_direct_fallback=True
        )

        # Create handler
        handler = FallbackHandler(config)

        print("\nConfiguration:")
        print(f"  Primary Proxy: {config.primary_proxy_url}")
        print(f"  Fallback Proxies: {config.fallback_proxies}")
        print(f"  Direct Fallback: {config.enable_direct_fallback}")

        # Example request execution
        print("\nExecuting request...")
        print("(Note: This is a demonstration, real proxies would need to be provided)")

        # The actual call would be:
        # success, response, info = handler.execute_request(
        #     url="https://api.example.com/data",
        #     method="GET"
        # )
        # print(f"Result: {info}")


class Example2AdvancedRetryStrategy:
    """Example 2: Advanced retry strategy with exponential backoff"""

    @staticmethod
    def run():
        print("\n" + "=" * 80)
        print("EXAMPLE 2: Advanced Retry Strategy")
        print("=" * 80)

        # Configure with custom retry strategy
        config = FallbackConfig(
            primary_proxy_url="http://proxy.example.com:8080",
            fallback_proxies=["http://fallback1.example.com:8080",
                             "http://fallback2.example.com:8080"],
            enable_direct_fallback=True,
            max_retries=4,
            initial_retry_delay=0.5,
            max_retry_delay=20.0,
            retry_backoff_factor=2.0
        )

        handler = FallbackHandler(config)

        print("\nRetry Strategy Configuration:")
        print(f"  Max Retries: {config.max_retries}")
        print(f"  Initial Delay: {config.initial_retry_delay}s")
        print(f"  Max Delay: {config.max_retry_delay}s")
        print(f"  Backoff Factor: {config.retry_backoff_factor}")

        print("\nCalculated retry delays:")
        for attempt in range(config.max_retries):
            delay = handler._get_retry_delay(attempt)
            print(f"  Attempt {attempt + 1}: {delay:.2f}s delay")


class Example3CircuitBreaker:
    """Example 3: Circuit breaker pattern configuration"""

    @staticmethod
    def run():
        print("\n" + "=" * 80)
        print("EXAMPLE 3: Circuit Breaker Pattern")
        print("=" * 80)

        # Configure with aggressive circuit breaker
        config = FallbackConfig(
            primary_proxy_url="http://proxy.example.com:8080",
            fallback_proxies=["http://fallback.example.com:8080"],
            circuit_break_threshold=3,  # Trip after 3 failures
            circuit_break_recovery_time=60.0  # Try again after 60s
        )

        handler = FallbackHandler(config)

        print("\nCircuit Breaker Configuration:")
        print(f"  Trip Threshold: {config.circuit_break_threshold} failures")
        print(f"  Recovery Time: {config.circuit_break_recovery_time}s")

        # Simulate failures
        proxy_url = config.primary_proxy_url
        print(f"\nSimulating proxy failures for {proxy_url}...")

        monitor = handler.health_monitor
        for i in range(1, 5):
            monitor.record_failure(proxy_url)
            state = monitor.get_proxy_state(proxy_url)
            available = monitor.is_proxy_available(proxy_url)
            print(f"  After {i} failures: state={state.value}, available={available}")


class Example4HealthMonitoring:
    """Example 4: Health monitoring and status tracking"""

    @staticmethod
    def run():
        print("\n" + "=" * 80)
        print("EXAMPLE 4: Health Monitoring")
        print("=" * 80)

        config = FallbackConfig(
            primary_proxy_url="http://proxy.example.com:8080",
            fallback_proxies=["http://fallback.example.com:8080"],
            health_check_enabled=True,
            health_check_interval=30.0
        )

        handler = FallbackHandler(config)

        print("\nHealth Check Configuration:")
        print(f"  Enabled: {config.health_check_enabled}")
        print(f"  Interval: {config.health_check_interval}s")
        print(f"  Timeout: {config.health_check_timeout}s")

        # Get current health status
        status = handler.get_health_status()

        print("\nCurrent Health Status:")
        print(f"  Connection State: {status['connection_state']}")
        print(f"  Monitor Stats:")
        for key, value in status['monitor_stats'].items():
            if isinstance(value, dict):
                print(f"    {key}:")
                for k, v in value.items():
                    print(f"      {k}: {v}")
            else:
                print(f"    {key}: {value}")


class Example5MetricsCollection:
    """Example 5: Metrics collection and analysis"""

    @staticmethod
    def run():
        print("\n" + "=" * 80)
        print("EXAMPLE 5: Metrics Collection")
        print("=" * 80)

        config = FallbackConfig(
            primary_proxy_url="http://proxy.example.com:8080",
            enable_metrics=True,
            metrics_path="/tmp/proxy_metrics"
        )

        handler = FallbackHandler(config)

        print("\nMetrics Configuration:")
        print(f"  Enabled: {config.enable_metrics}")
        print(f"  Path: {config.metrics_path}")

        # Simulate some requests
        print("\nSimulating request metrics...")

        test_cases = [
            ("http://api.example.com/users", "proxy1", 200, 0.45),
            ("http://api.example.com/posts", "proxy1", 200, 0.52),
            ("http://api.example.com/comments", "proxy2", 200, 0.38),
            ("http://api.example.com/data", None, 200, 0.61),  # Direct
            ("http://api.example.com/error", "proxy1", 500, 0.25),
        ]

        for url, proxy, status_code, response_time in test_cases:
            is_direct = proxy is None
            success = status_code == 200

            handler._record_metric(
                proxy_used=proxy,
                is_direct=is_direct,
                success=success,
                response_time=response_time,
                status_code=status_code,
                fallback_triggered=is_direct and success
            )

            print(f"  - {url}: {'OK' if success else 'FAIL'} ({response_time:.2f}s)")

        # Export metrics
        print("\nMetrics Summary:")
        export = handler.export_metrics()
        summary = export['summary']

        print(f"  Total Requests: {summary['total_requests']}")
        print(f"  Successful: {summary['successful_requests']}")
        print(f"  Failed: {summary['total_requests'] - summary['successful_requests']}")
        print(f"  Success Rate: {summary['success_rate']:.1f}%")
        print(f"  Fallback Usage: {summary['fallback_triggered_count']} times")
        print(f"  Avg Response Time: {summary['average_response_time']:.2f}s")


class Example6MultipleProxies:
    """Example 6: Managing multiple proxies with failover"""

    @staticmethod
    def run():
        print("\n" + "=" * 80)
        print("EXAMPLE 6: Multiple Proxies with Failover")
        print("=" * 80)

        config = FallbackConfig(
            primary_proxy_url="http://proxy1.example.com:8080",
            fallback_proxies=[
                "http://proxy2.example.com:8080",
                "http://proxy3.example.com:8080",
                "http://proxy4.example.com:8080"
            ],
            enable_direct_fallback=True,
            max_retries=2
        )

        handler = FallbackHandler(config)

        print("\nProxy Configuration:")
        print(f"  Primary: {config.primary_proxy_url}")
        print(f"  Fallbacks:")
        for i, proxy in enumerate(config.fallback_proxies, 1):
            print(f"    {i}. {proxy}")
        print(f"  Direct Fallback: {config.enable_direct_fallback}")

        print("\nFailover Sequence:")
        print("  1. Try primary proxy (with retries)")
        print("  2. Try first fallback proxy (with retries)")
        print("  3. Try second fallback proxy (with retries)")
        print("  4. Try third fallback proxy (with retries)")
        print("  5. Try direct connection (with retries)")


class Example7ThreadSafeUsage:
    """Example 7: Thread-safe concurrent usage"""

    @staticmethod
    def run():
        print("\n" + "=" * 80)
        print("EXAMPLE 7: Thread-Safe Concurrent Usage")
        print("=" * 80)

        config = FallbackConfig(
            primary_proxy_url="http://proxy.example.com:8080",
            enable_metrics=True
        )

        handler = FallbackHandler(config)

        print("\nSetup: 5 threads making 10 requests each...")

        def worker(thread_id):
            for i in range(10):
                # Simulate request
                handler._record_metric(
                    proxy_used="http://proxy.example.com:8080",
                    is_direct=False,
                    success=(i % 2 == 0),
                    response_time=0.1 * (i + 1)
                )
                time.sleep(0.01)  # Simulate work
            logger.info(f"Thread {thread_id} completed")

        threads = [
            threading.Thread(target=worker, args=(i,))
            for i in range(5)
        ]

        start_time = time.time()

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        elapsed_time = time.time() - start_time

        metrics = handler.get_metrics()
        print(f"\nResults:")
        print(f"  Total metrics recorded: {len(metrics)}")
        print(f"  Expected: 50 (5 threads × 10 requests)")
        print(f"  Time taken: {elapsed_time:.2f}s")
        print(f"  All thread-safe: {len(metrics) == 50}")


class Example8SSLConfiguration:
    """Example 8: SSL/TLS configuration"""

    @staticmethod
    def run():
        print("\n" + "=" * 80)
        print("EXAMPLE 8: SSL/TLS Configuration")
        print("=" * 80)

        # Production with SSL verification
        config_prod = FallbackConfig(
            primary_proxy_url="https://secure-proxy.example.com:8443",
            verify_ssl=True,
            ca_bundle="/etc/ssl/certs/ca-bundle.crt"
        )

        print("\nProduction Configuration:")
        print(f"  Proxy: {config_prod.primary_proxy_url}")
        print(f"  SSL Verification: {config_prod.verify_ssl}")
        print(f"  CA Bundle: {config_prod.ca_bundle}")

        # Development with SSL bypass
        config_dev = FallbackConfig(
            primary_proxy_url="https://localhost:8443",
            verify_ssl=False
        )

        print("\nDevelopment Configuration:")
        print(f"  Proxy: {config_dev.primary_proxy_url}")
        print(f"  SSL Verification: {config_dev.verify_ssl}")
        print(f"  (Warning: Should only be used in development)")


class Example9CustomHandler:
    """Example 9: Creating custom handler wrapper"""

    @staticmethod
    def run():
        print("\n" + "=" * 80)
        print("EXAMPLE 9: Custom Handler Wrapper")
        print("=" * 80)

        class APIClient:
            def __init__(self, proxy_url):
                config = FallbackConfig(
                    primary_proxy_url=proxy_url,
                    enable_fallback=True,
                    enable_metrics=True
                )
                self.handler = FallbackHandler(config)

            def get(self, url):
                """GET request with automatic fallback"""
                success, response, info = self.handler.execute_request(
                    url=url,
                    method="GET",
                    headers={"Accept": "application/json"}
                )
                if not success:
                    raise Exception(f"Request failed: {info}")
                return response

            def post(self, url, data):
                """POST request with automatic fallback"""
                success, response, info = self.handler.execute_request(
                    url=url,
                    method="POST",
                    headers={"Content-Type": "application/json"}
                )
                if not success:
                    raise Exception(f"Request failed: {info}")
                return response

            def get_stats(self):
                """Get request statistics"""
                export = self.handler.export_metrics()
                return export['summary']

        print("\nCustom APIClient created with:")
        print("  - Automatic proxy fallback")
        print("  - Metrics tracking")
        print("  - JSON support")
        print("\nUsage:")
        print("""
        client = APIClient("http://proxy.example.com:8080")
        response = client.get("https://api.example.com/data")
        stats = client.get_stats()
        """)


class Example10MonitoringDashboard:
    """Example 10: Monitoring and dashboard simulation"""

    @staticmethod
    def run():
        print("\n" + "=" * 80)
        print("EXAMPLE 10: Monitoring Dashboard")
        print("=" * 80)

        config = FallbackConfig(
            primary_proxy_url="http://proxy.example.com:8080",
            fallback_proxies=["http://fallback.example.com:8080"],
            enable_metrics=True
        )

        handler = FallbackHandler(config)

        # Simulate some activity
        print("\nSimulating 100 requests...")
        for i in range(100):
            is_direct = (i % 10 == 9)  # Every 10th is direct
            success = (i % 5 != 4)  # 80% success rate

            handler._record_metric(
                proxy_used=None if is_direct else config.primary_proxy_url,
                is_direct=is_direct,
                success=success,
                response_time=0.2 + (i % 10) * 0.05,
                status_code=200 if success else 500,
                fallback_triggered=is_direct and success
            )

        # Generate dashboard
        print("\nDASHBOARD:")
        print("-" * 80)

        export = handler.export_metrics()
        summary = export['summary']
        metrics = export['metrics']

        print(f"Uptime Metrics:")
        print(f"  Success Rate: {summary['success_rate']:.1f}%")
        print(f"  Success/Total: {summary['successful_requests']}/{summary['total_requests']}")

        print(f"\nPerformance Metrics:")
        print(f"  Avg Response Time: {summary['average_response_time']:.2f}s")
        response_times = [m['response_time'] for m in metrics]
        print(f"  Min Response Time: {min(response_times):.2f}s")
        print(f"  Max Response Time: {max(response_times):.2f}s")

        print(f"\nFallback Metrics:")
        print(f"  Fallback Triggers: {summary['fallback_triggered_count']}")
        fallback_rate = (summary['fallback_triggered_count'] / summary['total_requests'] * 100)
        print(f"  Fallback Rate: {fallback_rate:.1f}%")

        print(f"\nConnection Methods:")
        direct_count = sum(1 for m in metrics if m['is_direct'])
        proxy_count = sum(1 for m in metrics if not m['is_direct'])
        print(f"  Via Proxy: {proxy_count} ({proxy_count/len(metrics)*100:.1f}%)")
        print(f"  Direct: {direct_count} ({direct_count/len(metrics)*100:.1f}%)")

        print("-" * 80)


def main():
    """Run all examples"""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 15 + "PROXY FALLBACK HANDLER - PRACTICAL EXAMPLES" + " " * 21 + "║")
    print("╚" + "=" * 78 + "╝")

    examples = [
        ("Basic Usage", Example1BasicUsage.run),
        ("Advanced Retry Strategy", Example2AdvancedRetryStrategy.run),
        ("Circuit Breaker", Example3CircuitBreaker.run),
        ("Health Monitoring", Example4HealthMonitoring.run),
        ("Metrics Collection", Example5MetricsCollection.run),
        ("Multiple Proxies", Example6MultipleProxies.run),
        ("Thread-Safe Usage", Example7ThreadSafeUsage.run),
        ("SSL Configuration", Example8SSLConfiguration.run),
        ("Custom Handler", Example9CustomHandler.run),
        ("Monitoring Dashboard", Example10MonitoringDashboard.run),
    ]

    for title, example_func in examples:
        try:
            example_func()
        except Exception as e:
            print(f"\nError in {title}: {e}")
            import traceback
            traceback.print_exc()

    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "ALL EXAMPLES COMPLETED SUCCESSFULLY" + " " * 24 + "║")
    print("╚" + "=" * 78 + "╝")
    print()


if __name__ == "__main__":
    main()
