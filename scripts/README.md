# Data Generation Scripts

Scripts for Phase 6: AI Training Data Collection

---

## 🚀 Quick Start

### Step 1: Generate Scenario Grid (~5 seconds)

```bash
# Generate conservative grid (4,050 scenarios)
python data/scenarios/generation_script.py --output scenario_grid_v1.json

# Or generate expanded grid (45,000+ scenarios)
python data/scenarios/generation_script.py --output scenario_grid_v2.json --version v2 --expanded
```

**Output:** `data/scenarios/scenario_grid_v1.json` (all parameter combinations)

### Step 2: Run Simulations (~13 minutes for 4,050 scenarios)

```bash
# Run all scenarios in parallel
python scripts/generate_training_data.py --scenario-file data/scenarios/scenario_grid_v1.json

# Or run in batches (safer for memory)
python scripts/generate_training_data.py \
  --scenario-file data/scenarios/scenario_grid_v1.json \
  --batch-size 100

# Sequential for debugging
python scripts/generate_training_data.py \
  --scenario-file data/scenarios/scenario_grid_v1.json \
  --sequential
```

**Outputs:**
- `data/raw/training_data_v1_TIMESTAMP.pkl` (raw results)
- `data/processed/training_data_v1_TIMESTAMP.csv` (ML-ready CSV)
- `data/processed/training_data_v1_TIMESTAMP_metadata.json` (metadata)

### Step 3: Train Model (see `docs/AI_Training_Guide.md`)

```python
import pandas as pd
from sklearn.ensemble import RandomForestRegressor

# Load training data
data = pd.read_csv('data/processed/training_data_v1_TIMESTAMP.csv')

# Features and target
X = data[['n_presses', 'topology', 'max_delay_sec', 'refractory_pct', 'variation']]
y = data['win_rate']

# Encode categorical
X['topology'] = X['topology'].map({'ring': 0, 'all_to_all': 1, 'line': 2, 'star': 3})

# Train
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X, y)

# Predict optimal params for 7 presses
X_pred = [[7, 0, 5, 30, 0.1]]  # 7 presses, ring, 5s, 30%, 0.1
predicted_win_rate = model.predict(X_pred)
print(f"Predicted win rate: {predicted_win_rate[0]:.1f}%")
```

---

## 📊 Script Details

### `data/scenarios/generation_script.py`

**Purpose:** Generate all parameter combinations for systematic exploration

**Parameters:**
- `--output`: Output filename (default: scenario_grid_v1.json)
- `--version`: Version tag (default: v1)
- `--expanded`: Use expanded parameter grid (more scenarios)

**Conservative Grid (v1):**
- 5 press counts × 3 mixes × 2 topologies × 3 delays × 3 refractory × 3 variations × 5 seeds
- Total: **4,050 scenarios**
- Estimated time: ~13 minutes

**Expanded Grid (v2):**
- 5 press counts × 5 mixes × 4 topologies × 5 delays × 3 refractory × 3 variations × 5 seeds
- Total: **45,000 scenarios**
- Estimated time: ~2.5 hours

### `scripts/generate_training_data.py`

**Purpose:** Run simulations for all scenarios and save results

**Parameters:**
- `--scenario-file`: Input JSON scenario grid (required)
- `--output-dir`: Directory for raw results (default: data/raw)
- `--processed-dir`: Directory for processed CSV (default: data/processed)
- `--batch-size`: Process in batches (optional, e.g., 100)
- `--sequential`: Run sequentially instead of parallel (debugging)
- `--max-workers`: Maximum parallel workers (default: CPU count)
- `--limit`: Limit to first N scenarios (testing)

**Features:**
- Parallel execution (GPU-accelerated)
- Batch processing (memory-safe)
- Progress tracking
- Automatic CSV generation for ML
- Metadata tracking

---

## 🧪 Testing the Pipeline

### Quick Test (10 scenarios, ~2 seconds)

