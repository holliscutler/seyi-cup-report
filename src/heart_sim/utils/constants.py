"""
Research-Validated Constants for Cardiac Servo Press Simulation

All values sourced from research documentation:
- research/QUICK_REFERENCE.md
- research/DAY1_RESEARCH_SUMMARY.md
"""

# ============================================================================
# SERVO PRESS SPECIFICATIONS (From Research)
# ============================================================================

# Standard press capacities (tons)
PRESS_CAPACITIES = {
    'SMALL_100T': 100,      # 1000 kN
    'MEDIUM_200T': 200,     # 2000 kN
    'LARGE_300T': 300,      # 3000 kN
    'HEAVY_600T': 600,      # 6000 kN
}

# Research-validated power ranges (kW)
# Source: QUICK_REFERENCE.md, Section "Profile Variations by Press Capacity"
POWER_RANGES = {
    'SMALL_100T': {'peak': 85, 'avg': 30, 'idle': 5},
    'MEDIUM_200T': {'peak': 180, 'avg': 65, 'idle': 5},
    'LARGE_300T': {'peak': 270, 'avg': 100, 'idle': 8},
    'HEAVY_600T': {'peak': 500, 'avg': 180, 'idle': 10},
}

# Research-validated cycle times (seconds)
# Source: QUICK_REFERENCE.md
CYCLE_TIMES = {
    'SMALL_100T': 18.0,     # Fast press, 30-60 SPM
    'MEDIUM_200T': 25.0,    # Standard press, 20-40 SPM
    'LARGE_300T': 35.0,     # Slow press, 15-25 SPM
    'HEAVY_600T': 40.0,     # Heavy press, 8-15 SPM
}

# ============================================================================
# PHASE DURATIONS (From Research)
# ============================================================================

# Standard phase structure from QUICK_REFERENCE.md
# Based on 200-ton servo press (25 seconds total cycle)
# Approach: 0-7s (28%), Forming: 7-15s (32%), Return: 15-21s (24%), Idle: 21-25s (16%)

STANDARD_PHASE_RATIOS = {
    'approach': 0.28,   # 28% of cycle - rapid descent
    'forming': 0.32,    # 32% of cycle - high power deformation
    'return': 0.24,     # 24% of cycle - fast return to top
    'idle': 0.16,       # 16% of cycle - waiting for next part
}

# Power levels per phase (as fraction of peak power)
# Source: QUICK_REFERENCE.md, "Standard Profile Template"
PHASE_POWER_LEVELS = {
    'approach': {
        'start': 0.20,   # 20% of peak at start
        'end': 0.30,     # 30% of peak at end (ramping up)
    },
    'forming': {
        'start': 0.60,   # 60% of peak at contact
        'peak': 1.00,    # 100% of peak during forming
        'end': 0.70,     # 70% of peak at release
    },
    'return': {
        'start': 0.40,   # 40% of peak
        'end': 0.20,     # 20% of peak
    },
    'idle': {
        'constant': 0.05,  # 5% of peak (motor idling)
    }
}

# ============================================================================
# CARDIAC COORDINATION PARAMETERS
# ============================================================================

# Refractory period (based on cardiac physiology adapted to servo presses)
# This is the minimum rest after high-power operation
MIN_REFRACTORY_RATIO = 0.30  # 30% of cycle time minimum rest

# Collision prediction window (seconds)
# How far ahead to predict neighbor peaks
PREDICTION_WINDOW_SEC = 10.0

# Maximum delay allowed (seconds)
# From current implementation and practical constraints
MAX_DELAY_DEFAULT_SEC = 5.0

# Collision risk threshold
# Above this value, we consider it a collision requiring delay
COLLISION_RISK_THRESHOLD = 0.5

# Forming phase overlap tolerance (fraction of cycle)
# How much forming phase overlap is acceptable
FORMING_OVERLAP_TOLERANCE = 0.35

# ============================================================================
# TAIWAN ELECTRICITY PRICING (From Research)
# ============================================================================

