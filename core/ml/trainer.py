import joblib
import os
import copy
from sklearn.model_selection import train_test_split
from core.ml.features import load_transactions, engineer_features
from core.ml.registry import MODEL_REGISTRY
from core.ml.evaluator import evaluate_model, compare_models


def train_all_models(user):
    """
    Loads data, engineers features, trains all 4 models,
    evaluates each one, returns the best model and results
    """

    print(f"\nStarting training for user: {user.username}")

    # ── STEP 1: Load data from PostgreSQL ────────────
    print("Loading transactions from database...")
    df = load_transactions(user)

    if df.empty:
        print("No transactions found. Cannot train.")
        return None, None, None

    print(f"Loaded {len(df)} transactions")

    # ── STEP 2: Engineer features ─────────────────────
    print("Engineering features...")
    X, y, metadata, monthly = engineer_features(df)

    if X.empty:
        print("Feature engineering failed.")
        return None, None, None

    print(f"Feature matrix shape: {X.shape}")
    print(f"Target vector shape:  {y.shape}")

    # ── STEP 3: Train/test split ──────────────────────
    # 80% training, 20% testing
    # shuffle=False keeps time order intact
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, shuffle=False
    )

    print(f"Training samples: {len(X_train)}")
    print(f"Testing samples:  {len(X_test)}")

    # ── STEP 4: Train and evaluate all 4 models ───────
    results = {}
    trained_models = {}

    for model_name, model_pipeline in MODEL_REGISTRY.items():
        print(f"Training {model_name}...")

        # Deep copy prevents models sharing state
        model = copy.deepcopy(model_pipeline)

        # Train
        model.fit(X_train, y_train)

        # Evaluate on test data
        metrics = evaluate_model(model, X_test, y_test)

        results[model_name] = metrics
        trained_models[model_name] = model

        print(f"  MAE: {metrics['mae']}  RMSE: {metrics['rmse']}")

    # ── STEP 5: Compare and pick winner ──────────────
    best_model_name = compare_models(results)
    best_model = trained_models[best_model_name]

    # ── STEP 6: Save best model to disk ──────────────
    os.makedirs('ml_models', exist_ok=True)
    model_path = f'ml_models/{user.username}_best_model.pkl'
    joblib.dump(best_model, model_path)
    print(f"Best model saved: {model_path}")

    # Also save metadata for predictions
    metadata_path = f'ml_models/{user.username}_metadata.pkl'
    joblib.dump({'monthly': monthly, 'metadata': metadata}, metadata_path)

    return best_model, best_model_name, results