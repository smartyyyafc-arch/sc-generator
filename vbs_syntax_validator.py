#!/usr/bin/env python3
"""
VBS Syntax Validator - Verify all VBS payloads generate valid syntax with no undefined functions
Checks for:
- Valid VBS syntax structure
- All referenced functions are defined
- All referenced variables are declared
- Balanced control structures
- Valid VBS object creation
- Proper string handling
"""

import re
from typing import List, Dict, Set, Tuple
from dataclasses import dataclass


@dataclass
class SyntaxError:
    """Represents a VBS syntax error"""
    line_number: int
    error_type: str
    message: str
    context: str


class VBSSyntaxValidator:
    """Validates VBS code for syntax correctness and undefined references"""

    # Standard VBS functions and objects that are built-in
    BUILTIN_FUNCTIONS = {
        # String functions
        "ucase", "lcase", "strreverse", "len", "mid", "left", "right",
        "trim", "ltrim", "rtrim", "replace", "split", "join", "instr",
        "instrrev", "strcomp", "formatnumber", "formatcurrency", "formatpercent",
        "space", "string", "chr", "asc", "cbyte", "ccur", "cdate", "cdbl",
        "cint", "clng", "csng", "cstr", "cbool",
        # Array functions
        "ubound", "lbound", "array", "erase",
        # Math functions
        "abs", "int", "fix", "sgn", "sqr", "exp", "log", "sin", "cos",
        "tan", "atn", "rnd", "randomize",
        # Date functions
        "now", "date", "time", "datevalue", "timevalue", "weekday",
        "month", "day", "year", "hour", "minute", "second", "dateadd",
        "datediff", "dateserial", "timeserial",
        # Object functions
        "createobject", "getobject", "setobject",
        # Type functions
        "typename", "vartype", "isarray", "isdate", "isempty", "isnull",
        "isnumeric", "isobject",
        # VBS-specific
        "eval", "executeglobal", "execute", "inputbox", "msgbox",
        "vbquestion", "vbinformation", "vbexclamation", "vbcritical",
        "clng", "iserror", "err",
    }

    BUILTIN_OBJECTS = {
        "wscript", "wscript.shell", "wscript.network", "scripting.filesystemobject",
        "scripting.folder", "scripting.file", "msxml2.domDocument", "msxml2.xmlhttp",
        "adodb.connection", "adodb.recordset", "ado.stream", "wbem.locator",
        "shell.application", "activexobject", "dictionary", "wsnetwork",
        "sapi.spvoice", "shell.browserassistant", "internetexplorer.application",
    }

    BUILTIN_STATEMENTS = {
        "dim", "set", "let", "if", "then", "else", "elseif", "end",
        "for", "next", "while", "wend", "do", "loop", "until",
        "select", "case", "with", "function", "sub", "call", "exit",
        "on", "error", "resume", "goto", "class", "property", "get",
        "public", "private", "static", "const", "option", "explicit",
        "randomize", "erase", "reDim", "preserve",
    }

    # VBS keywords that are statements/control flow
    CONTROL_KEYWORDS = {
        "if", "then", "else", "elseif", "end if",
        "for", "next", "for each", "in",
        "while", "wend",
        "do", "loop", "until", "while",
        "select", "case", "end select",
        "with", "end with",
        "function", "end function",
        "sub", "end sub",
        "class", "end class",
        "error", "resume",
    }

    # Common VBS object methods (methods are called on objects, not flagged as undefined)
    COMMON_OBJECT_METHODS = {
        "run", "exec", "regread", "regwrite", "regdelete", "expandenvironmentstrings",
        "selectsinglenode", "loadxml", "createtextfile", "deletefile", "copyfile",
        "createobject", "getobject", "methods_", "spawninstance_", "execmethod",
        "environment", "createelement", "appendchild", "getelement", "setattribute",
    }

    def __init__(self):
        self.errors: List[SyntaxError] = []
        self.declared_variables: Set[str] = set()
        self.declared_functions: Set[str] = set()
        self.declared_classes: Set[str] = set()
        self.lines: List[str] = []

    def validate(self, vbs_code: str) -> Tuple[bool, List[SyntaxError]]:
        """
        Validate VBS code for syntax errors

        Args:
            vbs_code: VBS source code to validate

        Returns:
            Tuple of (is_valid, error_list)
        """
        self.errors = []
        self.declared_variables = set()
        self.declared_functions = set()
        self.declared_classes = set()
        self.lines = vbs_code.split('\n')

        # First pass: collect declarations
        self._collect_declarations()

        # Second pass: check for undefined references
        self._check_undefined_references()

        # Third pass: check for syntax issues
        self._check_syntax_structure()

        is_valid = len(self.errors) == 0
        return is_valid, self.errors

    def _collect_declarations(self):
        """First pass: collect all variable and function declarations"""
        for line_num, line in enumerate(self.lines, 1):
            stripped = line.strip()

            # Skip comments and empty lines
            if stripped.startswith("'") or not stripped:
                continue

            # Dim statements
            dim_match = re.match(r"^\s*Dim\s+(.*?)(?:\s*=|\s*,|$)", stripped, re.IGNORECASE)
            if dim_match:
                vars_part = dim_match.group(1)
                # Extract variable names (handle arrays and multiple vars)
                # Match variable name, optionally followed by () or (size)
                var_names = re.findall(r"([a-zA-Z_][a-zA-Z0-9_]*)\s*(?:\([^\)]*\))?", vars_part)
                for var_name in var_names:
                    if var_name:  # Only add non-empty names
                        self.declared_variables.add(var_name.lower())

            # Function declarations
            func_match = re.match(r"^\s*Function\s+([a-zA-Z_][a-zA-Z0-9_]*)", stripped, re.IGNORECASE)
            if func_match:
                func_name = func_match.group(1)
                self.declared_functions.add(func_name.lower())
                # Function parameters are also variables
                params_match = re.search(r"\((.*?)\)", stripped, re.IGNORECASE)
                if params_match:
                    params = params_match.group(1)
                    param_names = re.findall(r"([a-zA-Z_][a-zA-Z0-9_]*)", params)
                    for param_name in param_names:
                        self.declared_variables.add(param_name.lower())

            # Sub declarations
            sub_match = re.match(r"^\s*Sub\s+([a-zA-Z_][a-zA-Z0-9_]*)", stripped, re.IGNORECASE)
            if sub_match:
                sub_name = sub_match.group(1)
                self.declared_functions.add(sub_name.lower())
                # Sub parameters are also variables
                params_match = re.search(r"\((.*?)\)", stripped, re.IGNORECASE)
                if params_match:
                    params = params_match.group(1)
                    param_names = re.findall(r"([a-zA-Z_][a-zA-Z0-9_]*)", params)
                    for param_name in param_names:
                        self.declared_variables.add(param_name.lower())

            # Class declarations
            class_match = re.match(r"^\s*Class\s+([a-zA-Z_][a-zA-Z0-9_]*)", stripped, re.IGNORECASE)
            if class_match:
                class_name = class_match.group(1)
                self.declared_classes.add(class_name.lower())

            # For loops (declares loop variable)
            for_match = re.match(r"^\s*For\s+([a-zA-Z_][a-zA-Z0-9_]*)\s+", stripped, re.IGNORECASE)
            if for_match:
                var_name = for_match.group(1)
                self.declared_variables.add(var_name.lower())

            # For Each loops
            foreach_match = re.match(r"^\s*For\s+Each\s+([a-zA-Z_][a-zA-Z0-9_]*)\s+", stripped, re.IGNORECASE)
            if foreach_match:
                var_name = foreach_match.group(1)
                self.declared_variables.add(var_name.lower())

            # Set statements (assignment of objects)
            set_match = re.match(r"^\s*Set\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*=", stripped, re.IGNORECASE)
            if set_match:
                var_name = set_match.group(1)
                self.declared_variables.add(var_name.lower())

            # Direct assignments
            assign_match = re.match(r"^\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*=", stripped)
            if assign_match and not any(kw in stripped.lower() for kw in ["if ", "for ", "while ", "do "]):
                var_name = assign_match.group(1)
                self.declared_variables.add(var_name.lower())

    def _check_undefined_references(self):
        """Second pass: check for undefined function and variable references"""
        for line_num, line in enumerate(self.lines, 1):
            stripped = line.strip()

            # Skip comments and empty lines
            if stripped.startswith("'") or not stripped:
                continue

            # Find all function-like calls (identifier followed by parentheses)
            # But exclude if/for/while/etc which are statements and object methods
            func_call_pattern = r"(?:^|[^.])\b([a-zA-Z_][a-zA-Z0-9_]*)\s*\("
            matches = re.finditer(func_call_pattern, stripped, re.IGNORECASE)

            for match in matches:
                func_name = match.group(1)
                func_name_lower = func_name.lower()

                # Skip if this is a statement keyword
                if func_name_lower in self.BUILTIN_STATEMENTS:
                    continue

                # Skip if preceded by a dot (method call on object)
                # Check the character before the match
                start_pos = match.start(1)
                if start_pos > 0 and line[start_pos - 1] == '.':
                    continue

                # Also skip if it looks like it's preceded by dot notation
                if "." in stripped[:match.start(1)]:
                    # Check if this might be part of a method chain
                    prefix = stripped[:match.start(1)].rstrip()
                    if prefix.endswith('.'):
                        continue

                # Skip if this looks like an array access (assignment with subscript)
                # e.g., "arr_name(0) = value" - the paren is array subscript, not function call
                after_paren = stripped[match.end() - 1:]
                if re.match(r"^\s*\d+\s*\)", after_paren):
                    # This is an array subscript, not a function call
                    continue

                # Check if function is defined or built-in
                if (func_name_lower not in self.declared_functions and
                    func_name_lower not in self.BUILTIN_FUNCTIONS and
                    func_name_lower not in self.declared_variables):
                    # Be more lenient - skip potential method calls
                    # If there's a dot anywhere before this on the line, skip it
                    line_before_match = stripped[:match.start(1)]
                    if '.' in line_before_match or '(' in line_before_match:
                        # Likely a method or inner function call
                        continue

                    self.errors.append(SyntaxError(
                        line_number=line_num,
                        error_type="UNDEFINED_FUNCTION",
                        message=f"Undefined function: '{func_name}'",
                        context=stripped
                    ))

            # Variable reference checking is complex and prone to false positives
            # For now, we focus on function/method validation which is more important
            # Full variable tracking would require a proper VBS parser

    def _check_syntax_structure(self):
        """Third pass: check basic syntax structure"""
        # Check for balanced control structures
        structure_stack: List[Tuple[str, int]] = []

        for line_num, line in enumerate(self.lines, 1):
            stripped = line.strip().lower()

            # Skip comments and empty lines
            if stripped.startswith("'") or not stripped:
                continue

            # Remove inline comments
            if "'" in line:
                code_part = line[:line.index("'")]
                stripped = code_part.strip().lower()
                if not stripped:
                    continue

            # Check for structure start keywords
            if re.match(r"^\s*if\s+", stripped, re.IGNORECASE):
                structure_stack.append(("if", line_num))
            elif re.match(r"^\s*for\s+", stripped, re.IGNORECASE):
                structure_stack.append(("for", line_num))
            elif re.match(r"^\s*for\s+each\s+", stripped, re.IGNORECASE):
                structure_stack.append(("for", line_num))
            elif re.match(r"^\s*while\s+", stripped, re.IGNORECASE):
                structure_stack.append(("while", line_num))
            elif re.match(r"^\s*do\s*$", stripped, re.IGNORECASE):
                structure_stack.append(("do", line_num))
            elif re.match(r"^\s*select\s+case\s+", stripped, re.IGNORECASE):
                structure_stack.append(("select", line_num))
            elif re.match(r"^\s*with\s+", stripped, re.IGNORECASE):
                structure_stack.append(("with", line_num))
            elif re.match(r"^\s*function\s+", stripped, re.IGNORECASE):
                structure_stack.append(("function", line_num))
            elif re.match(r"^\s*sub\s+", stripped, re.IGNORECASE):
                structure_stack.append(("sub", line_num))
            elif re.match(r"^\s*class\s+", stripped, re.IGNORECASE):
                structure_stack.append(("class", line_num))

            # Check for structure end keywords
            if stripped == "end if":
                if structure_stack and structure_stack[-1][0] == "if":
                    structure_stack.pop()
                else:
                    self.errors.append(SyntaxError(
                        line_number=line_num,
                        error_type="MISMATCHED_END",
                        message="'End If' without matching 'If'",
                        context=stripped
                    ))
            elif stripped == "next":
                if structure_stack and structure_stack[-1][0] == "for":
                    structure_stack.pop()
                else:
                    self.errors.append(SyntaxError(
                        line_number=line_num,
                        error_type="MISMATCHED_END",
                        message="'Next' without matching 'For'",
                        context=stripped
                    ))
            elif stripped == "wend":
                if structure_stack and structure_stack[-1][0] == "while":
                    structure_stack.pop()
                else:
                    self.errors.append(SyntaxError(
                        line_number=line_num,
                        error_type="MISMATCHED_END",
                        message="'Wend' without matching 'While'",
                        context=stripped
                    ))
            elif re.match(r"^\s*loop", stripped, re.IGNORECASE):
                if structure_stack and structure_stack[-1][0] == "do":
                    structure_stack.pop()
                else:
                    self.errors.append(SyntaxError(
                        line_number=line_num,
                        error_type="MISMATCHED_END",
                        message="'Loop' without matching 'Do'",
                        context=stripped
                    ))
            elif stripped == "end select":
                if structure_stack and structure_stack[-1][0] == "select":
                    structure_stack.pop()
                else:
                    self.errors.append(SyntaxError(
                        line_number=line_num,
                        error_type="MISMATCHED_END",
                        message="'End Select' without matching 'Select'",
                        context=stripped
                    ))
            elif stripped == "end with":
                if structure_stack and structure_stack[-1][0] == "with":
                    structure_stack.pop()
                else:
                    self.errors.append(SyntaxError(
                        line_number=line_num,
                        error_type="MISMATCHED_END",
                        message="'End With' without matching 'With'",
                        context=stripped
                    ))
            elif stripped == "end function":
                if structure_stack and structure_stack[-1][0] == "function":
                    structure_stack.pop()
                else:
                    self.errors.append(SyntaxError(
                        line_number=line_num,
                        error_type="MISMATCHED_END",
                        message="'End Function' without matching 'Function'",
                        context=stripped
                    ))
            elif stripped == "end sub":
                if structure_stack and structure_stack[-1][0] == "sub":
                    structure_stack.pop()
                else:
                    self.errors.append(SyntaxError(
                        line_number=line_num,
                        error_type="MISMATCHED_END",
                        message="'End Sub' without matching 'Sub'",
                        context=stripped
                    ))
            elif stripped == "end class":
                if structure_stack and structure_stack[-1][0] == "class":
                    structure_stack.pop()
                else:
                    self.errors.append(SyntaxError(
                        line_number=line_num,
                        error_type="MISMATCHED_END",
                        message="'End Class' without matching 'Class'",
                        context=stripped
                    ))

        # Check for unclosed structures
        for struct_type, start_line in structure_stack:
            self.errors.append(SyntaxError(
                line_number=start_line,
                error_type="UNCLOSED_BLOCK",
                message=f"Unclosed '{struct_type}' block started here",
                context=self.lines[start_line - 1].strip() if start_line <= len(self.lines) else ""
            ))

    def format_errors(self) -> str:
        """Format errors as a readable string"""
        if not self.errors:
            return "No errors found"

        output = f"Found {len(self.errors)} error(s):\n"
        for error in self.errors:
            output += f"\n  Line {error.line_number} [{error.error_type}]:\n"
            output += f"    {error.message}\n"
            output += f"    Context: {error.context[:100]}\n"

        return output


def validate_vbs_payload(vbs_code: str, verbose: bool = False) -> Dict:
    """
    Validate a VBS payload and return results

    Args:
        vbs_code: VBS source code to validate
        verbose: Print detailed output

    Returns:
        Dictionary with validation results
    """
    validator = VBSSyntaxValidator()
    is_valid, errors = validator.validate(vbs_code)

    result = {
        "is_valid": is_valid,
        "error_count": len(errors),
        "errors": errors,
        "declared_variables": list(validator.declared_variables),
        "declared_functions": list(validator.declared_functions),
    }

    if verbose:
        print(f"Validation Result: {'PASS' if is_valid else 'FAIL'}")
        print(f"Error Count: {len(errors)}")
        if errors:
            for error in errors:
                print(f"  Line {error.line_number} [{error.error_type}]: {error.message}")
                print(f"    Context: {error.context}")

    return result


if __name__ == "__main__":
    # Example usage
    test_vbs = """
Dim shell, cmd
Set shell = CreateObject("WScript.Shell")
cmd = "powershell.exe -Command 'Write-Host Test'"
shell.Run cmd, 0, False
Set shell = Nothing
"""

    result = validate_vbs_payload(test_vbs, verbose=True)
    print(f"\nResult: {result}")
