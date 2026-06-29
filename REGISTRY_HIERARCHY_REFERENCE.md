# Registry Storage - Key Hierarchy Reference Guide

Quick reference for common registry key hierarchies and their implementations.

## Registry Hierarchy Patterns

### Pattern 1: Standard Application Settings

```
Hive: HKEY_LOCAL_MACHINE\Software

Path Structure:
├── Vendor Name
│   └── Product Name
│       ├── Settings
│       │   ├── Version
│       │   ├── InstallDate
│       │   ├── InstallPath
│       │   └── Publisher
│       ├── Features
│       │   ├── Feature_DarkMode
│       │   ├── Feature_Analytics
│       │   └── Feature_CloudSync
│       └── Components
│           ├── Database
│           │   ├── Host
│           │   ├── Port
│           │   ├── Username
│           │   └── PoolSize
│           └── Cache
│               ├── Enabled
│               ├── Size
│               └── TTL

Example Implementation:
HKEY_LOCAL_MACHINE\Software\MyCompany\MyApplication\Settings\Version = "2.1.0"
```

**TypeScript Implementation**:

```typescript
// Application settings
const appSettings = new SoftwareHiveStorage('MyCompany\\MyApplication\\Settings');
await appSettings.write('Version', '2.1.0');

// Features
const features = new SoftwareHiveStorage('MyCompany\\MyApplication\\Features');
await features.write('Feature_DarkMode', 'true');

// Component configuration
const database = new SoftwareHiveStorage('MyCompany\\MyApplication\\Components\\Database');
await database.write('Host', 'localhost');
await database.write('Port', '5432');
```

---

### Pattern 2: User-Specific Preferences

```
Hive: HKEY_CURRENT_USER

Path Structure:
├── Software
│   └── Vendor Name
│       └── Product Name
│           ├── Preferences
│           │   ├── Theme
│           │   ├── Language
│           │   ├── TimeFormat
│           │   ├── DateFormat
│           │   └── FontSize
│           ├── History
│           │   ├── LastUsedFile
│           │   ├── LastLoginTime
│           │   └── LastLoggedInUser
│           ├── Bookmarks
│           │   ├── Bookmark_1
│           │   ├── Bookmark_2
│           │   └── Bookmark_Count
│           └── WindowState
│               ├── WindowWidth
│               ├── WindowHeight
│               ├── WindowX
│               ├── WindowY
│               └── IsMaximized

Example Implementation:
HKEY_CURRENT_USER\Software\MyCompany\MyApplication\Preferences\Theme = "Dark"
HKEY_CURRENT_USER\Software\MyCompany\MyApplication\History\LastLoginTime = "2026-06-29T10:30:00Z"
```

**TypeScript Implementation**:

```typescript
const userPreferences = new CurrentUserHiveStorage(
  'Software\\MyCompany\\MyApplication\\Preferences'
);
await userPreferences.write('Theme', 'Dark');
await userPreferences.write('Language', 'en-US');

const userHistory = new CurrentUserHiveStorage(
  'Software\\MyCompany\\MyApplication\\History'
);
await userHistory.write('LastLoginTime', new Date().toISOString());
```

---

### Pattern 3: Windows Service Configuration

```
Hive: HKEY_LOCAL_MACHINE\System

Path Structure:
├── ControlSet001
│   └── Services
│       └── ServiceName
│           ├── DisplayName
│           ├── Description
│           ├── ImagePath
│           ├── Start (Startup Type)
│           ├── Type
│           ├── ErrorControl
│           ├── DependOnService
│           ├── ObjectName
│           └── Parameters
│               ├── ServiceDll
│               ├── LogPath
│               ├── DebugEnabled
│               └── ConfigFile

Example Implementation:
HKEY_LOCAL_MACHINE\System\ControlSet001\Services\MyService\DisplayName = "My Service"
HKEY_LOCAL_MACHINE\System\ControlSet001\Services\MyService\Start = "2" (Automatic)
HKEY_LOCAL_MACHINE\System\ControlSet001\Services\MyService\Parameters\ServiceDll = "...\\MyService.dll"
```

**TypeScript Implementation**:

```typescript
const serviceConfig = new SystemHiveStorage(
  'ControlSet001\\Services\\MyService'
);
await serviceConfig.write('DisplayName', 'My Custom Service');
await serviceConfig.write('Start', '2'); // Automatic
await serviceConfig.write('ImagePath', 'C:\\Program Files\\MyService\\MyService.exe');

const serviceParams = new SystemHiveStorage(
  'ControlSet001\\Services\\MyService\\Parameters'
);
await serviceParams.write('ServiceDll', '%SystemRoot%\\System32\\MyService.dll');
```

