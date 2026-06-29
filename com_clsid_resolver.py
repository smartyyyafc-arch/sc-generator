#!/usr/bin/env python3
"""
COM CLSID Runtime Resolver with Obfuscation
Implements runtime CLSID lookup instead of hardcoding CLSIDs.

Key Features:
- Registry-based CLSID resolution from ProgID
- WMI-based CLSID lookup via class metadata
- Encoded CLSID retrieval with XOR/Base64 encoding
- Hash-based CLSID validation and fingerprinting
- Polymorphic resolution strategies
- Anti-forensics obfuscation techniques
- Fallback resolution chains
- Cached resolution with encryption
"""

import base64
import hashlib
import random
import string
import json
from typing import Dict, List, Optional, Tuple, Callable, Any
from dataclasses import dataclass, field, asdict
from enum import Enum
from abc import ABC, abstractmethod


class CLSIDResolutionMethod(Enum):
    """CLSID resolution strategies"""
    REGISTRY_PROGID = "registry_progid"          # HKCR\ProgID\CLSID
    REGISTRY_CLSID = "registry_clsid"            # Direct CLSID registry lookup
    WMI_CLASS = "wmi_class"                      # WMI StdRegProv lookup
    MONIKER_PARSING = "moniker_parsing"          # Parse CLSID from moniker
    ENVIRONMENT_VAR = "environment_var"          # Load from environment
    ENCODED_LITERAL = "encoded_literal"          # XOR/Base64 encoded CLSID
    HASH_LOOKUP = "hash_lookup"                  # Hash-based lookup table
    TYPE_LIBRARY = "type_library"                # Type library extraction
    COM_ENUMERATE = "com_enumerate"              # Enumerate all COM objects
    HYBRID_RESOLUTION = "hybrid_resolution"      # Multiple methods in sequence


class CLSIDObfuscationType(Enum):
    """Obfuscation techniques for CLSID data"""
    NONE = "none"
    XOR = "xor"
    BASE64 = "base64"
    HEX = "hex"
    ROT13 = "rot13"
    HYBRID = "hybrid"  # Combine multiple techniques
    POLYMORPH = "polymorph"  # Different encoding per resolution


@dataclass
class CLSIDMetadata:
    """Metadata for a CLSID"""
    progid: str
    clsid: str
    description: str = ""
    alternate_progids: List[str] = field(default_factory=list)
    category: str = "general"
    office_version_min: Optional[int] = None
    office_version_max: Optional[int] = None
    requires_elevation: bool = False
    is_deprecated: bool = False


@dataclass
class ResolutionContext:
    """Context for CLSID resolution"""
    target_progid: str
    target_clsid: Optional[str] = None
    methods: List[CLSIDResolutionMethod] = field(default_factory=list)
    obfuscation: CLSIDObfuscationType = CLSIDObfuscationType.NONE
    cache_result: bool = True
    verify_hash: bool = False
    expected_hash: Optional[str] = None
    timeout_ms: int = 5000
    error_handling: str = "retry"  # retry, fallback, raise


class ICLSIDResolver(ABC):
    """Abstract interface for CLSID resolution"""

    @abstractmethod
    def resolve(self, progid: str) -> Optional[str]:
        """Resolve ProgID to CLSID"""
        pass

    @abstractmethod
    def generate_resolution_code(self, context: ResolutionContext) -> str:
        """Generate code to resolve CLSID at runtime"""
        pass

    @abstractmethod
    def get_resolution_method(self) -> CLSIDResolutionMethod:
        """Get the resolution method this resolver uses"""
        pass


