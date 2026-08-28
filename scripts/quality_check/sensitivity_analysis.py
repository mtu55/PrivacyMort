"""
Sensitivity Analysis: Scenario Threshold and Severity Scale
============================================================
Evaluates stability of scenario rankings across different
minimum incident thresholds and severity weightings.

Baseline severity has three empirical levels (1,4,6). Severity 0 is
defined but empty after cleaning. Alternative vectors are three-element
robustness perturbations, not competing severity definitions.

Primary severity analysis: all observed scenarios (count >= 1).

Input:  results/mort_scenarios_final.xlsx
Output: results/sensitivity_analysis.xlsx
        results/severity_sens_table.tex
"""

from pathlib import Path

import pandas as pd
from scipy.stats import spearmanr


# === CONFIGURATION ===
ROOT_DIR = Path(__file__).resolve().parent.parent.parent

INPUT_FILE = ROOT_DIR / "results" / "mort_scenarios_final.xlsx"
OUTPUT_FILE = ROOT_DIR / "results" / "sensitivity_analysis.xlsx"
TEX_FILE = ROOT_DIR / "results" / "severity_sens_table.tex"

THRESHOLDS = [3, 5, 10, 15]
REFERENCE_THRESHOLD = 5
OBSERVED_MIN_COUNT = 1
SEVERITY_MIN_COUNT = 1
TOP_K = 5

SCENARIO_COLS = [
    "has_personal_data",
    "has_special_categories",
    "has_credentials",
    "LINDDUN categories",
    "AssetTech",
]

# avg_severity holds the empirical severity values (1,4,6).
BASELINE_SCALE = {1: 1, 4: 4, 6: 6}

ALT_SCALES = {
    "linear": {1: 1, 4: 3, 6: 5},
    "convex": {1: 1, 4: 4, 6: 16},
    "concave": {1: 1, 4: 5, 6: 6},
    "flat": {1: 2, 4: 3, 6: 4},
}


def apply_severity(df, mapping):
    """Calculate scenario risk under a given severity mapping."""
    mapped_severity = df["avg_severity"].round().map(mapping)

    if mapped_severity.isna().any():
        unexpected = sorted(
            df.loc[mapped_severity.isna(), "avg_severity"].dropna().unique()
        )
        raise ValueError(
            f"Severity mapping failed for unexpected values: {unexpected}"
        )

    return df["likelihood"] * mapped_severity


def scenario_keys(df):
    """Return stable scenario identifiers for overlap comparisons."""
    key_frame = df[SCENARIO_COLS].astype(object).fillna("<missing>")
    return list(key_frame.itertuples(index=False, name=None))


def get_top_k(df):
    """Return the top-k scenarios by recalculated baseline risk."""
    return df.nlargest(TOP_K, "risk_baseline").copy()