---

### Pattern 4: Windows Version & Compatibility

```
Hive: HKEY_LOCAL_MACHINE\Software\Microsoft\Windows\CurrentVersion

Path Structure:
├── CurrentVersion
├── CurrentBuild
├── CurrentBuildNumber
├── CurrentMajorVersionNumber
├── CurrentMinorVersionNumber
├── CurrentVersionValue
├── InstallationPath
├── ProgramFilesPath
├── ApplicationAssociation (Compatibility)
├── AppName
│   ├── CompatibilityMode
│   ├── MinimumOSVersion
│   ├── MaximumOSVersion
│   ├── SupportedArchitectures
│   │   ├── x86
│   │   ├── x64
│   │   └── ARM64
│   └── DeprecatedFeatures

Example Implementation:
HKEY_LOCAL_MACHINE\Software\Microsoft\Windows\CurrentVersion\CurrentVersion = "10.0"
HKEY_LOCAL_MACHINE\Software\Microsoft\Windows\CurrentVersion\CurrentBuildNumber = "26100"
HKEY_LOCAL_MACHINE\Software\Microsoft\Windows\CurrentVersion\MyApp\CompatibilityMode = "Windows10Plus"
```

**TypeScript Implementation**:

```typescript
// Read OS version info
const osVersion = new CurrentVersionHiveStorage('');
const version = await osVersion.read('CurrentVersion');
const build = await osVersion.read('CurrentBuildNumber');

// Store app compatibility
const compat = new CurrentVersionHiveStorage('MyApp');
await compat.write('CompatibilityMode', 'Windows10Plus');
await compat.write('MinimumOSVersion', '10.0');
await compat.write('SupportedArchitectures', 'x64');
```

---

### Pattern 5: Feature Flags Hierarchy

```
Global Feature Flags:
HKEY_LOCAL_MACHINE\Software\MyCompany\MyApplication\Features
├── Feature_BetaFeatures: "false"
├── Feature_AnalyticsEnabled: "true"
├── Feature_CloudSync: "false"
├── Feature_DarkModeSupport: "true"
├── Feature_NewUI: "false"
└── Feature_OfflineMode: "true"

User-Specific Overrides:
HKEY_CURRENT_USER\Software\MyCompany\MyApplication\Features
├── Feature_BetaFeatures_user123: "true" (Override for user123)
├── Feature_DarkModeSupport: "true" (Override for all users)
└── Feature_NewUI: "true" (Override for all users)

Environment-Specific:
HKEY_LOCAL_MACHINE\Software\MyCompany\MyApplication\Environments
├── Development
│   ├── Feature_DebugMode: "true"
│   ├── Feature_VerboseLogging: "true"
│   └── Feature_MockData: "true"
├── Staging
│   ├── Feature_DebugMode: "false"
│   ├── Feature_VerboseLogging: "true"
│   └── Feature_MockData: "false"
└── Production
    ├── Feature_DebugMode: "false"
    ├── Feature_VerboseLogging: "false"
    └── Feature_MockData: "false"
```

**TypeScript Implementation**:

```typescript
// Global defaults
const globalFlags = new SoftwareHiveStorage('MyCompany\\MyApplication\\Features');
await globalFlags.write('Feature_BetaFeatures', 'false');
await globalFlags.write('Feature_AnalyticsEnabled', 'true');

// User overrides
const userFlags = new CurrentUserHiveStorage(
  'Software\\MyCompany\\MyApplication\\Features'
);
await userFlags.write('Feature_BetaFeatures_user123', 'true');

// Environment-specific
const devFlags = new SoftwareHiveStorage(
  'MyCompany\\MyApplication\\Environments\\Development'
);
await devFlags.write('Feature_DebugMode', 'true');
```

---

### Pattern 6: Multi-Tenant Application

```
HKEY_LOCAL_MACHINE\Software\MyCompany\MyApplication\Tenants

├── Tenant_A
│   ├── TenantId: "tenant-a-001"
│   ├── TenantName: "Acme Corporation"
│   ├── License: "ENTERPRISE"
│   ├── DatabaseConnection: "Server=db-a.example.com;..."
│   ├── ApiKey: "[encrypted]"
│   ├── MaxUsers: "1000"
│   ├── ExpiryDate: "2027-12-31"
│   └── IsActive: "true"
│
├── Tenant_B
│   ├── TenantId: "tenant-b-002"
│   ├── TenantName: "Beta Company"
│   ├── License: "PROFESSIONAL"
│   ├── DatabaseConnection: "Server=db-b.example.com;..."
│   ├── ApiKey: "[encrypted]"
│   ├── MaxUsers: "500"
│   ├── ExpiryDate: "2026-12-31"
│   └── IsActive: "true"
│
└── Tenant_C
    ├── TenantId: "tenant-c-003"
    ├── TenantName: "Gamma Ltd"
    ├── License: "TRIAL"
    ├── DatabaseConnection: "Server=db-c.example.com;..."
    ├── ApiKey: "[encrypted]"
    ├── MaxUsers: "10"
    ├── ExpiryDate: "2026-07-29"
    └── IsActive: "false"
```

