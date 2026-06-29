#!/usr/bin/env python3
"""
Performance Test: WMI vs WScript.Shell Execution
Measures latency and performance characteristics of both execution methods
"""

import json
import time
import subprocess
import statistics
from typing import Dict, List, Tuple
from dataclasses import dataclass
import tempfile
import os


@dataclass
class PerformanceMetrics:
    """Performance metrics for execution methods"""
    method: str
    samples: List[float]
    min_latency_ms: float
    max_latency_ms: float
    mean_latency_ms: float
    median_latency_ms: float
    std_dev_ms: float
    p95_latency_ms: float
    p99_latency_ms: float

    def to_dict(self):
        return {
            "method": self.method,
            "samples": self.samples,
            "min_latency_ms": round(self.min_latency_ms, 3),
            "max_latency_ms": round(self.max_latency_ms, 3),
            "mean_latency_ms": round(self.mean_latency_ms, 3),
            "median_latency_ms": round(self.median_latency_ms, 3),
            "std_dev_ms": round(self.std_dev_ms, 3),
            "p95_latency_ms": round(self.p95_latency_ms, 3),
            "p99_latency_ms": round(self.p99_latency_ms, 3),
        }


class WScriptShellExecutor:
    """WScript.Shell execution method"""

    @staticmethod
    def generate_vbs_code(command: str) -> str:
        """Generate VBS code using WScript.Shell"""
        return f'''
Set objShell = CreateObject("WScript.Shell")
objShell.Run "{command}", 0, False
Set objShell = Nothing
'''

    @staticmethod
    def create_test_vbs(command: str) -> str:
        """Create temporary VBS file"""
        fd, path = tempfile.mkstemp(suffix='.vbs')
        os.write(fd, WScriptShellExecutor.generate_vbs_code(command).encode())
        os.close(fd)
        return path

    @staticmethod
    def execute(command: str) -> float:
        """Execute command via WScript.Shell and return latency in ms"""
        vbs_path = WScriptShellExecutor.create_test_vbs(command)
        try:
            start_time = time.perf_counter()
            subprocess.run(['cscript.exe', vbs_path],
                         capture_output=True, timeout=5)
            end_time = time.perf_counter()
            return (end_time - start_time) * 1000
        finally:
            try:
                os.unlink(vbs_path)
            except:
                pass


class WMIExecutor:
    """WMI (WbemScripting.SWbemLocator) execution method"""

    @staticmethod
    def generate_vbs_code(command: str) -> str:
        """Generate VBS code using WMI (SWbemLocator)"""
        return f'''
Dim objLocator, objConn, objService, objMethod, objResult
Set objLocator = CreateObject("WbemScripting.SWbemLocator")
Set objConn = objLocator.ConnectServer(".", "root\\cimv2")
Set objService = objConn.Get("Win32_Process")
Set objMethod = objService.Methods_("Create")
Dim inParams
Set inParams = objMethod.InParameters.SpawnInstance_()
inParams.CommandLine = "{command}"
Set objResult = objConn.ExecMethod("Win32_Process", "Create", inParams)
Set objMethod = Nothing
Set objService = Nothing
Set objConn = Nothing
Set objLocator = Nothing
'''

    @staticmethod
    def create_test_vbs(command: str) -> str:
        """Create temporary VBS file"""
        fd, path = tempfile.mkstemp(suffix='.vbs')
        os.write(fd, WMIExecutor.generate_vbs_code(command).encode())
        os.close(fd)
        return path

    @staticmethod
    def execute(command: str) -> float:
        """Execute command via WMI and return latency in ms"""
        vbs_path = WMIExecutor.create_test_vbs(command)
        try:
            start_time = time.perf_counter()
            subprocess.run(['cscript.exe', vbs_path],
                         capture_output=True, timeout=5)
            end_time = time.perf_counter()
            return (end_time - start_time) * 1000
        finally:
            try:
                os.unlink(vbs_path)
            except:
                pass


