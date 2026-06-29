# Registry Storage Variants - Quick Reference Card

## The 4 Hive Variants at a Glance

```
┌──────────────────────────────────────────────────────────────────┐
│                    HIVE SELECTION CHEATSHEET                     │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  SOFTWARE HIVE (SoftwareHiveStorage)                             │
│  ├─ Path: HKLM\Software\MyApp                                    │
│  ├─ Scope: All users (global)                                    │
│  ├─ Access: Admin to write, User to read                         │
│  ├─ Best for: App version, license, features                    │
│  └─ Example: await storage.write('Version', '1.0.0')            │
│                                                                   │
│  CURRENT USER HIVE (CurrentUserHiveStorage)                      │
│  ├─ Path: HKCU\Software\MyApp                                    │
│  ├─ Scope: Single user only                                      │
│  ├─ Access: User can read/write own settings                    │
│  ├─ Best for: Themes, preferences, UI state                     │
│  └─ Example: await storage.write('Theme', 'Dark')               │
│                                                                   │
│  CURRENT VERSION HIVE (CurrentVersionHiveStorage)                │
│  ├─ Path: HKLM\Software\Microsoft\Windows\CurrentVersion\MyApp  │
│  ├─ Scope: System-wide OS settings                               │
│  ├─ Access: Admin to write, User to read                         │
│  ├─ Best for: OS compatibility, version detection                │
│  └─ Example: await storage.write('MinOS', '10.0')               │
│                                                                   │
│  SYSTEM HIVE (SystemHiveStorage)                                 │
│  ├─ Path: HKLM\System\ControlSet001\Services\MyApp               │
│  ├─ Scope: System-critical only                                  │
│  ├─ Access: Admin/System only                                    │
│  ├─ Best for: Services, drivers, boot config                     │
│  └─ Example: await storage.write('Start', '2')                  │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘
```

## Common Code Patterns

### Pattern 1: Single Hive Read/Write
```javascript
const { SoftwareHiveStorage } = require('./registry-storage-variants');

const storage = new SoftwareHiveStorage('MyApp');
await storage.write('Version', '1.0.0');
const version = await storage.read('Version');
```

### Pattern 2: User Preferences
```javascript
const { CurrentUserHiveStorage } = require('./registry-storage-variants');

const userStorage = new CurrentUserHiveStorage('Software\\MyApp');
await userStorage.write('Theme', 'Dark');
await userStorage.write('Language', 'en-US');
```

### Pattern 3: Multi-Hive Manager
```javascript
const { MultiHiveRegistryManager } = require('./registry-storage-variants');

const manager = new MultiHiveRegistryManager('MyApp');
await manager.writeToAllHives('Key', 'value');
const result = await manager.readFromFirstAvailable('Key');
```

### Pattern 4: Factory Pattern
```javascript
const { RegistryStorageFactory } = require('./registry-storage-variants');

const variants = RegistryStorageFactory.createAllVariants('MyApp');
for (const [name, storage] of variants) {
  const value = await storage.read('SomeKey');
}
```

### Pattern 5: Try/Catch with Null Check
```javascript
const value = await storage.read('Key');
if (value !== null) {
  console.log('Found:', value);
} else {
  console.log('Not found - using default');
}
```

## Method Reference

### All Storage Variants
```javascript
await storage.read(key)           // Returns: string | null
await storage.write(key, value)   // Throws: on error
await storage.delete(key)         // Throws: on error
await storage.exists(key)         // Returns: boolean
await storage.listKeys()          // Returns: string[]
```

### MultiHiveRegistryManager Only
```javascript
await manager.writeToAllHives(key, value)
await manager.readFromHive('software', key)
await manager.readFromFirstAvailable(key)  // Returns: {value, hive} | null
await manager.deleteFromAllHives(key)
manager.getStorageByHive('software')
manager.getStorages()  // Returns: {software, currentUser, currentVersion, system}
```

## Hive Selection Matrix

```
┌─────────────────────────────┬───────────┬────────────┬─────────────┐
│ Scenario                    │ Hive      │ Elevation  │ User Scope  │
├─────────────────────────────┼───────────┼────────────┼─────────────┤
│ Application version         │ Software  │ Admin      │ All         │
│ User theme preference       │ CurUser   │ None       │ Single      │
│ License key                 │ Software  │ Admin      │ All         │
│ Window size/position        │ CurUser   │ None       │ Single      │
│ Feature flags (global)      │ Software  │ Admin      │ All         │
│ Feature flags (user)        │ CurUser   │ None       │ Single      │
│ OS compatibility            │ CurVer    │ Admin      │ All         │
│ Service startup type        │ System    │ Admin      │ System      │
│ Recent files list           │ CurUser   │ None       │ Single      │
│ Installation path           │ Software  │ Admin      │ All         │
│ User language setting       │ CurUser   │ None       │ Single      │
│ Minimum OS version          │ CurVer    │ Admin      │ All         │
└─────────────────────────────┴───────────┴────────────┴─────────────┘
```

## Quick Decision Tree

```
START
 │
 ├─ Is this a user preference? 
 │  YES → Use HKEY_CURRENT_USER
 │  NO  ↓
 │
 ├─ Does admin need write access?
 │  YES ↓
 │  NO  → Use HKEY_CURRENT_USER (if not service)
 │
 ├─ Is this a Windows service?
 │  YES → Use SYSTEM HIVE
 │  NO  ↓
 │
 ├─ Is this OS-specific?
 │  YES → Use CURRENT VERSION
 │  NO  ↓
 │
 └─ Use SOFTWARE HIVE
```

## Error Handling Quick Guide

