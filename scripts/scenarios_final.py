# scripts/scenarios.py
# Scenario construction and baseline risk estimation for PrivacyMort
#
# Scenario structure:
#   s = (LINDDUN, DataCategory, AssetTech)
#
#   DataCategory is a composite of three binary flags:
#     has_personal_data, has_special_categories, has_credentials
#
#   AssetContext is treated as a descriptive dimension: not used for
#   grouping but reported as a distribution within each scenario
#   (sheet 'scenarios_context').
#
#   CredentialProtection (formerly Data Protection State) is reported
#   only for scenarios where has_credentials = 1. It measures the
#   cryptographic quality of password storage at the time of the incident
#   and carries no meaningful signal for non-credential scenarios.
#
#   TargetType is excluded: only 33 of 2,037 incidents (1.6%) are
#   classified as Individual, providing no statistical discriminatory
#   power across scenarios.
#
# Likelihood   = n_scenario / N_total
# BaselineRisk = Likelihood × avg_severity
#
# Output: results/mort_scenarios_v8.xlsx
#   Sheet 'scenarios':             all scenarios with likelihood and baseline risk
#   Sheet 'scenarios_context':     AssetContext distribution per scenario
#   Sheet 'credential_protection': hashing quality distribution for
#                                  credential scenarios only

import pandas as pd
from pathlib import Path


# ---------------------------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------------------------

INPUT_FILE  = Path(__file__).parent.parent / "data" / "processed" / "privacyrisq_assets_final.xlsx"
OUTPUT_FILE = Path(__file__).parent.parent / "results" / "mort_scenarios_final.xlsx"

LINDDUN_EXCLUDE = []
MIN_COUNT       = 1
TOP_N_PRINT     = 10


# ---------------------------------------------------------------------------
# SEVERITY
# ---------------------------------------------------------------------------

def get_severity(row):
    p = row['has_personal_data']      == 1
    s = row['has_special_categories'] == 1
    c = row['has_credentials']        == 1

    if c and p and s:  return 6
    elif c and p:      return 4
    elif p and s:      return 4
    elif c and s:      return 4
    elif s:            return 1
    elif c:            return 1
    elif p:            return 1
    else:              return 0


# ---------------------------------------------------------------------------
# LINDDUN CLEANING
# ---------------------------------------------------------------------------

def clean_linddun(combination, exclude):
    if pd.isna(combination):
        return None
    cats = [c.strip() for c in str(combination).split(',')]
    cats = [c for c in cats if c not in exclude]
    return ', '.join(cats) if cats else None


# ---------------------------------------------------------------------------
# SCENARIO CONSTRUCTION
# ---------------------------------------------------------------------------

def build_scenarios(df):
    # LINDDUN-Filter
    df['LINDDUN categories'] = df['LINDDUN categories'].apply(
        lambda x: clean_linddun(x, LINDDUN_EXCLUDE)
    )
    df = df[df['LINDDUN categories'].notna()].copy()
    print(f"After LINDDUN filter:  {df['Incident ID'].nunique()} incidents")

    # Severity-Filter
    df['severity'] = df.apply(get_severity, axis=1)
    df = df[df['severity'] > 0].copy()
    print(f"After severity filter: {df['Incident ID'].nunique()} incidents")

    # Nenner ERST JETZT bestimmen — nur gefilterte Incidents
    total_incidents = df['Incident ID'].nunique()
    print(f"Likelihood denominator (post-filter): {total_incidents}")

    scenario_cols = [
        'has_personal_data',
        'has_special_categories',
        'has_credentials',
        'LINDDUN categories',
        'AssetTech',
    ]

    scenarios = df.groupby(scenario_cols).agg(
        count        = ('Incident ID', 'nunique'),
        avg_severity = ('severity', 'mean'),
    ).reset_index()

    scenarios['likelihood']    = scenarios['count'] / total_incidents
    scenarios['baseline_risk'] = scenarios['likelihood'] * scenarios['avg_severity']

    scenarios = scenarios[scenarios['count'] >= MIN_COUNT]
    scenarios = scenarios.sort_values('baseline_risk', ascending=False).reset_index(drop=True)
    scenarios.index += 1
    scenarios.index.name = 'scenario_rank'
    scenarios = scenarios.reset_index()

    return scenarios, df, total_incidents


