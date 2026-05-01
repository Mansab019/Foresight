import pandas as pd
from datetime import datetime
from .models import Transaction


# Valid categories our system accepts
VALID_CATEGORIES = [
    'food', 'transport', 'rent', 'utilities',
    'entertainment', 'healthcare', 'shopping',
    'education', 'other'
]


def clean_dataframe(df):
    """
    Takes a raw DataFrame from CSV
    Returns a cleaned DataFrame ready for saving
    """

    # Step 1 — strip whitespace from column names
    # CSV files often have spaces in headers
    df.columns = df.columns.str.strip().str.lower()

    # Step 2 — drop rows where amount or date is missing
    # We cannot save a transaction without these two
    df = df.dropna(subset=['amount', 'date'])

    # Step 3 — convert amount to a number
    # CSV stores everything as text — we need float
    df['amount'] = pd.to_numeric(df['amount'], errors='coerce')

    # Step 4 — drop rows where amount conversion failed
    df = df.dropna(subset=['amount'])

    # Step 5 — remove negative or zero amounts
    # An expense must be a positive number
    df = df[df['amount'] > 0]

    # Step 6 — convert date column to proper date format
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df = df.dropna(subset=['date'])

    # Step 7 — clean and validate category
    df['category'] = df['category'].str.strip().str.lower()
    df['category'] = df['category'].apply(
        lambda x: x if x in VALID_CATEGORIES else 'other'
    )

    # Step 8 — clean description
    df['description'] = df['description'].fillna('').str.strip()

    return df


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


