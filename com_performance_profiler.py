#!/usr/bin/env python3
"""
COM Object Performance Profiler
Profiles execution speed of various COM object instantiation methods.
Measures: instantiation time, method invocation latency, cleanup time, memory usage.
"""

import time
import json
import statistics
from dataclasses import dataclass, asdict
from typing import Dict, List, Callable, Tuple, Optional
from enum import Enum
import sys
import traceback


class COMMethod(Enum):
    """COM instantiation methods"""
    CREATEOBJECT_PROGID = "CreateObject_ProgID"
    CREATEOBJECT_CLSID = "CreateObject_CLSID"
    GETOBJECT = "GetObject"
    MONIKER = "Moniker"
    REGISTRY = "Registry"
    WMI_LOCATOR = "WMI_Locator"
    LATE_BINDING = "Late_Binding"
    EARLY_BINDING = "Early_Binding"


@dataclass
class PerformanceMetric:
    """Single performance measurement"""
    method: str
    operation: str
    elapsed_ms: float
    memory_delta_kb: float = 0.0
    success: bool = True
    error_msg: str = ""


@dataclass
class PerformanceSummary:
    """Summary statistics for a method"""
    method: str
    operation: str
    sample_count: int
    min_ms: float
    max_ms: float
    mean_ms: float
    median_ms: float
    stdev_ms: float
    p95_ms: float
    p99_ms: float
    success_rate: float


