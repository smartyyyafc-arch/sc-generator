#!/usr/bin/env python3
"""
COM Object Polymorphic Loader
Implements polymorphism where the same code can use different COM objects
through a unified, abstracted interface.

Key Features:
- Abstract base class defining COM object interface
- Multiple concrete COM implementations
- Loader factory for instantiation at runtime
- Strategy pattern for method invocation
- Fallback chains for resilience
- Configuration-driven object selection
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Callable, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
import random
import string


class COMObjectType(Enum):
    """Enumeration of COM object types"""
    SHELL = "shell"
    WMI_LOCATOR = "wmi_locator"
    EXCEL = "excel"
    WORD = "word"
    MSXML = "msxml"
    ADODB = "adodb"
    INTERNET_EXPLORER = "ie"
    OUTLOOK = "outlook"
    WSCRIPT = "wscript"
    UNKNOWN = "unknown"


class COMInstantiationMethod(Enum):
    """Enumeration of COM instantiation methods"""
    CREATE_OBJECT_PROGID = "createobject_progid"
    CREATE_OBJECT_CLSID = "createobject_clsid"
    GET_OBJECT_RUNNING = "getobject_running"
    GET_OBJECT_MONIKER = "getobject_moniker"
    GET_OBJECT_WMI = "getobject_wmi"
    NEW_KEYWORD = "new_keyword"
    REMOTE_DCOM = "remote_dcom"
    REGISTRY_LOOKUP = "registry_lookup"
    ENCODED_PROGID = "encoded_progid"
    INLINE_CLASS = "inline_class"
    CLSID_MONIKER = "clsid_moniker"


@dataclass
class COMObjectMetadata:
    """Metadata describing a COM object variant"""
    object_type: COMObjectType
    progid: str
    clsid: Optional[str] = None
    instantiation_method: COMInstantiationMethod = COMInstantiationMethod.CREATE_OBJECT_PROGID
    fallback_methods: List[COMInstantiationMethod] = field(default_factory=list)
    requires_library_reference: bool = False
    supports_remote: bool = False
    supports_encoding: bool = False
    encoding_types: List[str] = field(default_factory=lambda: ["base64", "hex"])
    version_range: Tuple[int, int] = (1, 20)
    description: str = ""
    category: str = "general"


class ICOMObject(ABC):
    """Abstract interface for COM objects"""

    @abstractmethod
    def get_progid(self) -> str:
        """Get ProgID of COM object"""
        pass

    @abstractmethod
    def get_clsid(self) -> Optional[str]:
        """Get CLSID of COM object"""
        pass

    @abstractmethod
    def get_instantiation_code(self) -> str:
        """Get VBScript code to instantiate the COM object"""
        pass

    @abstractmethod
    def get_execution_code(self, method: str, *args) -> str:
        """Get code to execute a method on the COM object"""
        pass

    @abstractmethod
    def get_object_type(self) -> COMObjectType:
        """Get the type of COM object"""
        pass

    @abstractmethod
    def get_method_signature(self) -> Dict[str, List[str]]:
        """Get available methods and their signatures"""
        pass


class ShellCOMObject(ICOMObject):
    """WScript.Shell COM object implementation"""

    def __init__(self, use_remote: bool = False, remote_machine: str = "."):
        self.use_remote = use_remote
        self.remote_machine = remote_machine
        self._var_name = f"shell_{self._random_suffix()}"

    def _random_suffix(self) -> str:
        return ''.join(random.choices(string.ascii_letters + string.digits, k=6))

    def get_progid(self) -> str:
        return "WScript.Shell"

    def get_clsid(self) -> Optional[str]:
        return "{F935DC22-1CF0-11D0-ADB9-00C04FD58A0B}"

    def get_instantiation_code(self) -> str:
        if self.use_remote:
            return f"""Dim {self._var_name}
On Error Resume Next
Set {self._var_name} = CreateObject("{self.get_progid()}", "{self.remote_machine}")
On Error GoTo 0"""
        else:
            return f"""Dim {self._var_name}
