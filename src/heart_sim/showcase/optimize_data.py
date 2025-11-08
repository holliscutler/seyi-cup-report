"""
Optimize showcase data by removing unnecessary fields.

The full pickle contains all timestep data which is huge (115 MB).
This script creates a lightweight version with just aggregate power arrays.

Usage:
    python src/heart_sim/showcase/optimize_data.py
"""

import pickle
import json
from pathlib import Path

DATA_DIR = Path(__file__).parent / 'data'

print("Loading full results...")
with open(DATA_DIR / 'showcase_results.pkl', 'rb') as f:
    full_results = pickle.load(f)

print(f"Original size: {(DATA_DIR / 'showcase_results.pkl').stat().st_size / 1024 / 1024:.1f} MB")

# Create optimized version with only needed data
optimized = {}

for scenario_key, results in full_results.items():
    optimized[scenario_key] = {
        'baseline': {
            'summary': results['baseline']['summary'],
            'params': results['baseline']['params'],
            'aggregate_power': results['baseline']['full_results']['history']['aggregate_power'],
            'time': results['baseline']['full_results']['history']['time'],
        },
        'static': {
            'summary': results['static']['summary'],
            'params': results['static']['params'],
            'aggregate_power': results['static']['full_results']['history']['aggregate_power'],
            'time': results['static']['full_results']['history']['time'],
        },
        'ai': {
            'summary': results['ai']['summary'],
            'params': results['ai']['params'],
            'aggregate_power': results['ai']['full_results']['history']['aggregate_power'],
            'time': results['ai']['full_results']['history']['time'],
        },
    }

# Save optimized version
output_path = DATA_DIR / 'showcase_results_optimized.pkl'
with open(output_path, 'wb') as f:
    pickle.dump(optimized, f, protocol=pickle.HIGHEST_PROTOCOL)

new_size = output_path.stat().st_size / 1024 / 1024
print(f"Optimized size: {new_size:.1f} MB")
print(f"Reduction: {100 * (1 - new_size / (115)):.1f}%")
print(f"Saved to: {output_path}")
