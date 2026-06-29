# Environment Variable Storage Scopes - Quick Reference Guide

## At a Glance

| Aspect | PROCESS | USER | SYSTEM |
|--------|---------|------|--------|
| **Storage** | Memory | Registry/File | Registry/etc |
| **Persistence** | Session only | Permanent | Permanent |
| **Visibility** | Current PID | Current user | All users |
| **Privileges** | None | None | Admin/Root |
| **Detection Risk** | Minimal | Moderate | High |
| **Recommended** | YES | YES | NO |

---

## PROCESS Scope Quick Start

### When to Use
- Temporary payload staging
- Single process execution
- Command injection scenarios
- No persistence needed

### Key Storage Locations
```
Memory: process.env (heap/stack)
Lifetime: Current process execution
Cleanup: Automatic on exit
```

### Quick Implementation
```javascript
// Write
process.env.PAYLOAD_0 = 'encoded_data_chunk_1';
process.env.PAYLOAD_1 = 'encoded_data_chunk_2';

// Read
const chunk1 = process.env.PAYLOAD_0;
const chunk2 = process.env.PAYLOAD_1;

// Cleanup (auto)
// Process exit → automatic cleanup
```

### Advantages
- No filesystem/registry writes
- Invisible to external tools
- Fastest access
- Complete cleanup on exit

### Disadvantages
- Lost on process termination
- Limited to single process context

---

## USER Scope Quick Start

### When to Use
- User-level persistence needed
- Configuration storage
- Cross-process payload access
- Single-user malware

### Key Storage Locations

**Windows:**
```
Registry: HKEY_CURRENT_USER\Environment
Command: reg query HKEY_CURRENT_USER\Environment
Detection: Registry monitoring, profiling
```

**Unix/Linux:**
```
Files: ~/.bashrc, ~/.zshrc, ~/.profile
Command: cat ~/.bashrc | grep VAR_NAME
Detection: File inspection, audit logs
```

### Quick Implementation (Windows Registry)

```javascript
// Write
const regKey = new Winreg({
  hive: Winreg.HKEY_CURRENT_USER,
  key: '\\Environment',
});
regKey.set('PAYLOAD_0', Winreg.REG_SZ, 'encoded_data', callback);

// Read
regKey.get('PAYLOAD_0', (err, item) => {
  const value = item.value;
});

// Cleanup
regKey.remove('PAYLOAD_0', callback);
```

### Quick Implementation (Bash/Shell RC)

```bash
# Write
echo "export PAYLOAD_0='encoded_data'" >> ~/.bashrc

# Read
source ~/.bashrc
echo $PAYLOAD_0

# Cleanup
sed -i '/PAYLOAD_0/d' ~/.bashrc
```

### Advantages
- Survives process/session restart
- Accessible from multiple processes
- User-level integration

### Disadvantages
- Detectable via registry/file inspection
- Requires manual cleanup
- Audited on some systems

---

## SYSTEM Scope Quick Start

### When to Use
- **NOT RECOMMENDED** in most scenarios
- Only when cross-user visibility required
- High-privilege environments with coverage

### Key Storage Locations

**Windows:**
```
Registry: HKEY_LOCAL_MACHINE\System\CurrentControlSet\Control\Session Manager\Environment
Privilege: Administrator required
Detection: System audit logs, EDR monitoring
```

**Unix/Linux:**
```
Files: /etc/environment, /etc/profile.d/
Privilege: sudo/root required
Detection: System-wide auditing
```

### Why Not Recommended
- Requires administrative privileges
- Highly visible to administrators
- Monitored by EDR/security solutions
- Creates extensive forensic evidence
- Easy to discover during inspections
- System-wide audit logs
- High risk of detection

### If You Must Use System Scope
```javascript
// 1. Check admin privileges
const isAdmin = await checkAdminPrivileges();
if (!isAdmin) throw new Error('Admin required');

// 2. Write with extreme caution
const regKey = new Winreg({
  hive: Winreg.HKEY_LOCAL_MACHINE,
  key: '\\System\\CurrentControlSet\\Control\\Session Manager\\Environment',
});

// 3. Implement immediate cleanup
await cleanupSystemRegistry(payloadId);

// 4. Monitor for detection
watchForSecurityAlerts();
```