On Error Resume Next
Set {self._var_name} = CreateObject("{self.get_progid()}")
On Error GoTo 0"""

    def get_execution_code(self, method: str, *args) -> str:
        args_str = ", ".join(f'"{arg}"' for arg in args)
        if method.lower() == "run":
            return f"{self._var_name}.Run {args_str}"
        elif method.lower() == "exec":
            return f"Set exec = {self._var_name}.Exec({args_str})"
        elif method.lower() == "regread":
            return f"result = {self._var_name}.RegRead({args_str})"
        elif method.lower() == "regwrite":
            return f"{self._var_name}.RegWrite {args_str}"
        else:
            return f"{self._var_name}.{method} {args_str}"

    def get_object_type(self) -> COMObjectType:
        return COMObjectType.SHELL

    def get_method_signature(self) -> Dict[str, List[str]]:
        return {
            "Run": ["command", "windowStyle (optional)", "waitOnReturn (optional)"],
            "Exec": ["command"],
            "RegRead": ["regPath"],
            "RegWrite": ["regPath", "value"],
            "RegDelete": ["regPath"],
            "CreateShortcut": ["pathLink"],
            "ExpandEnvironmentStrings": ["string"],
            "Popup": ["text", "seconds (optional)", "title (optional)", "type (optional)"]
        }


class WMILocatorCOMObject(ICOMObject):
    """WbemScripting.SWbemLocator COM object implementation"""

    def __init__(self, namespace: str = "root\\cimv2", use_remote: bool = False, remote_host: str = "."):
        self.namespace = namespace
        self.use_remote = use_remote
        self.remote_host = remote_host
        self._var_name = f"wmi_{self._random_suffix()}"
        self._svc_var = f"svc_{self._random_suffix()}"

    def _random_suffix(self) -> str:
        return ''.join(random.choices(string.ascii_letters + string.digits, k=6))

    def get_progid(self) -> str:
        return "WbemScripting.SWbemLocator"

    def get_clsid(self) -> Optional[str]:
        return "{76A64158-CB41-11D1-8B02-00600806D9B6}"

    def get_instantiation_code(self) -> str:
        code = f"""Dim {self._var_name}, {self._svc_var}
On Error Resume Next
Set {self._var_name} = CreateObject("{self.get_progid()}")
Set {self._svc_var} = {self._var_name}.ConnectServer("{self.remote_host}", "{self.namespace}")
On Error GoTo 0"""
        return code

    def get_execution_code(self, method: str, *args) -> str:
        if method.lower() == "get":
            class_name = args[0] if args else "Win32_Process"
            return f"Set wmiClass = {self._svc_var}.Get(\"{class_name}\")"
        elif method.lower() == "execquery":
            query = args[0] if args else ""
            return f"Set results = {self._svc_var}.ExecQuery(\"{query}\")"
        elif method.lower() == "create":
            class_name = args[0] if args else "Win32_Process"
            return f"Set wmiClass = {self._svc_var}.Get(\"{class_name}\")\nSet instance = wmiClass.SpawnInstance_()"
        else:
            args_str = ", ".join(f'"{arg}"' for arg in args)
            return f"{self._svc_var}.{method}({args_str})"

    def get_object_type(self) -> COMObjectType:
        return COMObjectType.WMI_LOCATOR

    def get_method_signature(self) -> Dict[str, List[str]]:
        return {
            "Get": ["className"],
            "ExecQuery": ["query"],
            "Create": ["className"],
            "InstancesOf": ["className"],
            "SubclassesOf": ["className"]
        }


class ExcelCOMObject(ICOMObject):
    """Excel.Application COM object implementation"""

    def __init__(self, version: int = 0):
        self.version = version
        self._var_name = f"excel_{self._random_suffix()}"

    def _random_suffix(self) -> str:
        return ''.join(random.choices(string.ascii_letters + string.digits, k=6))

    def get_progid(self) -> str:
        if self.version > 0:
            return f"Excel.Application.{self.version}"
        return "Excel.Application"

    def get_clsid(self) -> Optional[str]:
        return "{00024500-0000-0000-C000-000000000046}"

    def get_instantiation_code(self) -> str:
        return f"""Dim {self._var_name}
On Error Resume Next
Set {self._var_name} = CreateObject("{self.get_progid()}")
If Not IsEmpty({self._var_name}) Then
    {self._var_name}.Visible = False
