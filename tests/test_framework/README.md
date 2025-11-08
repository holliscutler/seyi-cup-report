# Test Framework - Modular Testing for Cardiac Coordination

**Systematic, reusable, and extensible testing framework for cardiac coordination algorithm.**

---

## 🎯 Features

- ✅ **Modular Design**: Separate concerns (config, run, analyze, report)
- ✅ **No Code Duplication**: Reusable components
- ✅ **Parallel Execution**: Run scenarios concurrently for speed
- ✅ **Multiple Output Formats**: JSON, CSV, Markdown
- ✅ **Easy Parameter Sweeps**: Built-in factory functions
- ✅ **Extensible**: Easy to add new metrics or scenarios

---

## 📁 Structure

```
test_framework/
├── __init__.py         # Exports all main functions
├── scenarios.py        # ScenarioConfig and factory functions
├── runner.py           # Simulation execution (single and batch)
├── analyzers.py        # Analysis functions (power, coordination, cost)
├── comparators.py      # Comparison and aggregation logic
└── reporters.py        # Report generators (JSON, CSV, Markdown)
```

---

## 🚀 Quick Start

### Basic Usage

```python
from test_framework import (
    create_single_scenario,
    run_scenario,
    compare_single_scenario
)

# Create scenario
config = create_single_scenario(
    n_presses=6,
    mix='realistic',
    duration_sec=1800,  # 30 minutes
    seed=42
)

# Run simulation
result = run_scenario(config, verbose=True)

# Analyze
comparison = compare_single_scenario(result)
print(f"Peak reduction: {comparison['comparison']['peak_reduction_pct']:.1f}%")
```

### Seed Sweep

```python
from test_framework import create_seed_sweep, run_batch, aggregate_across_seeds

# Test multiple seeds for statistical significance
scenarios = create_seed_sweep(
    n_presses=6,
    mix='realistic',
    topology='ring',
    seeds=[42, 123, 456, 789, 1024],
    duration_sec=1800
)

# Run all scenarios in parallel
results = run_batch(scenarios, parallel=True)

# Aggregate statistics
summary = aggregate_across_seeds(results)
print(f"Mean peak reduction: {summary['peak_reduction']['mean_pct']:.1f}%")
print(f"Win rate: {summary['win_rate']:.1f}%")
```

### Press Count Scaling

```python
from test_framework import (
    create_scenario_grid,
    run_batch,
    compare_across_press_counts,
    generate_markdown_report
)

# Test 4-8 presses × 10 seeds each
scenarios = create_scenario_grid(
    presses_list=[4, 5, 6, 7, 8],
    seeds=range(42, 52),  # 10 seeds
    duration_sec=3600,    # 1 hour
    mix='realistic',
    topology='ring'
)

# Run in parallel (100 scenarios)
results = run_batch(scenarios, parallel=True)

# Analyze scaling
scaling = compare_across_press_counts(results)

# Generate report
generate_markdown_report(scaling, "scaling_report.md")
```

---

## 📊 Scenario Factories

### 1. Single Scenario

```python
create_single_scenario(
    n_presses=6,
    mix='realistic',
    topology='ring',
    duration_sec=1800,
    max_delay_sec=5.0,
    variation=0.1,
    seed=42,
    name="my_scenario"  # Optional
)
```

### 2. Seed Sweep

```python
# Test multiple seeds for same configuration
create_seed_sweep(
    n_presses=6,
    mix='realistic',
    topology='ring',
    seeds=[42, 123, 456, 789, 1024],
    duration_sec=1800
)
```

### 3. Press Count Sweep

```python
# Test different fleet sizes
create_press_count_sweep(
    presses_list=[4, 5, 6, 7, 8],
    mix='realistic',
    topology='ring',
    seed=42,
    duration_sec=1800
)
```

### 4. Scenario Grid

```python
# Test all combinations of presses × seeds
create_scenario_grid(
    presses_list=[4, 5, 6, 7, 8],
    seeds=range(42, 62),  # 20 seeds
    mix='realistic',
    topology='ring',
    duration_sec=3600
)
# Returns 5 × 20 = 100 scenarios
```

### 5. Topology Comparison

```python
# Test all topologies
create_topology_comparison(
    n_presses=6,
    mix='realistic',
    seed=42,
    duration_sec=1800
)
# Returns 4 scenarios (ring, line, all_to_all, star)
```

### 6. Mix Comparison

```python
# Test all fleet mixes
create_mix_comparison(
    n_presses=6,
    topology='ring',
    seed=42,
    duration_sec=1800
)
# Returns 5 scenarios (realistic, varied, uniform, small, large)
```

### 7. Delay Sweep

