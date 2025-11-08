# heart_sim v2.0 - Cardiac Coordination for Servo Presses

**Research-validated, modular simulation of cardiac-inspired coordination for servo press energy optimization.**

---

## 🎉 What's New in v2.0

### ✅ **Fully Research-Aligned**
- Power profiles based on `research/QUICK_REFERENCE.md` and `research/DAY1_RESEARCH_SUMMARY.md`
- All values validated against literature (100-600 ton presses, 18-40s cycles, 85-500 kW peaks)
- Taiwan electricity pricing from official Taipower data
- 8 validated press templates (small_fast, medium_standard, large_slow, etc.)

### ✅ **Modular Architecture**
- **Separated concerns**: Power profiles, presses, coordination, simulation, metrics, cost
- **Clean interfaces**: Each module has clear responsibilities
- **AI-ready**: Data output formatted for future ML training

### ✅ **Production Quality**
- Comprehensive test suite (5/5 tests passing)
- Type hints throughout
- Extensive documentation
- Research citations in code

---

## 📁 Module Structure

```
src/heart_sim/
├── power_profiles/      # Research-based power consumption profiles
│   ├── profile_base.py         # PowerProfile class with phase definitions
│   ├── validated_profiles.py   # 8 research-validated templates
│   └── profile_generator.py    # Create profiles with variations
│
├── press/               # Cardiac press models
│   ├── press_config.py         # PressConfig dataclass
│   └── cardiac_press.py        # CardiacPress with heart-inspired logic
│
├── coordination/        # Network coordination
│   ├── topology.py             # Ring, line, all-to-all, star topologies
│   └── coordinator.py          # CardiacCoordinator manages press network
│
├── simulation/          # Simulation engine & analysis
│   ├── engine.py               # SimulationEngine runs timesteps
│   ├── metrics.py              # MetricsCollector calculates performance
│   └── data_output.py          # Format data for AI/reports
│
├── cost/                # Taiwan electricity pricing
│   └── taiwan_pricing.py       # TaiwanCostCalculator with TOU rates
│
└── utils/               # Constants and utilities
    └── constants.py            # Research-validated constants
```

---

## 🚀 Quick Start

### Basic Usage

```python
from heart_sim import create_coordinator_auto, SimulationEngine, create_summary_report

# Create a coordinator with 6 presses (realistic mix)
coordinator = create_coordinator_auto(
    n_presses=6,
    mix='realistic',    # Weighted toward medium presses
    topology='ring',
    seed=42
)

# Run simulation
engine = SimulationEngine(coordinator)
results = engine.run(duration_sec=300.0, verbose=True)

# Print summary
print(create_summary_report(results))
```

### Baseline vs Cardiac Comparison

```python
from heart_sim import (
    create_coordinator_from_templates,
    SimulationEngine,
    MetricsCollector,
    compare_baseline_vs_cardiac_costs
)

# Define templates for consistent comparison
templates = ['medium_standard', 'medium_coining', 'large_slow', 'small_fast']

# Baseline (no coordination)
baseline_coord = create_coordinator_from_templates(
    templates, topology='ring', max_delay_sec=0.0, seed=42
)
baseline_engine = SimulationEngine(baseline_coord)
baseline_results = baseline_engine.run(duration_sec=300.0)

# Cardiac (with coordination)
cardiac_coord = create_coordinator_from_templates(
    templates, topology='ring', max_delay_sec=5.0, seed=42
)
cardiac_engine = SimulationEngine(cardiac_coord)
cardiac_results = cardiac_engine.run(duration_sec=300.0)

# Compare
comparison = MetricsCollector.compare_baseline_vs_cardiac(
    baseline_results, cardiac_results
)
print(f"Peak Reduction: {comparison['peak_reduction_pct']:.2f}%")

# Cost comparison
cost_comparison = compare_baseline_vs_cardiac_costs(
    baseline_results, cardiac_results
)
print(f"Cost Savings: NT$ {cost_comparison['savings']['total_savings_ntd']:.0f}")
```

### Custom Press Fleet

```python
from heart_sim import (
    create_power_profile,
    PressConfig,
    CardiacCoordinator,
    SimulationEngine
)

# Create custom profiles
profiles = [
    create_power_profile('small_fast', variation=0.1, seed=1),
    create_power_profile('medium_standard', variation=0.1, seed=2),
    create_power_profile('large_slow', variation=0.1, seed=3),
]

# Create press configs
configs = [
    PressConfig(
        press_id=f"Press_{chr(65+i)}",
        power_profile=profile,
        max_delay_sec=5.0
    )
    for i, profile in enumerate(profiles)
]

# Create coordinator and run
coordinator = CardiacCoordinator(configs, topology='ring', seed=42)
engine = SimulationEngine(coordinator)
results = engine.run(duration_sec=300.0)
```

---

## 🔬 Research Alignment

### Power Profiles

All templates based on `research/QUICK_REFERENCE.md`:

| Template | Capacity | Peak Power | Cycle Time | Source |
|----------|----------|------------|------------|--------|
| `small_fast` | 100T | 85 kW | 18s | QUICK_REFERENCE.md |
| `medium_standard` | 200T | 180 kW | 25s | QUICK_REFERENCE.md (reference) |
| `medium_coining` | 200T | 190 kW | 30s | Motion Profile Types |
| `large_slow` | 300T | 270 kW | 35s | QUICK_REFERENCE.md |
| `medium_pulsating` | 200T | 185 kW | 28s | Research finding: 92.3% greater depth |
| `small_high_speed` | 100T | 90 kW | 15s | High-volume applications |
| `medium_heavy_gauge` | 200T | 195 kW | 32s | AHSS materials |
| `large_progressive` | 300T | 280 kW | 38s | Multi-stage forming |

