/**
 * Registry Cleanup Integration Patterns
 * Real-world integration patterns for automatic cleanup
 */

import {
  RegistryCleanupHandler,
  initializeCleanupHandler,
  getCleanupHandler,
  withCleanupContext,
} from './registry-cleanup-handler';
import {
  MultiHiveRegistryManager,
  SoftwareHiveStorage,
  CurrentUserHiveStorage,
  RegistryHive,
} from './registry-storage-variants';

/**
 * Integration Pattern 1: Service Initialization with Cleanup
 * Ensures service cleanup on shutdown
 */
export class RegistryServiceWithCleanup {
  private handler: RegistryCleanupHandler;
  private manager: MultiHiveRegistryManager;
  private isRunning: boolean = false;

  constructor(serviceName: string) {
    this.handler = new RegistryCleanupHandler({ verbose: true });
    this.manager = new MultiHiveRegistryManager(serviceName);
  }

  async start(): Promise<void> {
    console.log('[Service] Starting with registry cleanup...');
    this.handler.startTracking();
    this.isRunning = true;

    // Setup shutdown handler
    this.setupShutdownHandler();
  }

  async stop(): Promise<void> {
    console.log('[Service] Stopping and cleaning up registry...');
    this.isRunning = false;

    const result = await this.handler.executeCleanup();
    console.log(`[Service] Cleanup complete: ${result.entriesCleaned} entries cleaned`);
  }

  private setupShutdownHandler(): void {
    const signals = ['SIGINT', 'SIGTERM', 'SIGHUP'];

    for (const signal of signals) {
      process.on(signal, async () => {
        console.log(`[Service] Received ${signal}, shutting down...`);
        await this.stop();
        process.exit(0);
      });
    }
  }

  async registerService(serviceData: Record<string, string>): Promise<void> {
    if (!this.isRunning) {
      throw new Error('Service not started');
    }

    for (const [key, value] of Object.entries(serviceData)) {
      await this.manager.writeToAllHives(key, value);
      this.handler.addEntry(RegistryHive.HKLM_SOFTWARE, key, null);
    }
  }
}

/**
 * Integration Pattern 2: Application Installer with Rollback
 * Install application settings with automatic rollback on failure
 */
export class InstallableApplicationWithCleanup {
  private handler: RegistryCleanupHandler;
  private appName: string;

  constructor(appName: string) {
    this.appName = appName;
    this.handler = new RegistryCleanupHandler({
      verbose: true,
      trackOriginalValues: true,
    });
  }

  async install(): Promise<boolean> {
    const { result, cleanup } = await withCleanupContext(
      async (handler) => {
        try {
          console.log(`[Installer] Installing ${this.appName}...`);

          // Step 1: Register application
          await this.registerApplication(handler);

          // Step 2: Install settings
          await this.installSettings(handler);

          // Step 3: Configure features
          await this.configureFeatures(handler);

          console.log(`[Installer] Installation successful`);
          return true;
        } catch (error) {
          console.error(`[Installer] Installation failed:`, error);
          // Cleanup will automatically run on error
          return false;
        }
      },
      { verbose: true }
    );

    console.log(
      `[Installer] Cleanup: ${cleanup.entriesCleaned} entries processed`
    );
    return result;
  }

  private async registerApplication(
    handler: RegistryCleanupHandler
  ): Promise<void> {
    const storage = new SoftwareHiveStorage(this.appName);
    const timestamp = new Date().toISOString();

    handler.addEntry(
      RegistryHive.HKLM_SOFTWARE,
      `${this.appName}\\InstallDate`,
      null
    );
    handler.addEntry(
      RegistryHive.HKLM_SOFTWARE,
      `${this.appName}\\Version`,
      null
    );

    console.log('[Installer] Application registered');
  }

