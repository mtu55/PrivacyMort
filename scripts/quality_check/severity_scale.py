# scripts/severity_sensitivity_check.py
# Standalone-Diagnose: Beeinflusst die Severity-Skala das BaselineRisk-Ranking?
#
# Beantwortet zwei Fragen:
#   1) DIAGNOSE:     Liegen die Top-Szenarien in einer oder mehreren
#                    Severity-Klassen? (-> ist die Skala ueberhaupt relevant?)
#   2) SENSITIVITAET: Wie stabil ist das Ranking ueber alternative Skalen?
#
# Nutzt EXAKT dieselbe Szenario-Definition wie scenarios.py.

import pandas as pd
from pathlib import Path
from scipy.stats import spearmanr, kendalltau

# ---------------------------------------------------------------------------
# CONFIGURATION  (identisch zu scenarios.py)
# ---------------------------------------------------------------------------
INPUT_FILE = Path(__file__).parent.parent.parent / "data" / "processed" / "archive" / "privacyrisq_assetsv8.xlsx"
OUTPUT_FILE = Path(__file__).parent.parent.parent / "results" / "archive" / "severity_sensitivity_v8.xlsx"

LINDDUN_EXCLUDE = []
MIN_COUNT       = 1
TOP_K           = 5

SCENARIO_COLS = [
    'has_personal_data',
    'has_special_categories',
    'has_credentials',
    'LINDDUN categories',
    'AssetTech',
]

# Anzahl betroffener Kategorien -> Severity.
# S0 repliziert exakt deine get_severity()-Logik (alle 2er-Kombis = 4).
SEVERITY_SCALES = {
    "S0_baseline":    {0: 0, 1: 1, 2: 4, 3: 6},
    "S1_linear":      {0: 0, 1: 1, 2: 2, 3: 3},
    "S2_quadratic":   {0: 0, 1: 1, 2: 4, 3: 9},
    "S3_exponential": {0: 0, 1: 1, 2: 2, 3: 4},
    "S4_steep":       {0: 0, 1: 1, 2: 3, 3: 9},
    "S5_flat":        {0: 0, 1: 1, 2: 1.5, 3: 2},
}


# ---------------------------------------------------------------------------
# LINDDUN CLEANING  (aus scenarios.py uebernommen)
# ---------------------------------------------------------------------------
def clean_linddun(combination, exclude):
    if pd.isna(combination):
        return None
    cats = [c.strip() for c in str(combination).split(',')]
    cats = [c for c in cats if c not in exclude]
    return ', '.join(cats) if cats else None


# ---------------------------------------------------------------------------
# SCENARIO CONSTRUCTION  (parametrisiert nach Severity-Skala)
# ---------------------------------------------------------------------------
def build_scenarios(df, scale):
    total_incidents = df['Incident ID'].nunique()

    df = df.copy()
    df['LINDDUN categories'] = df['LINDDUN categories'].apply(
        lambda x: clean_linddun(x, LINDDUN_EXCLUDE)
    )
    df = df[df['LINDDUN categories'].notna()].copy()

    n_cat = (
            (df['has_personal_data']      == 1).astype(int)
            + (df['has_special_categories'] == 1).astype(int)
            + (df['has_credentials']        == 1).astype(int)
    )
    df['n_categories'] = n_cat
    df['severity'] = n_cat.map(scale)
    df = df[df['severity'] > 0].copy()

    scen = df.groupby(SCENARIO_COLS).agg(
        count        = ('Incident ID', 'nunique'),
        avg_severity = ('severity', 'mean'),
        n_categories = ('n_categories', 'mean'),
    ).reset_index()

    scen['likelihood']    = scen['count'] / total_incidents
    scen['baseline_risk'] = scen['likelihood'] * scen['avg_severity']
    scen = scen[scen['count'] >= MIN_COUNT].copy()

    # Stabiler Szenario-Schluessel fuer den Vergleich ueber Skalen
    scen['scenario_id'] = scen[SCENARIO_COLS].astype(str).agg(' | '.join, axis=1)
    return scen.set_index('scenario_id')


