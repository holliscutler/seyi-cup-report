"""
Research-Validated Power Profile Templates

All profiles based on:
- research/QUICK_REFERENCE.md
- research/DAY1_RESEARCH_SUMMARY.md
- src/swarm/power_profiles.py (PROFILE_TEMPLATES)

Each template represents real servo press behavior documented in literature.
"""

from typing import Dict, Any
from ..utils.constants import (
    POWER_RANGES,
    CYCLE_TIMES,
    STANDARD_PHASE_RATIOS,
    PHASE_POWER_LEVELS,
)


# ============================================================================
# PROFILE TEMPLATES (Research-Based)
# ============================================================================

VALIDATED_TEMPLATES: Dict[str, Dict[str, Any]] = {

    # ---------------------------------------------------------------------
    # SMALL_FAST: 100-ton press, fast cycles
    # Source: QUICK_REFERENCE.md - "Small Press (100 tons)"
    # Applications: Small stampings, electronics
    # SPM: 30-60
    # ---------------------------------------------------------------------
    'small_fast': {
        'press_type': 'SMALL_100T',
        'capacity_tons': 100,
        'peak_power_kw': 85,
        'cycle_time_sec': 18.0,
        'motion_type': 'STANDARD',

        # Phase structure (fractions of cycle time)
        'phases': {
            'approach': {
                'duration_ratio': 0.28,      # 5.0s out of 18s
                'power_start_ratio': 0.20,   # 17 kW
                'power_end_ratio': 0.30,     # 25.5 kW
                'curve_type': 'ramp',
            },
            'forming': {
                'duration_ratio': 0.33,      # 6.0s out of 18s
                'power_start_ratio': 0.60,   # 51 kW
                'power_peak_ratio': 1.00,    # 85 kW
                'power_end_ratio': 0.70,     # 59.5 kW
                'curve_type': 'bell',
            },
            'return': {
                'duration_ratio': 0.24,      # 4.3s out of 18s
                'power_start_ratio': 0.40,   # 34 kW
                'power_end_ratio': 0.20,     # 17 kW
                'curve_type': 'ramp',
            },
            'idle': {
                'duration_ratio': 0.15,      # 2.7s out of 18s
                'power_start_ratio': 0.05,   # 4.25 kW
                'power_end_ratio': 0.05,     # 4.25 kW
                'curve_type': 'constant',
            },
        },

        'metadata': {
            'description': 'Small, fast press for high-volume production',
            'applications': 'Small stampings, electronics components',
            'typical_spm': '30-60',
            'energy_per_cycle_kwh': 0.25,
        }
    },

    # ---------------------------------------------------------------------
    # MEDIUM_STANDARD: 200-ton press, standard cycles
    # Source: QUICK_REFERENCE.md - "Medium Press (200 tons)"
    # This is the reference profile from research
    # Applications: Automotive parts, general stamping
    # SPM: 20-40
    # ---------------------------------------------------------------------
    'medium_standard': {
        'press_type': 'MEDIUM_200T',
        'capacity_tons': 200,
        'peak_power_kw': 180,
        'cycle_time_sec': 25.0,
        'motion_type': 'STANDARD',

        # Phase structure matches QUICK_REFERENCE.md example
        # Approach: 0-7s (28%), Forming: 7-15s (32%), Return: 15-21s (24%), Idle: 21-25s (16%)
        'phases': {
            'approach': {
                'duration_ratio': 0.28,      # 7.0s out of 25s
                'power_start_ratio': 0.20,   # 36 kW
                'power_end_ratio': 0.30,     # 54 kW
                'curve_type': 'ramp',
            },
            'forming': {
                'duration_ratio': 0.32,      # 8.0s out of 25s
                'power_start_ratio': 0.60,   # 108 kW
                'power_peak_ratio': 1.00,    # 180 kW
                'power_end_ratio': 0.70,     # 126 kW
                'curve_type': 'bell',
            },
            'return': {
                'duration_ratio': 0.24,      # 6.0s out of 25s
                'power_start_ratio': 0.40,   # 72 kW
                'power_end_ratio': 0.20,     # 36 kW
                'curve_type': 'ramp',
            },
            'idle': {
                'duration_ratio': 0.16,      # 4.0s out of 25s
                'power_start_ratio': 0.05,   # 9 kW
                'power_end_ratio': 0.05,     # 9 kW
                'curve_type': 'constant',
            },
        },

        'metadata': {
            'description': 'Standard 200-ton press, most common in factories',
            'applications': 'Automotive parts, general metal stamping',
            'typical_spm': '20-40',
            'energy_per_cycle_kwh': 0.45,
        }
    },

    # ---------------------------------------------------------------------
    # MEDIUM_COINING: 200-ton press with dwell (coining operation)
    # Source: QUICK_REFERENCE.md - Motion Profile Types - "Coining"
    # Applications: High-precision parts, springback control
    # Dwell time: 2-5 seconds typical (using 3s)
    # ---------------------------------------------------------------------
    'medium_coining': {
        'press_type': 'MEDIUM_200T',
        'capacity_tons': 200,
        'peak_power_kw': 190,     # Slightly higher due to sustained force
        'cycle_time_sec': 30.0,   # +20% longer than standard
        'motion_type': 'COINING',

        'phases': {
            'approach': {
                'duration_ratio': 0.23,      # 7.0s out of 30s
                'power_start_ratio': 0.20,   # 38 kW
                'power_end_ratio': 0.30,     # 57 kW
                'curve_type': 'ramp',
            },
            'forming': {
                'duration_ratio': 0.43,      # 13.0s out of 30s (includes 3s dwell)
                'power_start_ratio': 0.60,   # 114 kW
                'power_peak_ratio': 1.00,    # 190 kW (sustained during dwell)
                'power_end_ratio': 0.70,     # 133 kW
                'curve_type': 'bell',        # But with plateau at peak
                'has_dwell': True,
                'dwell_duration_sec': 3.0,
            },
            'return': {
                'duration_ratio': 0.20,      # 6.0s out of 30s
                'power_start_ratio': 0.40,   # 76 kW
                'power_end_ratio': 0.20,     # 38 kW
                'curve_type': 'ramp',
            },
            'idle': {
                'duration_ratio': 0.14,      # 4.0s out of 30s
                'power_start_ratio': 0.05,   # 9.5 kW
                'power_end_ratio': 0.05,     # 9.5 kW
                'curve_type': 'constant',
            },
        },

        'metadata': {
            'description': 'Coining press with dwell at BDC for precision',
            'applications': 'High-precision parts, springback control, coining',
            'typical_spm': '15-30',
            'energy_per_cycle_kwh': 0.60,
            'dwell_time_sec': 3.0,
        }
    },

    # ---------------------------------------------------------------------
    # LARGE_SLOW: 300-ton press, slower cycles
    # Source: QUICK_REFERENCE.md - "Large Press (300 tons)"
    # Applications: Heavy structural parts, deep draw
    # SPM: 15-25
    # ---------------------------------------------------------------------
    'large_slow': {
        'press_type': 'LARGE_300T',
        'capacity_tons': 300,
        'peak_power_kw': 270,
        'cycle_time_sec': 35.0,
        'motion_type': 'STANDARD',

        'phases': {
            'approach': {
                'duration_ratio': 0.28,      # 9.8s out of 35s
                'power_start_ratio': 0.20,   # 54 kW
                'power_end_ratio': 0.30,     # 81 kW
                'curve_type': 'ramp',
            },
            'forming': {
                'duration_ratio': 0.34,      # 12.0s out of 35s
                'power_start_ratio': 0.60,   # 162 kW
                'power_peak_ratio': 1.00,    # 270 kW
                'power_end_ratio': 0.70,     # 189 kW
                'curve_type': 'bell',
            },
            'return': {
                'duration_ratio': 0.23,      # 8.0s out of 35s
                'power_start_ratio': 0.40,   # 108 kW
                'power_end_ratio': 0.20,     # 54 kW
                'curve_type': 'ramp',
            },
            'idle': {
                'duration_ratio': 0.15,      # 5.2s out of 35s
                'power_start_ratio': 0.05,   # 13.5 kW
                'power_end_ratio': 0.05,     # 13.5 kW
                'curve_type': 'constant',
            },
        },

        'metadata': {
            'description': 'Large press for heavy structural parts',
            'applications': 'Heavy structural components, deep drawing',
            'typical_spm': '15-25',
            'energy_per_cycle_kwh': 0.75,
        }
    },

    # ---------------------------------------------------------------------
    # MEDIUM_PULSATING: 200-ton press with pulsating motion
    # Source: QUICK_REFERENCE.md - Motion Profile Types - "Pulsating"
    # Research finding: 92.3% greater forming depth
    # Applications: Complex forming, re-lubrication
    # ---------------------------------------------------------------------
    'medium_pulsating': {
        'press_type': 'MEDIUM_200T',
        'capacity_tons': 200,
        'peak_power_kw': 185,
        'cycle_time_sec': 28.0,    # +10-20% vs standard
        'motion_type': 'PULSATING',

        'phases': {
            'approach': {
                'duration_ratio': 0.25,      # 7.0s out of 28s
                'power_start_ratio': 0.20,   # 37 kW
                'power_end_ratio': 0.30,     # 55.5 kW
                'curve_type': 'ramp',
            },
            'forming': {
                'duration_ratio': 0.36,      # 10.0s out of 28s (includes pause)
                'power_start_ratio': 0.60,   # 111 kW
                'power_peak_ratio': 1.00,    # 185 kW
                'power_end_ratio': 0.70,     # 129.5 kW
                'curve_type': 'bell',
                'has_pulse': True,
                'pulse_pause_ratio': 0.1,    # 10% of forming time is pause
            },
            'return': {
                'duration_ratio': 0.24,      # 6.7s out of 28s
                'power_start_ratio': 0.40,   # 74 kW
                'power_end_ratio': 0.20,     # 37 kW
                'curve_type': 'ramp',
            },
            'idle': {
                'duration_ratio': 0.15,      # 4.3s out of 28s
                'power_start_ratio': 0.05,   # 9.25 kW
                'power_end_ratio': 0.05,     # 9.25 kW
                'curve_type': 'constant',
            },
        },

        'metadata': {
            'description': 'Pulsating motion for complex forming operations',
            'applications': 'Complex forming, re-lubrication, AHSS materials',
            'typical_spm': '18-35',
            'energy_per_cycle_kwh': 0.52,
            'research_note': '92.3% greater forming depth vs standard (literature)',
        }
    },

    # ---------------------------------------------------------------------
    # SMALL_HIGH_SPEED: 100-ton press optimized for speed
    # Source: Derived from research for high-volume applications
    # Applications: Blanking, piercing, high-speed stamping
    # SPM: 50-60
    # ---------------------------------------------------------------------
    'small_high_speed': {
        'press_type': 'SMALL_100T',
        'capacity_tons': 100,
        'peak_power_kw': 90,
        'cycle_time_sec': 15.0,    # Very fast
        'motion_type': 'STANDARD',

        'phases': {
            'approach': {
                'duration_ratio': 0.27,      # 4.0s out of 15s
                'power_start_ratio': 0.25,   # 22.5 kW (faster = more power)
                'power_end_ratio': 0.35,     # 31.5 kW
                'curve_type': 'ramp',
            },
            'forming': {
                'duration_ratio': 0.33,      # 5.0s out of 15s
                'power_start_ratio': 0.65,   # 58.5 kW
                'power_peak_ratio': 1.00,    # 90 kW
                'power_end_ratio': 0.70,     # 63 kW
                'curve_type': 'bell',
            },
            'return': {
                'duration_ratio': 0.27,      # 4.0s out of 15s
                'power_start_ratio': 0.45,   # 40.5 kW (faster return)
                'power_end_ratio': 0.25,     # 22.5 kW
                'curve_type': 'ramp',
            },
            'idle': {
                'duration_ratio': 0.13,      # 2.0s out of 15s
                'power_start_ratio': 0.05,   # 4.5 kW
                'power_end_ratio': 0.05,     # 4.5 kW
                'curve_type': 'constant',
            },
        },

        'metadata': {
            'description': 'High-speed small press for volume production',
            'applications': 'Blanking, piercing, high-volume stamping',
            'typical_spm': '50-60',
            'energy_per_cycle_kwh': 0.20,
        }
    },

    # ---------------------------------------------------------------------
    # MEDIUM_HEAVY_GAUGE: 200-ton press for thick materials (AHSS)
    # Source: Research mentions AHSS applications
    # Applications: Advanced high-strength steel forming
    # Slower cycles due to material requirements
    # ---------------------------------------------------------------------
    'medium_heavy_gauge': {
        'press_type': 'MEDIUM_200T',
        'capacity_tons': 200,
        'peak_power_kw': 195,      # Higher power for tough materials
        'cycle_time_sec': 32.0,    # Slower for AHSS
        'motion_type': 'STANDARD',

        'phases': {
            'approach': {
                'duration_ratio': 0.25,      # 8.0s out of 32s
                'power_start_ratio': 0.20,   # 39 kW
                'power_end_ratio': 0.30,     # 58.5 kW
                'curve_type': 'ramp',
            },
            'forming': {
                'duration_ratio': 0.38,      # 12.0s out of 32s (longer for AHSS)
                'power_start_ratio': 0.65,   # 126.75 kW
                'power_peak_ratio': 1.00,    # 195 kW
                'power_end_ratio': 0.75,     # 146.25 kW
                'curve_type': 'bell',
            },
            'return': {
                'duration_ratio': 0.22,      # 7.0s out of 32s
                'power_start_ratio': 0.40,   # 78 kW
                'power_end_ratio': 0.20,     # 39 kW
                'curve_type': 'ramp',
            },
            'idle': {
                'duration_ratio': 0.15,      # 5.0s out of 32s
                'power_start_ratio': 0.05,   # 9.75 kW
                'power_end_ratio': 0.05,     # 9.75 kW
                'curve_type': 'constant',
            },
        },

        'metadata': {
            'description': 'Medium press optimized for AHSS materials',
            'applications': 'Advanced high-strength steel, thick gauge forming',
            'typical_spm': '15-25',
            'energy_per_cycle_kwh': 0.65,
            'material_note': 'Optimized for AHSS',
        }
    },

    # ---------------------------------------------------------------------
    # LARGE_PROGRESSIVE: 300-ton progressive die press
    # Source: Research mentions multi-operation forming
    # Applications: Progressive die stamping
    # Multiple forming operations in single stroke
    # ---------------------------------------------------------------------
    'large_progressive': {
        'press_type': 'LARGE_300T',
        'capacity_tons': 300,
        'peak_power_kw': 280,
        'cycle_time_sec': 38.0,
        'motion_type': 'STANDARD',

        'phases': {
            'approach': {
                'duration_ratio': 0.26,      # 10.0s out of 38s
                'power_start_ratio': 0.20,   # 56 kW
                'power_end_ratio': 0.30,     # 84 kW
                'curve_type': 'ramp',
            },
            'forming': {
                'duration_ratio': 0.37,      # 14.0s out of 38s (multi-stage)
                'power_start_ratio': 0.60,   # 168 kW
                'power_peak_ratio': 1.00,    # 280 kW
                'power_end_ratio': 0.70,     # 196 kW
                'curve_type': 'bell',
                'is_progressive': True,
            },
            'return': {
                'duration_ratio': 0.23,      # 9.0s out of 38s
                'power_start_ratio': 0.40,   # 112 kW
                'power_end_ratio': 0.20,     # 56 kW
                'curve_type': 'ramp',
            },
            'idle': {
                'duration_ratio': 0.14,      # 5.0s out of 38s
                'power_start_ratio': 0.05,   # 14 kW
                'power_end_ratio': 0.05,     # 14 kW
                'curve_type': 'constant',
            },
        },

        'metadata': {
            'description': 'Large progressive die press, multi-stage forming',
            'applications': 'Progressive die stamping, complex multi-operation parts',
            'typical_spm': '12-20',
            'energy_per_cycle_kwh': 0.85,
            'tooling_note': 'Progressive die configuration',
        }
    },
}


# Quick access to template names
TEMPLATE_NAMES = list(VALIDATED_TEMPLATES.keys())

# Categorize templates by press size
TEMPLATES_BY_SIZE = {
    'SMALL': ['small_fast', 'small_high_speed'],
    'MEDIUM': ['medium_standard', 'medium_coining', 'medium_pulsating', 'medium_heavy_gauge'],
    'LARGE': ['large_slow', 'large_progressive'],
}

# Categorize templates by motion type
TEMPLATES_BY_MOTION = {
    'STANDARD': ['small_fast', 'small_high_speed', 'medium_standard',
                 'medium_heavy_gauge', 'large_slow', 'large_progressive'],
    'COINING': ['medium_coining'],
    'PULSATING': ['medium_pulsating'],
}