def write_latex_table(sev_corr, path, n_scenarios, min_count):
    """Write the primary severity-sensitivity table as LaTeX."""
    caption = (
        "Rank agreement of scenario risks under alternative severity "
        "weightings relative to the baseline weighting $(1,4,6)$ across "
        f"$N = {n_scenarios}$ scenarios retained under "
        f"$n \\ge {min_count}$."
    )

    labels = {
        "linear": "Linear",
        "convex": "Convex",
        "concave": "Concave",
        "flat": "Flat",
    }

    lines = [
        r"\begin{table}[t]",
        r"  \centering",
        f"  \\caption{{{caption}}}",
        r"  \label{tab:severity_sens}",
        r"  \begin{tabular}{llS[table-format=1.3]}",
        r"    \toprule",
        r"    Weighting & Vector & {$\rho$} \\",
        r"    \midrule",
    ]

    for row in sev_corr:
        name = row["scale"]
        vector = ALT_SCALES[name]
        vector_latex = rf"$({vector[1]},{vector[4]},{vector[6]})$"

        lines.append(
            f"    {labels[name]} & {vector_latex} & "
            f"{row['spearman_rho']:.3f} \\\\"
        )

    lines += [
        r"    \bottomrule",
        r"  \end{tabular}",
        r"\end{table}",
    ]

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    print(f"Loading: {INPUT_FILE}\n")
    df = pd.read_excel(INPUT_FILE)

    required_columns = set(
        SCENARIO_COLS + ["count", "likelihood", "avg_severity"]
    )
    missing_columns = required_columns - set(df.columns)

    if missing_columns:
        raise ValueError(
            f"Input file is missing required columns: {sorted(missing_columns)}"
        )

    # Retain all empirically observed scenarios.
    observed_df = df[df["count"] >= OBSERVED_MIN_COUNT].copy()

    if observed_df.empty:
        raise ValueError("No observed scenarios found.")

    assert not observed_df.duplicated(SCENARIO_COLS).any(), (
        "Duplicate scenario rows found. Each scenario must occur exactly once."
    )

    assert observed_df["avg_severity"].notna().all(), (
        "Missing avg_severity values found in observed scenarios."
    )

    levels = sorted(
        {round(x) for x in observed_df["avg_severity"].dropna()}
    )

    assert set(levels) <= set(BASELINE_SCALE), (
        f"Unexpected severity levels {levels}; expected only (1,4,6)."
    )

    # Recalculate baseline risk consistently for all analyses.
    observed_df["risk_baseline"] = apply_severity(
        observed_df,
        BASELINE_SCALE,
    )

    total_incidents = int(observed_df["count"].sum())

    print(f"Observed scenarios: {len(observed_df)}")
    print(f"Incidents represented: {total_incidents}\n")

    # -------------------------------------------------------
    # PART 1: Threshold Sensitivity
    # -------------------------------------------------------
    print("=== Part 1: Threshold Sensitivity ===\n")

    if REFERENCE_THRESHOLD not in THRESHOLDS:
        raise ValueError(
            "REFERENCE_THRESHOLD must be included in THRESHOLDS."
        )

    threshold_frames = {}
    threshold_counts = []
    threshold_top_rows = []

    for threshold in THRESHOLDS:
        filtered = observed_df[
            observed_df["count"] >= threshold
            ].copy()

        threshold_frames[threshold] = filtered

        retained_incidents = int(filtered["count"].sum())
        retained_share = (
            100 * retained_incidents / total_incidents
            if total_incidents > 0
            else 0
        )

        threshold_counts.append(
            {
                "threshold": threshold,
                "n_scenarios": len(filtered),
                "n_incidents": retained_incidents,
                "incident_share_pct": round(retained_share, 2),
            }
        )

        top = get_top_k(filtered)

        top_export = top[
            SCENARIO_COLS + ["count", "risk_baseline"]
            ].copy()

        top_export = top_export.rename(
            columns={"risk_baseline": "baseline_risk"}
        )

        top_export.insert(0, "rank", range(1, len(top_export) + 1))
        top_export.insert(0, "threshold", threshold)

        threshold_top_rows.append(top_export)

        print(f"--- Top-{TOP_K} at n>={threshold} ---")
        print(top_export.to_string(index=False))
        print()

    # Threshold filtering does not alter risk values among scenarios that
    # remain in both samples. Therefore, Spearman rho on their intersection
    # would be tautologically 1.000. We report top-k overlap instead.
    reference_df = threshold_frames[REFERENCE_THRESHOLD]

    if reference_df.empty:
        raise ValueError(
            f"No scenarios remain at n>={REFERENCE_THRESHOLD}."
        )

    reference_scenarios = set(scenario_keys(reference_df))
    reference_top_keys = scenario_keys(get_top_k(reference_df))

    threshold_stability = []

    print(
        f"--- Top-{TOP_K} stability relative to "
        f"n>={REFERENCE_THRESHOLD} ---"
    )

    for threshold in THRESHOLDS:
        filtered = threshold_frames[threshold]

        current_scenarios = set(scenario_keys(filtered))
        current_top_keys = scenario_keys(get_top_k(filtered))

        top_overlap = len(
            set(reference_top_keys).intersection(current_top_keys)
        )

        top_overlap_pct = (
            100 * top_overlap / len(reference_top_keys)
            if reference_top_keys
            else 0
        )

        same_order = current_top_keys == reference_top_keys

        threshold_stability.append(
            {
                "comparison": (
                    f"n>={threshold} vs n>={REFERENCE_THRESHOLD}"
                ),
                "n_scenarios": len(filtered),
                "shared_scenarios": len(
                    reference_scenarios.intersection(current_scenarios)
                ),
                "top_k_overlap": top_overlap,
                "top_k_overlap_pct": round(top_overlap_pct, 2),
                "same_top_k_order": same_order,
            }
        )

        print(
            f"n>={threshold} vs n>={REFERENCE_THRESHOLD}: "
            f"top-{TOP_K} overlap = {top_overlap}/"
            f"{len(reference_top_keys)}, "
            f"same order = {same_order}"
        )

    # -------------------------------------------------------
    # PART 2: Severity Scale Sensitivity
    # -------------------------------------------------------
    print("\n=== Part 2: Severity Scale Sensitivity ===\n")

    # Primary analysis: all observed scenarios, i.e., count >= 1.
    base_df = observed_df[
        observed_df["count"] >= SEVERITY_MIN_COUNT
        ].copy()

    if base_df.empty:
        raise ValueError(
            f"No scenarios remain at n>={SEVERITY_MIN_COUNT}."
        )

    base_df["risk_baseline"] = apply_severity(
        base_df,
        BASELINE_SCALE,
    )

    print(
        f"Severity analysis sample: {len(base_df)} scenarios "
        f"(n>={SEVERITY_MIN_COUNT})\n"
    )

    scale_corr = []

    for scale_name, mapping in ALT_SCALES.items():
        base_df[f"risk_{scale_name}"] = apply_severity(
            base_df,
            mapping,
        )

        rho, _ = spearmanr(
            base_df["risk_baseline"],
            base_df[f"risk_{scale_name}"],
        )

        if pd.isna(rho):
            raise ValueError(
                f"Spearman correlation could not be calculated for "
                f"{scale_name}."
            )

        vector = mapping

        print(
            f"{scale_name} "
            f"({vector[1]},{vector[4]},{vector[6]}) "
            f"vs baseline (1,4,6): rho = {rho:.4f}"
        )

        scale_corr.append(
            {
                "scale": scale_name,
                "vector": f"({vector[1]},{vector[4]},{vector[6]})",
                "n_scenarios": len(base_df),
                "spearman_rho": round(float(rho), 4),
            }
        )

    lowest = min(scale_corr, key=lambda row: row["spearman_rho"])
    highest = max(scale_corr, key=lambda row: row["spearman_rho"])

    print(
        f"\nrho range: {lowest['spearman_rho']:.3f} "
        f"({lowest['scale']}) to "
        f"{highest['spearman_rho']:.3f} "
        f"({highest['scale']})"
    )

    # -------------------------------------------------------
    # SAVE RESULTS
    # -------------------------------------------------------
    with pd.ExcelWriter(OUTPUT_FILE) as writer:
        pd.DataFrame(threshold_counts).to_excel(
            writer,
            sheet_name="threshold_counts",
            index=False,
        )

        pd.DataFrame(threshold_stability).to_excel(
            writer,
            sheet_name="threshold_stability",
            index=False,
        )

        pd.concat(
            threshold_top_rows,
            ignore_index=True,
        ).to_excel(
            writer,
            sheet_name="top5_by_threshold",
            index=False,
        )

        pd.DataFrame(scale_corr).to_excel(
            writer,
            sheet_name="scale_correlation",
            index=False,
        )

    write_latex_table(
        scale_corr,
        TEX_FILE,
        n_scenarios=len(base_df),
        min_count=SEVERITY_MIN_COUNT,
    )

    print(f"\nSaved to: {OUTPUT_FILE}")
    print(
        f"LaTeX:   {TEX_FILE} "
        f"(severity analysis: n>={SEVERITY_MIN_COUNT})"
    )