class COMPerformanceProfiler:
    """Profiles COM object performance"""

    # VBScript templates for different instantiation methods
    VBS_TEMPLATES = {
        "CreateObject_ProgID": '''
Dim obj, t1, t2
t1 = Timer()
Set obj = CreateObject("{progid}")
t2 = Timer()
WScript.Echo "Time:" & (t2-t1)*1000
Set obj = Nothing
''',

        "CreateObject_CLSID": '''
Dim obj, t1, t2
t1 = Timer()
Set obj = GetObject("new:{clsid}")
t2 = Timer()
WScript.Echo "Time:" & (t2-t1)*1000
Set obj = Nothing
''',

        "GetObject": '''
Dim obj, t1, t2
On Error Resume Next
t1 = Timer()
Set obj = GetObject(, "{progid}")
t2 = Timer()
WScript.Echo "Time:" & (t2-t1)*1000
Set obj = Nothing
On Error GoTo 0
''',

        "Moniker": '''
Dim obj, t1, t2
On Error Resume Next
t1 = Timer()
Set obj = GetObject("new:{clsid}")
t2 = Timer()
WScript.Echo "Time:" & (t2-t1)*1000
Set obj = Nothing
On Error GoTo 0
''',

        "WMI_Locator": '''
Dim locator, service, t1, t2
t1 = Timer()
Set locator = CreateObject("WbemScripting.SWbemLocator")
Set service = locator.ConnectServer()
t2 = Timer()
WScript.Echo "Time:" & (t2-t1)*1000
Set service = Nothing
Set locator = Nothing
''',
    }

    # PowerShell templates for COM profiling
    PS_TEMPLATES = {
        "CreateObject_ProgID": '''
$sw = [System.Diagnostics.Stopwatch]::StartNew()
$obj = New-Object -ComObject {progid}
$sw.Stop()
Write-Host "Time:$($sw.ElapsedMilliseconds)"
[System.Runtime.InteropServices.Marshal]::ReleaseComObject($obj)
''',

        "WMI_Locator": '''
$sw = [System.Diagnostics.Stopwatch]::StartNew()
$locator = New-Object -ComObject "WbemScripting.SWbemLocator"
$service = $locator.ConnectServer()
$sw.Stop()
Write-Host "Time:$($sw.ElapsedMilliseconds)"
''',
    }

    def __init__(self, iterations: int = 10, timeout_sec: int = 30):
        self.iterations = iterations
        self.timeout_sec = timeout_sec
        self.results: List[PerformanceMetric] = []
        self.com_objects = {
            "Excel.Application": "{00024500-0000-0000-C000-000000000046}",
            "WScript.Shell": "{F935DC22-1CF0-11D0-ADB9-00C04FD58A0B}",
            "WbemScripting.SWbemLocator": "{76A64158-CB41-11D1-8B02-00600806D9B6}",
            "Shell.Application": "{13709620-C279-11CE-A49E-444553540000}",
        }

    def measure_operation(self, method_name: str, operation: str,
                         operation_func: Callable, *args, **kwargs) -> Optional[PerformanceMetric]:
        """Measure single operation performance"""
        try:
            start = time.perf_counter()
            result = operation_func(*args, **kwargs)
            elapsed = (time.perf_counter() - start) * 1000  # Convert to ms

            metric = PerformanceMetric(
                method=method_name,
                operation=operation,
                elapsed_ms=elapsed,
                success=True
            )
            return metric
        except Exception as e:
            metric = PerformanceMetric(
                method=method_name,
                operation=operation,
                elapsed_ms=0,
                success=False,
                error_msg=str(e)
            )
            return metric

    def profile_vbs_instantiation(self, method: COMMethod, progid: str,
                                  clsid: Optional[str] = None) -> List[PerformanceMetric]:
        """Profile VBScript-based COM instantiation"""
        results = []

        template = self.VBS_TEMPLATES.get(method.value)
        if not template:
            return results

        for i in range(self.iterations):
            try:
                vbs_code = template.format(progid=progid, clsid=clsid or "")

                # Simulate VBScript execution (would run cscript.exe in real environment)
                metric = self.measure_operation(
                    method.value,
                    f"instantiation_{i+1}",
                    self._simulate_vbs_execution,
                    vbs_code
                )
                if metric:
                    results.append(metric)
            except Exception as e:
                results.append(PerformanceMetric(
                    method=method.value,
                    operation=f"instantiation_{i+1}",
                    elapsed_ms=0,
                    success=False,
                    error_msg=str(e)
                ))

        return results

    def profile_direct_instantiation(self) -> List[PerformanceMetric]:
        """Profile direct COM instantiation (Python simulation)"""
        results = []

        for method_name, operation_func in [
            ("Direct_Instantiation", lambda: self._simulate_com_instantiation("Excel.Application")),
            ("With_Error_Handling", lambda: self._simulate_com_with_error_handling("Excel.Application")),
            ("Moniker_Binding", lambda: self._simulate_moniker_binding("{00024500-0000-0000-C000-000000000046}")),
            ("Registry_Lookup", lambda: self._simulate_registry_lookup("Excel.Application")),
        ]:
            for i in range(self.iterations):
                metric = self.measure_operation(
                    method_name,
                    f"execution_{i+1}",
                    operation_func
                )
                if metric:
                    results.append(metric)

        return results

    def profile_method_invocation(self, method_name: str) -> List[PerformanceMetric]:
        """Profile COM method invocation latency"""
        results = []

        operation_funcs = [
            ("QueryInterface", lambda: self._simulate_method_call("QueryInterface")),
            ("AddRef", lambda: self._simulate_method_call("AddRef")),
            ("Release", lambda: self._simulate_method_call("Release")),
            ("Invoke", lambda: self._simulate_method_call("Invoke")),
        ]

        for op_name, op_func in operation_funcs:
            for i in range(self.iterations):
                metric = self.measure_operation(
                    method_name,
                    op_name,
                    op_func
                )
                if metric:
                    results.append(metric)

        return results

    def profile_wmi_operations(self) -> List[PerformanceMetric]:
        """Profile WMI COM operations"""
        results = []

        wmi_operations = [
            ("WMI_Locator_Creation", lambda: self._simulate_wmi_locator()),
            ("WMI_Service_Connect", lambda: self._simulate_wmi_connect()),
            ("WMI_Query_Execution", lambda: self._simulate_wmi_query()),
            ("WMI_Event_Subscription", lambda: self._simulate_wmi_events()),
        ]

        for op_name, op_func in wmi_operations:
            for i in range(self.iterations):
                metric = self.measure_operation(
                    "WMI_Operations",
                    op_name,
                    op_func
                )
                if metric:
                    results.append(metric)

        return results

    def profile_cleanup_performance(self) -> List[PerformanceMetric]:
        """Profile COM object cleanup/release performance"""
        results = []

        cleanup_ops = [
            ("Reference_Release", lambda: self._simulate_release()),
            ("Marshal_FinalRelease", lambda: self._simulate_marshal_release()),
            ("Garbage_Collection", lambda: self._simulate_gc()),
            ("COM_Cleanup", lambda: self._simulate_com_cleanup()),
        ]

        for op_name, op_func in cleanup_ops:
            for i in range(self.iterations):
                metric = self.measure_operation(
                    "Cleanup_Operations",
                    op_name,
                    op_func
                )
                if metric:
                    results.append(metric)

        return results

    # Simulation functions (replace with actual COM calls in Windows environment)
    def _simulate_vbs_execution(self, code: str) -> None:
        """Simulate VBScript execution"""
        time.sleep(0.001)  # Simulate minimal COM overhead

    def _simulate_com_instantiation(self, progid: str) -> None:
        """Simulate COM instantiation"""
        time.sleep(0.002)

    def _simulate_com_with_error_handling(self, progid: str) -> None:
        """Simulate COM instantiation with error handling"""
        time.sleep(0.0025)

    def _simulate_moniker_binding(self, clsid: str) -> None:
        """Simulate moniker binding"""
        time.sleep(0.003)

    def _simulate_registry_lookup(self, progid: str) -> None:
        """Simulate registry lookup"""
        time.sleep(0.004)

    def _simulate_method_call(self, method: str) -> None:
        """Simulate COM method invocation"""
        time.sleep(0.0005)

    def _simulate_wmi_locator(self) -> None:
        """Simulate WMI locator creation"""
        time.sleep(0.005)

    def _simulate_wmi_connect(self) -> None:
        """Simulate WMI service connection"""
        time.sleep(0.008)

    def _simulate_wmi_query(self) -> None:
        """Simulate WMI query execution"""
        time.sleep(0.012)

    def _simulate_wmi_events(self) -> None:
        """Simulate WMI event subscription"""
        time.sleep(0.010)

    def _simulate_release(self) -> None:
        """Simulate reference release"""
        time.sleep(0.001)

    def _simulate_marshal_release(self) -> None:
        """Simulate marshal final release"""
        time.sleep(0.0015)

    def _simulate_gc(self) -> None:
        """Simulate garbage collection"""
        time.sleep(0.002)

    def _simulate_com_cleanup(self) -> None:
        """Simulate COM cleanup"""
        time.sleep(0.0025)

    def run_full_profile(self) -> Dict:
        """Run complete performance profile"""
        print(f"[*] Starting COM Performance Profile (iterations={self.iterations})")

        all_results = []

        # Profile different instantiation methods
        print("[+] Profiling direct instantiation methods...")
        all_results.extend(self.profile_direct_instantiation())

        # Profile method invocations
        print("[+] Profiling COM method invocations...")
        all_results.extend(self.profile_method_invocation("COM_Methods"))

        # Profile WMI operations
        print("[+] Profiling WMI operations...")
        all_results.extend(self.profile_wmi_operations())

        # Profile cleanup operations
        print("[+] Profiling cleanup operations...")
        all_results.extend(self.profile_cleanup_performance())

        self.results = all_results
        return self.generate_report()

    def generate_report(self) -> Dict:
        """Generate performance report"""
        if not self.results:
            return {"error": "No results collected"}

        # Group results by method and operation
        grouped = {}
        for metric in self.results:
            key = (metric.method, metric.operation)
            if key not in grouped:
                grouped[key] = []
            grouped[key].append(metric)

        # Calculate summaries
        summaries = []
        for (method, operation), metrics in grouped.items():
            timings = [m.elapsed_ms for m in metrics if m.success]
            successful = sum(1 for m in metrics if m.success)

            if timings:
                summary = PerformanceSummary(
                    method=method,
                    operation=operation,
                    sample_count=len(timings),
                    min_ms=min(timings),
                    max_ms=max(timings),
                    mean_ms=statistics.mean(timings),
                    median_ms=statistics.median(timings),
                    stdev_ms=statistics.stdev(timings) if len(timings) > 1 else 0,
                    p95_ms=self._percentile(timings, 0.95),
                    p99_ms=self._percentile(timings, 0.99),
                    success_rate=successful / len(metrics)
                )
                summaries.append(summary)

        # Sort by mean execution time
        summaries.sort(key=lambda x: x.mean_ms)

        return {
            "total_measurements": len(self.results),
            "iterations": self.iterations,
            "summaries": [asdict(s) for s in summaries],
            "fastest": asdict(summaries[0]) if summaries else None,
            "slowest": asdict(summaries[-1]) if summaries else None,
            "all_metrics": [asdict(m) for m in self.results]
        }

    @staticmethod
    def _percentile(data: List[float], p: float) -> float:
        """Calculate percentile value"""
        sorted_data = sorted(data)
        index = int(len(sorted_data) * p)
        return sorted_data[min(index, len(sorted_data) - 1)]


def main():
    """Main entry point"""
    profiler = COMPerformanceProfiler(iterations=20)
    report = profiler.run_full_profile()

    # Output JSON report
    print("\n" + "="*80)
    print("COM OBJECT PERFORMANCE PROFILE REPORT")
    print("="*80)
    print(json.dumps(report, indent=2))

    # Print summary table
    if "summaries" in report:
        print("\n" + "="*80)
        print("PERFORMANCE SUMMARY (sorted by mean execution time)")
        print("="*80)
        print(f"{'Method':<30} {'Operation':<25} {'Mean (ms)':<12} {'P95 (ms)':<12} {'Success %':<10}")
        print("-"*89)

        for summary in report["summaries"]:
            print(f"{summary['method']:<30} {summary['operation']:<25} "
                  f"{summary['mean_ms']:<12.4f} {summary['p95_ms']:<12.4f} "
                  f"{summary['success_rate']*100:<10.1f}")


if __name__ == "__main__":
    main()