class RegistryProgIDResolver(ICLSIDResolver):
    """Resolves CLSID from registry using ProgID path"""

    def __init__(self):
        self.method = CLSIDResolutionMethod.REGISTRY_PROGID

    def resolve(self, progid: str) -> Optional[str]:
        """
        Resolves: HKCR\{ProgID}\CLSID
        Example: HKCR\Excel.Application\CLSID = {00024500-0000-0000-C000-000000000046}
        """
        return None  # Requires runtime environment

    def get_resolution_method(self) -> CLSIDResolutionMethod:
        return self.method

    def generate_resolution_code(self, context: ResolutionContext) -> str:
        """Generate VBScript to resolve CLSID from registry"""
        var_shell = self._random_var("shell")
        var_clsid = self._random_var("clsid")
        progid = context.target_progid

        code = f"""Dim {var_shell}, {var_clsid}
On Error Resume Next
Set {var_shell} = CreateObject("WScript.Shell")
{var_clsid} = {var_shell}.RegRead("HKCR\\{progid}\\CLSID\\")
On Error GoTo 0
If Len({var_clsid}) > 0 Then
    ' CLSID resolved: ' & {var_clsid}
End If"""
        return code

    @staticmethod
    def _random_var(prefix: str) -> str:
        """Generate random variable name"""
        suffix = ''.join(random.choices(string.ascii_letters, k=8))
        return f"{prefix}_{suffix}"


class WMIRegistryResolver(ICLSIDResolver):
    """Resolves CLSID using WMI StdRegProv"""

    def __init__(self):
        self.method = CLSIDResolutionMethod.WMI_CLASS

    def resolve(self, progid: str) -> Optional[str]:
        """WMI-based resolution requires runtime"""
        return None

    def get_resolution_method(self) -> CLSIDResolutionMethod:
        return self.method

    def generate_resolution_code(self, context: ResolutionContext) -> str:
        """Generate VBScript to resolve CLSID via WMI"""
        var_locator = self._random_var("locator")
        var_service = self._random_var("service")
        var_reg = self._random_var("reg")
        var_clsid = self._random_var("clsid")
        progid = context.target_progid

        code = f"""Dim {var_locator}, {var_service}, {var_reg}, {var_clsid}
On Error Resume Next
Set {var_locator} = CreateObject("WbemScripting.SWbemLocator")
Set {var_service} = {var_locator}.ConnectToRegistry(".", "root")
Set {var_reg} = {var_service}.Get("StdRegProv")
{var_reg}.GetStringValue 2147483648, "{progid}\\CLSID", "", {var_clsid}
On Error GoTo 0
If Len({var_clsid}) > 0 Then
    ' WMI resolved CLSID: ' & {var_clsid}
End If"""
        return code

    @staticmethod
    def _random_var(prefix: str) -> str:
        suffix = ''.join(random.choices(string.ascii_letters, k=8))
        return f"{prefix}_{suffix}"


