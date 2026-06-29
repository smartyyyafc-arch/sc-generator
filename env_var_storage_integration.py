#!/usr/bin/env python3
"""
Environment Variable Storage Integration
Integration with Flask API and payload generator
Provides endpoints for storing and retrieving payloads via environment variables
"""

from flask import Flask, request, jsonify
from env_var_storage import (
    EnvVarWriter, EnvVarReader, EnvVarConfig,
    EnvVarScope, EnvVarEncoding, create_env_var_writer
)
from typing import Dict, List, Optional, Tuple
import json
import logging


logger = logging.getLogger(__name__)


class EnvVarStorageManager:
    """Manages environment variable storage for payloads"""

    def __init__(self, default_scope: EnvVarScope = EnvVarScope.USER,
                 default_encoding: EnvVarEncoding = EnvVarEncoding.BASE64):
        """Initialize storage manager"""
        self.default_scope = default_scope
        self.default_encoding = default_encoding
        self.writers: Dict[str, EnvVarWriter] = {}
        self.readers: Dict[str, EnvVarReader] = {}

    def get_writer(self, scope: Optional[EnvVarScope] = None) -> EnvVarWriter:
        """Get or create writer for scope"""
        scope = scope or self.default_scope
        scope_key = scope.value

        if scope_key not in self.writers:
            config = EnvVarConfig(scope=scope, encoding=self.default_encoding)
            self.writers[scope_key] = EnvVarWriter(config)

        return self.writers[scope_key]

    def get_reader(self) -> EnvVarReader:
        """Get reader"""
        if "reader" not in self.readers:
            self.readers["reader"] = EnvVarReader()
        return self.readers["reader"]

    def store_payload(self, payload_id: str, payload_content: str,
                     scope: Optional[EnvVarScope] = None,
                     encoding: Optional[EnvVarEncoding] = None,
                     metadata: Optional[Dict] = None) -> Tuple[bool, List[str], str]:
        """Store payload in environment variables"""
        writer = self.get_writer(scope)

        # Update encoding if specified
        if encoding:
            writer.config.encoding = encoding

        try:
            success, vars_list, message = writer.write_to_env(payload_id, payload_content)

            if success and metadata:
                # Store additional metadata
                var_metadata = writer.get_var_metadata()
                for var_name in vars_list:
                    if var_name in var_metadata:
                        var_metadata[var_name].update(metadata)

            return success, vars_list, message
        except Exception as e:
            return False, [], str(e)

    def get_storage_info(self, payload_id: str) -> Dict:
        """Get information about stored payload"""
        writer = self.get_writer()
        metadata = writer.get_var_metadata()

        obfuscated_name = writer.obfuscate_var_name(payload_id)

        info = {
            "payload_id": payload_id,
            "obfuscated_name": obfuscated_name,
            "variables": {},
            "total_size": 0
        }

        for var_name, var_meta in metadata.items():
            if var_name.startswith(obfuscated_name):
                info["variables"][var_name] = var_meta
                info["total_size"] += var_meta.get("size", 0)

        return info

    def get_retrieval_script(self, payload_id: str, language: str = "vbs") -> Optional[str]:
        """Get script to retrieve payload"""
        writer = self.get_writer()
        try:
            return writer.get_retrieval_code(payload_id, language)
        except Exception as e:
            logger.error(f"Failed to generate retrieval script: {e}")
            return None

    def list_stored_payloads(self) -> List[Dict]:
        """List all stored payloads"""
        reader = self.get_reader()
        payloads = []

        vars_list = reader.list_payload_vars()
        for var_name in vars_list:
            payloads.append({
                "variable_name": var_name,
                "env_var": var_name
            })

        return payloads


