# AI Training Data Collection

**Phase 6: Systematic Parameter Exploration**

---

## 🎯 Objective

Generate diverse training data by systematically varying coordination parameters to train an ML model that predicts optimal settings for any press configuration.

---

## 📊 Data Generation Plan

### Feature Space (What We Vary)

#### 1. Press Configuration (Scenario-Defining)
```python
n_presses = [4, 5, 6, 7, 8]              # 5 values
mix = ['realistic', 'varied', 'uniform']  # 3 values (reduced for initial run)
# Note: 'small' and 'large' can be added later for expansion
```

#### 2. Coordination Parameters (What We're Optimizing)
```python
topology = ['ring', 'all_to_all']        # 2 values (start simple)
max_delay_sec = [3, 5, 7]                # 3 values
refractory_pct = [20, 30, 40]            # 3 values
variation = [0.05, 0.1, 0.15]            # 3 values
```

#### 3. Random Seeds (For Statistical Validity)
```python
seeds_per_config = 5                     # 5 seeds per unique configuration
base_seed = 42                           # Starting seed
```

### Constants
```python
duration_sec = 3600                      # 1 hour (constant)
```

---

## 📈 Dataset Size Calculation

### Initial Dataset (Conservative Approach)

**Parameter combinations:**
- Press configs: 5 × 3 = 15
- Coord params: 2 × 3 × 3 × 3 = 54
- Total unique configs: 15 × 54 = **810 configurations**
- With 5 seeds each: 810 × 5 = **4,050 total scenarios**

**Estimated Time (GPU-accelerated):**
- 100 scenarios in ~20 seconds
- 4,050 scenarios: ~13.5 minutes total

**Storage:**
- Each result: ~5-20 MB
- Total: ~20-80 GB (pickle format)
- CSV summary: ~2-5 MB

### Expanded Dataset (If Needed)

If we add:
- line, star topologies → 4 topologies total
- small, large mixes → 5 mixes total
- More delay values: [3, 4, 5, 6, 7] → 5 values

**Total:** 5 × 5 × 4 × 5 × 3 × 3 × 5 seeds = **45,000 scenarios** (~2.5 hours)

**Recommendation:** Start with initial dataset (4,050 scenarios), evaluate model performance, expand if needed.

---

## 🗂️ Data Organization

### Folder Structure
```
data/
├── README.md (this file)
├── scenarios/
│   ├── scenario_grid_v1.json          # Generated scenario configurations
│   └── generation_script.py           # Script to generate scenarios
├── raw/
│   ├── batch_001_results.pkl          # Raw simulation results (batched)
│   ├── batch_002_results.pkl
│   └── ...
├── processed/
│   ├── training_data_v1.csv           # Processed CSV for ML training
│   ├── training_data_v1_metadata.json # Metadata (timestamp, params, etc.)
│   └── feature_engineering_notes.md   # Documentation of feature encoding
└── models/
    ├── random_forest_v1.pkl           # Trained models
    ├── model_metrics_v1.json          # Performance metrics
    └── training_log_v1.md             # Training process documentation
```

---

## 📝 Data Schema

### Features (Input to ML Model)
```csv
n_presses,mix,topology,max_delay_sec,refractory_pct,variation,seed
4,realistic,ring,3,20,0.05,42
4,realistic,ring,3,20,0.05,43
4,realistic,ring,3,20,0.05,44
...
```

### Targets (Output - What We Measure)
```csv
win_rate_pct,peak_reduction_pct,mean_baseline_peak_kw,mean_cardiac_peak_kw,annual_savings_usd,mean_delays,collisions_avoided
95.0,10.13,710.3,633.6,6865,180,52
...
```

### Combined Training Data Format
```csv
# Features (X)                                                      | Targets (y)
n_presses,mix,topology,max_delay,refractory,variation,seed         | win_rate,peak_reduction,baseline_peak,cardiac_peak,savings,delays,collisions
4,realistic,ring,3,20,0.05,42                                      | 95.0,10.13,710.3,633.6,6865,180,52
```

---

## 🚀 Data Generation Strategy

### Phase 6.1: Generate Scenario Grid (5 minutes)
```python
# Create all parameter combinations
scenarios = create_comprehensive_grid(
    presses_list=[4, 5, 6, 7, 8],
    mixes=['realistic', 'varied', 'uniform'],
    topologies=['ring', 'all_to_all'],
    max_delays=[3, 5, 7],
    refractory_pcts=[20, 30, 40],
    variations=[0.05, 0.1, 0.15],
    seeds=range(42, 47)  # 5 seeds
)

# Save scenario grid
save_scenarios(scenarios, 'data/scenarios/scenario_grid_v1.json')
```

