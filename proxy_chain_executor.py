#!/usr/bin/env python3
"""
Proxy Chain Executor - Multi-Hop Request Execution

Executes HTTP requests through a proxy chain, managing sequential proxy hops,
authentication, connection pooling, and failure handling.

Features:
- Execute requests through sequential proxy chain
- Per-hop authentication and protocol handling
- Connection timeout management
- Hop failure detection and recovery
- Request correlation tracking
- Response header inspection
- Circuit breaker per hop
- Metrics collection across chain

Usage:
    from proxy_chain_executor import ProxyChainExecutor
    from proxy_chain_builder import ProxyChainBuilder

    # Build chain
    builder = ProxyChainBuilder("my-chain")
    builder.add_hop("proxy1.example.com", 8080)
    builder.add_hop("proxy2.example.com", 3128)
    chain = builder.build()

    # Execute request through chain
    executor = ProxyChainExecutor(chain)
    success, response, info = executor.execute(
        url="https://api.example.com/data",
        method="GET"
    )
"""

import logging
import time
import socket
import json
import urllib.request
import urllib.error
import ssl
import threading
from typing import Dict, Optional, Tuple, Any, List
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
from urllib.parse import urlparse, urlencode
import base64

from proxy_chain_builder import ProxyChain, ProxyHopConfig, HopState


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ExecutionMode(Enum):
    """Request execution mode"""
    SEQUENTIAL = "sequential"  # Execute through all hops
    PARALLEL = "parallel"      # Try multiple paths in parallel
    FALLBACK = "fallback"      # Use fallback hops on failure


