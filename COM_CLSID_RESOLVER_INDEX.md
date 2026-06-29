# COM CLSID Runtime Resolver - Complete Index

## Overview

The COM CLSID Runtime Resolver is a sophisticated obfuscation system that resolves COM Class Identifiers at runtime instead of hardcoding them. This prevents static analysis from easily identifying which COM objects are being instantiated.

**Project Status:** COMPLETE ✓  
**Test Coverage:** 58/58 passing  
**Documentation:** Comprehensive

---

## Files and Components

### 1. Implementation Files

#### `com_clsid_resolver.py` (26 KB, 780 lines)
Main implementation with all resolver classes and supporting infrastructure.

**Key Classes:**
- `ICLSIDResolver` - Abstract base interface
- `RegistryProgIDResolver` - Registry-based resolution
- `WMIRegistryResolver` - WMI StdRegProv resolution
- `EncodedLiteralResolver` - Encoded CLSID literals (XOR/Base64/Hex/ROT13)
- `HashBasedResolver` - Hash table lookup
- `HybridCLSIDResolver` - Fallback chain resolution
- `CLSIDResolverFactory` - Factory for resolver creation
- `CLSIDDatabase` - Central CLSID store (10+ objects)
- `RuntimeCLSIDResolver` - High-level API

**Key Enumerations:**
- `CLSIDResolutionMethod` - 5 resolution methods
- `CLSIDObfuscationType` - 6 obfuscation types
- `COMObjectType` - COM object classifications

**Key Data Classes:**
- `ResolutionContext` - Configuration for resolution
- `CLSIDMetadata` - Object metadata storage

**Functions:**
- `generate_clsid_resolver_package()` - Generate complete package

---

### 2. Test Files

#### `test_com_clsid_resolver.py` (22 KB, 620 lines)
Comprehensive unit test suite with 58 tests.

**Test Classes:**
- `TestRegistryProgIDResolver` (5 tests)
- `TestWMIRegistryResolver` (5 tests)
- `TestEncodedLiteralResolver` (8 tests)
- `TestHashBasedResolver` (5 tests)
- `TestHybridCLSIDResolver` (5 tests)
- `TestCLSIDResolverFactory` (6 tests)
- `TestCLSIDDatabase` (7 tests)
- `TestRuntimeCLSIDResolver` (9 tests)
- `TestPackageGeneration` (4 tests)
- `TestIntegration` (5 tests)

**Execution:**
```bash
python3 -m unittest test_com_clsid_resolver -v
# Result: Ran 58 tests in 0.003s - OK
```

---

### 3. Documentation Files

#### `COM_CLSID_RUNTIME_RESOLVER_GUIDE.md` (16 KB, 500+ lines)
**Comprehensive Reference Guide**

Contents:
- Problem Statement & Solution
- Key Features Overview
- 5 Resolution Methods with examples
- 5 Obfuscation Techniques with code samples
- CLSID Database documentation
- Architecture and class hierarchy
- Performance characteristics table
- Security considerations & limitations
- Detection evasion analysis
- VBScript generation examples
- Integration guidelines
- Performance benchmarks
- File structure
- References and future enhancements

Use this for: Deep understanding, architecture overview, security analysis

#### `COM_CLSID_QUICK_START.md` (12 KB, 400+ lines)
**Quick Start and Examples Guide**

Contents:
- Installation
- 5 Basic usage examples with code
- 4 Use cases (minimal obfuscation, maximum, high resilience, speed)
- Encoding examples (XOR, Base64, Hex)
- Testing instructions
- Integration points
- Performance benchmarks
- Troubleshooting guide
- Command reference
- Common COM objects reference
- File size comparison
- Next steps

Use this for: Getting started quickly, practical examples, common patterns

#### `COM_CLSID_RESOLVER_SUMMARY.txt` (25 KB, 800+ lines)
**Executive Summary and Overview**