### Phase 6.2: Run Simulations (15-30 minutes)
```bash
# Run in batches to avoid memory issues
python scripts/generate_training_data.py \
  --scenario-file data/scenarios/scenario_grid_v1.json \
  --output-dir data/raw/ \
  --batch-size 100 \
  --parallel \
  --max-workers 8
```

### Phase 6.3: Process Results (5 minutes)
```python
# Aggregate results into single CSV
process_results(
    input_dir='data/raw/',
    output_file='data/processed/training_data_v1.csv'
)
```

### Phase 6.4: Train Model (5-10 minutes)
```python
# Train Random Forest
from sklearn.ensemble import RandomForestRegressor

# Load data
data = pd.read_csv('data/processed/training_data_v1.csv')

# Features and targets
X = data[['n_presses', 'topology_encoded', 'max_delay', 'refractory', 'variation']]
y = data['win_rate']

# Train
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X, y)

# Save
with open('data/models/random_forest_v1.pkl', 'wb') as f:
    pickle.dump(model, f)
```

---

## 🎯 Success Criteria

### Data Quality
- ✅ All scenarios run successfully (no crashes)
- ✅ Results cover full parameter space
- ✅ Statistical validity (5+ seeds per configuration)
- ✅ Reasonable performance variance (not all identical)

### Model Performance
- ✅ Training R² > 0.7 (explains 70%+ of variance)
- ✅ Test R² > 0.6 (generalizes to unseen configs)
- ✅ Feature importance analysis shows sensible patterns
- ✅ Predictions align with Phase 5 baseline (sanity check)

### Validation
- ✅ Model predicts 4-press optimal params correctly
- ✅ Model predicts 7-press needs different params than 4-press
- ✅ Predicted win rates match actual within ±10%

---

## 📊 Exploratory Data Analysis Questions

After data collection, analyze:

1. **Parameter Importance**: Which parameters matter most?
   - Does topology have bigger impact than max_delay?
   - Is variation significant or noise?

2. **Configuration Patterns**:
   - Do small fleets (4-5 presses) prefer different settings than large (7-8)?
   - Does realistic mix behave differently than uniform?

3. **Performance Distribution**:
   - What's the range of win rates (worst to best)?
   - Are there clear "bad" parameter combinations?

4. **Interactions**:
   - Does ring topology + high delay work better than all_to_all + low delay?
   - Are there synergistic parameter combinations?

---

## 🔄 Iteration Plan

### v1 (Initial): Conservative Grid
- 4,050 scenarios
- Simple parameter ranges
- Validate approach

### v2 (Expanded): If v1 successful
- Add line, star topologies
- Add small, large mixes
- More granular delay values [3, 4, 5, 6, 7]
- Total: ~15,000-20,000 scenarios

### v3 (Fine-tuning): If needed
- Focus on promising parameter regions
- Add edge cases (extreme values)
- Test robustness

---

## 📝 Next Steps

1. **Create scenario generation script** (`data/scenarios/generation_script.py`)
2. **Create data processing script** (`scripts/generate_training_data.py`)
3. **Run v1 data collection** (4,050 scenarios)
4. **Analyze results** (exploratory data analysis)
5. **Train initial model** (Random Forest)
6. **Validate predictions** (compare to Phase 5 baseline)
7. **Iterate if needed** (expand to v2 if model performance good)

---

## 💡 Key Insights to Remember

**From Phase 5:**
- Static parameters (ring, 5s, 30%, 0.1) gave 60-95% win rate range
- This variance proves parameters need optimization per configuration
- Best: 4 presses (95%), Worst: 7 presses (60%)

**What ML Will Learn:**
- "For 4 presses + realistic mix → use topology X, delay Y, refractory Z"
- "For 7 presses + realistic mix → use topology A, delay B, refractory C"
- Essentially: a lookup table that generalizes to unseen configurations

**Why This Works:**
- We're not optimizing the algorithm itself
- We're finding optimal PARAMETERS for the proven algorithm
- The cardiac algorithm is the "engine", AI tunes the "settings"

---

**Ready to generate training data!** 🚀