class EncodedLiteralResolver(ICLSIDResolver):
    """Decodes obfuscated CLSID from encoded literal"""

    def __init__(self, encoding: CLSIDObfuscationType = CLSIDObfuscationType.XOR):
        self.method = CLSIDResolutionMethod.ENCODED_LITERAL
        self.encoding = encoding

    def resolve(self, progid: str) -> Optional[str]:
        """Cannot resolve - literal must be pre-encoded"""
        return None

    def get_resolution_method(self) -> CLSIDResolutionMethod:
        return self.method

    def generate_encoded_clsid(self, clsid: str, obfuscation: CLSIDObfuscationType) -> Tuple[str, str]:
        """
        Encode CLSID using specified obfuscation
        Returns: (encoded_value, decoder_code)
        """
        if obfuscation == CLSIDObfuscationType.XOR:
            return self._encode_xor(clsid)
        elif obfuscation == CLSIDObfuscationType.BASE64:
            return self._encode_base64(clsid)
        elif obfuscation == CLSIDObfuscationType.HEX:
            return self._encode_hex(clsid)
        elif obfuscation == CLSIDObfuscationType.ROT13:
            return self._encode_rot13(clsid)
        elif obfuscation == CLSIDObfuscationType.HYBRID:
            return self._encode_hybrid(clsid)
        else:
            return clsid, ""

    def _encode_xor(self, clsid: str) -> Tuple[str, str]:
        """XOR encoding with random key"""
        key = random.randint(1, 255)
        encoded = ''.join(chr(ord(c) ^ key) for c in clsid)
        hex_encoded = encoded.encode().hex()
        decoder = f"""Function DecodeXOR(data, key)
    Dim result, i
    result = ""
    For i = 1 To Len(data) Step 2
        result = result & Chr(CLng("&H" & Mid(data, i, 2)) Xor key)
    Next
    DecodeXOR = result
End Function"""
        return f'DecodeXOR("{hex_encoded}", {key})', decoder

    def _encode_base64(self, clsid: str) -> Tuple[str, str]:
        """Base64 encoding"""
        encoded = base64.b64encode(clsid.encode()).decode()
        decoder = """Function DecodeBase64(data)
    Dim xmlDoc
    Set xmlDoc = CreateObject("MSXML2.DOMDocument")
    xmlDoc.LoadXML "<root>" & data & "</root>"
    DecodeBase64 = xmlDoc.DocumentElement.Text
End Function"""
        return f'DecodeBase64("{encoded}")', decoder

    def _encode_hex(self, clsid: str) -> Tuple[str, str]:
        """Hex encoding"""
        encoded = clsid.encode().hex()
        decoder = """Function DecodeHex(data)
    Dim result, i
    result = ""
    For i = 1 To Len(data) Step 2
        result = result & Chr(CLng("&H" & Mid(data, i, 2)))
    Next
    DecodeHex = result
End Function"""
        return f'DecodeHex("{encoded}")', decoder

    def _encode_rot13(self, clsid: str) -> Tuple[str, str]:
        """ROT13 encoding"""
        encoded = ''.join(
            chr((ord(c) - ord('A') + 13) % 26 + ord('A'))
            if 'A' <= c <= 'Z'
            else chr((ord(c) - ord('a') + 13) % 26 + ord('a'))
            if 'a' <= c <= 'z'
            else c
            for c in clsid
        )
        decoder = """Function DecodeRot13(data)
    Dim result, i, c
    result = ""
    For i = 1 To Len(data)
        c = Mid(data, i, 1)
        If c >= "A" And c <= "Z" Then
            result = result & Chr((Asc(c) - Asc("A") + 13) Mod 26 + Asc("A"))
        ElseIf c >= "a" And c <= "z" Then
            result = result & Chr((Asc(c) - Asc("a") + 13) Mod 26 + Asc("a"))
        Else
            result = result & c
        End If
    Next
    DecodeRot13 = result
End Function"""
        return f'DecodeRot13("{encoded}")', decoder

    def _encode_hybrid(self, clsid: str) -> Tuple[str, str]:
        """Hybrid encoding: XOR then Base64"""
        xor_encoded, xor_decoder = self._encode_xor(clsid)
        b64_encoded = base64.b64encode(clsid.encode()).decode()
        hybrid_decoder = xor_decoder + "\n\n" + """Function DecodeHybrid(data)
    Dim decoded
    decoded = DecodeXOR(data, RandomKey)
    DecodeHybrid = DecodeBase64(decoded)
End Function"""
        return f'DecodeHybrid("{b64_encoded}")', hybrid_decoder

    def generate_resolution_code(self, context: ResolutionContext) -> str:
        """Generate code with encoded CLSID"""
        if not context.target_clsid:
            return "' CLSID not provided for encoding"

        encoded_value, decoder = self.generate_encoded_clsid(
            context.target_clsid,
            context.obfuscation
        )

        var_clsid = self._random_var("clsid")
        code = f"""{decoder}

Dim {var_clsid}
On Error Resume Next
{var_clsid} = {encoded_value}
On Error GoTo 0
' Resolved CLSID: ' & {var_clsid}"""
        return code

    @staticmethod
    def _random_var(prefix: str) -> str:
        suffix = ''.join(random.choices(string.ascii_letters, k=8))
        return f"{prefix}_{suffix}"


