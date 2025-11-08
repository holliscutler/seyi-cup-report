"""
Parameter Recommendation Script

Uses trained AI model to recommend optimal coordination parameters
for a given press configuration.

Usage:
    # Recommend for specific scenario
    python scripts/recommend_parameters.py --n-presses 7 --mix realistic

    # Batch recommendations for all scenarios
    python scripts/recommend_parameters.py --batch

    # Use specific model file
    python scripts/recommend_parameters.py --n-presses 5 --mix varied --model models/cardiac_optimizer_20251104_232737.pkl
"""

import sys
import os
import argparse
import pickle
import pandas as pd
import numpy as np
from pathlib import Path
from itertools import product

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


def load_model(model_file):
    """Load trained model and metadata."""
    with open(model_file, 'rb') as f:
        data = pickle.load(f)

    print(f"✓ Loaded model from {model_file}")
    print(f"  Timestamp: {data['timestamp']}")
    print(f"  Test R²: {data['metrics']['test']['r2']:.4f}")
    print(f"  Test RMSE: {data['metrics']['test']['rmse']:.2f}%")

    return data['model'], data['encoders'], data['feature_names']


def recommend_parameters(model, encoders, feature_names, n_presses, mix):
    """
    Recommend optimal coordination parameters for a given scenario.

    Returns:
        best_params: Dict of recommended parameters
        predictions: DataFrame of all predictions
    """
    print(f"\n🔍 Finding optimal parameters for:")
    print(f"   n_presses: {n_presses}")
    print(f"   mix: {mix}")

    # Define parameter space to search
    topologies = ['ring', 'all_to_all']
    max_delays = [3, 5, 7]
    refractory_pcts = [20, 30, 40]
    variations = [0.05, 0.1, 0.15]

    # Generate all combinations
    combinations = list(product(topologies, max_delays, refractory_pcts, variations))
    print(f"\n   Testing {len(combinations)} parameter combinations...")

    # Create feature matrix
    rows = []
    for topology, max_delay, refractory_pct, variation in combinations:
        row = {
            'n_presses': n_presses,
            'mix': mix,
            'topology': topology,
            'max_delay_sec': max_delay,
            'refractory_pct': refractory_pct,
            'variation': variation,
        }
        rows.append(row)

    df = pd.DataFrame(rows)

    # Encode categorical variables
    for col in ['mix', 'topology']:
        df[col] = encoders[col].transform(df[col])

    # Predict
    X = df[feature_names].values
    predictions = model.predict(X)

    # Add predictions back to dataframe (decoded)
    results = pd.DataFrame(rows)  # Use original (decoded) values
    results['predicted_peak_reduction'] = predictions

    # Sort by predicted performance
    results = results.sort_values('predicted_peak_reduction', ascending=False)

    # Best parameters
    best = results.iloc[0]
    best_params = {
        'topology': best['topology'],
        'max_delay_sec': best['max_delay_sec'],
        'refractory_pct': best['refractory_pct'],
        'variation': best['variation'],
        'predicted_peak_reduction': best['predicted_peak_reduction'],
    }

    print(f"\n✨ Recommended Parameters:")
    print(f"   Topology: {best_params['topology']}")
    print(f"   Max Delay: {best_params['max_delay_sec']}s")
    print(f"   Refractory: {best_params['refractory_pct']}%")
    print(f"   Variation: {best_params['variation']}")
    print(f"   Predicted Peak Reduction: {best_params['predicted_peak_reduction']:.1f}%")

    # Show top 5
    print(f"\n📊 Top 5 Parameter Combinations:")
    for i, row in results.head(5).iterrows():
        print(f"   {row['topology']:12s} | delay={row['max_delay_sec']}s | refract={row['refractory_pct']}% | var={row['variation']:.2f} → {row['predicted_peak_reduction']:5.1f}%")

    return best_params, results


def batch_recommendations(model, encoders, feature_names):
    """Generate recommendations for all common scenarios."""
    press_counts = [4, 5, 6, 7, 8]
    mixes = ['realistic', 'varied', 'uniform']

    print("\n" + "=" * 90)
    print("BATCH PARAMETER RECOMMENDATIONS")
    print("=" * 90)

    all_recommendations = []

    for n_presses in press_counts:
        for mix in mixes:
            best_params, _ = recommend_parameters(model, encoders, feature_names, n_presses, mix)

            recommendation = {
                'n_presses': n_presses,
                'mix': mix,
                **best_params
            }
            all_recommendations.append(recommendation)

    # Create summary table
    df = pd.DataFrame(all_recommendations)

    print("\n" + "=" * 90)
    print("SUMMARY: OPTIMAL PARAMETERS BY SCENARIO")
    print("=" * 90)
    print(f"\n{df.to_string(index=False)}")

    # Save to CSV
    output_file = Path('models') / 'parameter_recommendations.csv'
    df.to_csv(output_file, index=False)
    print(f"\n✓ Saved recommendations to {output_file}")

    return df


def main():
    parser = argparse.ArgumentParser(
        description='Recommend optimal coordination parameters using trained AI model'
    )

    parser.add_argument(
        '--model',
        type=str,
        default=None,
        help='Path to trained model file (default: latest in models/)'
    )

    parser.add_argument(
        '--n-presses',
        type=int,
        help='Number of presses (4-8)'
    )

    parser.add_argument(
        '--mix',
        type=str,
        choices=['realistic', 'varied', 'uniform'],
        help='Fleet mix'
    )

    parser.add_argument(
        '--batch',
        action='store_true',
        help='Generate recommendations for all scenarios'
    )

    args = parser.parse_args()

    print("=" * 70)
    print("PARAMETER RECOMMENDATION - CARDIAC COORDINATION OPTIMIZER")
    print("=" * 70)

    # Find model file
    if args.model is None:
        # Use latest model
        model_dir = Path('models')
        model_files = sorted(model_dir.glob('cardiac_optimizer_*.pkl'))
        if not model_files:
            print("Error: No model files found in models/")
            print("Please train a model first: python scripts/train_model.py --data <csv_file>")
            sys.exit(1)
        model_file = model_files[-1]
    else:
        model_file = Path(args.model)

    # Load model
    model, encoders, feature_names = load_model(model_file)

    # Batch or single recommendation
    if args.batch:
        batch_recommendations(model, encoders, feature_names)
    else:
        if args.n_presses is None or args.mix is None:
            print("\nError: Must specify --n-presses and --mix (or use --batch)")
            print("\nExample:")
            print("  python scripts/recommend_parameters.py --n-presses 7 --mix realistic")
            sys.exit(1)

        recommend_parameters(model, encoders, feature_names, args.n_presses, args.mix)

    print("\n" + "=" * 70)
    print("RECOMMENDATION COMPLETE")
    print("=" * 70)
    print()


if __name__ == "__main__":
    main()