```python
# Test different delay budgets
create_delay_sweep(
    n_presses=6,
    mix='realistic',
    topology='ring',
    delay_values=[1.0, 2.5, 5.0, 7.5, 10.0],
    seed=42,
    duration_sec=1800
)
```

---

## 🔬 Analyzers

### Power Distribution Analysis

```python
from test_framework import analyze_power_distribution

analysis = analyze_power_distribution(results)
# Returns: mean, std, cv, peak, percentiles, spikes, histogram
```

### Coordination Behavior

```python
from test_framework import analyze_coordination_behavior

coord = analyze_coordination_behavior(cardiac_results)
# Returns: delays, collisions avoided, phase spread, per-press data
```

### Cost Savings

```python
from test_framework import analyze_cost_savings

cost = analyze_cost_savings(baseline_results, cardiac_results)
# Returns: monthly/annual savings (NT$ and USD), breakdown
```

### Energy Efficiency

```python
from test_framework import analyze_energy_efficiency

efficiency = analyze_energy_efficiency(results)
# Returns: load factor, peak-to-avg ratio, time above thresholds
```

### Stability Analysis

```python
from test_framework import analyze_stability

stability = analyze_stability(results)
# Returns: mean drift, std stability, autocorrelation
```

### All Analyzers

```python
from test_framework import analyze_all

full_analysis = analyze_all(baseline_results, cardiac_results)
# Returns comprehensive analysis with all metrics
```

---

## 📈 Comparators

### Single Scenario Comparison

```python
from test_framework import compare_single_scenario

comparison = compare_single_scenario(result)
# Returns comparison between baseline and cardiac for one scenario
```

### Aggregate Across Seeds

```python
from test_framework import aggregate_across_seeds

summary = aggregate_across_seeds(results)
# Returns aggregated statistics across multiple seeds
```

### Compare Across Press Counts

```python
from test_framework import compare_across_press_counts

scaling = compare_across_press_counts(results)
# Returns scaling analysis by press count
```

### Compare Across Topologies

```python
from test_framework import compare_across_topologies

topo_comparison = compare_across_topologies(results)
# Returns comparison by topology
```

### Find Best and Worst

```python
from test_framework import find_best_and_worst

extremes = find_best_and_worst(results)
# Returns best and worst performing scenarios
```

---

## 📝 Reporters

### JSON Report

```python
from test_framework import generate_json_report

generate_json_report(data, "report.json")
```

### CSV Summary

```python
from test_framework import generate_csv_summary

generate_csv_summary(summary, "summary.csv")
# Perfect for Excel/Google Sheets
```

### Markdown Report

```python
from test_framework import generate_markdown_report

generate_markdown_report(
    summary,
    "report.md",
    title="My Test Results"
)
```

### Console Summary

```python
from test_framework import generate_summary_table

print(generate_summary_table(summary))
```

---

## 💾 Saving and Loading Results

### Save Results

```python
from test_framework import save_results

# Save full results (pickle)
save_results(results, "results.pkl", format='pickle')

# Save metadata only (JSON)
save_results(results, "metadata.json", format='json')
```

### Load Results

```python
from test_framework import load_results

results = load_results("results.pkl")
```

### Filter Results

```python
from test_framework import filter_results

# Get only 6-press scenarios
six_press = filter_results(results, n_presses=6)

# Get only ring topology
ring_only = filter_results(results, topology='ring')

# Get specific seed
seed_42 = filter_results(results, seed=42)

# Chain filters
realistic_six = filter_results(results, n_presses=6, mix='realistic')
```

---

## 🏃 Runner Functions

### Run Single Scenario

```python
from test_framework import run_scenario

result = run_scenario(config, verbose=True)
```

### Run Batch (Sequential)

```python
from test_framework import run_batch

results = run_batch(scenarios, parallel=False, verbose=True)
```

### Run Batch (Parallel)

```python
# Use all CPU cores
results = run_batch(scenarios, parallel=True)

# Limit to 4 workers
results = run_batch(scenarios, parallel=True, max_workers=4)
```

---

## 🎯 Real-World Examples

### Example 1: Statistical Validation

```python
"""
Test if cardiac coordination consistently wins across seeds.
"""
from test_framework import *

# Create 20 scenarios with different seeds
scenarios = create_seed_sweep(
    n_presses=6,
    mix='realistic',
    topology='ring',
    seeds=range(42, 62),
    duration_sec=1800
)

# Run all
results = run_batch(scenarios, parallel=True)

# Aggregate
summary = aggregate_across_seeds(results)

print(f"Win rate: {summary['win_rate']:.1f}%")
print(f"Mean peak reduction: {summary['peak_reduction']['mean_pct']:.1f}%")
print(f"Std dev: {summary['peak_reduction']['std_pct']:.1f}%")
```

