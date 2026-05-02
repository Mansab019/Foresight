import pandas as pd
from .models import Transaction


# ─────────────────────────────────────────
# Valid categories our system accepts
# ─────────────────────────────────────────
VALID_CATEGORIES = [
    'food', 'transport', 'rent', 'utilities',
    'entertainment', 'healthcare', 'shopping',
    'education', 'other'
]


# ─────────────────────────────────────────
# FUNCTION 1 — clean_dataframe
# Used by import_csv to clean raw data
# ─────────────────────────────────────────
def clean_dataframe(df):
    """
    Takes a raw DataFrame from CSV
    Returns a cleaned DataFrame ready for saving
    """

    # Strip whitespace from column names
    df.columns = df.columns.str.strip().str.lower()

    # Drop rows where amount or date is missing
    df = df.dropna(subset=['amount', 'date'])

    # Convert amount column from text to number
    df['amount'] = pd.to_numeric(df['amount'], errors='coerce')

    # Drop rows where amount conversion failed
    df = df.dropna(subset=['amount'])

    # Remove negative or zero amounts
    df = df[df['amount'] > 0]

    # Convert date column to proper date format
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df = df.dropna(subset=['date'])

    # Clean and validate category
    df['category'] = df['category'].str.strip().str.lower()
    df['category'] = df['category'].apply(
        lambda x: x if x in VALID_CATEGORIES else 'other'
    )

    # Clean description
    df['description'] = df['description'].fillna('').str.strip()

    return df


# ─────────────────────────────────────────
# FUNCTION 2 — import_csv
# Handles our sample transactions.csv
# Long format: one row = one transaction
# ─────────────────────────────────────────
def import_csv(file_path, user):
    """
    Main function — reads CSV, cleans it, saves to PostgreSQL
    Returns a summary dict with results
    """

    summary = {
        'total_rows': 0,
        'imported': 0,
        'skipped': 0,
        'errors': []
    }

    try:
        # Read CSV file into a Pandas DataFrame
        df = pd.read_csv(file_path)
        summary['total_rows'] = len(df)

        # Clean the data
        df = clean_dataframe(df)

        # Loop through each row and save to database
        for index, row in df.iterrows():
            try:
                Transaction.objects.create(
                    user=user,
                    amount=row['amount'],
                    category=row['category'],
                    description=row['description'],
                    date=row['date'].date(),
                    source='csv'
                )
                summary['imported'] += 1

            except Exception as e:
                summary['skipped'] += 1
                summary['errors'].append(f"Row {index}: {str(e)}")

    except Exception as e:
        summary['errors'].append(f"File error: {str(e)}")

    return summary


# ─────────────────────────────────────────
# FUNCTION 3 — import_kaggle_monthly
# Handles Kaggle wide format dataset
# Wide format: one row = one whole month
# Transforms to long format using pd.melt()
# ─────────────────────────────────────────
def import_kaggle_monthly(file_path, user):
    """
    Reads wide format Kaggle monthly spending CSV
    Melts it into long format
    Saves each category per month as separate transaction
    """

    summary = {
        'total_rows': 0,
        'imported': 0,
        'skipped': 0,
        'errors': []
    }

    # Category mapping — we fill this after seeing
    # actual column names from print statement below
    COLUMN_MAP = {
    #     'Groceries (â,¹)':              'food',
    #     'Rent (â,¹)':                   'rent',
    #     'Transportation (â,¹)':         'transport',
    #     'Gym (â,¹)':                    'other',
    #     'Utilities (â,¹)':              'utilities',
    #     'Healthcare (â,¹)':             'healthcare',
    #     'Dining & Entertainment (â,¹)': 'entertainment',
    #     'Shopping & Wants (â,¹)':       'shopping',
    # 
        'Groceries (₹)':              'food',
        'Rent (₹)':                   'rent',
        'Transportation (₹)':         'transport',
        'Gym (₹)':                    'other',
        'Utilities (₹)':              'utilities',
        'Healthcare (₹)':             'healthcare',
        'Dining & Entertainment (₹)': 'entertainment',
        'Shopping & Wants (₹)':       'shopping',
     }

    try:
        # Read CSV — try utf-8 first
        df = pd.read_csv(file_path, encoding='utf-8')

        # IMPORTANT — print exact column names
        # so we can fix COLUMN_MAP if needed
        print("Columns found:", list(df.columns))

        # Parse Month column as dates
        df['date'] = pd.to_datetime(df['Month'], errors='coerce')
        df = df.dropna(subset=['date'])

        # Keep only columns that exist in both
        # our COLUMN_MAP and the actual CSV
        available_cols = {
            col: cat for col, cat in COLUMN_MAP.items()
            if col in df.columns
        }

        print("Matched columns:", list(available_cols.keys()))
        print("Unmatched columns:", [
            col for col in COLUMN_MAP.keys()
            if col not in df.columns
        ])

        # MELT — wide format to long format
        # This is the key transformation
        df_melted = df.melt(
            id_vars=['date'],
            value_vars=list(available_cols.keys()),
            var_name='raw_category',
            value_name='amount'
        )

        # Map raw column names to our categories
        df_melted['category'] = df_melted['raw_category'].map(available_cols)

        # Clean amounts
        df_melted['amount'] = pd.to_numeric(
            df_melted['amount'], errors='coerce'
        )

        # Remove zero, negative or missing amounts
        df_melted = df_melted[df_melted['amount'] > 0]
        df_melted = df_melted.dropna(subset=['amount', 'category'])

        summary['total_rows'] = len(df_melted)

        # Save each row to PostgreSQL
        for index, row in df_melted.iterrows():
            try:
                Transaction.objects.create(
                    user=user,
                    amount=row['amount'],
                    category=row['category'],
                    description='Kaggle monthly spending dataset',
                    date=row['date'].date(),
                    source='csv'
                )
                summary['imported'] += 1

            except Exception as e:
                summary['skipped'] += 1
                summary['errors'].append(f"Row {index}: {str(e)}")

    except Exception as e:
        summary['errors'].append(f"File error: {str(e)}")

    return summary