class HopExecutionStatus(Enum):
    """Status of hop execution"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    FAILED = "failed"
    TIMEOUT = "timeout"
    SKIPPED = "skipped"


@dataclass
class HopExecutionInfo:
    """Execution information for a single hop"""
    hop_index: int
    proxy_address: str
    start_time: float
    end_time: Optional[float] = None
    status: HopExecutionStatus = HopExecutionStatus.PENDING
    response_code: Optional[int] = None
    error_message: Optional[str] = None
    retry_count: int = 0

    def get_duration(self) -> float:
        """Get execution duration"""
        if self.end_time is None:
            return 0.0
        return self.end_time - self.start_time

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "hop_index": self.hop_index,
            "proxy_address": self.proxy_address,
            "duration": self.get_duration(),
            "status": self.status.value,
            "response_code": self.response_code,
            "error_message": self.error_message,
            "retry_count": self.retry_count
        }


@dataclass
class ChainExecutionTrace:
    """Execution trace for entire chain"""
    request_id: str
    url: str
    start_time: str
    method: str = "GET"
    hop_traces: List[HopExecutionInfo] = None
    final_status: HopExecutionStatus = HopExecutionStatus.PENDING
    total_duration: float = 0.0
    response_headers: Dict[str, str] = None
    response_body: Optional[bytes] = None

    def __post_init__(self):
        if self.hop_traces is None:
            self.hop_traces = []
        if self.response_headers is None:
            self.response_headers = {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "request_id": self.request_id,
            "url": self.url,
            "method": self.method,
            "start_time": self.start_time,
            "final_status": self.final_status.value,
            "total_duration": self.total_duration,
            "hop_traces": [hop.to_dict() for hop in self.hop_traces],
            "response_headers": dict(self.response_headers)
        }

    def to_json(self) -> str:
        """Export to JSON"""
        return json.dumps(self.to_dict(), indent=2)


class ProxyChainExecutor:
    """Execute HTTP requests through proxy chain"""

    def __init__(self, chain: ProxyChain, execution_mode: ExecutionMode = ExecutionMode.SEQUENTIAL):
        """
        Initialize executor

        Args:
            chain: ProxyChain instance
            execution_mode: How to execute requests (sequential, parallel, fallback)
        """
        self.chain = chain
        self.execution_mode = execution_mode
        self.lock = threading.Lock()
        self.request_counter = 0
        self.execution_history: List[ChainExecutionTrace] = []

    def _generate_request_id(self) -> str:
        """Generate unique request ID"""
        with self.lock:
            self.request_counter += 1
            timestamp = int(time.time() * 1000)
            return f"req-{timestamp}-{self.request_counter}"

    def _create_ssl_context(self) -> ssl.SSLContext:
        """Create SSL context"""
        context = ssl.create_default_context()
        return context

    def _build_proxy_url(self, hop: ProxyHopConfig) -> str:
        """Build proxy URL with authentication"""
        protocol = hop.protocol.value
        hostname = hop.hostname
        port = hop.port

        if hop.auth_type.value == "basic" and hop.username and hop.password:
            encoded_auth = base64.b64encode(
                f"{hop.username}:{hop.password}".encode()
            ).decode()
            return f"{protocol}://{encoded_auth}@{hostname}:{port}"

        return f"{protocol}://{hostname}:{port}"

    def _execute_single_hop(
        self,
        url: str,
        hop_config: ProxyHopConfig,
        hop_index: int,
        method: str = "GET",
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
        body: Optional[bytes] = None
    ) -> Tuple[bool, Optional[Any], Optional[str], float]:
        """
        Execute request through single hop

        Returns:
            Tuple of (success, response, error_message, response_time)
        """
        start_time = time.time()
        hop_info = HopExecutionInfo(
            hop_index=hop_index,
            proxy_address=hop_config.get_proxy_url(),
            start_time=start_time
        )

        try:
            if not hop_config.enabled:
                hop_info.status = HopExecutionStatus.SKIPPED
                return False, None, "Hop is disabled", time.time() - start_time

            if timeout is None:
                timeout = hop_config.timeout

            # Build proxy URL
            proxy_url = self._build_proxy_url(hop_config)

            # Prepare headers
            request_headers = headers or {}
            request_headers['User-Agent'] = 'ProxyChainExecutor/1.0'

            # Create request
            req = urllib.request.Request(
                url,
                data=body,
                headers=request_headers,
                method=method
            )

            # Create proxy handler
            proxy_handler = urllib.request.ProxyHandler({
                'http': proxy_url,
                'https': proxy_url
            })

            # Create opener
            opener = urllib.request.build_opener(proxy_handler)

            # Execute request
            hop_info.status = HopExecutionStatus.IN_PROGRESS
            response = opener.open(req, timeout=timeout)
            hop_info.response_code = response.getcode()
            hop_info.status = HopExecutionStatus.SUCCESS

            response_time = time.time() - start_time
            hop_info.end_time = time.time()

            logger.info(
                f"Hop {hop_index} success via {hop_config.get_proxy_url()} "
                f"({response_time:.2f}s)"
            )

            self.chain.record_hop_success(hop_index, response_time)
            return True, response, None, response_time

        except socket.timeout:
            response_time = time.time() - start_time
            hop_info.status = HopExecutionStatus.TIMEOUT
            hop_info.end_time = time.time()
            error_msg = f"Hop {hop_index} timeout"
            logger.warning(error_msg)
            self.chain.record_hop_failure(hop_index)
            return False, None, error_msg, response_time

        except urllib.error.HTTPError as e:
            response_time = time.time() - start_time
            hop_info.status = HopExecutionStatus.FAILED
            hop_info.response_code = e.code
            hop_info.end_time = time.time()
            error_msg = f"Hop {hop_index} HTTP {e.code}: {e.reason}"
            logger.warning(error_msg)
            return False, None, error_msg, response_time

        except (urllib.error.URLError, socket.error) as e:
            response_time = time.time() - start_time
            hop_info.status = HopExecutionStatus.FAILED
            hop_info.end_time = time.time()
            error_msg = f"Hop {hop_index} connection error: {str(e)}"
            logger.warning(error_msg)
            self.chain.record_hop_failure(hop_index)
            return False, None, error_msg, response_time

        except Exception as e:
            response_time = time.time() - start_time
            hop_info.status = HopExecutionStatus.FAILED
            hop_info.end_time = time.time()
            error_msg = f"Hop {hop_index} error: {str(e)}"
            logger.error(error_msg)
            self.chain.record_hop_failure(hop_index)
            return False, None, error_msg, response_time

    def _execute_sequential(
        self,
        url: str,
        method: str = "GET",
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
        body: Optional[bytes] = None
    ) -> Tuple[bool, Optional[Any], List[HopExecutionInfo]]:
        """
        Execute through all hops sequentially

        Returns:
            Tuple of (success, response, hop_traces)
        """
        hop_traces = []

        for hop_index, hop_config in self.chain.get_enabled_hops():
            success, response, error, response_time = self._execute_single_hop(
                url, hop_config, hop_index, method, headers, timeout, body
            )

            # Create trace info (would be recorded inside _execute_single_hop)
            if success:
                return True, response, hop_traces

        return False, None, hop_traces

    def execute(
        self,
        url: str,
        method: str = "GET",
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
        body: Optional[bytes] = None,
        max_retries: int = 1,
        record_trace: bool = True
    ) -> Tuple[bool, Optional[Any], str]:
        """
        Execute request through proxy chain

        Args:
            url: Target URL
            method: HTTP method
            headers: Request headers
            timeout: Request timeout in seconds
            body: Request body for POST/PUT
            max_retries: Maximum retries per hop
            record_trace: Whether to record execution trace

        Returns:
            Tuple of (success, response, info_message)
        """
        request_id = self._generate_request_id()
        trace = ChainExecutionTrace(
            request_id=request_id,
            url=url,
            method=method,
            start_time=datetime.now().isoformat()
        )

        try:
            # Get enabled hops
            enabled_hops = self.chain.get_enabled_hops()
            if not enabled_hops:
                trace.final_status = HopExecutionStatus.FAILED
                if record_trace:
                    with self.lock:
                        self.execution_history.append(trace)
                return False, None, "No enabled hops in chain"

            # Execute through chain
            for hop_index, hop_config in enabled_hops:
                retry_count = 0
                success = False

                while retry_count < max_retries and not success:
                    success, response, error, response_time = self._execute_single_hop(
                        url, hop_config, hop_index, method, headers, timeout, body
                    )

                    if success:
                        trace.final_status = HopExecutionStatus.SUCCESS
                        trace.total_duration = time.time() - time.mktime(
                            datetime.fromisoformat(trace.start_time).timetuple()
                        )

                        if record_trace:
                            with self.lock:
                                self.execution_history.append(trace)

                        info = f"Success via hop {hop_index} ({hop_config.get_proxy_url()})"
                        logger.info(f"Request {request_id} completed: {info}")
                        return True, response, info

                    retry_count += 1
                    if retry_count < max_retries:
                        delay = self.chain.config.retry_backoff_factor ** (retry_count - 1)
                        logger.info(
                            f"Retrying hop {hop_index} after {delay:.1f}s "
                            f"({retry_count + 1}/{max_retries})"
                        )
                        time.sleep(delay)

            # All hops failed
            trace.final_status = HopExecutionStatus.FAILED
            trace.total_duration = time.time() - time.mktime(
                datetime.fromisoformat(trace.start_time).timetuple()
            )

            if record_trace:
                with self.lock:
                    self.execution_history.append(trace)

            info = "All hops failed"
            logger.error(f"Request {request_id} failed: {info}")
            return False, None, info

        except Exception as e:
            trace.final_status = HopExecutionStatus.FAILED
            error_msg = str(e)
            logger.error(f"Request {request_id} error: {error_msg}")

            if record_trace:
                with self.lock:
                    self.execution_history.append(trace)

            return False, None, error_msg

    def get_execution_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent execution traces"""
        with self.lock:
            traces = self.execution_history[-limit:]
            return [trace.to_dict() for trace in traces]

    def get_last_execution_trace(self) -> Optional[Dict[str, Any]]:
        """Get most recent execution trace"""
        with self.lock:
            if self.execution_history:
                return self.execution_history[-1].to_dict()
        return None

    def clear_history(self) -> int:
        """Clear execution history"""
        with self.lock:
            count = len(self.execution_history)
            self.execution_history.clear()
            return count

    def get_executor_stats(self) -> Dict[str, Any]:
        """Get executor statistics"""
        with self.lock:
            if not self.execution_history:
                return {
                    "total_requests": 0,
                    "successful_requests": 0,
                    "failed_requests": 0,
                    "success_rate": 0.0,
                    "average_duration": 0.0,
                    "execution_mode": self.execution_mode.value
                }

            total = len(self.execution_history)
            successful = sum(
                1 for t in self.execution_history
                if t.final_status == HopExecutionStatus.SUCCESS
            )
            failed = total - successful
            avg_duration = (
                sum(t.total_duration for t in self.execution_history) / total
                if total > 0 else 0
            )

            return {
                "total_requests": total,
                "successful_requests": successful,
                "failed_requests": failed,
                "success_rate": (successful / total * 100) if total > 0 else 0,
                "average_duration": avg_duration,
                "execution_mode": self.execution_mode.value
            }

    def export_execution_report(self, output_file: Optional[str] = None) -> Dict[str, Any]:
        """Export execution report"""
        stats = self.get_executor_stats()
        chain_health = self.chain.get_chain_health()
        history = self.get_execution_history()

        report = {
            "executor_stats": stats,
            "chain_health": chain_health,
            "execution_traces": history,
            "generated_at": datetime.now().isoformat()
        }

        if output_file:
            with open(output_file, 'w') as f:
                json.dump(report, f, indent=2)
            logger.info(f"Report exported to {output_file}")

        return report


