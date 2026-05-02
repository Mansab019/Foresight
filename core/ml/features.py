import pandas as pd
import numpy as np
from django.contrib.auth.models import User
from core.models import Transaction


def load_transactions(user):
    """
    Load all transactions for a user from PostgreSQL
    Returns a clean Pandas DataFrame
    """
    qs = Transaction.objects.filter(user=user).values(
        'date', 'amount', 'category'
    )

    if not qs.exists():
        return pd.DataFrame()

    df = pd.DataFrame(list(qs))
    df['date'] = pd.to_datetime(df['date'])
    df['amount'] = df['amount'].astype(float)
    return df


def engineer_features(df):
    """
    Transform raw transactions into ML-ready features

    Input:  raw transactions DataFrame
    Output: feature matrix X and target vector y
    """

    if df.empty:
        return pd.DataFrame(), pd.Series()

    # ── STEP 1: Group by month and category ──────────
    # We predict monthly spending per category
    # So we aggregate daily transactions to monthly totals
    df['year_month'] = df['date'].dt.to_period('M')

    monthly = df.groupby(
        ['year_month', 'category']
    )['amount'].sum().reset_index()

    monthly['year_month_dt'] = monthly['year_month'].dt.to_timestamp()

    # ── STEP 2: Extract time features ────────────────
    monthly['month']     = monthly['year_month_dt'].dt.month
    monthly['quarter']   = monthly['year_month_dt'].dt.quarter
    monthly['year']      = monthly['year_month_dt'].dt.year

    # Month number from start — captures overall trend
    min_date = monthly['year_month_dt'].min()
    monthly['months_since_start'] = (
        (monthly['year_month_dt'].dt.year - min_date.year) * 12 +
        (monthly['year_month_dt'].dt.month - min_date.month)
    )

    # ── STEP 3: Rolling averages per category ────────
    # Sort first — rolling needs chronological order
    monthly = monthly.sort_values(['category', 'year_month_dt'])

    monthly['rolling_3m'] = monthly.groupby('category')['amount'].transform(
        lambda x: x.rolling(window=3, min_periods=1).mean()
    )

    monthly['rolling_6m'] = monthly.groupby('category')['amount'].transform(
        lambda x: x.rolling(window=6, min_periods=1).mean()
    )

    # ── STEP 4: Lag features ─────────────────────────
    # Last month's spending is a strong predictor
    monthly['lag_1m'] = monthly.groupby('category')['amount'].shift(1)
    monthly['lag_2m'] = monthly.groupby('category')['amount'].shift(2)

    # Fill NaN lags with rolling average
    monthly['lag_1m'] = monthly['lag_1m'].fillna(monthly['rolling_3m'])
    monthly['lag_2m'] = monthly['lag_2m'].fillna(monthly['rolling_3m'])

    # ── STEP 5: Category encoding ────────────────────
    # Models need numbers not strings
    category_map = {
        'food': 0, 'transport': 1, 'rent': 2,
        'utilities': 3, 'entertainment': 4,
        'healthcare': 5, 'shopping': 6,
        'education': 7, 'other': 8
    }
    monthly['category_code'] = monthly['category'].map(category_map).fillna(8)

    # ── STEP 6: Define features and target ───────────
    feature_cols = [
        'month',
        'quarter',
        'months_since_start',
        'rolling_3m',
        'rolling_6m',
        'lag_1m',
        'lag_2m',
        'category_code',
    ]

    # Drop rows with any remaining NaN values
    monthly = monthly.dropna(subset=feature_cols + ['amount'])

    X = monthly[feature_cols]
    y = monthly['amount']

    # Keep metadata for generating predictions later
    metadata = monthly[['category', 'year_month_dt']].copy()

    return X, y, metadata, monthly