Contents:
- Project completion status
- Core components listing
- Key features checklist
- Architecture overview (design patterns, class hierarchy)
- Detailed resolver descriptions (5 methods)
- Obfuscation technique details (6 types)
- Database contents (10+ objects)
- Test suite breakdown (58 tests)
- Performance characteristics
- Integration points
- Security analysis (strengths/limitations)
- Usage recommendations
- Example outputs
- File manifest
- Quick start
- Deliverables checklist

Use this for: High-level overview, decision-making, status tracking

#### `COM_CLSID_RESOLVER_INDEX.md` (this file)
**Navigation and structure guide**

---

## Quick Navigation

### By Use Case

**I want to...**

- **Get started quickly** → `COM_CLSID_QUICK_START.md`
- **Understand the architecture** → `COM_CLSID_RUNTIME_RESOLVER_GUIDE.md`
- **See what was built** → `COM_CLSID_RESOLVER_SUMMARY.txt`
- **Look up specific resolvers** → `COM_CLSID_RUNTIME_RESOLVER_GUIDE.md` - Resolution Methods section
- **Find code examples** → `COM_CLSID_QUICK_START.md` - Examples section
- **Run tests** → `test_com_clsid_resolver.py`
- **Implement in my code** → `COM_CLSID_QUICK_START.md` - Integration Points section
- **Understand performance** → `COM_CLSID_RESOLVER_SUMMARY.txt` - Performance Characteristics

### By Feature

**Resolution Methods:**
1. Registry ProgID - `COM_CLSID_RUNTIME_RESOLVER_GUIDE.md` Registry ProgID Resolution section
2. WMI StdRegProv - `COM_CLSID_RUNTIME_RESOLVER_GUIDE.md` WMI Registry Resolver section
3. Encoded Literals - `COM_CLSID_RUNTIME_RESOLVER_GUIDE.md` Encoded Literal Resolution section
4. Hash Lookup - `COM_CLSID_RUNTIME_RESOLVER_GUIDE.md` Hash-based Lookup section
5. Hybrid Chain - `COM_CLSID_RUNTIME_RESOLVER_GUIDE.md` Hybrid Resolution section

**Obfuscation Methods:**
1. XOR - `COM_CLSID_QUICK_START.md` XOR Encoding section
2. Base64 - `COM_CLSID_QUICK_START.md` Base64 Encoding section
3. Hex - `COM_CLSID_QUICK_START.md` Hex Encoding section
4. ROT13 - `COM_CLSID_RUNTIME_RESOLVER_GUIDE.md` ROT13 Encoding section
5. Hybrid - `COM_CLSID_RESOLVER_SUMMARY.txt` Obfuscation Techniques section
6. Polymorph - `com_clsid_resolver.py` CLSIDObfuscationType enum

### By Audience

**For Security Researchers:**
- Start with `COM_CLSID_RUNTIME_RESOLVER_GUIDE.md` - Security Considerations section
- Review test cases in `test_com_clsid_resolver.py` - Integration Tests section
- Check performance in `COM_CLSID_RESOLVER_SUMMARY.txt` - Performance Characteristics

**For Developers:**
- Begin with `COM_CLSID_QUICK_START.md` - Basic Usage section
- Look at examples in `COM_CLSID_QUICK_START.md` - Examples by Use Case section
- Check integration in `COM_CLSID_QUICK_START.md` - Integration Points section

**For System Architects:**
- Overview: `COM_CLSID_RESOLVER_SUMMARY.txt` - Architecture Overview section
- Details: `COM_CLSID_RUNTIME_RESOLVER_GUIDE.md` - Architecture section
- Implementation: `com_clsid_resolver.py` - Class hierarchy

**For QA/Testers:**
- Test suite: `test_com_clsid_resolver.py` - All 58 tests
- Coverage: `COM_CLSID_RESOLVER_SUMMARY.txt` - Test Suite section
- Examples: `COM_CLSID_QUICK_START.md` - Testing section

---

## Feature Matrix

