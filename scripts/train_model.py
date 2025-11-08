"""
AI Model Training Script

Trains a Random Forest model to predict optimal coordination parameters
based on press configuration (count, mix, topology).

Usage:
    # Train model on generated data
    python scripts/train_model.py --data data/processed/training_data_v1_20251104_230136.csv

    # Train with custom settings
    python scripts/train_model.py --data <csv_file> --test-size 0.2 --n-estimators 200
"""

import sys
import os
import argparse
import pickle
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime

from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


def load_and_preprocess_data(csv_file):
    """
    Load training data and prepare features.

    Returns:
        df: Full dataframe
        X: Feature matrix (scenario + parameters)
        y: Target (peak_reduction_pct)
        feature_names: List of feature names
        encoders: Dict of label encoders for categorical features
    """
    print(f"\n📂 Loading data from {csv_file}...")
    df = pd.read_csv(csv_file)

    print(f"   Loaded {len(df)} scenarios")
    print(f"   Columns: {list(df.columns)}")

    # Feature columns
    feature_cols = [
        'n_presses',           # Scenario input
        'mix',                 # Scenario input (categorical)
        'topology',            # Parameter (categorical)
        'max_delay_sec',       # Parameter
        'refractory_pct',      # Parameter
        'variation',           # Parameter
    ]

    # Create feature matrix
    X = df[feature_cols].copy()

    # Encode categorical variables
    encoders = {}
    for col in ['mix', 'topology']:
        le = LabelEncoder()
        X[col] = le.fit_transform(X[col])
        encoders[col] = le
        print(f"   Encoded '{col}': {dict(zip(le.classes_, le.transform(le.classes_)))}")

    # Target variable
    y = df['peak_reduction_pct'].values

    print(f"\n✓ Preprocessed data:")
    print(f"   Features shape: {X.shape}")
    print(f"   Target shape: {y.shape}")
    print(f"   Target range: [{y.min():.1f}%, {y.max():.1f}%]")
    print(f"   Target mean: {y.mean():.1f}%")

    return df, X, y, feature_cols, encoders


def train_model(X, y, test_size=0.2, n_estimators=100, random_state=42):
    """
    Train Random Forest model.

    Returns:
        model: Trained model
        X_train, X_test, y_train, y_test: Split data
        metrics: Dict of performance metrics
    """
    print(f"\n🚀 Training Random Forest model...")
    print(f"   n_estimators: {n_estimators}")
    print(f"   test_size: {test_size}")
    print(f"   random_state: {random_state}")

    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state
    )

    print(f"\n   Training set: {len(X_train)} samples")
    print(f"   Test set: {len(X_test)} samples")

    # Train model
    model = RandomForestRegressor(
        n_estimators=n_estimators,
        random_state=random_state,
        n_jobs=-1,  # Use all CPU cores
        verbose=1
    )

    model.fit(X_train, y_train)

    print(f"\n✓ Model trained!")

    # Evaluate
    y_pred_train = model.predict(X_train)
    y_pred_test = model.predict(X_test)

    metrics = {
        'train': {
            'mse': mean_squared_error(y_train, y_pred_train),
            'rmse': np.sqrt(mean_squared_error(y_train, y_pred_train)),
            'mae': mean_absolute_error(y_train, y_pred_train),
            'r2': r2_score(y_train, y_pred_train),
        },
        'test': {
            'mse': mean_squared_error(y_test, y_pred_test),
            'rmse': np.sqrt(mean_squared_error(y_test, y_pred_test)),
            'mae': mean_absolute_error(y_test, y_pred_test),
            'r2': r2_score(y_test, y_pred_test),
        }
    }

    print(f"\n📊 Model Performance:")
    print(f"   Training:")
    print(f"      R² Score: {metrics['train']['r2']:.4f}")
    print(f"      RMSE: {metrics['train']['rmse']:.2f}%")
    print(f"      MAE: {metrics['train']['mae']:.2f}%")
    print(f"   Test:")
    print(f"      R² Score: {metrics['test']['r2']:.4f}")
    print(f"      RMSE: {metrics['test']['rmse']:.2f}%")
    print(f"      MAE: {metrics['test']['mae']:.2f}%")

    return model, X_train, X_test, y_train, y_test, metrics