---

## Scope Selection Decision Tree

```
START
  |
  v
Do you need persistence?
  |
  +-- NO --> Use PROCESS Scope
  |           (fastest, cleanest, auto-cleanup)
  |
  +-- YES --> Check admin privileges
              |
              +-- YES --> Use USER Scope (safer than SYSTEM)
              |           (avoid SYSTEM scope entirely)
              |
              +-- NO --> Use USER Scope if available
                         Otherwise fall back to PROCESS
```

---

## Payload Encoding Reference

### Size Overhead

| Encoding | Overhead | Use Case |
|----------|----------|----------|
| Base64 | +33% | Maximum compatibility |
| Hex | +100% | Direct encoding |
| Multi-layer | +300%+ | Maximum obfuscation |

### Quick Encoding

```javascript
// Base64
const b64 = Buffer.from(payload).toString('base64');
const orig = Buffer.from(b64, 'base64').toString();

// Hex
const hex = Buffer.from(payload).toString('hex');
const orig = Buffer.from(hex, 'hex').toString();
```

---

## Retrieval Fallback Strategies

When standard naming fails, try these alternatives:

1. **Standard**: `PREFIX_0`, `PREFIX_1`
2. **Double Underscore**: `PREFIX__0`, `PREFIX__1`
3. **Chunk Naming**: `PREFIX_CHUNK_0`, `PREFIX_CHUNK_1`
4. **Data Prefixed**: `PREFIX_DATA_0`, `PREFIX_DATA_1`
5. **No Separator**: `PREFIX0`, `PREFIX1`
6. **Hex Index**: `PREFIX_0x0`, `PREFIX_0x1`
7. **Legacy**: `XPREFIX_DATA_CHUNK_0`
8. **Abbreviated**: `P_0`, `P_1` (first letter)
9. **Windows Format**: `PREFIX_VAR_0`, `PREFIX_VAR_1`
10. **Packed Format**: `PREFIXDATA_0`, `PREFIXDATA_1`

---

## Cleanup Checklist

### PROCESS Scope
- [x] Auto cleanup on exit (no action needed)
- [x] Optional: Manual cleanup before exit

### USER Scope
- [ ] Stop all running processes using variables
- [ ] Delete registry keys (Windows) or RC entries (Unix)
- [ ] Reload shell environment
- [ ] Verify removal: `reg query HKEY_CURRENT_USER\Environment` (Windows)
- [ ] Verify removal: `echo $VAR_NAME` returns empty (Unix)

### SYSTEM Scope
- [ ] Obtain admin/root access
- [ ] Delete registry keys (Windows) or /etc/environment entries (Unix)
- [ ] Restart affected services
- [ ] Monitor for security alerts
- [ ] Check audit logs

---

## Detection Vectors

### PROCESS Scope Detection
- Memory inspection (debugger, memory dump)
- Process listing (if variables exposed)
- Runtime analysis
- **Risk Level: LOW**

### USER Scope Detection
- Registry monitoring (Windows Defender, EDR)
- RC file inspection during profile audit
- System enumeration scripts
- Account analysis tools
- **Risk Level: MODERATE**

### SYSTEM Scope Detection
- System-wide registry monitoring (automatic)
- /etc/environment parsing (automatic)
- Security Information and Event Management (SIEM)
- EDR solutions (very high detection probability)
- Admin review of system variables
- **Risk Level: HIGH** (not recommended)

---

## Performance Notes

### Access Speed
```
PROCESS: O(1) - Memory lookup only
USER:    O(1) - Registry/file cached access
SYSTEM:  O(1) - Registry/file cached access
```

### Startup Time Impact
```
PROCESS: None (in-memory only)
USER:    <10ms (shell initialization)
SYSTEM:  <10ms (system startup)
```

### Cleanup Time
```
PROCESS: <1ms (automatic)
USER:    10-50ms (registry/file ops)
SYSTEM:  50-200ms (admin ops, event logs)
```

---

## Platform-Specific Notes