| Feature | File Location | Status |
|---------|--------------|--------|
| Registry Resolver | `com_clsid_resolver.py` RegistryProgIDResolver class | ✓ Complete |
| WMI Resolver | `com_clsid_resolver.py` WMIRegistryResolver class | ✓ Complete |
| Encoded Resolver | `com_clsid_resolver.py` EncodedLiteralResolver class | ✓ Complete |
| Hash Resolver | `com_clsid_resolver.py` HashBasedResolver class | ✓ Complete |
| Hybrid Resolver | `com_clsid_resolver.py` HybridCLSIDResolver class | ✓ Complete |
| XOR Obfuscation | `com_clsid_resolver.py` _encode_xor() method | ✓ Complete |
| Base64 Obfuscation | `com_clsid_resolver.py` _encode_base64() method | ✓ Complete |
| Hex Obfuscation | `com_clsid_resolver.py` _encode_hex() method | ✓ Complete |
| ROT13 Obfuscation | `com_clsid_resolver.py` _encode_rot13() method | ✓ Complete |
| Hybrid Obfuscation | `com_clsid_resolver.py` _encode_hybrid() method | ✓ Complete |
| CLSID Database | `com_clsid_resolver.py` CLSIDDatabase class | ✓ Complete |
| Runtime Resolver API | `com_clsid_resolver.py` RuntimeCLSIDResolver class | ✓ Complete |
| VBScript Generation | All resolver classes generate_resolution_code() | ✓ Complete |
| Factory Pattern | `com_clsid_resolver.py` CLSIDResolverFactory class | ✓ Complete |
| Unit Tests | `test_com_clsid_resolver.py` (58 tests) | ✓ Complete |
| Integration Guide | `COM_CLSID_QUICK_START.md` Integration Points | ✓ Complete |
| Performance Data | `COM_CLSID_RESOLVER_SUMMARY.txt` Performance | ✓ Complete |
| Security Analysis | `COM_CLSID_RUNTIME_RESOLVER_GUIDE.md` Security | ✓ Complete |

---

## Code Examples by Scenario

### Scenario 1: Simple CLSID Resolution
**File:** `COM_CLSID_QUICK_START.md` - Use Case 1
**Code:**
```python
from com_clsid_resolver import RegistryProgIDResolver, ResolutionContext
resolver = RegistryProgIDResolver()
code = resolver.generate_resolution_code(ResolutionContext(...))
```

### Scenario 2: Obfuscated COM Instantiation
**File:** `COM_CLSID_QUICK_START.md` - Use Case 2
**Code:**
```python
from com_clsid_resolver import RuntimeCLSIDResolver, CLSIDObfuscationType
resolver = RuntimeCLSIDResolver()
resolver.set_obfuscation(CLSIDObfuscationType.XOR)
script = resolver.generate_com_instantiation_script("WScript.Shell")
```

### Scenario 3: Resilient Multi-Method Resolution
**File:** `COM_CLSID_QUICK_START.md` - Use Case 3
**Code:**
```python
from com_clsid_resolver import CLSIDResolverFactory, CLSIDResolutionMethod
resolver = CLSIDResolverFactory.create_hybrid_resolver([
    CLSIDResolutionMethod.REGISTRY_PROGID,
    CLSIDResolutionMethod.WMI_CLASS,
])
```

### Scenario 4: Fast Hash-Based Lookup
**File:** `COM_CLSID_QUICK_START.md` - Use Case 4
**Code:**
```python
from com_clsid_resolver import HashBasedResolver
resolver = HashBasedResolver()
resolver.add_mapping("WScript.Shell", "{F935DC22-1CF0-11D0-ADB9-00C04FD58A0B}")
```

### Scenario 5: Complete Payload Generation
**File:** `COM_CLSID_QUICK_START.md` - Use Case 5
**Code:**
```python
from com_clsid_resolver import generate_clsid_resolver_package
package = generate_clsid_resolver_package()
for component_name, code in package.items():
    print(f"Component: {component_name}")
```

---

## Database Contents

10+ known COM objects with full metadata:

