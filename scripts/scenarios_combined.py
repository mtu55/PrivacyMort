"""
Scenario Construction and Baseline Risk
=========================================
Builds privacy risk scenarios from labeled incidents and computes
baseline risk scores per scenario.

LINDDUN categories are treated as full combinations (not exploded),
as 95-100% of technical threat categories co-occur with others.
Unawareness and Non-compliance are excluded due to systematic
misalignment with LINDDUN threat tree definitions.

Input:  data/processed/privacyrisq_labeled.xlsx
Output: results/mort_scenarios.xlsx
"""

import pandas as pd
from pathlib import Path

# === CONFIGURATION ===
INPUT_FILE  = Path(__file__).parent.parent / "data" / "processed" / "privacyrisq_labeled.xlsx"
OUTPUT_FILE = Path(__file__).parent.parent / "results" / "mort_scenarios.xlsx"

# LINDDUN categories to exclude
LINDDUN_EXCLUDE = ['Unawareness', 'Non-compliance']

# Asset types to exclude
ASSET_EXCLUDE = ['Unknown', 'Services provided by supplier']

# Minimum incidents per scenario
MIN_COUNT = 5


# === FUNCTIONS ===

def get_severity(row):
    """
    Derives severity score (1-4) from GDPR data category combination.

    Scale grounded in GDPR Art. 4(1) and Art. 9:
      4 - Credentials + Personal + Special categories (worst case)
      3 - Any combination involving Art. 9 data, or Credentials + Personal
      2 - Credentials only
      1 - Personal data only (Art. 4 baseline)
    """
    p = row['has_personal_data'] == 1
    s = row['has_special_categories'] == 1
    c = row['has_credentials'] == 1

    if c and p and s:   return 4  # Worst case
    elif c and p:       return 3  # Identity + access compromised
    elif p and s:       return 3  # Art. 9 + identifiable
    elif c and s:       return 3  # Art. 9 + access compromised
    elif s:             return 3  # Art. 9 alone: inherently high sensitivity
    elif c:             return 2  # Credentials without personal context
    elif p:             return 1  # Art. 4 baseline
    else:               return 0


def clean_linddun(combination, exclude):
    """
    Removes excluded categories from a LINDDUN combination string.
    Returns None if no valid categories remain.
    """
    if pd.isna(combination):
        return None
    cats = [c.strip() for c in str(combination).split(',')]
    cats = [c for c in cats if c not in exclude]
    return ', '.join(cats) if cats else None


def build_scenarios(df):
    total_incidents = df['Incident ID'].nunique()
    print(f"Total unique incidents (baseline for likelihood): {total_incidents}")

    # Filter Asset Types
    df = df[~df['Asset Type'].isin(ASSET_EXCLUDE)].copy()
    print(f"After Asset Type filter:  {df['Incident ID'].nunique()} incidents")

    # Remove excluded LINDDUN categories from combinations
    df['LINDDUN categories'] = df['LINDDUN categories'].apply(
        lambda x: clean_linddun(x, LINDDUN_EXCLUDE)
    )

    # Drop incidents where no valid LINDDUN category remains
    df = df[df['LINDDUN categories'].notna()].copy()
    print(f"After LINDDUN filter:     {df['Incident ID'].nunique()} incidents")

    # Compute severity per incident
    df['severity'] = df.apply(get_severity, axis=1)
    df = df[df['severity'] > 0]
    print(f"After severity filter:    {df['Incident ID'].nunique()} incidents")

    # Define scenario dimensions
    scenario_cols = [
        'has_personal_data',
        'has_special_categories',
        'has_credentials',
        'LINDDUN categories',
        'Asset Type',
    ]

    # Aggregate to scenario level
    scenarios = df.groupby(scenario_cols).agg(
        count=('Incident ID', 'nunique'),
        avg_severity=('severity', 'mean'),
    ).reset_index()

    # Likelihood relative to total incident population
    scenarios['likelihood'] = scenarios['count'] / total_incidents
    scenarios['baseline_risk'] = scenarios['likelihood'] * scenarios['avg_severity']

    # Remove sparse scenarios
    scenarios = scenarios[scenarios['count'] >= MIN_COUNT]
    scenarios = scenarios.sort_values('baseline_risk', ascending=False)

    return scenarios, total_incidents


# === MAIN ===

if __name__ == "__main__":
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    print(f"Loading: {INPUT_FILE}\n")
    df = pd.read_excel(INPUT_FILE)
    print(f"Loaded {len(df)} incidents\n")

    scenarios, total = build_scenarios(df)

    print(f"\n--- Results ---")
    print(f"Total incidents (N):    {total}")
    print(f"Valid scenarios (n≥{MIN_COUNT}): {len(scenarios)}")
    print(f"\nTop 15 scenarios:")
    print(scenarios.head(15).to_string(index=False))

    scenarios.to_excel(OUTPUT_FILE, index=False)
    print(f"\nSaved to: {OUTPUT_FILE}")