# ---------------------------------------------------------------------------
# ASSETCONTEXT DISTRIBUTION
# ---------------------------------------------------------------------------

def analyze_asset_context(df_filtered, scenarios):
    scenario_cols = [
        'has_personal_data',
        'has_special_categories',
        'has_credentials',
        'LINDDUN categories',
        'AssetTech',
    ]

    rows = []

    for _, scen in scenarios.iterrows():
        mask = pd.Series(True, index=df_filtered.index)
        for col in scenario_cols:
            mask &= (df_filtered[col] == scen[col])

        incidents = df_filtered[mask]
        n = len(incidents)

        ctx_counts = (
            incidents['AssetContext']
            .fillna('Not reported')
            .value_counts()
        )

        for ctx, cnt in ctx_counts.items():
            rows.append({
                'scenario_rank':      int(scen['scenario_rank']),
                'baseline_risk':      round(scen['baseline_risk'], 4),
                'LINDDUN categories': scen['LINDDUN categories'],
                'AssetTech':          scen['AssetTech'],
                'AssetContext':        ctx,
                'count':              cnt,
                'pct':                round(cnt / n * 100, 1),
            })

    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# CREDENTIAL PROTECTION DISTRIBUTION
#
# Reported only for scenarios where has_credentials = 1.
# Measures the cryptographic quality of password storage (hashing algorithm)
# at the time of the incident. Signal comes almost exclusively from HIBP,
# where breach metadata includes algorithm information.
# For non-credential scenarios this dimension is undefined and excluded.
# ---------------------------------------------------------------------------

def analyze_credential_protection(df_filtered, scenarios):
    scenario_cols = [
        'has_personal_data',
        'has_special_categories',
        'has_credentials',
        'LINDDUN categories',
        'AssetTech',
    ]

    # Only credential scenarios
    cred_scenarios = scenarios[scenarios['has_credentials'] == 1]

    rows = []

    for _, scen in cred_scenarios.iterrows():
        mask = pd.Series(True, index=df_filtered.index)
        for col in scenario_cols:
            mask &= (df_filtered[col] == scen[col])

        incidents = df_filtered[mask]
        n = len(incidents)

        cp_counts = (
            incidents['Data Protection State']
            .fillna('Not reported')
            .value_counts()
        )

        for state, cnt in cp_counts.items():
            rows.append({
                'scenario_rank':          int(scen['scenario_rank']),
                'baseline_risk':          round(scen['baseline_risk'], 4),
                'LINDDUN categories':     scen['LINDDUN categories'],
                'AssetTech':              scen['AssetTech'],
                'CredentialProtection':   state,
                'count':                  cnt,
                'pct':                    round(cnt / n * 100, 1),
            })

    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# ENTRY POINT
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    print(f"Loading: {INPUT_FILE}\n")
    df_raw = pd.read_excel(INPUT_FILE)
    print(f"Loaded {len(df_raw)} rows\n")

    scenarios, df_clean, total = build_scenarios(df_raw)

    print(f"\n--- Scenario Results ---")
    print(f"Total incidents (N):     {total}")
    print(f"Valid scenarios (n≥{MIN_COUNT}):  {len(scenarios)}")
    print(f"\nTop {TOP_N_PRINT} scenarios by Baseline Risk:")
    print(scenarios.head(TOP_N_PRINT).to_string(index=False))

    ctx_dist = analyze_asset_context(df_clean, scenarios)
    cp_dist  = analyze_credential_protection(df_clean, scenarios)

    print(f"\n--- AssetContext Distribution (Top 3) ---")
    print(ctx_dist[ctx_dist['scenario_rank'] <= 3].to_string(index=False))

    print(f"\n--- Credential Protection Distribution (credential scenarios only) ---")
    print(cp_dist[cp_dist['scenario_rank'] <= 5].to_string(index=False))

    with pd.ExcelWriter(OUTPUT_FILE, engine='openpyxl') as writer:
        scenarios.to_excel(writer, sheet_name='scenarios',             index=False)
        ctx_dist.to_excel(writer,  sheet_name='scenarios_context',     index=False)
        cp_dist.to_excel(writer,   sheet_name='credential_protection', index=False)

    print(f"\nSaved → {OUTPUT_FILE}")
    print("  Sheets: scenarios | scenarios_context | credential_protection")