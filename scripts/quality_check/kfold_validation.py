# scripts/kfold_validation.py
# k-fold Cross-Validation (Variante A: Ranking-Stabilität) für PrivacyMort
#
# Testet die Robustheit des Szenario-Rankings gegenüber Stichprobenvariation.
# Verwendet EXAKT dieselbe Szenario-/Severity-Logik wie scenarios.py
# (importiert die Funktionen, um Divergenz zu vermeiden).

import numpy as np
import pandas as pd
from pathlib import Path
from scipy.stats import spearmanr

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))  # scripts/ zum Suchpfad hinzufügen

# Logik aus scenarios.py wiederverwenden (identische Severity/LINDDUN-Regeln)
from scenarios_final import get_severity, clean_linddun, LINDDUN_EXCLUDE, MIN_COUNT

INPUT_FILE  = Path(__file__).parent.parent.parent / "data" / "processed" / "privacyrisq_assets_final.xlsx"
OUTPUT_FILE = Path(__file__).parent.parent.parent / "results" / "kfold_validation_results.xlsx"

K           = 5
RANDOM_SEED = 42

SCENARIO_COLS = [
    'has_personal_data',
    'has_special_categories',
    'has_credentials',
    'LINDDUN categories',
    'AssetTech',
]


def scenario_key(row):
    """Eindeutiger Szenario-Schlüssel für Ranking-Vergleiche."""
    return tuple(row[c] for c in SCENARIO_COLS)


def build_ranking(df):
    """
    Baut das Szenario-Ranking nach exakt derselben Logik wie scenarios.py.
    Erwartet ein df, bei dem LINDDUN bereits bereinigt und severity gesetzt ist.
    Gibt DataFrame mit scenario_key, baseline_risk, rank zurück.
    """
    total_incidents = df['Incident ID'].nunique()

    scenarios = df.groupby(SCENARIO_COLS).agg(
        count        = ('Incident ID', 'nunique'),
        avg_severity = ('severity', 'mean'),
    ).reset_index()

    scenarios['likelihood']    = scenarios['count'] / total_incidents
    scenarios['baseline_risk'] = scenarios['likelihood'] * scenarios['avg_severity']
    scenarios = scenarios[scenarios['count'] >= MIN_COUNT]

    scenarios = scenarios.sort_values('baseline_risk', ascending=False).reset_index(drop=True)
    scenarios['rank'] = scenarios.index + 1
    scenarios['scenario_key'] = scenarios.apply(scenario_key, axis=1)

    return scenarios[['scenario_key', 'count', 'baseline_risk', 'rank']]


def prepare(df):
    """LINDDUN-Filter + Severity-Filter (wie in scenarios.py.build_scenarios)."""
    df = df.copy()
    df['LINDDUN categories'] = df['LINDDUN categories'].apply(
        lambda x: clean_linddun(x, LINDDUN_EXCLUDE)
    )
    df = df[df['LINDDUN categories'].notna()].copy()
    df['severity'] = df.apply(get_severity, axis=1)
    df = df[df['severity'] > 0].copy()
    return df


if __name__ == "__main__":
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    print(f"Loading: {INPUT_FILE}")
    df_raw = pd.read_excel(INPUT_FILE)
    print(f"Rohzeilen: {len(df_raw)}")

    df = prepare(df_raw)
    N = df['Incident ID'].nunique()
    print(f"N_effektiv (nach LINDDUN- + Severity-Filter, unique Incident ID): {N}")

    # --- Baseline-Ranking auf Gesamtkorpus ---
    baseline = build_ranking(df)
    baseline_ranks = baseline.set_index('scenario_key')['rank']
    print(f"Szenarien gesamt: {len(baseline)}")

    # --- k-fold auf Incident-Ebene (nicht Zeilen-Ebene) ---
    unique_ids = df['Incident ID'].unique()
    rng = np.random.default_rng(RANDOM_SEED)
    shuffled = rng.permutation(unique_ids)
    folds = np.array_split(shuffled, K)

    results = []
    for i in range(K):
        test_ids  = set(folds[i])
        train_ids = set(np.concatenate([folds[j] for j in range(K) if j != i]))
        train_df  = df[df['Incident ID'].isin(train_ids)]

        fold_ranking = build_ranking(train_df)
        fold_ranks   = fold_ranking.set_index('scenario_key')['rank']

        common = baseline_ranks.index.intersection(fold_ranks.index)
        rho, p = spearmanr(baseline_ranks.loc[common], fold_ranks.loc[common])

        results.append({
            'fold':             i + 1,
            'train_incidents':  train_df['Incident ID'].nunique(),
            'fold_scenarios':   len(fold_ranking),
            'common_scenarios': len(common),
            'spearman_rho':     round(rho, 4),
            'p_value':          round(p, 8),
        })
        print(f"Fold {i+1}: train={train_df['Incident ID'].nunique()}, "
              f"common={len(common)}, rho={rho:.4f}")

    res_df = pd.DataFrame(results)

    summary = pd.DataFrame([{
        'k':               K,
        'random_seed':     RANDOM_SEED,
        'N_effektiv':      N,
        'total_scenarios': len(baseline),
        'mean_rho':        round(res_df['spearman_rho'].mean(), 4),
        'std_rho':         round(res_df['spearman_rho'].std(ddof=1), 4),
        'min_rho':         round(res_df['spearman_rho'].min(), 4),
        'max_rho':         round(res_df['spearman_rho'].max(), 4),
    }])

    print("\n=== Zusammenfassung ===")
    print(summary.to_string(index=False))

    baseline_out = baseline.copy()
    baseline_out['scenario_key'] = baseline_out['scenario_key'].astype(str)

    with pd.ExcelWriter(OUTPUT_FILE, engine='openpyxl') as writer:
        summary.to_excel(writer,      sheet_name='summary',          index=False)
        res_df.to_excel(writer,       sheet_name='per_fold',         index=False)
        baseline_out.to_excel(writer, sheet_name='baseline_ranking', index=False)

    print(f"\nSaved → {OUTPUT_FILE}")