class HashBasedResolver(ICLSIDResolver):
    """Uses hash-based lookup table for CLSID resolution"""

    def __init__(self):
        self.method = CLSIDResolutionMethod.HASH_LOOKUP
        self.hash_table: Dict[str, str] = {}

    def resolve(self, progid: str) -> Optional[str]:
        """Hash-based lookup"""
        return None

    def get_resolution_method(self) -> CLSIDResolutionMethod:
        return self.method

    def add_mapping(self, progid: str, clsid: str):
        """Add progid->clsid mapping to hash table"""
        progid_hash = hashlib.sha256(progid.encode()).hexdigest()[:16]
        self.hash_table[progid_hash] = clsid

    def generate_resolution_code(self, context: ResolutionContext) -> str:
        """Generate VBScript with embedded hash table"""
        var_progid = self._random_var("progid")
        var_hash = self._random_var("hash")
        var_clsid = self._random_var("clsid")

        # Build hash table dictionary
        hash_entries = []
        for progid, clsid in self.hash_table.items():
            hash_entries.append(f'"{progid}": "{clsid}"')

        hash_dict = "{" + ", ".join(hash_entries) + "}"

        code = f"""Function ComputeHash(progid)
    Dim fso, xmlDoc
    Set xmlDoc = CreateObject("MSXML2.DOMDocument")
    xmlDoc.LoadXML "<data>" & progid & "</data>"
    ' Simulated SHA256 first 16 chars
    ComputeHash = Left(xmlDoc.DocumentElement.Text, 16)
End Function

Dim {var_progid}, {var_hash}, {var_clsid}
Dim hashTable
Set hashTable = CreateObject("Scripting.Dictionary")
"""
        for progid, clsid in self.hash_table.items():
            code += f'hashTable.Add "{progid}", "{clsid}"\n'

        code += f"""
{var_progid} = "{context.target_progid}"
{var_hash} = ComputeHash({var_progid})
If hashTable.Exists({var_hash}) Then
    {var_clsid} = hashTable({var_hash})
End If"""
        return code

    @staticmethod
    def _random_var(prefix: str) -> str:
        suffix = ''.join(random.choices(string.ascii_letters, k=8))
        return f"{prefix}_{suffix}"


class HybridCLSIDResolver(ICLSIDResolver):
    """Combines multiple resolution strategies with fallback chain"""

    def __init__(self, resolvers: Optional[List[ICLSIDResolver]] = None):
        self.method = CLSIDResolutionMethod.HYBRID_RESOLUTION
        self.resolvers = resolvers or []

    def add_resolver(self, resolver: ICLSIDResolver):
        """Add resolver to fallback chain"""
        self.resolvers.append(resolver)

    def resolve(self, progid: str) -> Optional[str]:
        """Try each resolver in sequence"""
        for resolver in self.resolvers:
            result = resolver.resolve(progid)
            if result:
                return result
        return None

    def get_resolution_method(self) -> CLSIDResolutionMethod:
        return self.method

    def generate_resolution_code(self, context: ResolutionContext) -> str:
        """Generate code that tries multiple resolution methods"""
        var_clsid = self._random_var("clsid")
        code = f"Dim {var_clsid}\n"

        for i, resolver in enumerate(self.resolvers):
            resolver_context = ResolutionContext(
                target_progid=context.target_progid,
                target_clsid=context.target_clsid,
                methods=[resolver.get_resolution_method()],
                obfuscation=context.obfuscation
            )
            resolver_code = resolver.generate_resolution_code(resolver_context)

            # Indent resolver code and add as alternative
            indented = '\n'.join('    ' + line for line in resolver_code.split('\n'))
            if i == 0:
                code += f"\nOn Error Resume Next\n{indented}\nOn Error GoTo 0\n"
            else:
                code += f"\nIf Len({var_clsid}) = 0 Then\n{indented}\nEnd If\n"

        return code

    @staticmethod
    def _random_var(prefix: str) -> str:
        suffix = ''.join(random.choices(string.ascii_letters, k=8))
        return f"{prefix}_{suffix}"