End If
On Error GoTo 0"""

    def get_execution_code(self, method: str, *args) -> str:
        if method.lower() == "open":
            filepath = args[0] if args else ""
            return f"{self._var_name}.Workbooks.Open \"{filepath}\""
        elif method.lower() == "getobject":
            filepath = args[0] if args else ""
            return f"Set obj = {self._var_name}.ActiveWorkbook"
        elif method.lower() == "run":
            macro_name = args[0] if args else ""
            return f"{self._var_name}.Run \"{macro_name}\""
        else:
            args_str = ", ".join(f'"{arg}"' for arg in args)
            return f"{self._var_name}.{method}({args_str})"

    def get_object_type(self) -> COMObjectType:
        return COMObjectType.EXCEL

    def get_method_signature(self) -> Dict[str, List[str]]:
        return {
            "Workbooks.Open": ["Filename", "UpdateLinks (optional)"],
            "Run": ["Macro"],
            "Quit": [],
            "ActiveWorkbook": [],
            "ActiveSheet": []
        }


class MSXMLCOMObject(ICOMObject):
    """MSXML2.DOMDocument COM object implementation"""

    def __init__(self, version: int = 6):
        self.version = version
        self._var_name = f"msxml_{self._random_suffix()}"

    def _random_suffix(self) -> str:
        return ''.join(random.choices(string.ascii_letters + string.digits, k=6))

    def get_progid(self) -> str:
        return f"MSXML2.DOMDocument.{self.version}.0"

    def get_clsid(self) -> Optional[str]:
        return "{F5078F32-C551-11D3-89B9-0000F81FE221}"

    def get_instantiation_code(self) -> str:
        return f"""Dim {self._var_name}
