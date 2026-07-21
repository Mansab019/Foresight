import joblib
import pandas as pd
import numpy as np
from datetime import date
from dateutil.relativedelta import relativedelta
from core.models import Prediction


def generate_predictions(user, best_model_name='unknown', batch=None):
    """
    Loads the saved best model
    Generates next month predictions per category
    Saves predictions to PostgreSQL predictions table
    If batch is given, uses that upload's own model and
    tags the saved predictions with the same batch, keeping
    them separate from the user's main merged forecast
    """

    print(f"\nGenerating predictions for: {user.username}")

    # ── STEP 1: Load saved model ──────────────────────
    suffix = f'_batch{batch.id}' if batch is not None else ''
    model_path = f'ml_models/{user.username}{suffix}_best_model.pkl'
    metadata_path = f'ml_models/{user.username}{suffix}_metadata.pkl'

    try:
        model = joblib.load(model_path)
        saved = joblib.load(metadata_path)
        monthly = saved['monthly']
    except FileNotFoundError:
        print("No trained model found. Run training first.")
        return []

    # ── STEP 2: Build next month features ────────────
    next_month = date.today().replace(day=1) + relativedelta(months=1)
    categories = monthly['category'].unique()

    prediction_rows = []

    for category in categories:
        cat_data = monthly[monthly['category'] == category].sort_values('year_month_dt')

        if cat_data.empty:
            continue

        # Get latest values for this category
        latest = cat_data.iloc[-1]

        category_map = {
            'food': 0, 'transport': 1, 'rent': 2,
            'utilities': 3, 'entertainment': 4,
            'healthcare': 5, 'shopping': 6,
            'education': 7, 'other': 8
        }

        # Build feature row for next month
        feature_row = {
            'month':              next_month.month,
            'quarter':            (next_month.month - 1) // 3 + 1,
            'months_since_start': latest['months_since_start'] + 1,
            'rolling_3m':         latest['rolling_3m'],
            'rolling_6m':         latest['rolling_6m'],
            'lag_1m':             latest['amount'],
            'lag_2m':             latest['lag_1m'],
            'category_code':      category_map.get(category, 8),
        }

        X_pred = pd.DataFrame([feature_row])

        # ── STEP 3: Predict ───────────────────────────
        predicted_amount = model.predict(X_pred)[0]

        # Ensure prediction is not negative
        predicted_amount = max(0, round(predicted_amount, 2))

        prediction_rows.append({
            'category': category,
            'predicted_amount': predicted_amount,
        })

    # ── STEP 4: Save predictions to PostgreSQL ────────
    # Delete old predictions for this user/batch and month
    Prediction.objects.filter(
        user=user,
        batch=batch,
        prediction_month=next_month
    ).delete()

    saved_predictions = []

    for row in prediction_rows:
        pred = Prediction.objects.create(
            user=user,
            batch=batch,
            category=row['category'],
            predicted_amount=row['predicted_amount'],
            prediction_month=next_month,
            model_version=f'{best_model_name}_v1.0'
        )
        saved_predictions.append(pred)
        print(f"  {row['category']:<15} → {row['predicted_amount']}")

    print(f"\nSaved {len(saved_predictions)} predictions to database")
    return saved_predictions