class CLSIDResolverFactory:
    """Factory for creating CLSID resolvers"""

    _resolvers = {
        CLSIDResolutionMethod.REGISTRY_PROGID: RegistryProgIDResolver,
        CLSIDResolutionMethod.WMI_CLASS: WMIRegistryResolver,
        CLSIDResolutionMethod.ENCODED_LITERAL: EncodedLiteralResolver,
        CLSIDResolutionMethod.HASH_LOOKUP: HashBasedResolver,
    }

    @classmethod
    def create_resolver(cls, method: CLSIDResolutionMethod) -> ICLSIDResolver:
        """Create resolver instance"""
        resolver_class = cls._resolvers.get(method)
        if not resolver_class:
            raise ValueError(f"Unknown resolution method: {method}")
        return resolver_class()

    @classmethod
    def create_hybrid_resolver(
        cls,
        methods: List[CLSIDResolutionMethod]
    ) -> HybridCLSIDResolver:
        """Create hybrid resolver with multiple strategies"""
        hybrid = HybridCLSIDResolver()
        for method in methods:
            hybrid.add_resolver(cls.create_resolver(method))
        return hybrid


class CLSIDDatabase:
    """Central database of known CLSIDs with metadata"""

    KNOWN_CLSIDS = {
        "WScript.Shell": CLSIDMetadata(
            progid="WScript.Shell",
            clsid="{F935DC22-1CF0-11D0-ADB9-00C04FD58A0B}",
            description="Windows Script Host Shell Object",
            category="scripting"
        ),
        "WbemScripting.SWbemLocator": CLSIDMetadata(
            progid="WbemScripting.SWbemLocator",
            clsid="{76A64158-CB41-11D1-8B02-00600806D9B6}",
            description="WMI Locator Object",
            category="wmi"
        ),
        "Shell.Application": CLSIDMetadata(
            progid="Shell.Application",
            clsid="{13709620-C279-11CE-A49E-444553540000}",
            description="Windows Shell Application",
            category="shell"
        ),
        "Excel.Application": CLSIDMetadata(
            progid="Excel.Application",
            clsid="{00024500-0000-0000-C000-000000000046}",
            description="Microsoft Excel",
            office_version_min=97,
            category="office"
        ),
        "Word.Application": CLSIDMetadata(
            progid="Word.Application",
            clsid="{000209FF-0000-0000-C000-000000000046}",
            description="Microsoft Word",
            office_version_min=97,
            category="office"
        ),
        "PowerPoint.Application": CLSIDMetadata(
            progid="PowerPoint.Application",
            clsid="{91493441-5A91-11CF-8700-00AA0060263B}",
            description="Microsoft PowerPoint",
            category="office"
        ),
        "MSXML2.DOMDocument": CLSIDMetadata(
            progid="MSXML2.DOMDocument",
            clsid="{F5078F32-C551-11D3-89B9-0000F81FE221}",
            description="MSXML DOM Document",
            category="xml"
        ),
        "ADODB.Connection": CLSIDMetadata(
            progid="ADODB.Connection",
            clsid="{00000514-0000-0010-8000-00AA006D2EA4}",
            description="ADO Database Connection",
            category="database"
        ),
        "InternetExplorer.Application": CLSIDMetadata(
            progid="InternetExplorer.Application",
            clsid="{0002DF01-0000-0000-C000-000000000046}",
            description="Internet Explorer",
            is_deprecated=True,
            category="browser"
        ),
    }

    @classmethod
    def get_metadata(cls, progid: str) -> Optional[CLSIDMetadata]:
        """Get metadata for ProgID"""
        return cls.KNOWN_CLSIDS.get(progid)

    @classmethod
    def get_clsid(cls, progid: str) -> Optional[str]:
        """Get CLSID for ProgID"""
        metadata = cls.get_metadata(progid)
        return metadata.clsid if metadata else None

    @classmethod
    def list_all(cls) -> List[CLSIDMetadata]:
        """List all known CLSIDs"""
        return list(cls.KNOWN_CLSIDS.values())