  private async installSettings(
    handler: RegistryCleanupHandler
  ): Promise<void> {
    const settings = {
      AutoUpdate: 'true',
      CheckForUpdates: 'true',
      UpdateInterval: '86400',
    };

    for (const [key, value] of Object.entries(settings)) {
      handler.addEntry(
        RegistryHive.HKLM_SOFTWARE,
        `${this.appName}\\Settings\\${key}`,
        null
      );
    }

    console.log('[Installer] Settings installed');
  }

  private async configureFeatures(
    handler: RegistryCleanupHandler
  ): Promise<void> {
    const features = {
      FeatureA: 'true',
      FeatureB: 'false',
      FeatureC: 'true',
    };

    for (const [key, value] of Object.entries(features)) {
      handler.addEntry(
        RegistryHive.HKLM_SOFTWARE,
        `${this.appName}\\Features\\${key}`,
        null
      );
    }

    console.log('[Installer] Features configured');
  }
}

/**
 * Integration Pattern 3: Transaction-like Registry Operations
 * Atomic registry operations with rollback support
 */
export class RegistryTransaction {
  private handler: RegistryCleanupHandler;
  private operations: Array<{
    hive: RegistryHive;
    key: string;
    value: string;
  }> = [];

  constructor() {
    this.handler = new RegistryCleanupHandler({ verbose: false });
  }

  begin(): void {
    console.log('[Transaction] Started');
    this.handler.startTracking();
    this.operations = [];
  }

  addOperation(hive: RegistryHive, key: string, value: string): void {
    this.operations.push({ hive, key, value });
    this.handler.addEntry(hive, key, null);
  }

  async commit(): Promise<boolean> {
    try {
      console.log(`[Transaction] Committing ${this.operations.length} operations`);

      // In real implementation, actually write to registry
      for (const op of this.operations) {
        console.log(`[Transaction] Writing ${op.hive}\\${op.key}`);
      }

      console.log('[Transaction] Committed successfully');
      return true;
    } catch (error) {
      await this.rollback();
      return false;
    }
  }

  async rollback(): Promise<void> {
    console.log('[Transaction] Rolling back');
    const result = await this.handler.executeCleanup();
    console.log(
      `[Transaction] Rollback complete: ${result.entriesCleaned} entries cleaned`
    );
  }

  getOperationCount(): number {
    return this.operations.length;
  }
}

/**
 * Integration Pattern 4: Configuration Profile Manager
 * Switch between configuration profiles with automatic cleanup
 */
export class ConfigurationProfileManager {
  private handler: RegistryCleanupHandler;
  private currentProfile: string | null = null;
  private profiles: Map<string, Record<string, string>> = new Map();

  constructor() {
    this.handler = new RegistryCleanupHandler({ verbose: true });
  }

  registerProfile(name: string, settings: Record<string, string>): void {
    this.profiles.set(name, settings);
    console.log(`[ProfileManager] Registered profile: ${name}`);
  }

  async switchProfile(profileName: string): Promise<boolean> {
    const { result, cleanup } = await withCleanupContext(
      async (handler) => {
        const profile = this.profiles.get(profileName);
        if (!profile) {
          throw new Error(`Profile not found: ${profileName}`);
        }

        console.log(`[ProfileManager] Switching to profile: ${profileName}`);

        // Apply profile settings
        for (const [key, value] of Object.entries(profile)) {
          handler.addEntry(
            RegistryHive.HKEY_CURRENT_USER,
            `Software\\CurrentProfile\\${key}`,
            null
          );
        }

        this.currentProfile = profileName;
        return true;
      },
      { verbose: true }
    );

    console.log(`[ProfileManager] Cleanup: ${cleanup.entriesCleaned} entries`);
    return result;
  }

  getCurrentProfile(): string | null {
    return this.currentProfile;
  }
}

/**
 * Integration Pattern 5: Feature Toggle Management
 * Enable/disable features with automatic registry cleanup
 */
