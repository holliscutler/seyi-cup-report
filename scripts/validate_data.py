"""Quick data validation script"""
import pandas as pd
import sys

if len(sys.argv) < 2:
    print("Usage: python scripts/validate_data.py <csv_file>")
    sys.exit(1)

csv_file = sys.argv[1]
df = pd.read_csv(csv_file)

print('='*70)
print('TEST DATA VALIDATION')
print('='*70)
print(f'\n📊 Dataset Shape: {df.shape[0]} rows × {df.shape[1]} columns')

print(f'\n✅ Columns ({len(df.columns)}):')
for col in df.columns:
    print(f'   - {col}')

print(f'\n📈 Feature Ranges (X):')
print(f'   n_presses: {df["n_presses"].unique()}')
print(f'   mix: {df["mix"].unique()}')
print(f'   topology: {df["topology"].unique()}')
print(f'   max_delay_sec: {df["max_delay_sec"].unique()}')
print(f'   refractory_pct: {df["refractory_pct"].unique()}')
print(f'   variation: {df["variation"].unique()}')
print(f'   seeds: {sorted(df["seed"].unique())}')

print(f'\n🎯 Target Statistics (y):')
print(f'   Win rate: {df["cardiac_wins"].sum()}/{len(df)} = {df["cardiac_wins"].sum()/len(df)*100:.1f}%')
print(f'   Peak reduction: {df["peak_reduction_pct"].min():.1f}% to {df["peak_reduction_pct"].max():.1f}%')
print(f'   Mean peak reduction: {df["peak_reduction_pct"].mean():.1f}%')
print(f'   Annual savings: ${df["annual_savings_usd"].min():.0f} to ${df["annual_savings_usd"].max():.0f}')
print(f'   Total delays: {df["total_delays"].min():.0f} to {df["total_delays"].max():.0f}')
print(f'   Collisions avoided: {df["collisions_avoided"].min():.0f} to {df["collisions_avoided"].max():.0f}')

print(f'\n🔍 Data Quality Checks:')
print(f'   Null values: {df.isnull().sum().sum()}')
print(f'   Duplicates: {df.duplicated().sum()}')
print(f'   Unique scenarios: {df["scenario_name"].nunique()}')

print(f'\n✨ Sample Performance:')
wins = df[df['cardiac_wins'] == True]
losses = df[df['cardiac_wins'] == False]
if len(wins) > 0:
    print(f'   Wins ({len(wins)}): avg peak reduction = {wins["peak_reduction_pct"].mean():.1f}%, avg savings = ${wins["annual_savings_usd"].mean():.0f}')
if len(losses) > 0:
    print(f'   Losses ({len(losses)}): avg peak reduction = {losses["peak_reduction_pct"].mean():.1f}%, avg savings = ${losses["annual_savings_usd"].mean():.0f}')

print(f'\n' + '='*70)
print('✅ TEST DATA LOOKS GOOD!' if df.isnull().sum().sum() == 0 else '⚠️  WARNING: Contains null values')
print('='*70)
