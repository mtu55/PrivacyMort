# scripts/scenarios.py
# Scenario construction and baseline risk estimation for PrivacyMort
#
# Scenario structure:
#   s = (LINDDUN, DataCategory, AssetTech)
#
#   DataCategory is a composite of three binary flags:
#     has_personal_data, has_special_categories, has_credentials
#
#   AssetContext and Data Protection State are treated as descriptive
#   dimensions: they are not used for grouping but are analyzed as
#   distributions within each scenario (sheets 'scenarios_context'
#   and 'scenarios_dps').
#
#   TargetType is excluded from scenario construction: only 33 of 2,037
#   incidents (1.6%) are classified as Individual. The dimension has no
#   statistical discriminatory power and is retained in the dataset for
#   qualitative inspection only.
#
# Likelihood  = n_scenario / N_total
# BaselineRisk = Likelihood × avg_severity
#
# Output: results/mort_scenarios.xlsx
#   Sheet 'scenarios':         all scenarios with likelihood and baseline risk
#   Sheet 'scenarios_context': AssetContext distribution per scenario
#   Sheet 'scenarios_dps':     Data Protection State distribution per scenario

import pandas as pd
from pathlib import Path


# ---------------------------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------------------------

INPUT_FILE  = Path(__file__).parent.parent / "data" / "processed" / "privacyrisq_assets.xlsx"
OUTPUT_FILE = Path(__file__).parent.parent / "results" / "mort_scenarios.xlsx"

# LINDDUN categories to exclude from scenario construction.
# Empty by default: all categories are included.
LINDDUN_EXCLUDE = []

# Minimum number of incidents a scenario must contain to be reported.
MIN_COUNT = 1

# Number of top scenarios printed to console for quick inspection.
TOP_N_PRINT = 10


# ---------------------------------------------------------------------------
# SEVERITY
#
# Derived from three binary flags. The asymmetric scale reflects the
# non-linear increase in re-identification and harm potential when
# multiple sensitive data types co-occur.
#
#   0 : no personal data of any kind  → incident excluded downstream
#   1 : exactly one data type present
#   4 : two data types present
#   6 : all three types present
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
#
# Strips whitespace from comma-separated combinations and removes any
# excluded categories. Returns None if the result is empty so the row
# can be dropped cleanly downstream.
# ---------------------------------------------------------------------------

def clean_linddun(combination, exclude):
    if pd.isna(combination):
        return None
    cats = [c.strip() for c in str(combination).split(',')]
    cats = [c for c in cats if c not in exclude]
    return ', '.join(cats) if cats else None


# ---------------------------------------------------------------------------
# SCENARIO CONSTRUCTION
#
# All incidents are included regardless of AssetTech or AssetContext
# classification status. Unknown is treated as a valid category value.
#
# Steps:
#   1. Record total N before any filtering (likelihood denominator).
#   2. Clean and filter LINDDUN categories.
#   3. Compute severity and drop zero-severity incidents.
#   4. Group by (DataCategory, LINDDUN, AssetTech) and aggregate.
#   5. Compute likelihood and baseline risk.
#   6. Apply MIN_COUNT filter and sort by baseline risk descending.
# ---------------------------------------------------------------------------

def build_scenarios(df):
    total_incidents = df['Incident ID'].nunique()
    print(f"Total unique incidents (N, likelihood denominator): {total_incidents}")

    # Step 2
    df['LINDDUN categories'] = df['LINDDUN categories'].apply(
        lambda x: clean_linddun(x, LINDDUN_EXCLUDE)
    )
    df = df[df['LINDDUN categories'].notna()].copy()
    print(f"After LINDDUN filter:  {df['Incident ID'].nunique()} incidents")

    # Step 3
    df['severity'] = df.apply(get_severity, axis=1)
    df = df[df['severity'] > 0].copy()
    print(f"After severity filter: {df['Incident ID'].nunique()} incidents")

    # Step 4
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

    # Step 5
    scenarios['likelihood']    = scenarios['count'] / total_incidents
    scenarios['baseline_risk'] = scenarios['likelihood'] * scenarios['avg_severity']

    # Step 6
    scenarios = scenarios[scenarios['count'] >= MIN_COUNT]
    scenarios = scenarios.sort_values('baseline_risk', ascending=False).reset_index(drop=True)
    scenarios.index += 1  # scenario_rank starts at 1
    scenarios.index.name = 'scenario_rank'
    scenarios = scenarios.reset_index()

    return scenarios, df, total_incidents


# ---------------------------------------------------------------------------
# ASSETCONTEXT DISTRIBUTION
#
# For every scenario, computes the distribution of AssetContext values
# across the matching incidents. Returned in long format with count and
# percentage columns.
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

        # Replace NaN with explicit label before counting
        ctx_counts = (
            incidents['AssetContext']
            .fillna('Not reported')
            .value_counts()
        )

        for ctx, cnt in ctx_counts.items():
            rows.append({
                'scenario_rank':          int(scen['scenario_rank']),
                'baseline_risk':          round(scen['baseline_risk'], 4),
                'LINDDUN categories':     scen['LINDDUN categories'],
                'AssetTech':              scen['AssetTech'],
                'AssetContext':           ctx,
                'count':                  cnt,
                'pct':                    round(cnt / n * 100, 1),
            })

    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# DATA PROTECTION STATE DISTRIBUTION
#
# For every scenario, computes the distribution of Data Protection State
# values across the matching incidents. Returned in long format.
# ---------------------------------------------------------------------------

def analyze_dps(df_filtered, scenarios):
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

        dps_counts = (
            incidents['Data Protection State']
            .fillna('Not reported')
            .value_counts()
        )

        for state, cnt in dps_counts.items():
            rows.append({
                'scenario_rank':          int(scen['scenario_rank']),
                'baseline_risk':          round(scen['baseline_risk'], 4),
                'LINDDUN categories':     scen['LINDDUN categories'],
                'AssetTech':              scen['AssetTech'],
                'Data Protection State':  state,
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
    dps_dist = analyze_dps(df_clean, scenarios)

    print(f"\n--- AssetContext Distribution (Top 3) ---")
    print(ctx_dist[ctx_dist['scenario_rank'] <= 3].to_string(index=False))

    print(f"\n--- Data Protection State Distribution (Top 3) ---")
    print(dps_dist[dps_dist['scenario_rank'] <= 3].to_string(index=False))

    with pd.ExcelWriter(OUTPUT_FILE, engine='openpyxl') as writer:
        scenarios.to_excel(writer,  sheet_name='scenarios',         index=False)
        ctx_dist.to_excel(writer,   sheet_name='scenarios_context', index=False)
        dps_dist.to_excel(writer,   sheet_name='scenarios_dps',     index=False)

    print(f"\nSaved → {OUTPUT_FILE}")
    print("  Sheets: scenarios | scenarios_context | scenarios_dps")