**TypeScript Implementation**:

```typescript
class TenantConfiguration {
  private storage: SoftwareHiveStorage;
  
  constructor() {
    this.storage = new SoftwareHiveStorage('MyCompany\\MyApplication\\Tenants');
  }
  
  async createTenant(tenantId: string, config: Record<string, string>) {
    const storage = new SoftwareHiveStorage(
      `MyCompany\\MyApplication\\Tenants\\Tenant_${tenantId}`
    );
    
    for (const [key, value] of Object.entries(config)) {
      await storage.write(key, value);
    }
  }
  
  async getTenant(tenantId: string): Promise<Record<string, string>> {
    const storage = new SoftwareHiveStorage(
      `MyCompany\\MyApplication\\Tenants\\Tenant_${tenantId}`
    );
    
    const keys = await storage.listKeys();
    const config: Record<string, string> = {};
    
    for (const key of keys) {
      const value = await storage.read(key);
      if (value !== null) {
        config[key] = value;
      }
    }
    
    return config;
  }
}
```

---

### Pattern 7: Hierarchical Settings with Inheritance

```
Application Hierarchy with Inheritance:
┌─ GLOBAL (HKLM\Software\MyApp)
│  ├── Version: "2.0"
│  ├── UpdateInterval: "86400"
│  └── LogLevel: "INFO"
│
├─ DEPARTMENT (HKCU\Software\MyApp\Departments\Sales)
│  ├── LogLevel: "DEBUG" (Overrides global)
│  ├── ReportFormat: "PDF"
│  └── ApprovalRequired: "true"
│
└─ TEAM (HKCU\Software\MyApp\Teams\SalesEast)
   ├── ReportFormat: "EXCEL" (Overrides department)
   ├── MaxRecords: "5000"
   └── AutoSubmit: "true"

Resolution Logic:
1. Check Team level (highest priority)
2. Check Department level
3. Check Global level (lowest priority)
```

**TypeScript Implementation**:

```typescript
class HierarchicalSettings {
  private global: SoftwareHiveStorage;
  private departmentStorage: CurrentUserHiveStorage;
  private teamStorage: CurrentUserHiveStorage;
  
  constructor(dept: string, team: string) {
    this.global = new SoftwareHiveStorage('MyCompany\\MyApplication');
    this.departmentStorage = new CurrentUserHiveStorage(
      `Software\\MyCompany\\MyApplication\\Departments\\${dept}`
    );
    this.teamStorage = new CurrentUserHiveStorage(
      `Software\\MyCompany\\MyApplication\\Teams\\${team}`
    );
  }
  
  async getSetting(key: string): Promise<string | null> {
    // Team level (highest priority)
    let value = await this.teamStorage.read(key);
    if (value !== null) return value;
    
    // Department level
    value = await this.departmentStorage.read(key);
    if (value !== null) return value;
    
    // Global level (lowest priority)
    return await this.global.read(key);
  }
}
```

---

### Pattern 8: Configuration Snapshots

```
Application Configuration Snapshots:
HKEY_LOCAL_MACHINE\Software\MyCompany\MyApplication\Snapshots

├── Snapshot_20260629_093000
│   ├── Version: "2.1.0"
│   ├── DatabaseHost: "prod-db-01"
│   ├── MaxConnections: "100"
│   ├── DebugMode: "false"
│   └── CreatedAt: "2026-06-29T09:30:00Z"
│
├── Snapshot_20260628_143000
│   ├── Version: "2.0.9"
│   ├── DatabaseHost: "prod-db-02"
│   ├── MaxConnections: "50"
│   ├── DebugMode: "false"
│   └── CreatedAt: "2026-06-28T14:30:00Z"
│
└── Current
    ├── Version: "2.1.0"
    ├── DatabaseHost: "prod-db-01"
    ├── MaxConnections: "100"
    └── DebugMode: "false"
```

**TypeScript Implementation**:

