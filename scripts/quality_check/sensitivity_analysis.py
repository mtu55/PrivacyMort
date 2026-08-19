"""
Sensitivity Analysis: Scenario Threshold and Severity Scale
=============================================================
Evaluates stability of scenario rankings across different
minimum incident thresholds and severity weightings.

Baseline severity has THREE empirical levels {1,4,6}. Severity 0 is
defined but empty after cleaning (N=2037 -> N=2035). Alternative vectors
are 3-element robustness perturbations, NOT competing definitions.

Input:  results/mort_scenarios_final.xlsx
Output: results/sensitivity_analysis.xlsx
        results/severity_sens_table.tex   (ready to include as LaTeX)
"""

import pandas as pd
from scipy.stats import spearmanr
from pathlib import Path

# === CONFIGURATION ===
INPUT_FILE  = Path(__file__).parent.parent.parent / "results" / "mort_scenarios_final.xlsx"
OUTPUT_FILE = Path(__file__).parent.parent.parent / "results" / "sensitivity_analysis.xlsx"
TEX_FILE    = Path(__file__).parent.parent.parent / "results" / "severity_sens_table.tex"

THRESHOLDS = [3, 5, 10, 15]
SCENARIO_COLS = [
    'has_personal_data', 'has_special_categories',
    'has_credentials', 'LINDDUN categories', 'AssetTech'
]

# === SEVERITY SCALES ===
# avg_severity already holds the severity VALUES {1,4,6}.
# Baseline is the identity; alternatives remap the three levels.
BASELINE_SCALE = {1: 1, 4: 4, 6: 6}
ALT_SCALES = {
    'linear':  {1: 1, 4: 3, 6: 5},    # {1,3,5}
    'convex':  {1: 1, 4: 4, 6: 16},   # {1,4,16}
    'concave': {1: 1, 4: 5, 6: 6},    # {1,5,6}
    'flat':    {1: 2, 4: 3, 6: 4},    # {2,3,4}
}


def apply_severity(df, mapping):
    """Map rounded avg_severity through a scale; fall back to raw value."""
    return df['likelihood'] * df['avg_severity'].map(
        lambda x: mapping.get(round(x), x)
    )


def write_latex_table(sev_corr, path):
    lines = [
        r"\begin{table}[t]",
        r"  \centering",
        r"  \caption{Severity-weighting sensitivity. Spearman rank "
        r"correlation between the baseline severity $\{1,4,6\}$ and four "
        r"three-element perturbations.}",
        r"  \label{tab:severity_sens}",
        r"  \begin{tabular}{llS[table-format=1.3]}",
        r"    \toprule",
        r"    Weighting & Vector & {$\rho$} \\",
        r"    \midrule",
    ]
    label = {'linear': 'Linear', 'convex': 'Convex',
             'concave': 'Concave', 'flat': 'Flat'}
    for row in sev_corr:
        name = row['scale']
        v = ALT_SCALES[name]
        vec = rf"$\{{{v[1]},{v[4]},{v[6]}\}}$"
        lines.append(f"    {label[name]} & {vec} & {row['spearman_rho']:.3f} \\\\")
    lines += [r"    \bottomrule", r"  \end{tabular}", r"\end{table}"]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    print(f"Loading: {INPUT_FILE}\n")
    df = pd.read_excel(INPUT_FILE)

    # Safety: after cleaning only the three-level scale {1,4,6} may remain
    levels = sorted({round(x) for x in df['avg_severity'].dropna()})
    assert set(levels) <= {1, 4, 6}, (
        f"Unexpected severity levels {levels}; expected the cleaned "
        f"three-level scale {{1,4,6}} (N=2035)."
    )

    # -------------------------------------------------------
    # PART 1: Threshold Sensitivity
    # -------------------------------------------------------
    print("=== Part 1: Threshold Sensitivity ===\n")

    print("--- Valid scenarios per threshold ---")
    threshold_counts = []
    for n in THRESHOLDS:
        count = len(df[df['count'] >= n])
        print(f"n>={n}: {count} scenarios")
        threshold_counts.append({'threshold': n, 'n_scenarios': count})
    print()

    for n in THRESHOLDS:
        filtered = df[df['count'] >= n]
        top5 = filtered.nlargest(5, 'baseline_risk')[
            SCENARIO_COLS + ['count', 'baseline_risk']
            ].reset_index(drop=True)
        top5.index += 1
        print(f"--- Top-5 at n>={n} ---")
        print(top5.to_string())
        print()

    print("--- Spearman correlation vs n>=5 baseline ---")
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
            on=SCENARIO_COLS, suffixes=('_base', f'_n{n}')
        )
        corr, p = spearmanr(merged['baseline_risk_base'], merged[f'baseline_risk_n{n}'])
        print(f"n>={n} vs n>=5: rho = {corr:.4f}, p = {p:.4f}")
        threshold_corr.append({'comparison': f'n>={n} vs n>=5',
                               'spearman_rho': round(corr, 4),
                               'p_value': round(p, 4)})

    # -------------------------------------------------------
    # PART 2: Severity Scale Sensitivity  (baseline {1,4,6})
    # -------------------------------------------------------
    print("\n=== Part 2: Severity Scale Sensitivity ===\n")

    base_df = df[df['count'] >= 5].copy()
    base_df['risk_baseline'] = apply_severity(base_df, BASELINE_SCALE)

    scale_corr = []
    for scale_name, mapping in ALT_SCALES.items():
        base_df[f'risk_{scale_name}'] = apply_severity(base_df, mapping)
        corr, p = spearmanr(base_df['risk_baseline'], base_df[f'risk_{scale_name}'])
        v = mapping
        print(f"{scale_name} {{{v[1]},{v[4]},{v[6]}}} vs baseline {{1,4,6}}: "
              f"rho = {corr:.4f}, p = {p:.4f}")
        scale_corr.append({'scale': scale_name,
                           'vector': f'{{{v[1]},{v[4]},{v[6]}}}',
                           'spearman_rho': round(corr, 4),
                           'p_value': round(p, 4)})

    lo = min(scale_corr, key=lambda r: r['spearman_rho'])
    hi = max(scale_corr, key=lambda r: r['spearman_rho'])
    print(f"\nrho range: {lo['spearman_rho']:.3f} ({lo['scale']}) to "
          f"{hi['spearman_rho']:.3f} ({hi['scale']})")

    # -------------------------------------------------------
    # SAVE
    # -------------------------------------------------------
    with pd.ExcelWriter(OUTPUT_FILE) as writer:
        pd.DataFrame(threshold_counts).to_excel(
            writer, sheet_name='threshold_counts', index=False)
        pd.DataFrame(threshold_corr).to_excel(
            writer, sheet_name='threshold_correlation', index=False)
        pd.DataFrame(scale_corr).to_excel(
            writer, sheet_name='scale_correlation', index=False)

    write_latex_table(scale_corr, TEX_FILE)

    print(f"\nSaved to: {OUTPUT_FILE}")
    print(f"LaTeX:   {TEX_FILE}  (include as tab:severity_sens)")