On Error Resume Next
Set {self._var_name} = CreateObject("{self.get_progid()}")
On Error GoTo 0"""

    def get_execution_code(self, method: str, *args) -> str:
        if method.lower() == "load":
            xml_file = args[0] if args else ""
            return f"{self._var_name}.Load \"{xml_file}\""
        elif method.lower() == "loadxml":
            xml_string = args[0] if args else ""
            return f"{self._var_name}.LoadXML \"{xml_string}\""
        elif method.lower() == "getelement":
            tag = args[0] if args else ""
            return f"Set elem = {self._var_name}.GetElementsByTagName(\"{tag}\")"
        else:
            args_str = ", ".join(f'"{arg}"' for arg in args)
            return f"{self._var_name}.{method}({args_str})"

    def get_object_type(self) -> COMObjectType:
        return COMObjectType.MSXML

    def get_method_signature(self) -> Dict[str, List[str]]:
        return {
            "Load": ["filename"],
            "LoadXML": ["xmlString"],
            "Save": ["filename"],
            "GetElementsByTagName": ["tagName"],
            "SelectNodes": ["xpath"],
            "SelectSingleNode": ["xpath"]
        }


class COMPolymorphicLoader:
    """
    Polymorphic COM object loader implementing factory pattern
    Loads and manages different COM object implementations through unified interface
    """

    def __init__(self):
        self._objects: Dict[COMObjectType, ICOMObject] = {}
        self._metadata: Dict[COMObjectType, COMObjectMetadata] = self._initialize_metadata()
        self._fallback_chains: Dict[COMObjectType, List[COMObjectType]] = self._initialize_fallbacks()
        self._loaded_objects: Dict[COMObjectType, ICOMObject] = {}

    def _initialize_metadata(self) -> Dict[COMObjectType, COMObjectMetadata]:
        """Initialize metadata for all COM objects"""
        return {
            COMObjectType.SHELL: COMObjectMetadata(
                object_type=COMObjectType.SHELL,
                progid="WScript.Shell",
                clsid="{F935DC22-1CF0-11D0-ADB9-00C04FD58A0B}",
                instantiation_method=COMInstantiationMethod.CREATE_OBJECT_PROGID,
                fallback_methods=[
                    COMInstantiationMethod.CREATE_OBJECT_CLSID,
                    COMInstantiationMethod.REGISTRY_LOOKUP
                ],
                supports_remote=True,
                description="WScript.Shell - System operations and command execution",
                category="system"
            ),
            COMObjectType.WMI_LOCATOR: COMObjectMetadata(
                object_type=COMObjectType.WMI_LOCATOR,
                progid="WbemScripting.SWbemLocator",
                clsid="{76A64158-CB41-11D1-8B02-00600806D9B6}",
                instantiation_method=COMInstantiationMethod.CREATE_OBJECT_PROGID,
                fallback_methods=[
                    COMInstantiationMethod.GET_OBJECT_WMI,
                    COMInstantiationMethod.CREATE_OBJECT_CLSID
                ],
                supports_remote=True,
                description="WbemScripting.SWbemLocator - WMI operations",
                category="wmi"
            ),
            COMObjectType.EXCEL: COMObjectMetadata(
                object_type=COMObjectType.EXCEL,
                progid="Excel.Application",
                clsid="{00024500-0000-0000-C000-000000000046}",
                instantiation_method=COMInstantiationMethod.CREATE_OBJECT_PROGID,
                fallback_methods=[
                    COMInstantiationMethod.CREATE_OBJECT_CLSID,
                    COMInstantiationMethod.GET_OBJECT_RUNNING
                ],
                version_range=(2007, 2024),
                description="Excel.Application - Spreadsheet operations",
                category="office"
            ),
            COMObjectType.MSXML: COMObjectMetadata(
                object_type=COMObjectType.MSXML,
                progid="MSXML2.DOMDocument",
                clsid="{F5078F32-C551-11D3-89B9-0000F81FE221}",
                instantiation_method=COMInstantiationMethod.CREATE_OBJECT_PROGID,
                fallback_methods=[
                    COMInstantiationMethod.CREATE_OBJECT_CLSID
                ],
                supports_encoding=True,
                description="MSXML2.DOMDocument - XML operations",
                category="xml"
            ),
        }

    def _initialize_fallbacks(self) -> Dict[COMObjectType, List[COMObjectType]]:
        """Initialize fallback chains for resilience"""
        return {
            COMObjectType.SHELL: [COMObjectType.WMI_LOCATOR],
            COMObjectType.WMI_LOCATOR: [COMObjectType.SHELL],
            COMObjectType.EXCEL: [COMObjectType.MSXML],
            COMObjectType.MSXML: [],
        }

    def load_object(self, object_type: COMObjectType, **kwargs) -> ICOMObject:
        """
        Load a COM object of specified type
        Implements factory pattern for object creation
        """
        if object_type in self._loaded_objects:
            return self._loaded_objects[object_type]

        obj = None

        if object_type == COMObjectType.SHELL:
            obj = ShellCOMObject(
                use_remote=kwargs.get("use_remote", False),
                remote_machine=kwargs.get("remote_machine", ".")
            )
        elif object_type == COMObjectType.WMI_LOCATOR:
            obj = WMILocatorCOMObject(
                namespace=kwargs.get("namespace", "root\\cimv2"),
                use_remote=kwargs.get("use_remote", False),
                remote_host=kwargs.get("remote_host", ".")
            )
        elif object_type == COMObjectType.EXCEL:
            obj = ExcelCOMObject(version=kwargs.get("version", 0))
        elif object_type == COMObjectType.MSXML:
            obj = MSXMLCOMObject(version=kwargs.get("version", 6))
        else:
            raise ValueError(f"Unsupported COM object type: {object_type}")

        self._loaded_objects[object_type] = obj
        return obj

    def get_object_metadata(self, object_type: COMObjectType) -> COMObjectMetadata:
        """Get metadata for a COM object type"""
        return self._metadata.get(object_type)

    def get_fallback_chain(self, object_type: COMObjectType) -> List[COMObjectType]:
        """Get fallback chain for a COM object type"""
        return self._fallback_chains.get(object_type, [])

    def generate_polymorphic_code(self,
                                 object_type: COMObjectType,
                                 method: str,
                                 *method_args,
                                 fallback: bool = True,
                                 use_error_handling: bool = True) -> str:
        """
        Generate VBScript code using polymorphic COM object
        Supports fallback chains for resilience
        """
        primary_obj = self.load_object(object_type)
        code_parts = []

        if use_error_handling:
            code_parts.append("On Error Resume Next")

        # Primary instantiation
        code_parts.append(primary_obj.get_instantiation_code())
        code_parts.append(f"If Not IsEmpty({primary_obj._var_name}) Then")
        code_parts.append(f"    {primary_obj.get_execution_code(method, *method_args)}")
        code_parts.append("End If")

        # Fallback chain
        if fallback:
            fallback_types = self.get_fallback_chain(object_type)
            for fallback_type in fallback_types:
                fallback_obj = self.load_object(fallback_type)
                code_parts.append(f"If IsEmpty({primary_obj._var_name}) Then")
                code_parts.append(fallback_obj.get_instantiation_code())
                code_parts.append(f"    If Not IsEmpty({fallback_obj._var_name}) Then")
                code_parts.append(f"        {fallback_obj.get_execution_code(method, *method_args)}")
                code_parts.append("    End If")
                code_parts.append("End If")

        if use_error_handling:
            code_parts.append("On Error GoTo 0")

        return "\n".join(code_parts)

    def generate_all_variants(self) -> Dict[str, Dict]:
        """Generate code for all COM object types"""
        variants = {}

        for obj_type in COMObjectType:
            if obj_type == COMObjectType.UNKNOWN:
                continue

            try:
                obj = self.load_object(obj_type)
                metadata = self.get_object_metadata(obj_type)

                variants[obj_type.value] = {
                    "progid": obj.get_progid(),
                    "clsid": obj.get_clsid(),
                    "instantiation_code": obj.get_instantiation_code(),
                    "object_type": obj.get_object_type().value,
                    "description": metadata.description if metadata else "",
                    "category": metadata.category if metadata else "general",
                    "methods": obj.get_method_signature(),
                    "supports_remote": metadata.supports_remote if metadata else False
                }
            except Exception as e:
                pass

        return variants

    def list_available_objects(self) -> List[str]:
        """List all available COM object types"""
        return [obj.value for obj in COMObjectType if obj != COMObjectType.UNKNOWN]

    def export_to_json(self) -> str:
        """Export loader configuration as JSON"""
        config = {
            "available_objects": self.list_available_objects(),
            "variants": self.generate_all_variants(),
            "fallback_chains": {
                k.value: [f.value for f in v]
                for k, v in self._fallback_chains.items()
            }
        }
        return json.dumps(config, indent=2)


class COMPolymorphicCodeGenerator:
    """High-level code generator using polymorphic loader"""

    def __init__(self):
        self.loader = COMPolymorphicLoader()

    def generate_command_executor(self, command: str) -> str:
        """Generate code to execute a system command"""
        return self.loader.generate_polymorphic_code(
            COMObjectType.SHELL,
            "Run",
            command
        )

    def generate_wmi_query_executor(self, query: str, namespace: str = "root\\cimv2") -> str:
        """Generate code to execute WMI query"""
        return self.loader.generate_polymorphic_code(
            COMObjectType.WMI_LOCATOR,
            "ExecQuery",
            query
        )

    def generate_registry_reader(self, reg_path: str) -> str:
        """Generate code to read registry"""
        return self.loader.generate_polymorphic_code(
            COMObjectType.SHELL,
            "RegRead",
            reg_path
        )

    def generate_file_operations(self, operation: str, filepath: str) -> str:
        """Generate code for file operations using available COM objects"""
        if operation.lower() == "open":
            return self.loader.generate_polymorphic_code(
                COMObjectType.EXCEL,
                "Open",
                filepath
            )
        else:
            return self.loader.generate_polymorphic_code(
                COMObjectType.SHELL,
                "Exec",
                f"cmd /c type {filepath}"
            )

    def export_library(self, output_format: str = "json") -> str:
        """Export complete polymorphic loader library"""
        if output_format == "json":
            return self.loader.export_to_json()
        else:
            raise ValueError(f"Unsupported format: {output_format}")


def demonstrate_polymorphism():
    """Demonstrate polymorphic COM object usage"""

    print("=" * 90)
    print("COM OBJECT POLYMORPHIC LOADER DEMONSTRATION")
    print("=" * 90 + "\n")

    loader = COMPolymorphicLoader()

    # Example 1: Direct shell execution
    print("[EXAMPLE 1: Shell Command Execution]")
    print("-" * 90)
    code = loader.generate_polymorphic_code(COMObjectType.SHELL, "Run", "calc.exe")
    print(code)
    print()

    # Example 2: WMI query execution
    print("[EXAMPLE 2: WMI Query Execution]")
    print("-" * 90)
    code = loader.generate_polymorphic_code(
        COMObjectType.WMI_LOCATOR,
        "ExecQuery",
        "SELECT * FROM Win32_Process"
    )
    print(code)
    print()

    # Example 3: Registry reading with fallback
    print("[EXAMPLE 3: Registry Reading with Fallback Chain]")
    print("-" * 90)
    code = loader.generate_polymorphic_code(
        COMObjectType.SHELL,
        "RegRead",
        "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run",
        fallback=True
    )
    print(code)
    print()

    # Example 4: Available COM objects
    print("[EXAMPLE 4: Available COM Objects]")
    print("-" * 90)
    available = loader.list_available_objects()
    for obj_type in available:
        print(f"  - {obj_type}")
    print()

    # Example 5: High-level code generator
    print("[EXAMPLE 5: High-Level Code Generator]")
    print("-" * 90)
    gen = COMPolymorphicCodeGenerator()
    code = gen.generate_command_executor("powershell.exe -NoProfile -Command 'Get-Process'")
    print(code)
    print()

    # Example 6: Export configuration
    print("[EXAMPLE 6: Loader Configuration (JSON)]")
    print("-" * 90)
    config = loader.export_to_json()
    print(config[:500] + "...")  # Print first 500 chars
    print()


if __name__ == "__main__":
    demonstrate_polymorphism()