```bash
# Generate small test grid
python data/scenarios/generation_script.py --output test_grid.json

# Edit test_grid.json to only keep first 10 scenarios

# Run test
python scripts/generate_training_data.py \
  --scenario-file data/scenarios/test_grid.json \
  --limit 10
```

### Medium Test (100 scenarios, ~20 seconds)

```bash
python scripts/generate_training_data.py \
  --scenario-file data/scenarios/scenario_grid_v1.json \
  --limit 100 \
  --batch-size 50
```

### Full Test 

```bash
python scripts/generate_training_data.py \
  --scenario-file data/scenarios/test_grid.json \
  --batch-size 50

python scripts/generate_training_data.py \
  --scenario-file data/scenarios/test_grid.json \
  --batch-size 200

python scripts/generate_training_data.py \
  --scenario-file data/scenarios/test_grid.json \
  --batch-size 50 \
  --csv-only
```
---

## 📝 Output Format

### CSV Schema (for ML training)

```csv
# Features (X) - what we vary
n_presses,mix,topology,seed,max_delay_sec,refractory_pct,variation

# Targets (y) - what we measure
cardiac_wins,win_rate,peak_reduction_pct,baseline_peak_kw,cardiac_peak_kw,
energy_change_kwh,annual_savings_usd,mean_delays,collisions_avoided

# Metadata
duration_sec,scenario_name
```

**Example row:**
```csv
4,realistic,ring,42,5,30,0.1,True,100.0,10.13,710.3,633.6,-0.5,6865,180,52,3600,v1_p4_realistic_ring_d5_r30_v0.1_s42
```

---

## ⚡ Performance Tips

### For Fast Generation:
- Use parallel mode (default)
- Let max_workers auto-detect CPU count
- Use batch processing for large grids

### For Memory Safety:
- Use `--batch-size 100` to limit memory
- Results are saved incrementally per batch
- Can resume if interrupted (just skip completed batches)

### For Debugging:
- Use `--limit 10` to test with few scenarios
- Use `--sequential` to see detailed errors
- Check individual scenario results in batch files

---

## 🔄 Workflow Example

```bash
# 1. Generate scenario grid
python data/scenarios/generation_script.py --output scenario_grid_v1.json

# Output: ✓ Generated 4050 scenarios
#         Unique configs: 810
#         Seeds per config: 5
#         Estimated time: 13.5 minutes

# 2. Run simulations
python scripts/generate_training_data.py \
  --scenario-file data/scenarios/scenario_grid_v1.json \
  --batch-size 100

# Output: Running in 41 batches of 100
#         Batch 1/41 (100 scenarios)...
#         ✓ Saved batch to data/raw/batch_001_results.pkl
#         ...
#         ✓ All 4050 simulations complete!
#         ✓ Saved complete results to data/raw/training_data_v1_20251104_214500.pkl
#         ✓ Processed 4050 results to CSV
#
#         Summary Statistics:
#           Win rate: 86.2%
#           Mean peak reduction: 7.8%
#           Peak reduction range: [-5.2%, 25.3%]

# 3. Train model (see AI_Training_Guide.md)
```

---

## 🐛 Troubleshooting

### "ModuleNotFoundError: No module named 'tests.test_framework'"

Solution: Run from project root
```bash
cd /path/to/servo-heart
python scripts/generate_training_data.py ...
```

### Simulations running slowly

- Check GPU is being utilized
- Reduce batch_size
- Use --sequential to identify bottleneck

### Out of memory errors

- Reduce batch_size to 50 or 25
- Results are saved per batch, so you can continue

### Want to resume interrupted run

- Check which batches completed in data/raw/
- Skip completed batches manually, or just re-run (will overwrite)

---

## 📚 Related Documentation

- **Data plan**: `data/README.md`
- **AI training guide**: `docs/AI_Training_Guide.md`
- **Test framework**: `tests/test_framework/README.md`
- **Implementation plan**: `guidelines/Implementation_Plan.md`

---

