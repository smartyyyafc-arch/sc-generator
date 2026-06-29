# Registry Hives - Comprehensive Comparison

## Quick Reference

| Hive | Class | Scope | Access | Best For |
|------|-------|-------|--------|----------|
| HKLM Software | `SoftwareHiveStorage` | All Users | Admin Write | Global settings |
| HKEY_CURRENT_USER | `CurrentUserHiveStorage` | Single User | User RW | User preferences |
| CurrentVersion | `CurrentVersionHiveStorage` | System | Admin Write | OS settings |
| System | `SystemHiveStorage` | System | Admin Only | Services/Drivers |

## Detailed Comparison

### 1. HKEY_LOCAL_MACHINE\Software

#### Implementation
```javascript
new SoftwareHiveStorage('MyApp')
// Path: HKEY_LOCAL_MACHINE\Software\MyApp
```

#### Characteristics
- **Visibility**: All users see the same values
- **Persistence**: Survives user logoff
- **Elevation**: Admin required to write
- **Scope**: Computer-wide settings
- **Registry Size Impact**: Global registry growth

#### Use Cases
```javascript
// Application version
await storage.write('Version', '2.1.0');

// Company/publisher info
await storage.write('Publisher', 'Acme Corp');

// Installation path (for uninstallers)
await storage.write('InstallPath', 'C:\\Program Files\\MyApp');

// License information
await storage.write('LicenseKey', 'ABC123-DEF456');

// Feature availability
await storage.write('MaxConnections', '100');
```

#### Permissions
- Read: Standard user
- Write: Administrator
- Delete: Administrator
- Modify: Administrator

#### Advantages
- Shared across all users
- Persistent and reliable
- Standard location for software registry
- Easy to uninstall (clear one location)

#### Disadvantages
- Requires elevation to modify
- Single point of configuration
- Can't have user-specific overrides
- Registry access can be audited

### 2. HKEY_CURRENT_USER

#### Implementation
```javascript
new CurrentUserHiveStorage('Software\\MyApp')
// Path: HKEY_CURRENT_USER\Software\MyApp
```

#### Characteristics
- **Visibility**: Only current user sees values
- **Persistence**: Lost on user deletion
- **Elevation**: User can read/write own hive
- **Scope**: User-specific settings
- **Registry Size Impact**: Per-user growth

#### Use Cases
```javascript
// User theme preference
await userStorage.write('Theme', 'Dark');

// UI customization
await userStorage.write('FontSize', '14');
await userStorage.write('ColorScheme', 'HighContrast');

// Window state
await userStorage.write('LastWindowWidth', '1920');
await userStorage.write('LastWindowHeight', '1080');

// User preferences
await userStorage.write('Language', 'en-US');
await userStorage.write('AutoSave', 'true');

// Recent items
await userStorage.write('RecentFile1', 'C:\\Documents\\report.txt');
```

#### Permissions
- Read: User can read own hive
- Write: User can modify own settings
- Delete: User can delete own settings
- Modify: User can change own values

#### Advantages
- No elevation required
- User isolation (each user has own settings)
- Faster access (no ACL checks)
- Privacy-friendly (settings not visible to others)

#### Disadvantages
- Not shared across users
- Lost when user is deleted
- Each user needs separate configuration
- No global override possible

### 3. HKEY_LOCAL_MACHINE\Software\Microsoft\Windows\CurrentVersion

#### Implementation
```javascript
new CurrentVersionHiveStorage('MyApp')
// Path: HKEY_LOCAL_MACHINE\Software\Microsoft\Windows\CurrentVersion\MyApp
```

#### Characteristics
- **Visibility**: System-wide visibility
- **Persistence**: Tied to OS installation
- **Elevation**: Admin required to write
- **Scope**: OS-level settings
- **Registry Size Impact**: System registry growth

#### Standard Values Available
```javascript
// Read existing OS values
const versionStorage = new CurrentVersionHiveStorage('');
const version = await versionStorage.read('CurrentVersion');  // e.g., "10.0"
const build = await versionStorage.read('CurrentBuildNumber');  // e.g., "19045"
const releaseId = await versionStorage.read('ReleaseId');  // e.g., "23H2"
```