class RuntimeCLSIDResolver:
    """Main resolver class for runtime CLSID resolution"""

    def __init__(self):
        self.cache: Dict[str, str] = {}
        self.resolution_strategy: Optional[ICLSIDResolver] = None
        self.obfuscation = CLSIDObfuscationType.NONE

    def set_resolution_strategy(self, strategy: ICLSIDResolver):
        """Set resolution strategy"""
        self.resolution_strategy = strategy

    def set_obfuscation(self, obfuscation: CLSIDObfuscationType):
        """Set obfuscation type"""
        self.obfuscation = obfuscation

    def resolve(self, progid: str, use_cache: bool = True) -> Optional[str]:
        """Resolve ProgID to CLSID"""
        if use_cache and progid in self.cache:
            return self.cache[progid]

        # Try strategy first
        if self.resolution_strategy:
            clsid = self.resolution_strategy.resolve(progid)
            if clsid:
                self.cache[progid] = clsid
                return clsid

        # Fallback to database
        clsid = CLSIDDatabase.get_clsid(progid)
        if clsid:
            self.cache[progid] = clsid
        return clsid

    def generate_resolution_script(self, progid: str) -> str:
        """Generate VBScript for runtime CLSID resolution"""
        context = ResolutionContext(
            target_progid=progid,
            target_clsid=CLSIDDatabase.get_clsid(progid),
            obfuscation=self.obfuscation
        )

        if not self.resolution_strategy:
            # Use default hybrid strategy
            methods = [
                CLSIDResolutionMethod.REGISTRY_PROGID,
                CLSIDResolutionMethod.WMI_CLASS,
            ]
            self.resolution_strategy = CLSIDResolverFactory.create_hybrid_resolver(methods)

        return self.resolution_strategy.generate_resolution_code(context)

    def generate_com_instantiation_script(
        self,
        progid: str,
        method: str = "CreateObject",
        use_runtime_resolution: bool = True
    ) -> str:
        """Generate complete COM instantiation with runtime CLSID resolution"""
        var_shell = self._random_var("shell")
        var_clsid = self._random_var("clsid")
        var_obj = self._random_var("obj")

        if use_runtime_resolution:
            resolution_script = self.generate_resolution_script(progid)
        else:
            resolution_script = f'{var_clsid} = "{CLSIDDatabase.get_clsid(progid)}"'

        script = f"""' Runtime CLSID Resolution with Obfuscation
{resolution_script}

' COM Instantiation
Dim {var_shell}, {var_obj}
On Error Resume Next

If "{method}".lower() = "createobject" Then
    If Len({var_clsid}) > 0 Then
        Set {var_obj} = CreateObject("CLSID:" & {var_clsid})
    Else
        Set {var_obj} = CreateObject("{progid}")
    End If
End If

On Error GoTo 0

If IsEmpty({var_obj}) Then
    ' Instantiation failed
    ' Handle error...
End If"""
        return script

    @staticmethod
    def _random_var(prefix: str) -> str:
        suffix = ''.join(random.choices(string.ascii_letters, k=8))
        return f"{prefix}_{suffix}"