### Example 2: Scaling Analysis

```python
"""
Test how algorithm scales from 4 to 8 presses.
"""
from test_framework import *

scenarios = create_scenario_grid(
    presses_list=[4, 5, 6, 7, 8],
    seeds=range(42, 52),  # 10 seeds per count
    duration_sec=3600     # 1 hour
)

results = run_batch(scenarios, parallel=True)

scaling = compare_across_press_counts(results)

# Generate reports
generate_csv_summary(scaling, "scaling_results.csv")
generate_markdown_report(scaling, "scaling_report.md")
print(generate_summary_table(scaling))
```

### Example 3: Topology Comparison

```python
"""
Find which topology works best.
"""
from test_framework import *

scenarios = create_topology_comparison(
    n_presses=6,
    mix='realistic',
    seed=42,
    duration_sec=1800
)

results = run_batch(scenarios, parallel=True)

topo_comp = compare_across_topologies(results)

for topology, data in topo_comp['by_topology'].items():
    print(f"{topology:12s}: {data['peak_reduction']['mean_pct']:5.1f}% reduction")
```

### Example 4: Data Collection for AI Training

```python
"""
Collect comprehensive dataset for AI training.
"""
from test_framework import *

# Generate diverse scenarios
scenarios = []

# Vary press counts
for n_presses in [4, 5, 6, 7, 8]:
    # Vary topologies
    for topology in ['ring', 'line', 'all_to_all']:
        # Vary mixes
        for mix in ['realistic', 'varied', 'uniform']:
            # Multiple seeds for each combo
            for seed in range(42, 47):  # 5 seeds
                scenarios.append(create_single_scenario(
                    n_presses=n_presses,
                    mix=mix,
                    topology=topology,
                    seed=seed,
                    duration_sec=3600
                ))

print(f"Total scenarios: {len(scenarios)}")  # 5×3×3×5 = 225

# Run all (this will take a while!)
results = run_batch(scenarios, parallel=True)

# Save for AI training
save_results(results, "ai_training_dataset.pkl")
```

---

## 🛠️ Extending the Framework

### Add a New Analyzer

```python
# In analyzers.py
def analyze_my_custom_metric(results: Dict) -> Dict:
    """Analyze custom metric."""
    # Your analysis logic here
    return {
        'my_metric': value,
        # ...
    }
```

### Add a New Comparator

```python
# In comparators.py
def compare_my_custom_dimension(results: List[ScenarioResult]) -> Dict:
    """Compare across custom dimension."""
    # Group and analyze results
    return grouped_analysis
```

### Add a New Reporter

```python
# In reporters.py
def generate_my_custom_report(data: Dict, filename: str):
    """Generate custom format report."""
    # Your formatting logic
    pass
```

---

## ⚡ Performance Tips

### Parallel Execution

- **Use `parallel=True`** for multiple scenarios (much faster!)
- **Adjust `max_workers`** based on your CPU cores and memory
- **Long simulations** benefit most from parallelization

### Memory Management

- **Save intermediate results** using `save_results()` to avoid losing data
- **Use `format='json'`** if you only need metadata (smaller files)
- **Filter results** before analysis to reduce memory usage

### Time Estimation

For planning purposes:
- 30-minute simulation: ~30-60 seconds wall-clock time
- 1-hour simulation: ~60-120 seconds wall-clock time
- 100 scenarios × 1 hour × parallel: ~2-4 hours total (with 8 cores)

---

## 📚 Complete Example: Comprehensive Test

See `tests/test_comprehensive.py` for a full example that:
- Tests 4-8 presses
- Uses 20 seeds per press count
- Runs 1-hour simulations
- Generates all reports
- Supports CLI arguments

Usage:
```bash
# Full test (100 scenarios, parallel)
python tests/test_comprehensive.py

# Quick test (10-minute simulations)
python tests/test_comprehensive.py --quick

# Sequential execution
python tests/test_comprehensive.py --sequential

# Custom parameters
python tests/test_comprehensive.py --presses 4 5 6 --seeds 10 --duration 0.5
```

---

## 📞 Summary

The test framework provides a modular, reusable system for systematic testing with:

✅ **Easy scenario generation** (factories)
✅ **Parallel execution** (speed)
✅ **Comprehensive analysis** (power, cost, coordination)
✅ **Multiple report formats** (JSON, CSV, Markdown)
✅ **Extensible design** (add your own metrics)

Perfect for:
- Statistical validation
- Scaling analysis
- Parameter optimization
- Data collection for AI training
- Competition reporting

---

**Built for the SEYI 2025 Cup Competition** 🏆