#### Use Cases
```javascript
// Minimum OS version requirement
await storage.write('MinimumWindowsVersion', '10.0');

// Supported architectures
await storage.write('SupportedArchitectures', 'x64,ARM64');

// OS-specific features
await storage.write('RequiresWin11Features', 'true');

// Compatibility mode
await storage.write('CompatibilityMode', 'Windows10');

// API level
await storage.write('MinimumAPILevel', '19041');
```

#### Permissions
- Read: Standard user
- Write: Administrator
- Delete: Administrator

#### Advantages
- Standard OS configuration location
- Already used for version detection
- Organized by OS version
- Easy to find version-specific settings

#### Disadvantages
- Requires admin rights to write
- OS-centric (not app-specific)
- Changes with OS updates
- Limited for app-specific settings

### 4. HKEY_LOCAL_MACHINE\System

#### Implementation
```javascript
new SystemHiveStorage('ControlSet001\\Services\\MyService')
// Path: HKEY_LOCAL_MACHINE\System\ControlSet001\Services\MyService
```

#### Characteristics
- **Visibility**: System administrators only
- **Persistence**: Tied to system state
- **Elevation**: System/Admin required
- **Scope**: System hardware and services
- **Registry Size Impact**: Critical system growth

#### Control Sets
- **ControlSet001**: Current control set
- **ControlSet002**: Last known good
- **CurrentControlSet**: Symbolic link to active set

#### Use Cases
```javascript
// Service configuration
await storage.write('DisplayName', 'My Service');
await storage.write('Description', 'Handles important tasks');

// Service startup type
await storage.write('Start', '2');        // 2=Automatic
await storage.write('Start', '3');        // 3=Manual
await storage.write('Start', '4');        // 4=Disabled

// Service type
await storage.write('Type', '16');        // Win32_OwnProcess
await storage.write('Type', '32');        // Win32_ShareProcess

// Error handling
await storage.write('ErrorControl', '1'); // Normal

// Service executable
await storage.write('ImagePath', 'C:\\Windows\\System32\\svc.exe');
```

#### Permissions
- Read: Administrator
- Write: Administrator only
- Delete: Administrator only
- Modify: Administrator only

#### Advantages
- Direct service control
- Load order management
- Hardware profile support
- System integration

#### Disadvantages
- Requires admin/SYSTEM
- Changes affect boot sequence
- Incorrect config can break system
- Limited to system-level configs

## Storage Variant Capabilities

### Read Operations
```
┌─────────────────┬──────────┬──────────┬─────────────┬────────┐
│ Capability      │ Software │ CurUser  │ CurVersion  │ System │
├─────────────────┼──────────┼──────────┼─────────────┼────────┤
│ Read Existing   │    ✓     │    ✓     │      ✓      │   ✓    │
│ Read Nonexistent│    ✓     │    ✓     │      ✓      │   ✓    │
│ List All Keys   │    ✓     │    ✓     │      ✓      │   ✓    │
│ Check Existence │    ✓     │    ✓     │      ✓      │   ✓    │
└─────────────────┴──────────┴──────────┴─────────────┴────────┘
```

### Write Operations
```
┌─────────────────┬──────────┬──────────┬─────────────┬────────┐
│ Capability      │ Software │ CurUser  │ CurVersion  │ System │
├─────────────────┼──────────┼──────────┼─────────────┼────────┤
│ Write Value     │  Admin   │   User   │    Admin    │  Admin │
│ Update Value    │  Admin   │   User   │    Admin    │  Admin │
│ Delete Value    │  Admin   │   User   │    Admin    │  Admin │
│ Batch Write     │  Admin   │   User   │    Admin    │  Admin │
└─────────────────┴──────────┴──────────┴─────────────┴────────┘
```

## Decision Matrix

### Choose HKLM Software When:
- Settings apply to all users
- Need persistent global configuration
- Application version should be stored
- License info needs computer-wide access
- Uninstall information is needed

### Choose HKEY_CURRENT_USER When:
- Settings vary per user
- User preferences (theme, language)
- No elevation available
- User privacy is important
- Per-user customization needed

### Choose CurrentVersion When:
- Settings relate to Windows version
- OS compatibility checking
- Need to query OS version
- Installation media info needed
- System-level feature detection

### Choose System When:
- Configuring services
- Hardware profile management
- Boot configuration
- Driver settings
- System initialization

## Migration Paths

