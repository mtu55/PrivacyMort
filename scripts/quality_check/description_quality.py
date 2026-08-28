"""
Description Quality Over Time
==============================
Checks data completeness per incident across all relevant fields,
counted per year.

Input:  data/raw/privacyrisq_export.csv
Output: results/description_quality.xlsx
"""

import pandas as pd
from pathlib import Path

# === CONFIGURATION ===
INPUT_FILE  = Path(__file__).parent.parent.parent / "data" / "raw" / "privacyrisq_export.csv"
OUTPUT_FILE = Path(__file__).parent.parent.parent / "results" / "description_quality.xlsx"

# Fields to check and what counts as missing
RELEVANT_FIELDS = {
    'Asset Type':           ['Unknown', 'unknown', ''],
    'LINDDUN categories':   ['Unknown', 'unknown', 'Uknown', ''],
    'Threat Actor':         ['Unknown', 'unknown', ''],
    'Data Protection State':['Unknown', 'unknown', ''],
    'Techniques Used':      ['Unknown', 'unknown', 'Uknown', ''],
}


def is_missing(value, missing_values):
    if pd.isna(value):
        return True
    return str(value).strip() in missing_values


def detect_date_column(df):
    candidates = [c for c in df.columns if any(
        k in c.lower() for k in ['date', 'year', 'time', 'when']
    )]
    if not candidates:
        raise ValueError(
            f"No date column found. Available columns: {list(df.columns)}"
        )
    print(f"Using date column: '{candidates[0]}'")
    return candidates[0]


if __name__ == "__main__":
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    print(f"Loading: {INPUT_FILE}\n")
    df = pd.read_csv(INPUT_FILE, sep=None, engine='python', on_bad_lines='skip')
    print(f"Loaded {len(df)} incidents\n")

    # Only check fields that actually exist in the dataset
    available_fields = {
        field: missing for field, missing in RELEVANT_FIELDS.items()
        if field in df.columns
    }
    missing_fields = [f for f in RELEVANT_FIELDS if f not in df.columns]
    if missing_fields:
        print(f"Warning: fields not found in dataset: {missing_fields}\n")

    # Count missing fields per incident
    for field, missing_values in available_fields.items():
        df[f'_missing_{field}'] = df[field].apply(
            lambda x: is_missing(x, missing_values)
        ).astype(int)

    missing_cols = [f'_missing_{f}' for f in available_fields]
    df['n_missing_fields'] = df[missing_cols].sum(axis=1)
    n_fields = len(available_fields)

    # Date
    date_col = detect_date_column(df)
    df['year'] = pd.to_datetime(df[date_col], errors='coerce').dt.year
    df = df[df['year'].notna()]
    df['year'] = df['year'].astype(int)

    # Aggregate per year
    quality = df.groupby('year').agg(
        n_incidents       = ('n_missing_fields', 'count'),
        avg_missing       = ('n_missing_fields', 'mean'),
        pct_complete      = ('n_missing_fields', lambda x: (x == 0).mean() * 100),
    ).reset_index()

    quality['avg_missing'] = quality['avg_missing'].round(2)
    quality['pct_complete'] = quality['pct_complete'].round(1)

    # Per-field missing rate per year
    field_rates = df.groupby('year')[missing_cols].mean().mul(100).round(1)
    field_rates.columns = [f.replace('_missing_', '') for f in field_rates.columns]
    field_rates = field_rates.reset_index()

    result = quality.merge(field_rates, on='year')

    print(result.to_string(index=False))
    print(f"\n(Checked {n_fields} fields per incident)")

    result.to_excel(OUTPUT_FILE, index=False)
    print(f"\nSaved to: {OUTPUT_FILE}")