```javascript
// Missing key (returns null, no error)
const value = await storage.read('NonExistent');
// Result: null

// Permission denied (throws error)
try {
  await storage.write('Key', 'value');
} catch (error) {
  console.error('Access denied:', error.message);
}

// Multiple hives (tolerates failures)
await manager.writeToAllHives('Key', 'value');
// May warn: "Failed to write to 2 hives"
// But won't throw exception
```

## File Locations

| File | Location | Purpose |
|------|----------|---------|
| Source (TS) | `registry-storage-variants.ts` | TypeScript implementation |
| Source (JS) | `registry-storage-variants.js` | JavaScript implementation |
| Tests | `registry-storage-variants.test.js` | Test suite |
| Examples | `registry-storage-examples.js` | 10 practical examples |
| Docs | `REGISTRY_STORAGE_VARIANTS.md` | Full documentation |
| Comparison | `REGISTRY_HIVES_COMPARISON.md` | Hive comparison guide |
| Index | `REGISTRY_STORAGE_INDEX.md` | Project index |

## Installation & Setup

```bash
# Install dependency
npm install winreg

# Import in your code
const { 
  SoftwareHiveStorage,
  CurrentUserHiveStorage,
  CurrentVersionHiveStorage,
  SystemHiveStorage,
  MultiHiveRegistryManager,
  RegistryStorageFactory 
} = require('./registry-storage-variants');

# Run tests
npm test registry-storage-variants.test.js

# Run examples
node registry-storage-examples.js
```

## Performance Notes

```
Fastest:   HKEY_CURRENT_USER   (no elevation check)
           ↓
Medium:    HKLM Software       (standard ACL)
           CURRENT VERSION
           ↓
Slowest:   SYSTEM HIVE         (system validation)
```

## Permission Requirements

```
Operation   │ Software │ CurUser │ CurVersion │ System
────────────┼──────────┼─────────┼────────────┼────────
Read        │ User     │ User    │ User       │ Admin
Write       │ Admin    │ User    │ Admin      │ Admin
Delete      │ Admin    │ User    │ Admin      │ Admin
```

## Common Mistakes to Avoid

```javascript
// WRONG: Not checking for null
const value = await storage.read('Key');
console.log(value.length);  // Can crash if null

// RIGHT: Check for null
const value = await storage.read('Key');
if (value !== null) {
  console.log(value.length);
}

// WRONG: Expecting exception for missing key
try {
  const value = await storage.read('NonExistent');
  // Will not throw - value is just null
} catch (error) {
  // This won't execute
}

// RIGHT: Use null check
const value = await storage.read('NonExistent');
const result = value ?? 'default';

// WRONG: Not elevating for admin-required operations
await software.write('Key', 'value');  // May fail silently

// RIGHT: Request elevation before write
if (isAdmin()) {
  await software.write('Key', 'value');
} else {
  console.warn('Admin privileges required');
}
```

## Real-World Example

```javascript
const { MultiHiveRegistryManager } = require('./registry-storage-variants');

// Initialize manager
const manager = new MultiHiveRegistryManager('MyApp');

// Store global version (admin required)
const softwareStorage = manager.getStorageByHive('software');
await softwareStorage.write('Version', '2.1.0');

// Store user theme (no elevation)
const userStorage = manager.getStorageByHive('currentUser');
await userStorage.write('Theme', 'Dark');

// Store OS requirements
const versionStorage = manager.getStorageByHive('currentVersion');
await versionStorage.write('MinOS', '10.0');

// Read with fallback
const result = await manager.readFromFirstAvailable('ConfigKey');
if (result) {
  console.log(`Found in ${result.hive}: ${result.value}`);
}
```

## API Cheat Sheet

```javascript
// Single variants
new SoftwareHiveStorage(subPath)
new CurrentUserHiveStorage(subPath)
new CurrentVersionHiveStorage(subPath)
new SystemHiveStorage(subPath)

// Manager
new MultiHiveRegistryManager(appName, userPath, versionPath, systemPath)

// Factory
RegistryStorageFactory.createStorage(hive, subPath)
RegistryStorageFactory.createAllVariants(appName)

// Enums
RegistryHive.HKLM_SOFTWARE
RegistryHive.HKEY_CURRENT_USER
RegistryHive.CURRENT_VERSION
RegistryHive.HKLM_SYSTEM
```

## Testing Checklist

- [ ] Can read from Software hive
- [ ] Can write to Software hive (with admin)
- [ ] Can read from CurrentUser hive
- [ ] Can write to CurrentUser hive (no admin)
- [ ] Can read from CurrentVersion hive
- [ ] Can list keys from any hive
- [ ] Handle missing keys gracefully
- [ ] Manager can write to all hives
- [ ] Manager can read from first available
- [ ] Factory creates all variants correctly

## Documentation Navigation

```
START HERE
    ↓
REGISTRY_STORAGE_INDEX.md (Quick overview)
    ↓
REGISTRY_STORAGE_VARIANTS.md (Detailed docs)
    ↓
REGISTRY_HIVES_COMPARISON.md (Deep dive)
    ↓
registry-storage-examples.js (10 examples)
    ↓
registry-storage-variants.test.js (30+ tests)
```

## Key Takeaways

1. **4 different hives** for different use cases
2. **Consistent interface** across all variants
3. **No elevation needed** for CurrentUser hive
4. **Null returns**, not exceptions, for missing keys
5. **Multi-hive manager** for coordinated operations
6. **Factory pattern** for easy creation
7. **Full error handling** built-in
8. **Async/await** throughout
9. **Production ready** with comprehensive docs
10. **30+ tests** included for quality assurance