# Base rates (NT$/kWh)
# Source: DAY1_RESEARCH_SUMMARY.md, Part 3
TAIWAN_RATES = {
    'base': 4.27,           # Base industrial rate
    'off_peak': 4.27,       # Off-peak hours
    'peak': 7.50,           # Peak hours (10 AM-12 PM, 1-5 PM)
    'super_peak': 9.90,     # Super peak (3-9 PM for large users)
}

# Time-of-Use (TOU) hour definitions (24-hour format)
TOU_HOURS = {
    'super_peak': list(range(15, 21)),  # 3 PM - 9 PM
    'peak': list(range(10, 12)) + list(range(13, 15)),  # 10 AM-12 PM, 1-3 PM
    'off_peak': list(range(0, 10)) + list(range(21, 24)),  # Rest of day
}

# Demand charge (NT$/kW per month)
# Based on highest 15-minute average power consumption
# Source: Research notes - "30-40% of total bill"
DEMAND_CHARGE_RATE_NTD = 230.0  # NT$/kW per month

# Average TOU multiplier for energy cost calculation
# Used when exact time data not available
AVG_TOU_MULTIPLIER = 1.5

# ============================================================================
# SIMULATION PARAMETERS
# ============================================================================

# Default timestep (seconds)
DEFAULT_TIMESTEP_SEC = 0.5

# Default simulation duration (seconds)
DEFAULT_DURATION_SEC = 300.0  # 5 minutes

# Number of presses in typical factory scenario
TYPICAL_PRESS_COUNT = [4, 5, 6, 7, 8]

# Minimum data points for valid statistics
MIN_DATA_POINTS = 100

# ============================================================================
# MOTION PROFILE TYPES (From Research)
# ============================================================================

MOTION_TYPES = {
    'STANDARD': {
        'description': 'Standard sinusoidal (crank-like)',
        'use_case': 'Simple blanking, high volume',
        'dwell_time': 0.0,
    },
    'COINING': {
        'description': 'With dwell at bottom dead center',
        'use_case': 'High-precision, springback control',
        'dwell_time': 3.0,  # seconds
    },
    'PULSATING': {
        'description': 'Ramp → plateau → pause → resume',
        'use_case': 'Complex forming, re-lubrication',
        'dwell_time': 1.0,
        'has_pause': True,
    },
}

# ============================================================================
# PHYSICAL CONSTANTS
# ============================================================================

# Motor and transmission efficiencies
MOTOR_EFFICIENCY = 0.93        # 93% (servo motors are highly efficient)
TRANSMISSION_EFFICIENCY = 0.88  # 88% (ball screw, gears)
OVERALL_EFFICIENCY = MOTOR_EFFICIENCY * TRANSMISSION_EFFICIENCY

# Power factor for AC motors
POWER_FACTOR = 0.90

# Regenerative braking recovery (fraction of return energy)
REGENERATIVE_RECOVERY = 0.15  # 15% energy recovery during return stroke

# ============================================================================
# NETWORK TOPOLOGY TYPES
# ============================================================================

TOPOLOGY_TYPES = ['ring', 'line', 'all_to_all']

# ============================================================================
# VALIDATION THRESHOLDS
# ============================================================================

# Peak power validation (kW per ton of capacity)
# Rule of thumb: ~1 kW per kN of force → ~0.9 kW per ton
PEAK_POWER_PER_TON = 0.9  # kW/ton (approximate)

# Acceptable variation in generated profiles
PROFILE_VARIATION_RANGE = 0.15  # ±15%

# Phase duration validation (must sum to 1.0 ± tolerance)
PHASE_SUM_TOLERANCE = 0.01

# ============================================================================
# DATA OUTPUT FORMATS
# ============================================================================

# Keys for simulation output
OUTPUT_KEYS = {
    'metadata': 'experiment_metadata',
    'timeseries': 'timeseries_data',
    'metrics': 'performance_metrics',
    'ai_features': 'ai_training_features',
    'press_stats': 'press_individual_stats',
}

# Metrics to track
TRACKED_METRICS = [
    'peak_power_kw',
    'avg_power_kw',
    'total_energy_kwh',
    'peak_reduction_pct',
    'cost_savings_ntd',
    'total_delays',
    'collisions_avoided',
    'phase_spread_score',
]
