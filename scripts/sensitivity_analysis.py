"""
Sensitivity Analysis: Scenario Threshold and Severity Scale
=============================================================
Evaluates stability of scenario rankings across different
minimum incident thresholds and severity weightings.

Input:  results/mort_scenarios.xlsx
Output: results/sensitivity_analysis.xlsx
"""

import pandas as pd
from scipy.stats import spearmanr
from pathlib import Path

# === CONFIGURATION ===
INPUT_FILE  = Path(__file__).parent.parent / "results" / "mort_scenarios.xlsx"
OUTPUT_FILE = Path(__file__).parent.parent / "results" / "sensitivity_analysis.xlsx"

THRESHOLDS = [3, 5, 10, 15]
SCENARIO_COLS = [
    'has_personal_data', 'has_special_categories',
    'has_credentials', 'LINDDUN categories', 'Asset Type'
]

# === SEVERITY SCALES ===
SEVERITY_SCALES = {
    'current':     {0: 0, 1: 1, 2: 2, 3: 3, 4: 4},
    'exponential': {0: 0, 1: 1, 2: 2, 3: 4, 4: 8},
    'compressed':  {0: 0, 1: 1, 2: 1.5, 3: 2, 4: 3},
    'flat':        {0: 0, 1: 1, 2: 1.2, 3: 1.5, 4: 2},
    'linear_high': {0: 0, 1: 2, 2: 3, 3: 4, 4: 5},
}


if __name__ == "__main__":
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    print(f"Loading: {INPUT_FILE}\n")
    df = pd.read_excel(INPUT_FILE)

    # -------------------------------------------------------
    # PART 1: Threshold Sensitivity
    # -------------------------------------------------------
    print("=== Part 1: Threshold Sensitivity ===\n")

    print("--- Valid scenarios per threshold ---")
    threshold_counts = []
    for n in THRESHOLDS:
        count = len(df[df['count'] >= n])
        print(f"n≥{n}: {count} scenarios")
        threshold_counts.append({'threshold': n, 'n_scenarios': count})

    print()

    # Top-5 per threshold
    for n in THRESHOLDS:
        filtered = df[df['count'] >= n]
        top5 = filtered.nlargest(5, 'baseline_risk')[
            SCENARIO_COLS + ['count', 'baseline_risk']
        ].reset_index(drop=True)
        top5.index += 1
        print(f"--- Top-5 at n≥{n} ---")
        print(top5.to_string())
        print()

    # Spearman correlation vs n≥5 baseline
    print("--- Spearman correlation vs n≥5 baseline ---")
    baseline = df[df['count'] >= 5].sort_values(
        'baseline_risk', ascending=False
    ).reset_index(drop=True)

    threshold_corr = []
    for n in [3, 10, 15]:
        filtered = df[df['count'] >= n].sort_values(
            'baseline_risk', ascending=False
        ).reset_index(drop=True)
        merged = baseline.merge(
            filtered[SCENARIO_COLS + ['baseline_risk']],
            on=SCENARIO_COLS,
            suffixes=('_base', f'_n{n}')
        )
        corr, p = spearmanr(merged['baseline_risk_base'], merged[f'baseline_risk_n{n}'])
        print(f"n≥{n} vs n≥5: ρ = {corr:.4f}, p = {p:.4f}")
        threshold_corr.append({'comparison': f'n≥{n} vs n≥5', 'spearman_rho': round(corr, 4), 'p_value': round(p, 4)})

    # -------------------------------------------------------
    # PART 2: Severity Scale Sensitivity
    # -------------------------------------------------------
    print("\n=== Part 2: Severity Scale Sensitivity ===\n")

    base_df = df[df['count'] >= 5].copy()
    base_df['risk_current'] = base_df['likelihood'] * base_df['avg_severity'].map(
        lambda x: SEVERITY_SCALES['current'].get(round(x), x)
    )

    scale_corr = []
    for scale_name, mapping in SEVERITY_SCALES.items():
        if scale_name == 'current':
            continue
        base_df[f'risk_{scale_name}'] = base_df['likelihood'] * base_df['avg_severity'].map(
            lambda x: mapping.get(round(x), x)
        )
        corr, p = spearmanr(base_df['risk_current'], base_df[f'risk_{scale_name}'])
        print(f"{scale_name} vs current: ρ = {corr:.4f}, p = {p:.4f}")
        scale_corr.append({
            'comparison': f'{scale_name} vs current',
            'spearman_rho': round(corr, 4),
            'p_value': round(p, 4)
        })

    # -------------------------------------------------------
    # SAVE
    # -------------------------------------------------------
    with pd.ExcelWriter(OUTPUT_FILE) as writer:
        pd.DataFrame(threshold_counts).to_excel(
            writer, sheet_name='threshold_counts', index=False
        )
        pd.DataFrame(threshold_corr).to_excel(
            writer, sheet_name='threshold_correlation', index=False
        )
        pd.DataFrame(scale_corr).to_excel(
            writer, sheet_name='scale_correlation', index=False
        )

    print(f"\nSaved to: {OUTPUT_FILE}")