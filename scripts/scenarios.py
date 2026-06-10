"""
Scenario Construction and Baseline Risk
=========================================
Builds privacy risk scenarios from labeled incidents and computes
baseline risk scores per scenario.

Input:  data/processed/privacyrisq_labeled.xlsx
Output: results/mort_scenarios.xlsx
"""

import pandas as pd
from pathlib import Path

# === CONFIGURATION ===
INPUT_FILE  = Path(__file__).parent.parent / "data" / "processed" / "privacyrisq_labeled.xlsx"
OUTPUT_FILE = Path(__file__).parent.parent / "results" / "mort_scenarios.xlsx"


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


def build_scenarios(df):
    """
    Constructs scenarios as (AssetType, LINDDUN, DataCategory) triples
    and computes likelihood, severity and baseline risk.
    """
    total_incidents = df['Incident ID'].nunique()
    print(f"Total unique incidents: {total_incidents}")

    # Filter Asset Types with insufficient coverage
    df = df[~df['Asset Type'].isin(['Unknown', 'Services provided by supplier'])]
    print(f"After Asset Type filter: {df['Incident ID'].nunique()} incidents")

    # Explode LINDDUN combinations into individual rows
    df['LINDDUN categories'] = df['LINDDUN categories'].str.split(', ')
    df = df.explode('LINDDUN categories')

    # Remove Unawareness and Non-compliance (systematic misalignment)
    df = df[~df['LINDDUN categories'].isin(['Unawareness', 'Non-compliance'])]
    print(f"After LINDDUN filter:    {df['Incident ID'].nunique()} incidents")

    # Compute severity per incident
    df['severity'] = df.apply(get_severity, axis=1)
    df = df[df['severity'] > 0]

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
    scenarios = scenarios[scenarios['count'] >= 5]
    scenarios = scenarios.sort_values('baseline_risk', ascending=False)

    return scenarios


# === MAIN ===

if __name__ == "__main__":
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    print(f"Loading: {INPUT_FILE}\n")
    df = pd.read_excel(INPUT_FILE)
    print(f"Loaded {len(df)} incidents\n")

    scenarios = build_scenarios(df)

    print(f"\n--- Results ---")
    print(f"Valid scenarios (n>=5): {len(scenarios)}")
    print(f"\nTop 15 scenarios:")
    print(scenarios.head(15).to_string(index=False))

    scenarios.to_excel(OUTPUT_FILE, index=False)
    print(f"\nSaved to: {OUTPUT_FILE}")