# ---------------------------------------------------------------------------
# 1) DIAGNOSE
# ---------------------------------------------------------------------------
def diagnose(base):
    print("=" * 74)
    print("DIAGNOSE: Severity-Klassen der Top-Szenarien (S0_baseline)")
    print("=" * 74)

    top = base.sort_values('baseline_risk', ascending=False).head(TOP_K)
    show = top[['n_categories', 'avg_severity', 'likelihood', 'baseline_risk',
                'LINDDUN categories', 'AssetTech']].round(4)
    print(f"\nTop-{TOP_K} Szenarien nach BaselineRisk:\n")
    print(show.to_string())

    n_classes = top['n_categories'].nunique()
    print("\n" + "-" * 74)
    if n_classes == 1:
        cls = int(top['n_categories'].iloc[0])
        print(f">>> FALL 1: Alle Top-{TOP_K} in DERSELBEN Severity-Klasse "
              f"({cls} Kategorien).")
        print(">>> 'Skala egal' ist plausibel -> Likelihood dominiert das Ranking.")
        print(">>> Die Sensitivitaet unten liefert den empirischen Beleg dafuer.")
    else:
        print(f">>> FALL 2: Top-{TOP_K} MISCHEN {n_classes} Severity-Klassen "
              f"(Kategorien: {sorted(int(x) for x in top['n_categories'].unique())}).")
        print(">>> Skala KANN das Ranking drehen -> Sensitivitaet ist essenziell.")
    print("-" * 74 + "\n")


# ---------------------------------------------------------------------------
# 2) SENSITIVITAET
# ---------------------------------------------------------------------------
def sensitivity(df, base):
    print("=" * 74)
    print("SENSITIVITAET: Ranking-Stabilitaet vs. S0_baseline")
    print("=" * 74)

    base_rank = base['baseline_risk'].rank(ascending=False)
    base_top  = set(base['baseline_risk'].nlargest(TOP_K).index)

    rows = []
    for name, scale in SEVERITY_SCALES.items():
        if name == "S0_baseline":
            continue
        alt = build_scenarios(df, scale)
        common = base_rank.index.intersection(alt.index)
        alt_rank = alt.loc[common, 'baseline_risk'].rank(ascending=False)

        rho, _ = spearmanr(base_rank[common], alt_rank)
        tau, _ = kendalltau(base_rank[common], alt_rank)
        overlap = len(base_top & set(alt['baseline_risk'].nlargest(TOP_K).index))

        rows.append({
            'Skala':                 name,
            'Spearman_rho':          round(rho, 3),
            'Kendall_tau':           round(tau, 3),
            f'Top{TOP_K}_overlap':   f"{overlap}/{TOP_K}",
        })

    result = pd.DataFrame(rows)
    print("\n" + result.to_string(index=False) + "\n")

    min_rho = min(r['Spearman_rho'] for r in rows)
    all_top = all(r[f'Top{TOP_K}_overlap'] == f"{TOP_K}/{TOP_K}" for r in rows)

    print("-" * 74)
    print("FAZIT:")
    print(f"  Min. Spearman rho: {min_rho:.3f}")
    print(f"  Top-{TOP_K} in allen Skalen identisch: {'JA' if all_top else 'NEIN'}")
    if min_rho >= 0.9 and all_top:
        print("  => Ranking ROBUST gegenueber der Severity-Parametrisierung.")
    elif min_rho >= 0.9:
        print("  => Gesamtranking robust, Top-K variiert leicht -> im Paper zeigen.")
    else:
        print("  => Ranking sensitiv -> Severity-Wahl stark begruenden.")
    print("-" * 74)
    return result


# ---------------------------------------------------------------------------
# ENTRY POINT
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    print(f"Loading: {INPUT_FILE}\n")
    df_raw = pd.read_excel(INPUT_FILE)
    print(f"Loaded {len(df_raw)} rows\n")

    # Sanity: Fall A bestaetigen
    n_zero = (
            (df_raw['has_personal_data']      == 1).astype(int)
            + (df_raw['has_special_categories'] == 1).astype(int)
            + (df_raw['has_credentials']        == 1).astype(int)
            == 0
    ).sum()
    print(f"[Sanity] Incidents mit 0 Kategorien (severity=0): {n_zero} "
          f"(erwartet: 0)\n")

    base = build_scenarios(df_raw, SEVERITY_SCALES["S0_baseline"])
    diagnose(base)
    result = sensitivity(df_raw, base)

    with pd.ExcelWriter(OUTPUT_FILE, engine='openpyxl') as writer:
        result.to_excel(writer, sheet_name='sensitivity', index=False)
    print(f"\nSaved → {OUTPUT_FILE}")