export class FeatureToggleManager {
  private handler: RegistryCleanupHandler;
  private storage: SoftwareHiveStorage;
  private features: Map<string, boolean> = new Map();

  constructor(appName: string) {
    this.handler = new RegistryCleanupHandler({ verbose: true });
    this.storage = new SoftwareHiveStorage(appName);
  }

  async enableFeature(featureName: string): Promise<void> {
    const { result, cleanup } = await withCleanupContext(
      async (handler) => {
        console.log(`[FeatureToggle] Enabling ${featureName}`);

        handler.addEntry(
          RegistryHive.HKLM_SOFTWARE,
          `Features\\${featureName}`,
          'false'
        );

        this.features.set(featureName, true);
      },
      { verbose: false }
    );
  }

  async disableFeature(featureName: string): Promise<void> {
    const { result, cleanup } = await withCleanupContext(
      async (handler) => {
        console.log(`[FeatureToggle] Disabling ${featureName}`);

        handler.addEntry(
          RegistryHive.HKLM_SOFTWARE,
          `Features\\${featureName}`,
          'true'
        );

        this.features.set(featureName, false);
      },
      { verbose: false }
    );
  }

  isFeatureEnabled(featureName: string): boolean {
    return this.features.get(featureName) ?? false;
  }
}

/**
 * Integration Pattern 6: Audit Trail with Cleanup
 * Track all registry operations for audit with cleanup
 */
export class AuditedRegistryManager {
  private handler: RegistryCleanupHandler;
  private auditLog: Array<{
    timestamp: Date;
    operation: string;
    hive: RegistryHive;
    key: string;
  }> = [];

  constructor() {
    this.handler = new RegistryCleanupHandler({ verbose: false });
  }

  async performAuditedOperation(
    operation: string,
    hive: RegistryHive,
    key: string,
    originalValue?: string
  ): Promise<void> {
    const { result, cleanup } = await withCleanupContext(
      async (handler) => {
        console.log(`[Audit] ${operation}: ${hive}\\${key}`);

        handler.addEntry(hive, key, originalValue);

        this.auditLog.push({
          timestamp: new Date(),
          operation,
          hive,
          key,
        });
      },
      { verbose: false }
    );
  }

  getAuditLog(): typeof this.auditLog {
    return [...this.auditLog];
  }

  exportAuditLog(): string {
    return JSON.stringify(this.auditLog, null, 2);
  }

  async clearAuditLog(): Promise<void> {
    this.auditLog = [];
    console.log('[Audit] Log cleared');
  }
}

/**
 * Integration Pattern 7: Batch Registry Operations
 * Execute multiple registry operations with batch cleanup
 */
export class BatchRegistryOperations {
  private handler: RegistryCleanupHandler;

  constructor() {
    this.handler = new RegistryCleanupHandler({
      verbose: true,
      dryRun: false,
    });
  }

  async executeBatch(
    operations: Array<{
      hive: RegistryHive;
      key: string;
      value: string;
      originalValue?: string;
    }>
  ): Promise<{ success: number; failed: number }> {
    const { result, cleanup } = await withCleanupContext(
      async (handler) => {
        let success = 0;
        let failed = 0;

        for (const op of operations) {
          try {
            handler.addEntry(op.hive, op.key, op.originalValue);
            success++;
          } catch (error) {
            console.error(`Failed to process ${op.key}:`, error);
            failed++;
          }
        }

        return { success, failed };
      },
      { verbose: true }
    );

    console.log(`[Batch] Completed: ${result.success} success, ${result.failed} failed`);
    console.log(`[Batch] Cleanup: ${cleanup.entriesCleaned} entries processed`);

    return result;
  }
}

/**
 * Export integration patterns
 */
export {
  RegistryServiceWithCleanup,
  InstallableApplicationWithCleanup,
  RegistryTransaction,
  ConfigurationProfileManager,
  FeatureToggleManager,
  AuditedRegistryManager,
  BatchRegistryOperations,
};