```typescript
class ConfigurationSnapshots {
  private storage: SoftwareHiveStorage;
  
  constructor() {
    this.storage = new SoftwareHiveStorage('MyCompany\\MyApplication\\Snapshots');
  }
  
  async saveSnapshot(config: Record<string, string>): Promise<string> {
    const timestamp = new Date().toISOString().replace(/[:.]/g, '');
    const snapshotKey = `Snapshot_${timestamp}`;
    
    const snapshotStorage = new SoftwareHiveStorage(
      `MyCompany\\MyApplication\\Snapshots\\${snapshotKey}`
    );
    
    config['CreatedAt'] = new Date().toISOString();
    
    for (const [key, value] of Object.entries(config)) {
      await snapshotStorage.write(key, value);
    }
    
    return snapshotKey;
  }
  
  async restoreSnapshot(snapshotKey: string, target: SoftwareHiveStorage) {
    const snapshotStorage = new SoftwareHiveStorage(
      `MyCompany\\MyApplication\\Snapshots\\${snapshotKey}`
    );
    
    const keys = await snapshotStorage.listKeys();
    
    for (const key of keys) {
      if (key !== 'CreatedAt') {
        const value = await snapshotStorage.read(key);
        if (value !== null) {
          await target.write(key, value);
        }
      }
    }
  }
}
```

---

## Key Hierarchy Reference Table

| Level | Purpose | Hive | Permissions | Scope | Example Path |
|-------|---------|------|-------------|-------|--------------|
| **Organization** | Vendor identity | HKLM\Software | Admin | System-wide | `MyCompany` |
| **Application** | Product identity | HKLM\Software | Admin | System-wide | `MyCompany\MyApp` |
| **Component** | Functional area | HKLM\Software | Admin | System-wide | `MyCompany\MyApp\Database` |
| **Feature** | Individual setting | HKLM\Software | Admin | System-wide | `MyCompany\MyApp\Database\Host` |
| **User Prefs** | User-specific | HKCU\Software | User | Current user | `Software\MyCompany\MyApp\Preferences` |
| **User History** | User activity | HKCU\Software | User | Current user | `Software\MyCompany\MyApp\History` |
| **Service Config** | Windows service | HKLM\System | System | System-wide | `ControlSet001\Services\MyService` |
| **OS Compat** | OS version info | HKLM\...\CurrentVersion | Admin | System-wide | `CurrentVersion\MyApp` |

---

## Best Practice Naming Conventions

### Key Names

```
PascalCase: Version, InstallDate, DisplayName, MaxConnections
CamelCase (User facing): user name, password, email
SCREAMING_CASE (Constants): MAX_CONNECTIONS, DEFAULT_TIMEOUT
With Prefix: Feature_BetaMode, Service_Port, Config_Timeout
With Suffix: LastUpdated, CreatedBy, IsActive, WasChanged
```

### Path Hierarchy

```
Good:     Company\Product\Component\SubComponent\Setting
Bad:      MySettings, Config, Data
Optimal:  MyCompany\MyProduct\Features\Database\ConnectionTimeout
```

### Value Naming

```
Booleans:      "true" or "false"
Numbers:       "12345" (as string)
Timestamps:    ISO 8601: "2026-06-29T10:30:00Z"
Enums:         "Active", "Inactive", "Pending"
Versions:      "1.2.3" (semantic versioning)
Paths:         Windows paths or URIs
Secrets:       [encrypted] notation (never plaintext)
```

---

## Common Hierarchy Depth Patterns

### Shallow (1-2 levels)
```
✓ Simple applications
✓ Quick lookups
✗ Limited organization
✓ Example: AppName\Version, AppName\Theme
```

### Medium (3-4 levels)
```
✓ Organized component structure
✓ Good balance of depth and readability
✓ Example: Company\AppName\Components\Database
✗ Getting complex
```

### Deep (5+ levels)
```
✓ Highly organized
✓ Complex applications
✗ Performance overhead
✗ Difficult navigation
✓ Example: Company\App\Tenants\Tenant_A\Departments\Sales\Settings
```

**Recommendation**: Use 3-4 levels for most applications.

---

## Summary

Use this reference guide for:

- ✓ Designing registry hierarchies
- ✓ Following best practices
- ✓ Understanding common patterns
- ✓ Quick lookup of implementations
- ✓ Naming conventions
- ✓ Hierarchy depth recommendations

Refer to `REGISTRY_STORAGE_TECHNICAL_DOCUMENTATION.md` for detailed architecture and `REGISTRY_STORAGE_CODE_EXAMPLES.md` for implementation examples.