### Phase Structure

Based on 200-ton reference (25s cycle):
- **Approach**: 28% of cycle (7s) - rapid descent
- **Forming**: 32% of cycle (8s) - peak power deformation
- **Return**: 24% of cycle (6s) - fast return
- **Idle**: 16% of cycle (4s) - part loading/unloading

### Taiwan Pricing

From `research/DAY1_RESEARCH_SUMMARY.md`:
- Base rate: NT$4.27/kWh
- Peak hours (10 AM-12 PM, 1-5 PM): NT$7.50/kWh
- Super-peak (3-9 PM): NT$9.90/kWh
- Demand charge: NT$230/kW per month
- Demand charges = 30-40% of total bill

---

## 📊 Output Data Structure

### Simulation Results

```python
{
    'history': {
        'time': [...],                    # Time array
        'aggregate_power': [...],         # Total power over time
        'individual_powers': {...},       # Per-press power
        'phases': {...},                  # Per-press phase (0-1)
        'states': {...},                  # Per-press cardiac state
        'collision_risks': {...},         # Per-press collision risk
        'refractory_timers': {...},       # Per-press refractory countdown
        'delay_events': [...],            # Sparse event data
        'cycle_completions': [...],
        'forming_entries': [...],
    },
    'metadata': {
        'duration_sec': 300.0,
        'num_steps': 600,
        'num_presses': 6,
        'topology': 'ring',
        'pacemaker': 'Press_A',
    },
    'press_configs': {...},
    'final_press_stats': {...}
}
```

### Calculated Metrics

```python
{
    # Power metrics
    'peak_power_kw': 450.2,
    'avg_power_kw': 320.5,
    'total_energy_kwh': 26.7,
    'p90_power_kw': 420.1,
    'cv_power': 0.18,

    # Coordination metrics
    'total_delays': 42,
    'total_collisions_avoided': 38,
    'phase_spread_score': 0.85,
    'delay_rate': 0.12,
}
```

### AI Training Features

```python
{
    'peak_frequency': 0.05,              # How often at peak
    'avg_phase_std': 0.25,               # Phase synchronization
    'collision_density': 0.12,           # Collisions per second
    'delay_per_collision_avoided': 2.5,  # Efficiency metric
    'coordination_efficiency': 15.2,     # Collisions/delay_time
}
```

---

## 🧪 Testing

Run comprehensive test suite:

```bash
source venv/bin/activate
python tests/test_heart_sim.py
```

Tests cover:
1. ✅ Power profile system (validation, fleet generation)
2. ✅ Coordinator and topology setup
3. ✅ Simulation engine
4. ✅ Baseline vs cardiac comparison
5. ✅ Summary report generation

---

## 🔄 Differences from `src/heart` (v1.0)

| Feature | v1.0 (`src/heart`) | v2.0 (`src/heart_sim`) |
|---------|-------------------|----------------------|
| **Power Profiles** | Hardcoded in press | Separate PowerProfile class |
| **Phase Structure** | Fixed ratios | Research-validated, configurable |
| **Modularity** | Monolithic | Separated concerns |
| **Validation** | None | `validate_profile()` checks |
| **Cost Calc** | In coordinator | Separate TaiwanCostCalculator |
| **Data Output** | Basic dict | AI-ready formatting |
| **Templates** | None | 8 research-validated |
| **Testing** | Manual | Comprehensive suite |

---

## 💡 Design Philosophy

### Separation of Concerns

Each module has ONE responsibility:
- **power_profiles**: Define WHAT presses consume
- **press**: Define HOW presses behave (cardiac logic)
- **coordination**: Define WHO coordinates with WHOM
- **simulation**: Execute and record
- **cost**: Calculate financial impact
- **metrics**: Analyze performance

### Research-First

Every parameter traces back to research:
```python
# Bad (v1.0)
power = 100.0  # Magic number

# Good (v2.0)
peak_power = template['peak_power_kw']  # From VALIDATED_TEMPLATES
# Source: research/QUICK_REFERENCE.md, Section "Profile Variations"
```

### Future-Ready

Data structures designed for AI training:
- Standardized output format
- Feature extraction built-in
- Metadata preservation
- Experiment reproducibility (seeds)

---

## 🎯 Next Steps

### Immediate
1. ✅ All modules implemented
2. ✅ Tests passing
3. ⏳ Create visualization UI (refactor `app.py` to use heart_sim)

### Future
4. ⏳ Data collection for AI training
5. ⏳ ML model for parameter tuning
6. ⏳ Real-time optimization

---

## 📚 References

All values and concepts sourced from:
- `research/QUICK_REFERENCE.md` - Power profile templates
- `research/DAY1_RESEARCH_SUMMARY.md` - Literature review
- `research/EXECUTIVE_SUMMARY.md` - Research summary
- `src/heart/README.md` - Cardiac coordination principles
- `guidelines/Implementation_Plan.md` - Project roadmap

---

## 🤝 Contributing

When adding new features:
1. **Document research source** in code comments
2. **Add validation** for new parameters
3. **Update tests** to cover new functionality
4. **Maintain separation** of concerns

---

**Built for the SEYI 2025 Cup Competition**

*Bio-inspired coordination for sustainable manufacturing* 🌱⚡
