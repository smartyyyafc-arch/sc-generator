#!/bin/bash

# Command Obfuscation Utility
# Uses environment variables and string concatenation to obfuscate commands

# ============================================================================
# Helper Functions
# ============================================================================

# Obfuscate a string using character codes and environment variables
obfuscate_string() {
    local str="$1"
    local result=""
    local i

    for ((i = 0; i < ${#str}; i++)); do
        local char="${str:$i:1}"
        local code=$(printf '%d' "'$char")
        result+="\\x$(printf '%x' $code)"
    done

    echo "$result"
}

# Decode obfuscated string
decode_obfuscated() {
    local obf="$1"
    printf "$obf"
}

# ============================================================================
# Environment Variable Based Obfuscation
# ============================================================================

# Setup obfuscation variables
setup_obfuscation_env() {
    # Base building blocks stored in env variables
    export OBF_E="e"
    export OBF_C="c"
    export OBF_H="h"
    export OBF_O="o"
    export OBF_L="l"
    export OBF_S="s"
    export OBF_SPACE=" "
    export OBF_DASH="-"
    export OBF_SLASH="/"

    # Common command fragments
    export OBF_CMD_ECHO="echo"
    export OBF_CMD_LS="ls"
    export OBF_CMD_CAT="cat"
    export OBF_CMD_GREP="grep"
    export OBF_CMD_SED="sed"
    export OBF_CMD_AWK="awk"
    export OBF_CMD_BASH="bash"
    export OBF_CMD_SH="sh"

    # Obfuscated flags
    export OBF_FLAG_LA="${OBF_DASH}la"
    export OBF_FLAG_LH="${OBF_DASH}lh"
    export OBF_FLAG_R="${OBF_DASH}r"
    export OBF_FLAG_I="${OBF_DASH}i"
    export OBF_FLAG_N="${OBF_DASH}n"
}

# Build command with concatenation
build_obfuscated_cmd() {
    local parts=("$@")
    local cmd=""

    for part in "${parts[@]}"; do
        if [[ -v "OBF_$part" ]]; then
            cmd+="${!OBF_$part}"
        else
            cmd+="$part"
        fi
        cmd+=" "
    done

    echo "${cmd% }"
}

# ============================================================================
# Hex Encoding Obfuscation
# ============================================================================

# Encode command to hex
hex_encode_cmd() {
    local cmd="$1"
    xxd -p <<< "$cmd" | tr -d '\n'
}

# Decode and execute hex-encoded command
hex_decode_exec() {
    local hex="$1"
    # Pad if necessary
    if (( ${#hex} % 2 )); then
        hex="0$hex"
    fi
    xxd -r -p <<< "$hex"
}

# ============================================================================
# Reverse String Obfuscation
# ============================================================================

# Reverse a string
reverse_string() {
    local str="$1"
    local reversed=""
    local i

    for ((i = ${#str} - 1; i >= 0; i--)); do
        reversed+="${str:$i:1}"
    done

    echo "$reversed"
}

# Build and reverse command
build_reversed_cmd() {
    local parts=("$@")
    local cmd=""

    for part in "${parts[@]}"; do
        cmd+="$part "
    done

    reverse_string "${cmd% }"
}

# Execute reversed command
exec_reversed_cmd() {
    local rev_cmd="$1"
    local original=$(reverse_string "$rev_cmd")
    eval "$original"
}

# ============================================================================
# ROT13 Style Obfuscation
# ============================================================================

# ROT13 encode
rot13_encode() {
    local str="$1"
    echo "$str" | tr 'A-Za-z' 'N-ZA-Mn-za-m'
}

# ROT13 decode
rot13_decode() {
    local str="$1"
    echo "$str" | tr 'A-Za-z' 'N-ZA-Mn-za-m'
}

# ============================================================================
# Base64 Obfuscation
# ============================================================================

# Base64 encode command
b64_encode_cmd() {
    local cmd="$1"
    echo -n "$cmd" | base64
}

# Base64 decode and execute
b64_decode_exec() {
    local b64="$1"
    echo "$b64" | base64 -d
}

# ============================================================================
# Dynamic Command Construction
# ============================================================================

# Build command dynamically from parts
dynamic_cmd_build() {
    local IFS=$'\n'
    local cmd_parts=()

    # Read parts from arguments or stdin
    while IFS= read -r part; do
        cmd_parts+=("$part")
    done < <(printf '%s\n' "$@")

    # Shuffle and reconstruct
    printf '%s ' "${cmd_parts[@]}"
}

# ============================================================================
# Practical Examples
# ============================================================================

# Example 1: Obfuscate 'ls -la /tmp'
example_obfuscate_ls() {
    setup_obfuscation_env

    local cmd=$(build_obfuscated_cmd "OBF_CMD_LS" "OBF_FLAG_LA" "/tmp")
    echo "Obfuscated: $cmd"
    echo "Executing: "
    eval "$cmd"
}

# Example 2: Hex encode a command
example_hex_encode() {
    local cmd="echo 'Hello, World!'"
    local encoded=$(hex_encode_cmd "$cmd")
    echo "Original: $cmd"
    echo "Encoded: $encoded"
    echo "Decoded:"
    hex_decode_exec "$encoded"
}

# Example 3: Reverse string obfuscation
example_reverse_cmd() {
    local cmd="echo secret_message"
    local reversed=$(build_reversed_cmd $cmd)
    echo "Original: $cmd"
    echo "Reversed: $reversed"
    echo "Executed:"
    exec_reversed_cmd "$reversed"
}

# Example 4: ROT13 encoding
example_rot13() {
    local cmd="ls -la /etc/passwd"
    local encoded=$(rot13_encode "$cmd")
    echo "Original: $cmd"
    echo "ROT13: $encoded"
    echo "Decoded:"
    rot13_decode "$encoded"
}

# Example 5: Base64 encoding
example_base64() {
    local cmd="whoami"
    local encoded=$(b64_encode_cmd "$cmd")
    echo "Original: $cmd"
    echo "Base64: $encoded"
    echo "Decoded:"
    b64_decode_exec "$encoded"
}

# ============================================================================
# Advanced: Multi-layer Obfuscation
# ============================================================================

# Apply multiple obfuscation layers
multi_layer_obfuscate() {
    local cmd="$1"
    local layer1=$(hex_encode_cmd "$cmd")
    local layer2=$(b64_encode_cmd "$layer1")
    echo "$layer2"
}

# Decode multi-layer obfuscation
multi_layer_decode() {
    local obf="$1"
    local layer1=$(b64_decode_exec "$obf")
    local layer2=$(hex_decode_exec "$layer1")
    echo "$layer2"
}

# ============================================================================
# Main Menu
# ============================================================================

show_menu() {
    cat << EOF
=== Command Obfuscation Utility ===

1. Setup Environment Variables
2. Build Obfuscated Command
3. Hex Encode Command
4. Hex Decode Command
5. Reverse String Command
6. Execute Reversed Command
7. ROT13 Encode
8. ROT13 Decode
9. Base64 Encode
10. Base64 Decode
11. Multi-layer Obfuscation (Hex + Base64)
12. Multi-layer Decode
13. Run Examples

Examples:
  ./obfuscator.sh example_obfuscate_ls
  ./obfuscator.sh hex_encode_cmd "ls -la"
  ./obfuscator.sh b64_encode_cmd "whoami"
  ./obfuscator.sh multi_layer_obfuscate "cat /etc/passwd"

EOF
}

# ============================================================================
# Main Execution
# ============================================================================

if [[ $# -eq 0 ]]; then
    show_menu
elif [[ "$1" == "examples" ]]; then
    echo "=== Example 1: Environment Variable Obfuscation ==="
    example_obfuscate_ls
    echo ""
    echo "=== Example 2: Hex Encoding ==="
    example_hex_encode
    echo ""
    echo "=== Example 3: Reverse String ==="
    example_reverse_cmd
    echo ""
    echo "=== Example 4: ROT13 Encoding ==="
    example_rot13
    echo ""
    echo "=== Example 5: Base64 Encoding ==="
    example_base64
else
    # Direct function call
    "$@"
fi