class EnvVarFlaskIntegration:
    """Flask integration for environment variable storage"""

    def __init__(self, app: Flask, manager: Optional[EnvVarStorageManager] = None):
        """Initialize Flask integration"""
        self.app = app
        self.manager = manager or EnvVarStorageManager()
        self._register_routes()

    def _register_routes(self):
        """Register API routes"""

        @self.app.route('/api/env-storage/store', methods=['POST'])
        def store_payload():
            """Store payload in environment variables"""
            try:
                data = request.get_json()
                payload_id = data.get('payload_id')
                payload_content = data.get('payload_content')
                scope = data.get('scope', 'user')
                encoding = data.get('encoding', 'base64')

                if not payload_id or not payload_content:
                    return jsonify({'error': 'Missing payload_id or payload_content'}), 400

                # Convert string scope/encoding to enum
                scope_enum = EnvVarScope(scope)
                encoding_enum = EnvVarEncoding(encoding)

                success, vars_list, message = self.manager.store_payload(
                    payload_id, payload_content,
                    scope=scope_enum,
                    encoding=encoding_enum,
                    metadata=data.get('metadata')
                )

                if success:
                    return jsonify({
                        'success': True,
                        'payload_id': payload_id,
                        'variables': vars_list,
                        'count': len(vars_list),
                        'message': message
                    }), 200
                else:
                    return jsonify({
                        'success': False,
                        'error': message
                    }), 400

            except ValueError as e:
                return jsonify({'error': f'Invalid scope or encoding: {str(e)}'}), 400
            except Exception as e:
                logger.error(f"Error storing payload: {e}")
                return jsonify({'error': str(e)}), 500

        @self.app.route('/api/env-storage/retrieve/<payload_id>', methods=['GET'])
        def retrieve_payload(payload_id):
            """Get retrieval script for payload"""
            try:
                language = request.args.get('language', 'vbs')

                script = self.manager.get_retrieval_script(payload_id, language)
                if script:
                    return jsonify({
                        'success': True,
                        'payload_id': payload_id,
                        'language': language,
                        'script': script
                    }), 200
                else:
                    return jsonify({'error': 'Failed to generate retrieval script'}), 500

            except Exception as e:
                logger.error(f"Error retrieving script: {e}")
                return jsonify({'error': str(e)}), 500

        @self.app.route('/api/env-storage/info/<payload_id>', methods=['GET'])
        def get_storage_info(payload_id):
            """Get storage information for payload"""
            try:
                info = self.manager.get_storage_info(payload_id)
                return jsonify({
                    'success': True,
                    'info': info
                }), 200
            except Exception as e:
                logger.error(f"Error getting storage info: {e}")
                return jsonify({'error': str(e)}), 500

        @self.app.route('/api/env-storage/list', methods=['GET'])
        def list_payloads():
            """List all stored payloads"""
            try:
                payloads = self.manager.list_stored_payloads()
                return jsonify({
                    'success': True,
                    'payloads': payloads,
                    'count': len(payloads)
                }), 200
            except Exception as e:
                logger.error(f"Error listing payloads: {e}")
                return jsonify({'error': str(e)}), 500

        @self.app.route('/api/env-storage/config', methods=['GET'])
        def get_config():
            """Get storage configuration options"""
            return jsonify({
                'success': True,
                'scopes': [s.value for s in EnvVarScope],
                'encodings': [e.value for e in EnvVarEncoding],
                'default_scope': self.manager.default_scope.value,
                'default_encoding': self.manager.default_encoding.value
            }), 200

        @self.app.route('/api/env-storage/validate', methods=['POST'])
        def validate_payload():
            """Validate if payload can be stored"""
            try:
                data = request.get_json()
                payload_content = data.get('payload_content', '')

                writer = self.manager.get_writer()
                is_valid = writer._validate_env_var_value(payload_content)

                return jsonify({
                    'success': True,
                    'valid': is_valid,
                    'size': len(payload_content),
                    'max_size': 32767,
                    'message': 'Payload size is within limits' if is_valid else 'Payload exceeds size limits'
                }), 200

            except Exception as e:
                return jsonify({'error': str(e)}), 500


def create_env_var_storage_api(app: Flask) -> EnvVarFlaskIntegration:
    """Factory function to create Flask integration"""
    manager = EnvVarStorageManager()
    integration = EnvVarFlaskIntegration(app, manager)
    return integration


# Example usage and documentation
EXAMPLE_USAGE = """
# Environment Variable Storage Integration

## API Endpoints

### 1. Store Payload
POST /api/env-storage/store
{
    "payload_id": "myPayload",
    "payload_content": "Your payload content here",
    "scope": "user",  # or "system", "process"
    "encoding": "base64",  # or "hex", "chunked_base64", "chunked_hex", "raw"
    "metadata": {
        "type": "persistent",
        "version": "1.0"
    }
}

Response:
{
    "success": true,
    "payload_id": "myPayload",
    "variables": ["SC_VAR_ABC123_META", "SC_VAR_ABC123_CHUNK_000", ...],
    "count": 3,
    "message": "Successfully stored payload in 3 environment variables"
}

### 2. Get Retrieval Script
GET /api/env-storage/retrieve/myPayload?language=vbs

Response:
{
    "success": true,
    "payload_id": "myPayload",
    "language": "vbs",
    "script": "... VBS code to retrieve payload ..."
}

### 3. Get Storage Info
GET /api/env-storage/info/myPayload

Response:
{
    "success": true,
    "info": {
        "payload_id": "myPayload",
        "obfuscated_name": "SC_VAR_ABC123",
        "variables": {
            "SC_VAR_ABC123_META": {...},
            "SC_VAR_ABC123_CHUNK_000": {...}
        },
        "total_size": 1024
    }
}

### 4. List All Stored Payloads
GET /api/env-storage/list

Response:
{
    "success": true,
    "payloads": [
        {"variable_name": "SC_VAR_ABC123", "env_var": "SC_VAR_ABC123"},
        ...
    ],
    "count": 5
}

### 5. Get Configuration
GET /api/env-storage/config

Response:
{
    "success": true,
    "scopes": ["user", "system", "process"],
    "encodings": ["raw", "base64", "hex", "chunked_base64", "chunked_hex"],
    "default_scope": "user",
    "default_encoding": "base64"
}

### 6. Validate Payload
POST /api/env-storage/validate
{
    "payload_content": "Your payload content"
}

Response:
{
    "success": true,
    "valid": true,
    "size": 256,
    "max_size": 32767,
    "message": "Payload size is within limits"
}

## Usage in Flask App

from flask import Flask
from env_var_storage_integration import create_env_var_storage_api

app = Flask(__name__)
env_storage = create_env_var_storage_api(app)

if __name__ == '__main__':
    app.run(debug=True)
"""


if __name__ == "__main__":
    print(EXAMPLE_USAGE)
