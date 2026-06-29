# Polymorphic Obfuscation: Analysis Tools & Detection Methods

## Table of Contents
1. [Dynamic Analysis Tools](#dynamic-analysis-tools)
2. [Static Analysis Techniques](#static-analysis-techniques)
3. [Heuristic Detection Methods](#heuristic-detection-methods)
4. [Forensic Investigation](#forensic-investigation)
5. [Tool Implementations](#tool-implementations)

---

## Dynamic Analysis Tools

### 1. Memory-based Polymorphic Payload Extraction

```python
#!/usr/bin/env python3

import os
import sys
import subprocess
from typing import List, Tuple

class PolymorphicMemoryAnalyzer:
    """Extract and analyze polymorphic payloads from memory"""
    
    def __init__(self, process_id: int):
        self.pid = process_id
        self.memory_map = {}
        self.payloads = []
    
    def dump_process_memory(self, output_file: str) -> bool:
        """Dump entire process memory using gdb or similar"""
        
        try:
            # Using gdb to dump memory
            gdb_script = f"""
            set logging on
            set logging file {output_file}
            attach {self.pid}
            dump memory {output_file}.bin 0x0 0xffffffffffffffff
            detach
            quit
            """
            
            with open('/tmp/gdb_script.txt', 'w') as f:
                f.write(gdb_script)
            
            result = subprocess.run(['gdb', '-x', '/tmp/gdb_script.txt'],
                                  capture_output=True)
            
            return os.path.exists(output_file)
        
        except Exception as e:
            print(f"Error dumping memory: {e}")
            return False
    
    def find_polymorphic_patterns(self, memory_dump: bytes) -> List[Tuple[int, bytes]]:
        """Identify polymorphic code patterns in memory"""
        
        patterns = [
            # Decoder stub signatures
            b'\x55\x48\x89\xe5',  # push rbp; mov rbp, rsp
            b'\x48\x31\xc0',      # xor rax, rax
            
            # XOR loop patterns
            b'\x8a\x04\x07\x30\xc1\x88\x04\x07',  # mov al, [rdi]; xor al, cl; mov [rdi], al
            
            # String.fromCharCode patterns (JavaScript)
            b'String.fromCharCode',
            
            # eval patterns
            b'eval(',
            
            # Encoded payload markers
            b'\x00\x00\x00\x00\x00\x00\x00\x00',  # Large null blocks
        ]
        
        findings = []
        for pattern in patterns:
            offset = 0
            while True:
                pos = memory_dump.find(pattern, offset)
                if pos == -1:
                    break
                
                # Extract surrounding context (e.g., 512 bytes around pattern)
                start = max(0, pos - 256)
                end = min(len(memory_dump), pos + 256)
                context = memory_dump[start:end]
                
                findings.append((pos, context))
                offset = pos + 1
        
        return findings
    
    def identify_decoder_stubs(self, memory_sections: List[bytes]) -> List[dict]:
        """Identify and classify decoder stubs"""
        
        decoders = []
        
        for section in memory_sections:
            # Look for common decoder signatures
            
            # XOR decoder
            if self._is_xor_decoder(section):
                decoders.append({
                    'type': 'XOR',
                    'offset': len(decoders),
                    'data': section[:256]
                })
            
            # ADD decoder
            elif self._is_add_decoder(section):
                decoders.append({
                    'type': 'ADD',
                    'offset': len(decoders),
                    'data': section[:256]
                })
            
            # ROR decoder
            elif self._is_ror_decoder(section):
                decoders.append({
                    'type': 'ROR',
                    'offset': len(decoders),
                    'data': section[:256]
                })
        
        return decoders
    
    def _is_xor_decoder(self, data: bytes) -> bool:
        """Heuristic: Check if data contains XOR decoder pattern"""
        xor_indicators = [
            b'\x30',           # xor instruction
            b'\x8a\x04\x07',   # mov al, [rdi]
            b'\x88\x04\x07',   # mov [rdi], al
        ]
        
        matches = sum(1 for indicator in xor_indicators if indicator in data)
        return matches >= 2
    
    def _is_add_decoder(self, data: bytes) -> bool:
        """Heuristic: Check if data contains ADD decoder pattern"""
        add_indicators = [
            b'\x00',           # add instruction
            b'\x28',           # sub instruction
        ]
        
        matches = sum(1 for indicator in add_indicators if indicator in data)
        return matches >= 1
    
    def _is_ror_decoder(self, data: bytes) -> bool:
        """Heuristic: Check if data contains ROR decoder pattern"""
        ror_indicators = [
            b'\xd2\xcb',       # ror cl, dl
            b'\xd0',           # rol/ror instructions
        ]
        
        matches = sum(1 for indicator in ror_indicators if indicator in data)
        return matches >= 1
    
    def extract_encoded_payload(self, memory_dump: bytes, decoder_start: int) -> bytes:
        """Extract encoded payload following a decoder stub"""
        
        # Typical structure:
        # [Decoder Stub] [Size field] [Encrypted data]
        
        # Skip decoder (usually 50-200 bytes)
        payload_start = decoder_start + 128
        
        # Try to find payload size
        potential_size = int.from_bytes(
            memory_dump[payload_start:payload_start+4], 'little'
        )
        
        if potential_size > 0 and potential_size < 1000000:
            payload_end = payload_start + 4 + potential_size
            return memory_dump[payload_start:payload_end]
        
        return memory_dump[payload_start:payload_start+1024]


### 2. Runtime Decryption Interceptor

class DecryptionInterceptor:
    """Intercept and log polymorphic decryptions"""
    
    def __init__(self):
        self.decryptions = []
        self.hooks = {}
    
    def hook_decryption_function(self, func_name: str, callback):
        """Hook decryption function for logging"""
        self.hooks[func_name] = callback
    
    def log_decryption(self, encrypted: bytes, decrypted: bytes, key: bytes):
        """Log decryption event"""
        self.decryptions.append({
            'encrypted': encrypted.hex(),
            'decrypted': decrypted.hex(),
            'key': key.hex() if key else None,
            'timestamp': __import__('time').time()
        })
    
    def export_findings(self, output_file: str):
        """Export all intercepted decryptions"""
        import json
        
        with open(output_file, 'w') as f:
            json.dump(self.decryptions, f, indent=2)
```

---

## Static Analysis Techniques

### 1. Abstract Syntax Tree (AST) Analysis for Obfuscation

```python
import ast
import json
from typing import List, Dict

class PolymorphicASTAnalyzer:
    """Analyze AST to detect polymorphic obfuscation patterns"""
    
    def __init__(self, source_code: str):
        self.source = source_code
        self.tree = ast.parse(source_code)
        self.findings = []
    
    def analyze_obfuscation_indicators(self) -> Dict:
        """Score code for obfuscation indicators"""
        
        indicators = {
            'eval_usage': self.count_eval_usage(),
            'dynamic_execution': self.detect_dynamic_execution(),
            'string_encoding': self.detect_string_encoding(),
            'control_flow_flattening': self.detect_flattening(),
            'junk_code': self.detect_junk_code(),
            'variable_renaming': self.detect_variable_renaming(),
            'dead_code': self.detect_dead_code(),
        }
        
        return indicators
    
    def count_eval_usage(self) -> int:
        """Count eval, Function, etc. usage"""
        
        count = 0
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id in ['eval', 'exec', 'Function']:
                        count += 1
        
        return count
    
    def detect_dynamic_execution(self) -> List[str]:
        """Detect dynamic code generation patterns"""
        
        patterns = []
        
        for node in ast.walk(self.tree):
            # Check for String.fromCharCode
            if isinstance(node, ast.Call):
                func_repr = ast.unparse(node.func)
                if 'fromCharCode' in func_repr or 'chr' in func_repr:
                    patterns.append(ast.unparse(node))
        
        return patterns
    
    def detect_string_encoding(self) -> List[Dict]:
        """Detect encoded/obfuscated strings"""
        
        encodings = []
        
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                string_value = node.value
                
                # Check for suspiciously short strings with high entropy
                if 0 < len(string_value) < 256:
                    entropy = self._calculate_entropy(string_value)
                    
                    if entropy > 4.0:  # High entropy threshold
                        encodings.append({
                            'value': string_value[:50],
                            'length': len(string_value),
                            'entropy': entropy
                        })
        
        return encodings
    
    def detect_flattening(self) -> Dict:
        """Detect control flow flattening patterns"""
        
        # Look for state machine patterns:
        # while True: switch/case on state variable
        
        flattening_indicators = {
            'state_machines': 0,
            'switch_statements': 0,
            'infinite_loops': 0,
        }
        
        for node in ast.walk(self.tree):
            # Detect infinite while loops
            if isinstance(node, ast.While):
                if isinstance(node.test, ast.Constant) and node.test.value is True:
                    flattening_indicators['infinite_loops'] += 1
            
            # Detect switch-like structures (multiple if/elif)
            elif isinstance(node, ast.If):
                elif_count = 0
                current = node
                while isinstance(current, ast.If) and len(current.orelse) > 0:
                    if isinstance(current.orelse[0], ast.If):
                        elif_count += 1
                        current = current.orelse[0]
                    else:
                        break
                
                if elif_count > 5:  # Many elif = flattening
                    flattening_indicators['switch_statements'] += 1
        
        return flattening_indicators
    
    def detect_junk_code(self) -> int:
        """Detect unreachable or junk code"""
        
        junk_count = 0
        
        for node in ast.walk(self.tree):
            # Detect assignments that are never used
            if isinstance(node, ast.Assign):
                # Simplified: check if variable assigned to constant
                if isinstance(node.value, (ast.Constant, ast.BinOp)):
                    junk_count += 1  # Rough heuristic
        
        return junk_count
    
    def detect_variable_renaming(self) -> Dict:
        """Detect suspicious variable naming patterns"""
        
        import re
        
        var_names = set()
        suspicious_patterns = {
            'single_letter': 0,
            'single_underscore': 0,
            'random_hex': 0,
            'unicode_escapes': 0,
        }
        
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Name):
                var_names.add(node.id)
        
        for var in var_names:
            if len(var) == 1 and var.isalpha():
                suspicious_patterns['single_letter'] += 1
            
            if var.startswith('_') and len(var) > 1:
                suspicious_patterns['single_underscore'] += 1
            
            if re.match(r'^[_0-9a-f]{8,}$', var):
                suspicious_patterns['random_hex'] += 1
        
        return suspicious_patterns
    
    def detect_dead_code(self) -> List[str]:
        """Detect unreachable code"""
        
        dead_code = []
        
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Return):
                # Check if there's code after return
                if hasattr(node, 'lineno'):
                    dead_code.append(f"Dead code at line {node.lineno}")
        
        return dead_code
    
    @staticmethod
    def _calculate_entropy(data: str) -> float:
        """Calculate Shannon entropy of string"""
        
        from collections import Counter
        import math
        
        if not data:
            return 0
        
        counts = Counter(data)
        entropy = 0
        
        for count in counts.values():
            probability = count / len(data)
            entropy -= probability * math.log2(probability)
        
        return entropy
    
    def generate_report(self) -> str:
        """Generate analysis report"""
        
        indicators = self.analyze_obfuscation_indicators()
        
        report = "Polymorphic Obfuscation Analysis Report\n"
        report += "=" * 50 + "\n\n"
        
        # Obfuscation score
        obfuscation_score = 0
        obfuscation_score += indicators['eval_usage'] * 20
        obfuscation_score += len(indicators['dynamic_execution']) * 15
        obfuscation_score += len(indicators['string_encoding']) * 10
        obfuscation_score += indicators['control_flow_flattening']['infinite_loops'] * 30
        
        report += f"Obfuscation Score: {min(100, obfuscation_score)}/100\n\n"
        
        report += "Indicators:\n"
        for key, value in indicators.items():
            report += f"  {key}: {value}\n"
        
        return report
```

---

## Heuristic Detection Methods

### 1. Entropy-Based Detection

```python
class EntropyDetector:
    """Detect polymorphic code using entropy analysis"""
    
    @staticmethod
    def analyze_entropy(data: bytes) -> float:
        """Calculate Shannon entropy"""
        
        if not data:
            return 0
        
        from collections import Counter
        import math
        
        counts = Counter(data)
        entropy = 0
        
        for count in counts.values():
            probability = count / len(data)
            if probability > 0:
                entropy -= probability * math.log2(probability)
        
        return entropy
    
    @staticmethod
    def analyze_bytes_distribution(data: bytes) -> Dict[str, float]:
        """Analyze byte value distribution"""
        
        distribution = {
            'low_entropy': False,
            'high_entropy': False,
            'uniform_distribution': False,
            'sparse_usage': False,
        }
        
        entropy = EntropyDetector.analyze_entropy(data)
        
        # Encrypted data typically has high entropy (close to 8.0)
        if entropy > 7.5:
            distribution['high_entropy'] = True
        elif entropy < 3.0:
            distribution['low_entropy'] = True
        
        # Check if bytes are uniformly distributed
        from collections import Counter
        counts = Counter(data)
        unique_bytes = len(counts)
        
        if unique_bytes > len(data) * 0.8:
            distribution['uniform_distribution'] = True
        
        # Check for sparse byte usage
        if unique_bytes < len(data) * 0.2:
            distribution['sparse_usage'] = True
        
        return distribution


class ChiSquareDetector:
    """Chi-square test for randomness detection"""
    
    @staticmethod
    def chi_square_test(data: bytes) -> float:
        """Perform chi-square test for uniformity"""
        
        from collections import Counter
        
        expected_frequency = len(data) / 256  # 256 possible byte values
        chi_square = 0
        
        counts = Counter(data)
        
        for byte_val in range(256):
            observed = counts.get(byte_val, 0)
            chi_square += ((observed - expected_frequency) ** 2) / expected_frequency
        
        return chi_square
    
    @staticmethod
    def is_random(data: bytes, threshold: float = 267) -> bool:
        """Test if data appears random (threshold for 256 DOF)"""
        chi_sq = ChiSquareDetector.chi_square_test(data)
        return chi_sq > threshold
```

---

## Forensic Investigation

### 1. Malware Behavior Timeline

```python
class ForensicTimeline:
    """Reconstruct polymorphic malware execution timeline"""
    
    def __init__(self):
        self.events = []
    
    def record_event(self, event_type: str, data: Dict, timestamp: float):
        """Record execution event"""
        
        self.events.append({
            'type': event_type,
            'data': data,
            'timestamp': timestamp
        })
    
    def analyze_decoder_chain(self) -> List[Dict]:
        """Analyze sequence of decoder invocations"""
        
        decoder_events = [
            e for e in self.events 
            if e['type'] == 'decoder_execution'
        ]
        
        return decoder_events
    
    def detect_polymorphic_mutation_cycle(self) -> bool:
        """Detect if code is mutating during execution"""
        
        memory_events = [
            e for e in self.events 
            if e['type'] == 'memory_modification'
        ]
        
        # Look for repeated modifications to code sections
        if len(memory_events) > 3:
            for i in range(len(memory_events) - 1):
                e1 = memory_events[i]
                e2 = memory_events[i + 1]
                
                # If same address modified multiple times
                if e1['data'].get('address') == e2['data'].get('address'):
                    return True
        
        return False
    
    def generate_timeline_report(self, output_file: str):
        """Export timeline in readable format"""
        
        with open(output_file, 'w') as f:
            f.write("Polymorphic Malware Execution Timeline\n")
            f.write("=" * 50 + "\n\n")
            
            for event in sorted(self.events, key=lambda x: x['timestamp']):
                f.write(f"[{event['timestamp']:.2f}] {event['type']}\n")
                for key, value in event['data'].items():
                    f.write(f"  {key}: {value}\n")
                f.write("\n")
```

---

## Tool Implementations

### 1. Integrated Polymorphic Analysis Framework

```python
#!/usr/bin/env python3

class PolymorphicAnalysisFramework:
    """Complete framework for polymorphic code analysis"""
    
    def __init__(self, sample_path: str):
        self.sample = sample_path
        self.results = {}
    
    def run_full_analysis(self) -> Dict:
        """Run complete analysis pipeline"""
        
        # Step 1: Static analysis
        print("[*] Running static analysis...")
        static_results = self._static_analysis()
        self.results['static'] = static_results
        
        # Step 2: Dynamic analysis
        print("[*] Running dynamic analysis...")
        dynamic_results = self._dynamic_analysis()
        self.results['dynamic'] = dynamic_results
        
        # Step 3: Entropy analysis
        print("[*] Running entropy analysis...")
        entropy_results = self._entropy_analysis()
        self.results['entropy'] = entropy_results
        
        # Step 4: Generate report
        print("[*] Generating report...")
        self._generate_comprehensive_report()
        
        return self.results
    
    def _static_analysis(self) -> Dict:
        """Perform static analysis"""
        
        with open(self.sample, 'r') as f:
            source = f.read()
        
        analyzer = PolymorphicASTAnalyzer(source)
        return analyzer.analyze_obfuscation_indicators()
    
    def _dynamic_analysis(self) -> Dict:
        """Perform dynamic analysis"""
        # Placeholder for dynamic analysis
        return {}
    
    def _entropy_analysis(self) -> Dict:
        """Perform entropy analysis"""
        
        with open(self.sample, 'rb') as f:
            data = f.read()
        
        entropy = EntropyDetector.analyze_entropy(data)
        distribution = EntropyDetector.analyze_bytes_distribution(data)
        
        return {
            'entropy': entropy,
            'distribution': distribution,
            'is_random': ChiSquareDetector.is_random(data)
        }
    
    def _generate_comprehensive_report(self):
        """Generate comprehensive analysis report"""
        
        report = "POLYMORPHIC CODE ANALYSIS REPORT\n"
        report += "=" * 70 + "\n\n"
        
        # Static analysis results
        if 'static' in self.results:
            report += "STATIC ANALYSIS RESULTS\n"
            report += "-" * 70 + "\n"
            for key, value in self.results['static'].items():
                report += f"{key}: {value}\n"
            report += "\n"
        
        # Dynamic analysis results
        if 'dynamic' in self.results:
            report += "DYNAMIC ANALYSIS RESULTS\n"
            report += "-" * 70 + "\n"
            for key, value in self.results['dynamic'].items():
                report += f"{key}: {value}\n"
            report += "\n"
        
        # Entropy results
        if 'entropy' in self.results:
            report += "ENTROPY ANALYSIS\n"
            report += "-" * 70 + "\n"
            report += f"Shannon Entropy: {self.results['entropy']['entropy']:.4f}\n"
            report += f"Distribution: {self.results['entropy']['distribution']}\n"
            report += f"Random Data: {self.results['entropy']['is_random']}\n"
            report += "\n"
        
        # Conclusion
        report += "CONCLUSION\n"
        report += "-" * 70 + "\n"
        report += self._generate_conclusion()
        
        with open('polymorphic_analysis_report.txt', 'w') as f:
            f.write(report)
        
        print(report)
    
    def _generate_conclusion(self) -> str:
        """Generate analysis conclusion"""
        
        conclusion = ""
        
        static = self.results.get('static', {})
        entropy = self.results.get('entropy', {})
        
        # Scoring
        score = 0
        
        if static.get('eval_usage', 0) > 0:
            score += 20
            conclusion += "* High use of eval/dynamic execution\n"
        
        if entropy.get('is_random'):
            score += 30
            conclusion += "* Entropy analysis suggests encrypted/random data\n"
        
        if static.get('control_flow_flattening', {}).get('infinite_loops', 0) > 0:
            score += 25
            conclusion += "* Control flow flattening detected\n"
        
        if len(static.get('dynamic_execution', [])) > 0:
            score += 15
            conclusion += "* Dynamic code generation detected\n"
        
        if score > 50:
            conclusion += f"\nRISK LEVEL: HIGH (Score: {score}/100)\n"
            conclusion += "This code exhibits strong indicators of polymorphic obfuscation.\n"
        elif score > 30:
            conclusion += f"\nRISK LEVEL: MEDIUM (Score: {score}/100)\n"
            conclusion += "This code exhibits moderate obfuscation indicators.\n"
        else:
            conclusion += f"\nRISK LEVEL: LOW (Score: {score}/100)\n"
            conclusion += "This code shows minimal obfuscation indicators.\n"
        
        return conclusion
```

---

## Usage Examples

```bash
# Analyze JavaScript file for obfuscation
python3 -c "
from analysis_tools import PolymorphicAnalysisFramework

framework = PolymorphicAnalysisFramework('malware.js')
results = framework.run_full_analysis()
"

# Extract memory dump of running process
python3 -c "
from memory_tools import PolymorphicMemoryAnalyzer

analyzer = PolymorphicMemoryAnalyzer(pid=1234)
analyzer.dump_process_memory('/tmp/memory.bin')
findings = analyzer.find_polymorphic_patterns(open('/tmp/memory.bin', 'rb').read())
print(f'Found {len(findings)} potential decoder stubs')
"

# Run entropy analysis
python3 -c "
from detection_tools import EntropyDetector

data = open('encrypted_payload.bin', 'rb').read()
entropy = EntropyDetector.analyze_entropy(data)
print(f'Entropy: {entropy:.4f}')
"
```

---

## Conclusion

This toolkit provides comprehensive methods for:

1. **Memory analysis** to extract polymorphic payloads
2. **Static analysis** of code structure and obfuscation patterns
3. **Entropy-based detection** for encrypted/random data
4. **Heuristic detection** using behavioral signatures
5. **Forensic reconstruction** of malware execution flow

Defenders can use these techniques to:
- Identify polymorphic code in samples
- Extract and analyze hidden payloads
- Track mutation cycles
- Score obfuscation complexity
- Generate automated detection signatures