def cross_validate_model(model, X, y, cv=5):
    """Run cross-validation to assess model stability."""
    print(f"\n🔄 Running {cv}-fold cross-validation...")

    cv_scores = cross_val_score(
        model, X, y,
        cv=cv,
        scoring='r2',
        n_jobs=-1
    )

    print(f"\n   Cross-validation R² scores: {cv_scores}")
    print(f"   Mean: {cv_scores.mean():.4f}")
    print(f"   Std: {cv_scores.std():.4f}")

    return cv_scores


def analyze_feature_importance(model, feature_names):
    """Analyze which features are most important."""
    print(f"\n🔍 Feature Importance:")

    importances = model.feature_importances_
    indices = np.argsort(importances)[::-1]

    for i, idx in enumerate(indices):
        print(f"   {i+1}. {feature_names[idx]}: {importances[idx]:.4f}")

    return dict(zip(feature_names, importances))


def save_model(model, encoders, feature_names, metrics, output_dir='models'):
    """Save trained model and metadata."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Save model
    model_file = output_dir / f"cardiac_optimizer_{timestamp}.pkl"
    with open(model_file, 'wb') as f:
        pickle.dump({
            'model': model,
            'encoders': encoders,
            'feature_names': feature_names,
            'metrics': metrics,
            'timestamp': timestamp,
        }, f)

    print(f"\n✓ Model saved to {model_file}")

    return model_file


def main():
    parser = argparse.ArgumentParser(
        description='Train AI model for cardiac coordination optimization'
    )

    parser.add_argument(
        '--data',
        type=str,
        required=True,
        help='Path to training data CSV'
    )

    parser.add_argument(
        '--test-size',
        type=float,
        default=0.2,
        help='Fraction of data for test set (default: 0.2)'
    )

    parser.add_argument(
        '--n-estimators',
        type=int,
        default=100,
        help='Number of trees in Random Forest (default: 100)'
    )

    parser.add_argument(
        '--output-dir',
        type=str,
        default='models',
        help='Directory to save trained model (default: models)'
    )

    parser.add_argument(
        '--cv',
        type=int,
        default=5,
        help='Number of cross-validation folds (default: 5)'
    )

    args = parser.parse_args()

    print("=" * 70)
    print("AI MODEL TRAINING - CARDIAC COORDINATION OPTIMIZER")
    print("=" * 70)

    # Load and preprocess data
    df, X, y, feature_names, encoders = load_and_preprocess_data(args.data)

    # Train model
    model, X_train, X_test, y_train, y_test, metrics = train_model(
        X, y,
        test_size=args.test_size,
        n_estimators=args.n_estimators
    )

    # Cross-validation
    cv_scores = cross_validate_model(model, X, y, cv=args.cv)
    metrics['cv_scores'] = cv_scores.tolist()
    metrics['cv_mean'] = float(cv_scores.mean())
    metrics['cv_std'] = float(cv_scores.std())

    # Feature importance
    importances = analyze_feature_importance(model, feature_names)
    metrics['feature_importance'] = importances

    # Save model
    model_file = save_model(model, encoders, feature_names, metrics, args.output_dir)

    print("\n" + "=" * 70)
    print("MODEL TRAINING COMPLETE")
    print("=" * 70)
    print(f"\nModel file: {model_file}")
    print(f"\nTest Performance:")
    print(f"  R² Score: {metrics['test']['r2']:.4f}")
    print(f"  RMSE: {metrics['test']['rmse']:.2f}%")
    print(f"  MAE: {metrics['test']['mae']:.2f}%")
    print(f"\nCross-validation: {metrics['cv_mean']:.4f} ± {metrics['cv_std']:.4f}")
    print(f"\nTop 3 Features:")
    for i, (feat, imp) in enumerate(sorted(importances.items(), key=lambda x: x[1], reverse=True)[:3], 1):
        print(f"  {i}. {feat}: {imp:.4f}")
    print("\nNext step: Use this model to recommend optimal parameters!")
    print()


if __name__ == "__main__":
    main()