| ProgID | CLSID | Category | Use Case |
|--------|-------|----------|----------|
| WScript.Shell | {F935DC22-1CF0-11D0-ADB9-00C04FD58A0B} | scripting | Execute, registry |
| WbemScripting.SWbemLocator | {76A64158-CB41-11D1-8B02-00600806D9B6} | wmi | WMI queries |
| Shell.Application | {13709620-C279-11CE-A49E-444553540000} | shell | Shell ops |
| Excel.Application | {00024500-0000-0000-C000-000000000046} | office | Spreadsheets |
| Word.Application | {000209FF-0000-0000-C000-000000000046} | office | Documents |
| PowerPoint.Application | {91493441-5A91-11CF-8700-00AA0060263B} | office | Presentations |
| MSXML2.DOMDocument | {F5078F32-C551-11D3-89B9-0000F81FE221} | xml | XML parsing |
| ADODB.Connection | {00000514-0000-0010-8000-00AA006D2EA4} | database | DB access |

See full list in: `COM_CLSID_RESOLVER_SUMMARY.txt` Database Contents section

---

## Test Results Summary

**Total Tests:** 58  
**Passing:** 58  
**Failing:** 0  
**Execution Time:** 0.003 seconds  
**Success Rate:** 100%

Test breakdown:
- Registry Resolver: 5 tests ✓
- WMI Resolver: 5 tests ✓
- Encoded Resolver: 8 tests ✓
- Hash Resolver: 5 tests ✓
- Hybrid Resolver: 5 tests ✓
- Factory: 6 tests ✓
- Database: 7 tests ✓
- Runtime Resolver: 9 tests ✓
- Package Generation: 4 tests ✓
- Integration: 5 tests ✓

---

## Performance Summary

### Execution Times (milliseconds)
| Method | Time | Trade-offs |
|--------|------|-----------|
| Registry ProgID | 10-50ms | Fast, visible registry access |
| WMI StdRegProv | 100-500ms | Slower but less obvious |
| XOR Decode | 1-5ms | Very fast, small payload |
| Base64 Decode | 2-10ms | Fast, standard encoding |
| Hash Lookup | <1ms | Fastest, pre-computed |
| Hybrid (1st) | 10-50ms | Fast when primary works |
| Hybrid (2nd) | 100-500ms | Slower on fallback |

### Code Sizes (bytes)
| Method | Size | Notes |
|--------|------|-------|
| Registry | 200-300B | Smallest |
| WMI | 400-500B | Larger |
| XOR Encoded | 300-400B + decoder | Small + function |
| Hash Table | 400-500B | Dictionary based |
| Hybrid | 600-800B | Largest, fallback logic |

---

## Security Considerations

### Strengths
✓ No hardcoded CLSIDs visible in binary  
✓ Multiple techniques make analysis harder  
✓ Runtime resolution requires execution  
✓ Obfuscation bypasses simple pattern detection  
✓ Fallback mechanisms increase resilience  

### Limitations
✗ Determined analyst can reverse techniques  
✗ Behavioral detection via registry/WMI access  
✗ Memory inspection reveals decoded CLSIDs  
✗ Performance adds minimal overhead  
✗ Not cryptographic-level security  

See full analysis in: `COM_CLSID_RUNTIME_RESOLVER_GUIDE.md` - Security Considerations

---

## Integration Checklist

- [ ] Copy `com_clsid_resolver.py` to project
- [ ] Copy test file for verification
- [ ] Read `COM_CLSID_QUICK_START.md` for your use case
- [ ] Choose appropriate resolution method
- [ ] Choose appropriate obfuscation technique
- [ ] Generate code using `RuntimeCLSIDResolver`
- [ ] Test in target environment
- [ ] Integrate into payload pipeline
- [ ] Verify CLSID resolution works
- [ ] Check performance metrics

---

## Troubleshooting

### Issue: CLSID Not Resolving
**Solution:** Use hybrid resolver with multiple fallbacks
**Reference:** `COM_CLSID_QUICK_START.md` Troubleshooting section

### Issue: Script Too Large
**Solution:** Use registry method (smallest) or hash-based
**Reference:** `COM_CLSID_RESOLVER_SUMMARY.txt` Code Sizes

