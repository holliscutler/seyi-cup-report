# AI Training Guide

Complete guide for training and using the AI-powered parameter optimizer for Cardiac Coordination.

---

## 📚 Table of Contents

1. [Overview](#overview)
2. [Phase 6: Data Generation](#phase-6-data-generation)
3. [Phase 7: Model Training](#phase-7-model-training)
4. [Using the AI Optimizer](#using-the-ai-optimizer)
5. [Results & Validation](#results--validation)
6. [Understanding the Model](#understanding-the-model)

---

## Overview

### The Problem

Phase 5 testing revealed that **no single parameter set is optimal for all scenarios**:

- **4 presses**: 95% win rate with static parameters
- **7 presses**: 60% win rate with same parameters

This 35% performance gap indicated that different configurations (press count, fleet mix, topology) need different coordination parameters.

### The Solution: AI-Powered Optimization

Train a machine learning model to:
1. Learn patterns from 4,050 simulations across varied scenarios
2. Predict optimal parameters for any new scenario
3. Adapt recommendations based on fleet characteristics

### Results Preview

AI-optimized parameters for the challenging 7-press realistic scenario:

| Metric | Baseline (Static) | AI-Optimized | Improvement |
|--------|------------------|--------------|-------------|
| Win Rate | 60% | 100% | +40% |
| Peak Reduction | 4.8% | 13.0% | +8.2% |
| Annual Savings | $4,908 | $13,751 | +$8,843 |

---

## Phase 6: Data Generation

### Step 1: Generate Scenario Grid

Create all parameter combinations for systematic exploration:

```bash
python data/scenarios/generation_script.py --output scenario_grid_v1.json
```

**Parameter Space:**
- **Press counts**: 4, 5, 6, 7, 8
- **Fleet mixes**: realistic, varied, uniform
- **Topologies**: ring, all_to_all
- **Max delays**: 3s, 5s, 7s
- **Refractory periods**: 20%, 30%, 40%
- **Variations**: 0.05, 0.1, 0.15
- **Seeds**: 5 per configuration

**Total scenarios**: 4,050

### Step 2: Run Simulations

Generate training data by running all scenarios:

```bash
# Full generation (~13 minutes)
python scripts/generate_training_data.py \
  --scenario-file data/scenarios/scenario_grid_v1.json \
  --batch-size 50 \
  --csv-only
```

**Key Options:**
- `--batch-size 50`: Process in batches (memory-safe)
- `--csv-only`: Skip pickle files (saves 20 GB disk space)
- `--limit N`: Test with first N scenarios only
- `--sequential`: Debug mode (slower)

**Outputs:**
- `data/processed/training_data_v1_TIMESTAMP.csv` (732 KB)
- `data/processed/training_data_v1_TIMESTAMP_metadata.json`

### Step 3: Validate Data

Check data quality before training:

```bash
python scripts/validate_data.py data/processed/training_data_v1_TIMESTAMP.csv
```

**Expected Output:**
```
📊 Dataset Shape: 4050 rows × 18 columns
🎯 Target Statistics (y):
   Win rate: 3378/4050 = 83.4%
   Peak reduction: -21.6% to 37.0%
   Mean peak reduction: 9.3%
✅ TEST DATA LOOKS GOOD!
```

---

## Phase 7: Model Training

### Step 1: Train Model

Train Random Forest regressor on generated data:

```bash
python scripts/train_model.py \
  --data data/processed/training_data_v1_TIMESTAMP.csv \
  --n-estimators 100 \
  --cv 5
```

**Training Time**: ~5 seconds

**Model Performance:**
- Test R² Score: **0.27** (explains 27% of variance)
- RMSE: **8.30%** (average prediction error)
- Cross-validation: **0.31 ± 0.12**

**Outputs:**
- `models/cardiac_optimizer_TIMESTAMP.pkl` (trained model)

### Step 2: Feature Importance Analysis

The model reveals which factors matter most:

```
1. Fleet mix: 41.2%         ← Most important!
2. Number of presses: 22.9%
3. Max delay: 10.7%
4. Variation: 9.7%
5. Refractory: 7.9%
6. Topology: 7.6%
```

**Key Insight:** Scenario characteristics (mix, press count) matter more than coordination parameters. Different fleets have fundamentally different coordination potential.

### Step 3: Generate Recommendations

Get optimal parameters for all scenarios:

```bash
# Single scenario
python scripts/recommend_parameters.py \
  --n-presses 7 \
  --mix realistic

# All scenarios
python scripts/recommend_parameters.py --batch
```

**Output:**
- `models/parameter_recommendations.csv` (15 scenarios × optimal parameters)

---

## Using the AI Optimizer

### Quick Start: Get Recommendations

```bash
# For 7 presses, realistic mix
python scripts/recommend_parameters.py --n-presses 7 --mix realistic
```

**Output:**
```
✨ Recommended Parameters:
   Topology: all_to_all
   Max Delay: 7s
   Refractory: 30%
   Variation: 0.15
   Predicted Peak Reduction: 15.3%

📊 Top 5 Parameter Combinations:
   all_to_all | delay=7s | refract=30% | var=0.15 → 15.3%
   all_to_all | delay=7s | refract=40% | var=0.10 → 14.1%
   ...
```

### Example Recommendations

| Scenario | Topology | Delay | Refractory | Variation | Predicted |
|----------|----------|-------|------------|-----------|-----------|
| 4 presses, realistic | all_to_all | 7s | 40% | 0.10 | 18.3% |
| 7 presses, realistic | all_to_all | 7s | 30% | 0.15 | 15.3% |
| 8 presses, uniform | ring | 5s | 30% | 0.10 | 30.2% |

**Pattern Observations:**
- **Realistic fleets** → all_to_all, longer delays (7s)
- **Uniform fleets** → ring, shorter delays (5s)
- **Larger fleets** → more conservative parameters

---

## Results & Validation

### Validation Process

Compare AI recommendations against Phase 5 baseline (static parameters):

```bash
# Validate all scenarios (150 simulations)
python scripts/validate_ai_recommendations.py --seeds 5

# Validate specific scenario
python scripts/validate_ai_recommendations.py \
  --n-presses 7 \
  --mix realistic \
  --seeds 5
```

### Example: 7 Presses, Realistic Mix

**Baseline (Phase 5 static parameters):**
- Topology: ring, Delay: 5s, Refractory: 30%, Variation: 0.1
- Win rate: 60%
- Peak reduction: 4.8%

**AI-Optimized parameters:**
- Topology: all_to_all, Delay: 7s, Refractory: 30%, Variation: 0.15
- Win rate: 100% ⭐
- Peak reduction: 13.0%

**Improvement:**
- Win rate: +40%
- Peak reduction: +8.2%
- Annual savings: +$8,843

### Full Validation Results

See `results/validation/validation_summary_TIMESTAMP.csv` for complete results across all 15 scenarios.

**Expected Outcomes:**
- Most scenarios show improvement
- Uniform fleets benefit most (20-30% peak reduction)
- Realistic fleets show moderate improvement (10-20%)
- AI adapts parameters to scenario characteristics

---

## Understanding the Model

### What the Model Learns

The Random Forest model learns relationships between:

**Inputs (Features):**
- Press count (4-8)
- Fleet mix (realistic/varied/uniform)
- Topology (ring/all_to_all)
- Max delay (3-7s)
- Refractory period (20-40%)
- Variation (0.05-0.15)

**Output (Target):**
- Peak reduction percentage

### How Predictions Work

1. **You provide** scenario characteristics (press count, mix)
2. **Model tests** all 54 parameter combinations
3. **Model predicts** peak reduction for each combination
4. **System recommends** parameters with highest predicted reduction

### Model Limitations

1. **R² = 0.27**: Model explains 27% of variance
   - Other factors matter: random timing, load profiles, weather
   - Predictions are directional, not precise

2. **Training data scope**: Only tested on:
   - 4-8 presses
   - 3 fleet mixes
   - 2 topologies
   - 1-hour simulations

   Outside this range, predictions may be unreliable

3. **No guarantee**: Predictions are probabilistic
   - "15% predicted" means expected average over many runs
   - Individual runs will vary ±5-10% due to randomness

### When to Trust the Model

✅ **High confidence:**
- Scenarios similar to training data
- Consistent predictions across parameter combinations
- Large predicted differences (>5% gap)

⚠️ **Medium confidence:**
- Edge cases (8 presses, unusual mixes)
- Small predicted differences (<3% gap)

❌ **Low confidence:**
- Outside training range (>8 presses, <4 presses)
- Novel topologies not in training
- Very different simulation durations

---

## Troubleshooting

### Issue: Out of Memory During Data Generation

**Symptoms:** Process killed after 5-10 batches

**Solution:** Use smaller batches and `--csv-only` flag:
```bash
python scripts/generate_training_data.py \
  --scenario-file data/scenarios/scenario_grid_v1.json \
  --batch-size 50 \
  --csv-only
```

The `--csv-only` flag processes each batch incrementally, freeing memory immediately.

### Issue: Model Performance Lower Than Expected

**Diagnosis:**
1. Check data quality: `python scripts/validate_data.py <csv_file>`
2. Check for null values or duplicates
3. Verify full parameter coverage

**Solutions:**
- Generate more data (expand scenario grid to v2)
- Increase `--n-estimators` (100 → 200)
- Try different models (Gradient Boosting, Neural Networks)

### Issue: Recommendations Don't Improve Performance

**Possible Causes:**
1. **Random variation**: Run more seeds (5 → 10) for statistical significance
2. **Model uncertainty**: Check if predicted differences are small (<3%)
3. **Novel scenario**: Test scenario may be outside training distribution

**Solutions:**
- Validate with more seeds
- Check feature importance to understand what model learned
- Generate additional training data for edge cases

---

## Advanced Usage

### Training Custom Models

Modify training parameters for different trade-offs:

```bash
# More trees (slower, potentially better)
python scripts/train_model.py \
  --data <csv_file> \
  --n-estimators 200

# Larger test set (more conservative evaluation)
python scripts/train_model.py \
  --data <csv_file> \
  --test-size 0.3
```

### Generating Expanded Dataset

For better model performance, generate more data:

```bash
# Generate expanded grid (45,000 scenarios)
python data/scenarios/generation_script.py \
  --output scenario_grid_v2.json \
  --version v2 \
  --expanded

# Run simulations (~2.5 hours)
python scripts/generate_training_data.py \
  --scenario-file data/scenarios/scenario_grid_v2.json \
  --batch-size 100 \
  --csv-only
```

### Integration with Live Systems

To use AI recommendations in production:

1. Load trained model:
```python
import pickle
with open('models/cardiac_optimizer_TIMESTAMP.pkl', 'rb') as f:
    model_data = pickle.load(f)
    model = model_data['model']
    encoders = model_data['encoders']
```

2. Get recommendations:
```python
from scripts.recommend_parameters import recommend_parameters

best_params, predictions = recommend_parameters(
    model, encoders, feature_names,
    n_presses=7,
    mix='realistic'
)
```

3. Apply parameters to CoordinationManager:
```python
manager = CoordinationManager(
    topology=best_params['topology'],
    max_delay_sec=best_params['max_delay_sec'],
    refractory_pct=best_params['refractory_pct'],
    variation=best_params['variation']
)
```

---

## Next Steps

1. **Extend Parameters**: Extend parameters to model more realistic scenarios
2. **Online learning**: Update model as new data becomes available
3. **Multi-objective optimization**: Consider both peak reduction AND energy efficiency
4. **Real-time adaptation**: Adjust parameters dynamically based on live load profiles

---

## Related Documentation

- **Implementation Plan**: `guidelines/Implementation_Plan.md`
- **Data Generation**: `scripts/README.md`
- **Test Framework**: `tests/test_framework/README.md`
- **Simulation Details**: `src/heart_sim/README.md`