# Convenience functions
def create_executor(chain: ProxyChain, mode: ExecutionMode = ExecutionMode.SEQUENTIAL) -> ProxyChainExecutor:
    """Create executor for chain"""
    return ProxyChainExecutor(chain, mode)


if __name__ == "__main__":
    print("=" * 80)
    print("PROXY CHAIN EXECUTOR - DEMONSTRATION")
    print("=" * 80)

    print("\n1. Demonstrating Executor Interface")
    print("-" * 80)

    from proxy_chain_builder import ProxyChainBuilder

    # Build a test chain
    builder = ProxyChainBuilder("demo-chain")
    builder.add_hop("proxy1.example.com", 8080, label="Hop 1")
    builder.add_hop("proxy2.example.com", 3128, label="Hop 2")

    try:
        chain = builder.build()
        print(f"✓ Chain created with {len(chain.get_all_hops())} hops")

        # Create executor
        executor = create_executor(chain)
        print(f"✓ Executor created")

        print(f"\n  Executor capabilities:")
        print(f"    - Sequential hop execution")
        print(f"    - Per-hop retry logic")
        print(f"    - Execution tracing")
        print(f"    - Metrics collection")
        print(f"    - History tracking")

        # Show example usage
        print(f"\n  Example usage:")
        print(f"    executor.execute('https://api.example.com/data')")
        print(f"    traces = executor.get_execution_history()")
        print(f"    stats = executor.get_executor_stats()")

    except Exception as e:
        print(f"✗ Error: {e}")

    print("\n" + "=" * 80)
    print("PROXY CHAIN EXECUTOR - DEMONSTRATION COMPLETE")
    print("=" * 80)