### Software → CurrentUser
```javascript
async function migrateToUserHive(key, value) {
  const softwareStorage = new SoftwareHiveStorage('MyApp');
  const userStorage = new CurrentUserHiveStorage('Software\\MyApp');
  
  const value = await softwareStorage.read(key);
  if (value !== null) {
    await userStorage.write(key, value);
    // Option: delete from software hive
    // await softwareStorage.delete(key);
  }
}
```

### CurrentUser → Software
```javascript
async function migrateToGlobalHive(key) {
  const userStorage = new CurrentUserHiveStorage('Software\\MyApp');
  const softwareStorage = new SoftwareHiveStorage('MyApp');
  
  const value = await userStorage.read(key);
  if (value !== null) {
    await softwareStorage.write(key, value);
  }
}
```

## Multi-Hive Coordination

### Write to All Hives
```javascript
const manager = new MultiHiveRegistryManager('MyApp');
await manager.writeToAllHives('ConfigKey', 'value');
// Writes to: Software, CurrentUser, CurrentVersion, System
```

### Read from First Available
```javascript
const result = await manager.readFromFirstAvailable('ConfigKey');
// Returns: { value: 'found_value', hive: 'software' }
```

### Priority Order
Default read priority: Software → CurrentUser → CurrentVersion → System

## Performance Characteristics

### Read Performance
1. **HKEY_CURRENT_USER**: Fastest (no elevation check)
2. **HKLM Software**: Medium (single ACL check)
3. **CurrentVersion**: Medium (nested path)
4. **System**: Slowest (system-critical, full validation)

### Write Performance
1. **HKEY_CURRENT_USER**: Fastest (no elevation needed)
2. **HKLM variants**: Slower (requires elevation, ACL write)
3. **System**: Slowest (system validation)

### Caching Strategy
```javascript
// Cache frequently accessed values
const cache = {};

async function getCachedValue(storage, key) {
  if (!cache[key]) {
    cache[key] = await storage.read(key);
  }
  return cache[key];
}
```

## Error Scenarios

| Scenario | Software | CurUser | CurVersion | System |
|----------|----------|---------|------------|--------|
| Insufficient perms | Throw | Null | Throw | Throw |
| Key not found | Null | Null | Null | Null |
| Corrupted path | Throw | Throw | Throw | Throw |
| Elevation required | Error | OK | Error | Error |

## Best Practices

1. **Choose Right Hive First**: Don't migrate later
2. **Minimize Elevation**: Use CurrentUser when possible
3. **Handle Errors Gracefully**: Null returns instead of exceptions
4. **Prefer Read Over Write**: Reduce lock contention
5. **Batch Related Values**: Store together in same hive
6. **Document Paths**: Comment your registry paths
7. **Test Permissions**: Verify expected access level
8. **Use Factory Pattern**: Simplify hive selection

## Example: Complete Application

```javascript
// Global app config (admin, all users)
const globalConfig = new SoftwareHiveStorage('MyApp');

// User preferences (no admin needed)
const userPrefs = new CurrentUserHiveStorage('Software\\MyApp');

// OS compatibility settings
const osSettings = new CurrentVersionHiveStorage('MyApp');

// Service configuration (if applicable)
const serviceConfig = new SystemHiveStorage('ControlSet001\\Services\\MyApp');

async function initializeApplication() {
  // Store global version
  await globalConfig.write('Version', '2.1.0');

  // Store user theme
  await userPrefs.write('Theme', 'Dark');

  // Store OS requirements
  await osSettings.write('MinOS', '10.0');

  // If service exists, configure it
  try {
    await serviceConfig.write('Start', '2'); // Automatic
  } catch {
    // Not a service, skip
  }
}
```

## Registry Cleanup

```javascript
async function uninstallApplication(appName) {
  // Global settings
  const software = new SoftwareHiveStorage(appName);
  for (const key of await software.listKeys()) {
    await software.delete(key);
  }

  // User settings (current user only)
  const currentUser = new CurrentUserHiveStorage(`Software\\${appName}`);
  for (const key of await currentUser.listKeys()) {
    await currentUser.delete(key);
  }

  // OS settings
  const version = new CurrentVersionHiveStorage(appName);
  for (const key of await version.listKeys()) {
    await version.delete(key);
  }

  console.log(`Uninstalled ${appName}`);
}
```