class PerformanceTestHarness:
    """Harness for performance testing"""

    def __init__(self, num_samples: int = 20, command: str = "cmd.exe /c whoami"):
        self.num_samples = num_samples
        self.command = command
        self.results: Dict[str, PerformanceMetrics] = {}

    def run_test(self, executor_class, name: str) -> PerformanceMetrics:
        """Run performance test for executor"""
        print(f"\nTesting {name}...")
        samples = []

        for i in range(self.num_samples):
            try:
                latency = executor_class.execute(self.command)
                samples.append(latency)
                print(f"  Sample {i+1}/{self.num_samples}: {latency:.3f}ms")
            except Exception as e:
                print(f"  Sample {i+1}/{self.num_samples}: ERROR - {e}")
                return None

        sorted_samples = sorted(samples)
        metrics = PerformanceMetrics(
            method=name,
            samples=samples,
            min_latency_ms=min(samples),
            max_latency_ms=max(samples),
            mean_latency_ms=statistics.mean(samples),
            median_latency_ms=statistics.median(samples),
            std_dev_ms=statistics.stdev(samples) if len(samples) > 1 else 0.0,
            p95_latency_ms=sorted_samples[int(len(sorted_samples) * 0.95)],
            p99_latency_ms=sorted_samples[int(len(sorted_samples) * 0.99)],
        )

        self.results[name] = metrics
        return metrics

    def generate_comparison_report(self) -> Dict:
        """Generate comparison report"""
        report = {
            "test_configuration": {
                "num_samples": self.num_samples,
                "command_tested": self.command,
                "test_timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            },
            "results": {}
        }

        # Add individual results
        for name, metrics in self.results.items():
            report["results"][name] = metrics.to_dict()

        # Add comparison analysis
        if len(self.results) >= 2:
            methods = list(self.results.keys())
            wscript_metrics = self.results.get("WScript.Shell")
            wmi_metrics = self.results.get("WMI (SWbemLocator)")

            if wscript_metrics and wmi_metrics:
                wscript_mean = wscript_metrics.mean_latency_ms
                wmi_mean = wmi_metrics.mean_latency_ms

                if wscript_mean > 0:
                    speedup_factor = wmi_mean / wscript_mean
                    faster_method = "WMI (SWbemLocator)" if speedup_factor > 1 else "WScript.Shell"
                else:
                    speedup_factor = 0
                    faster_method = "Unknown"

                report["comparison"] = {
                    "faster_method": faster_method,
                    "speedup_factor": round(speedup_factor, 3),
                    "wscript_mean_ms": round(wscript_mean, 3),
                    "wmi_mean_ms": round(wmi_mean, 3),
                    "latency_difference_ms": round(abs(wscript_mean - wmi_mean), 3),
                    "percentage_difference": round(
                        ((wmi_mean - wscript_mean) / wscript_mean * 100) if wscript_mean > 0 else 0, 1
                    ),
                }

                # Variability analysis
                report["variability_analysis"] = {
                    "wscript_coefficient_of_variation": round(
                        (wscript_metrics.std_dev_ms / wscript_mean * 100) if wscript_mean > 0 else 0, 2
                    ),
                    "wmi_coefficient_of_variation": round(
                        (wmi_metrics.std_dev_ms / wmi_mean * 100) if wmi_mean > 0 else 0, 2
                    ),
                    "consistency_winner": (
                        "WScript.Shell"
                        if (wscript_metrics.std_dev_ms / wscript_mean) < (wmi_metrics.std_dev_ms / wmi_mean)
                        else "WMI (SWbemLocator)"
                    ),
                }

        return report

    def print_summary(self):
        """Print human-readable summary"""
        print("\n" + "="*70)
        print("PERFORMANCE TEST SUMMARY: WMI vs WScript.Shell")
        print("="*70)

        for name, metrics in self.results.items():
            print(f"\n{name}:")
            print(f"  Min Latency:     {metrics.min_latency_ms:.3f}ms")
            print(f"  Max Latency:     {metrics.max_latency_ms:.3f}ms")
            print(f"  Mean Latency:    {metrics.mean_latency_ms:.3f}ms")
            print(f"  Median Latency:  {metrics.median_latency_ms:.3f}ms")
            print(f"  Std Dev:         {metrics.std_dev_ms:.3f}ms")
            print(f"  P95 Latency:     {metrics.p95_latency_ms:.3f}ms")
            print(f"  P99 Latency:     {metrics.p99_latency_ms:.3f}ms")

        # Comparison
        if len(self.results) >= 2:
            print("\n" + "-"*70)
            print("COMPARISON ANALYSIS:")
            print("-"*70)
            wscript = self.results.get("WScript.Shell")
            wmi = self.results.get("WMI (SWbemLocator)")

            if wscript and wmi:
                diff = wmi.mean_latency_ms - wscript.mean_latency_ms
                pct_diff = (diff / wscript.mean_latency_ms * 100) if wscript.mean_latency_ms > 0 else 0

                print(f"WScript.Shell Mean: {wscript.mean_latency_ms:.3f}ms")
                print(f"WMI Mean:           {wmi.mean_latency_ms:.3f}ms")
                print(f"Difference:         {abs(diff):.3f}ms ({abs(pct_diff):.1f}%)")

                if diff > 0:
                    print(f"Winner:             WScript.Shell (faster by {abs(diff):.3f}ms)")
                else:
                    print(f"Winner:             WMI (faster by {abs(diff):.3f}ms)")

                print(f"\nConsistency (Coefficient of Variation):")
                wscript_cv = (wscript.std_dev_ms / wscript.mean_latency_ms * 100) if wscript.mean_latency_ms > 0 else 0
                wmi_cv = (wmi.std_dev_ms / wmi.mean_latency_ms * 100) if wmi.mean_latency_ms > 0 else 0
                print(f"  WScript.Shell CV: {wscript_cv:.2f}%")
                print(f"  WMI CV:           {wmi_cv:.2f}%")
                print(f"  More Consistent:  {'WScript.Shell' if wscript_cv < wmi_cv else 'WMI'}")

        print("\n" + "="*70)


def main():
    """Main test harness"""
    print("WMI vs WScript.Shell Performance Test")
    print("Testing command execution latency...")

    # Create test harness
    harness = PerformanceTestHarness(
        num_samples=20,
        command="cmd.exe /c echo test"
    )

    # Run tests
    print("\n[1/2] Testing WScript.Shell execution method...")
    wscript_result = harness.run_test(WScriptShellExecutor, "WScript.Shell")

    print("\n[2/2] Testing WMI (SWbemLocator) execution method...")
    wmi_result = harness.run_test(WMIExecutor, "WMI (SWbemLocator)")

    # Generate reports
    report = harness.generate_comparison_report()
    harness.print_summary()

    # Save results
    output_path = "/tmp/claude-0/-home-user-sc-generator/cea520eb-2877-52b0-bbd4-c38bff01b8ad/scratchpad/wmi_wscript_comparison.json"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(report, f, indent=2)

    print(f"\nDetailed results saved to: {output_path}")

    return report


if __name__ == "__main__":
    main()