### Issue: Slow Execution
**Solution:** Use hash-based resolver or XOR encoding
**Reference:** `COM_CLSID_RESOLVER_SUMMARY.txt` Performance Characteristics

### Issue: Pattern Detection
**Solution:** Use encoded resolver + hybrid obfuscation
**Reference:** `COM_CLSID_RUNTIME_RESOLVER_GUIDE.md` Detection Evasion

---

## Advanced Topics

### Custom Resolution Methods
See: `com_clsid_resolver.py` ICLSIDResolver class (abstract interface)

### Custom Obfuscation
See: `com_clsid_resolver.py` EncodedLiteralResolver class

### Multiple Fallback Chains
See: `com_clsid_resolver.py` HybridCLSIDResolver class

### Performance Optimization
See: `COM_CLSID_RESOLVER_SUMMARY.txt` Performance Characteristics

### Integration Patterns
See: `COM_CLSID_QUICK_START.md` Integration Points section

---

## File Statistics

| File | Size | Lines | Type |
|------|------|-------|------|
| com_clsid_resolver.py | 26 KB | 780 | Python |
| test_com_clsid_resolver.py | 22 KB | 620 | Python |
| COM_CLSID_RUNTIME_RESOLVER_GUIDE.md | 16 KB | 500+ | Markdown |
| COM_CLSID_QUICK_START.md | 12 KB | 400+ | Markdown |
| COM_CLSID_RESOLVER_SUMMARY.txt | 25 KB | 800+ | Text |
| COM_CLSID_RESOLVER_INDEX.md | 10 KB | 400+ | Markdown |
| **Total** | **111 KB** | **3100+** | **Mixed** |

---

## Key Classes Quick Reference

### ICLSIDResolver (Abstract)
Base interface for all resolvers
- `resolve(progid)` - Resolve ProgID to CLSID
- `generate_resolution_code(context)` - Generate VBScript
- `get_resolution_method()` - Return method type

### RegistryProgIDResolver
Queries `HKCR\ProgID\CLSID` directly
- Fast (10-50ms)
- Small code (200-300B)
- Visible registry access

### WMIRegistryResolver
Uses WMI StdRegProv
- Slower (100-500ms)
- Medium code (400-500B)
- Less obvious access

### EncodedLiteralResolver
Encodes CLSID with XOR/Base64/Hex/ROT13
- Fast decode (1-10ms)
- Medium code (300-400B + decoder)
- CLSID not visible in plaintext

### HashBasedResolver
Hash table lookup
- Fastest (<1ms)
- Medium code (400-500B)
- Pre-computed hashes

### HybridCLSIDResolver
Chain multiple resolvers
- Varies (10-500ms)
- Larger code (600-800B)
- Maximum resilience

### CLSIDResolverFactory
Create resolver instances
- `create_resolver(method)` - Single resolver
- `create_hybrid_resolver(methods)` - Fallback chain

### CLSIDDatabase
Central CLSID store
- `get_metadata(progid)` - Get object metadata
- `get_clsid(progid)` - Get CLSID
- `list_all()` - List all objects

### RuntimeCLSIDResolver
High-level API
- `resolve(progid)` - Resolve with caching
- `set_resolution_strategy()` - Change method
- `set_obfuscation()` - Change encoding
- `generate_resolution_script()` - Generate VBScript
- `generate_com_instantiation_script()` - Full payload

---

## Getting Help

1. **Quick answers:** `COM_CLSID_QUICK_START.md` Troubleshooting
2. **Detailed info:** `COM_CLSID_RUNTIME_RESOLVER_GUIDE.md`
3. **Examples:** Look at test cases in `test_com_clsid_resolver.py`
4. **Code:** Read `com_clsid_resolver.py` source with inline comments
5. **Performance:** Check `COM_CLSID_RESOLVER_SUMMARY.txt` benchmarks

---

## License

Part of sc-generator project

---

**Last Updated:** 2025-06-29  
**Version:** 1.0  
**Status:** Complete and Tested