### Windows
- **Registry Path**: `HKEY_CURRENT_USER\Environment` (USER)
- **Registry Path**: `HKEY_LOCAL_MACHINE\System\...\Environment` (SYSTEM)
- **Max Value Size**: 32,767 characters (standard strings)
- **Detection Tools**: Process Hacker, Registry Editor, EDR solutions

### Linux/Unix
- **Files**: `~/.bashrc`, `~/.zshrc`, `/etc/environment`, `/etc/profile.d/`
- **Detection Tools**: `grep`, `cat`, `env`, audit logs, EDR

### macOS
- **Files**: `~/.bash_profile`, `~/.zprofile`, `~/.config/fish/config.fish`
- **Plist Files**: `~/.launchd.conf` (deprecated)
- **Detection Tools**: System Preferences, audit logs

---

## Common Issues & Solutions

### Issue: Variables Not Visible After Write
**Cause**: Shell not reloaded (USER scope)
**Solution**: Run `source ~/.bashrc` (Unix) or restart shell

### Issue: Registry Write Permission Denied
**Cause**: Not running as administrator
**Solution**: Run as admin or use USER scope instead of SYSTEM

### Issue: Chunks Lost Between Processes
**Cause**: Using PROCESS scope for inter-process communication
**Solution**: Use USER or SYSTEM scope if data must survive process exit

### Issue: Detection by EDR
**Cause**: SYSTEM scope variables visible to security software
**Solution**: Use USER scope (much stealthier) or avoid persistence entirely

### Issue: Cleanup Incomplete
**Cause**: Process still running or registry locked
**Solution**: Ensure all child processes terminated before cleanup

---

## Best Practices Summary

1. **Default to PROCESS**: Use only when needed, auto-cleanup
2. **Prefer USER over SYSTEM**: USER is stealthier and doesn't require admin
3. **Avoid SYSTEM Scope**: High detection risk, not worth it in most cases
4. **Implement Fallback**: Multiple retrieval strategies for robustness
5. **Encode Properly**: Use Base64 or Hex, not raw data
6. **Clean Up**: Delete variables when done (except PROCESS which auto-cleans)
7. **Monitor Success**: Verify write and read operations
8. **Log Errors**: Track failures for debugging
9. **Test Retrieval**: Verify fallback mechanisms work
10. **Plan Exit Strategy**: Know how to clean up quickly if detected

---

## Configuration Template

```javascript
const scopeConfig = {
  // Scope selection
  scope: 'PROCESS', // or 'USER', avoid 'SYSTEM'
  
  // Encoding
  encoding: 'hex', // or 'base64'
  
  // Chunking
  chunkSize: 200, // bytes per variable
  prefix: 'SC', // variable name prefix
  
  // Behavior
  verbose: false, // logging
  autoCleanup: true, // auto cleanup on exit (PROCESS only)
  validateOnRead: true, // verify payload integrity
  
  // Fallback
  useFallbackPaths: true, // try alternative naming
  maxRetries: 3, // retry failed operations
};
```

---

## Summary Table

| Task | PROCESS | USER | SYSTEM |
|------|---------|------|--------|
| Write payload | ✓ Simple | ✓ Moderate | ✗ Complex |
| Persist | ✗ No | ✓ Yes | ✓ Yes |
| Easy cleanup | ✓ Auto | ✗ Manual | ✗ Manual |
| Stealthy | ✓ High | ~ Medium | ✗ Low |
| Inter-process | ✗ Child only | ✓ Yes | ✓ Yes |
| No privileges | ✓ Yes | ✓ Yes | ✗ No |
| Recommended | ✓ YES | ✓ YES | ✗ NO |

---

## Additional Resources

- Full documentation: `ENV_VAR_STORAGE_SCOPE_DOCUMENTATION.md`
- Implementation examples: `env-var-obfuscator.js`, `env-var-retrieval-handler.js`
- Cleanup utilities: `env-var-cleanup-handler.js`
- Environment naming: `ENV_VAR_NAMING_STRATEGY_GUIDE.md`

---

Generated: 2025 | Scope Documentation | Technical Reference