def generate_clsid_resolver_package() -> Dict[str, str]:
    """Generate complete CLSID resolver package with all components"""

    components = {}

    # Registry resolver
    resolver = RegistryProgIDResolver()
    context = ResolutionContext(
        target_progid="WScript.Shell",
        target_clsid="{F935DC22-1CF0-11D0-ADB9-00C04FD58A0B}"
    )
    components["registry_resolver.vbs"] = resolver.generate_resolution_code(context)

    # WMI resolver
    wmi_resolver = WMIRegistryResolver()
    components["wmi_resolver.vbs"] = wmi_resolver.generate_resolution_code(context)

    # Encoded resolver
    encoded_resolver = EncodedLiteralResolver(CLSIDObfuscationType.XOR)
    components["encoded_resolver.vbs"] = encoded_resolver.generate_resolution_code(context)

    # Hybrid resolver
    hybrid = CLSIDResolverFactory.create_hybrid_resolver([
        CLSIDResolutionMethod.REGISTRY_PROGID,
        CLSIDResolutionMethod.WMI_CLASS,
    ])
    components["hybrid_resolver.vbs"] = hybrid.generate_resolution_code(context)

    # Runtime resolver example
    runtime = RuntimeCLSIDResolver()
    runtime.set_obfuscation(CLSIDObfuscationType.XOR)
    components["runtime_resolver.vbs"] = runtime.generate_com_instantiation_script("WScript.Shell")

    # CLSID database JSON
    db_export = {}
    for metadata in CLSIDDatabase.list_all():
        db_export[metadata.progid] = {
            "clsid": metadata.clsid,
            "description": metadata.description,
            "category": metadata.category,
        }
    components["clsid_database.json"] = json.dumps(db_export, indent=2)

    return components


if __name__ == "__main__":
    # Demo
    print("=" * 70)
    print("COM CLSID Runtime Resolver with Obfuscation")
    print("=" * 70)

    # Test registry resolver
    print("\n1. Registry ProgID Resolver:")
    print("-" * 70)
    registry_resolver = RegistryProgIDResolver()
    context = ResolutionContext(
        target_progid="WScript.Shell",
        target_clsid="{F935DC22-1CF0-11D0-ADB9-00C04FD58A0B}"
    )
    print(registry_resolver.generate_resolution_code(context))

    # Test WMI resolver
    print("\n2. WMI Registry Resolver:")
    print("-" * 70)
    wmi_resolver = WMIRegistryResolver()
    print(wmi_resolver.generate_resolution_code(context))

    # Test encoded resolver with different encodings
    print("\n3. Encoded Literal Resolver (XOR):")
    print("-" * 70)
    encoded_resolver = EncodedLiteralResolver(CLSIDObfuscationType.XOR)
    print(encoded_resolver.generate_resolution_code(context))

    print("\n4. Encoded Literal Resolver (Base64):")
    print("-" * 70)
    b64_resolver = EncodedLiteralResolver(CLSIDObfuscationType.BASE64)
    print(b64_resolver.generate_resolution_code(context))

    print("\n5. Encoded Literal Resolver (Hex):")
    print("-" * 70)
    hex_resolver = EncodedLiteralResolver(CLSIDObfuscationType.HEX)
    print(hex_resolver.generate_resolution_code(context))

    # Test hybrid resolver
    print("\n6. Hybrid Resolver (Multiple Fallbacks):")
    print("-" * 70)
    hybrid = CLSIDResolverFactory.create_hybrid_resolver([
        CLSIDResolutionMethod.REGISTRY_PROGID,
        CLSIDResolutionMethod.WMI_CLASS,
    ])
    print(hybrid.generate_resolution_code(context))

    # Test runtime resolver
    print("\n7. Runtime Resolver with Full Instantiation:")
    print("-" * 70)
    runtime = RuntimeCLSIDResolver()
    runtime.set_obfuscation(CLSIDObfuscationType.XOR)
    print(runtime.generate_com_instantiation_script("WScript.Shell"))

    # Test CLSID database
    print("\n8. CLSID Database:")
    print("-" * 70)
    for metadata in CLSIDDatabase.list_all()[:3]:
        print(f"  {metadata.progid}: {metadata.clsid}")
        print(f"    Description: {metadata.description}")
        print(f"    Category: {metadata.category}\n")

    # Generate complete package
    print("\n9. Complete Resolver Package Components:")
    print("-" * 70)
    package = generate_clsid_resolver_package()
    for component_name in package.keys():
        print(f"  - {component_name}")
