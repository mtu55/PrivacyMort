# scripts/source_diagnostics.py
# Diagnostics for R1 (source heterogeneity) and R3 (LINDDUN axis validity)
#
# Reuses the scenario definition from scripts/scenarios.py:
#   s = (LINDDUN combination, DataCategory, AssetTech)
#
# Outputs: results/source_diagnostics.xlsx

import pandas as pd
import numpy as np
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent

def find_project_root(start: Path) -> Path:
    """Root is identified by containing data/processed, not just 'data'."""
    for candidate in [start, *start.parents]:
        if (candidate / "data" / "processed").is_dir():
            return candidate
    raise FileNotFoundError(f"No directory with data/processed found above {start}")

ROOT        = find_project_root(SCRIPT_DIR)
INPUT_FILE  = ROOT / "data" / "processed" / "privacyrisq_assets_final.xlsx"
OUTPUT_FILE = SCRIPT_DIR / "source_diagnostics.xlsx"

FLAGS = ['has_personal_data', 'has_special_categories', 'has_credentials']
SCENARIO_COLS = FLAGS + ['LINDDUN categories', 'AssetTech']


# ---------------------------------------------------------------------------
# SEVERITY (identical to scenarios.py)
# ---------------------------------------------------------------------------

def get_severity(row):
    p, s, c = (row[f] == 1 for f in FLAGS)
    if c and p and s:                        return 6
    if (c and p) or (p and s) or (c and s):  return 4
    if p or s or c:                          return 1
    return 0


def datacat_label(row):
    parts = [k for k, f in zip('PSC', FLAGS) if row[f] == 1]
    return '+'.join(parts) if parts else 'none'


# ---------------------------------------------------------------------------
# LOADING AND FILTERING (with an explicit attrition table for the paper)
# ---------------------------------------------------------------------------

def load_and_filter(path):
    df = pd.read_excel(path)
    stages = [('loaded rows', len(df)),
              ('unique incidents', df['Incident ID'].nunique())]

    df = df[df['LINDDUN categories'].notna()].copy()
    stages.append(('after LINDDUN filter', df['Incident ID'].nunique()))

    df['severity']    = df.apply(get_severity, axis=1)
    df['datacat']     = df.apply(datacat_label, axis=1)
    df['LINDDUN categories'] = df['LINDDUN categories'].astype(str).str.strip()
    df['Source']      = df['Source'].fillna('unknown').astype(str).str.strip()

    df = df[df['severity'] > 0].copy()
    stages.append(('after severity filter', df['Incident ID'].nunique()))

    attrition = pd.DataFrame(stages, columns=['stage', 'n_incidents'])
    return df, attrition


# ---------------------------------------------------------------------------
# 1. LINDDUN LABEL PREVALENCE, OVERALL AND BY SOURCE
# ---------------------------------------------------------------------------

def label_prevalence(df):
    exploded = (df.assign(label=df['LINDDUN categories'].str.split(','))
                .explode('label'))
    exploded['label'] = exploded['label'].str.strip()
    exploded = exploded[exploded['label'].ne('')]

    n_total = df['Incident ID'].nunique()
    n_src   = df.groupby('Source')['Incident ID'].nunique()

    overall = (exploded.groupby('label')['Incident ID'].nunique()
               .rename('n_total').to_frame())
    overall['pct_total'] = (overall['n_total'] / n_total * 100).round(1)

    by_src = (exploded.groupby(['label', 'Source'])['Incident ID'].nunique()
              .unstack(fill_value=0))
    pct_by_src = (by_src / n_src * 100).round(1)
    pct_by_src.columns = [f'pct_{c}' for c in pct_by_src.columns]

    out = overall.join(by_src).join(pct_by_src)
    pct_cols = [c for c in out.columns if c.startswith('pct_') and c != 'pct_total']
    if len(pct_cols) >= 2:
        out['max_pct_gap'] = (out[pct_cols].max(axis=1)
                              - out[pct_cols].min(axis=1)).round(1)
    return out.sort_values('n_total', ascending=False)


def combination_overlap(df):
    """Are the LINDDUN combinations themselves source-specific?"""
    combos = (df.groupby(['LINDDUN categories', 'Source'])['Incident ID']
              .nunique().unstack(fill_value=0))
    combos['n_total']      = combos.sum(axis=1)
    combos['n_sources']    = (combos.drop(columns='n_total') > 0).sum(axis=1)
    combos['source_exclusive'] = combos['n_sources'] == 1
    return combos.sort_values('n_total', ascending=False)


# ---------------------------------------------------------------------------
# 2. SCENARIO TABLE AND RANK STABILITY ACROSS SOURCES
# ---------------------------------------------------------------------------

def build_scenarios(df):
    n_total = df['Incident ID'].nunique()
    sc = (df.groupby(SCENARIO_COLS + ['datacat'], dropna=False)
          .agg(count=('Incident ID', 'nunique'),
               severity=('severity', 'max'),
               sev_min=('severity', 'min'))
          .reset_index())
    # severity is fully determined by the three flags -> sanity check
    assert (sc['severity'] == sc['sev_min']).all(), "severity varies within scenario"
    sc = sc.drop(columns='sev_min')
    sc['likelihood']    = sc['count'] / n_total
    sc['baseline_risk'] = sc['likelihood'] * sc['severity']
    sc = sc.sort_values('baseline_risk', ascending=False).reset_index(drop=True)
    sc['rank'] = np.arange(1, len(sc) + 1)
    return sc, n_total


def rank_stability(df):
    """Build the ranking per source and compare on shared scenarios."""
    keys = SCENARIO_COLS
    frames = {}
    for src, g in df.groupby('Source'):
        sc, n = build_scenarios(g)
        frames[src] = sc.set_index(keys)[['count', 'baseline_risk', 'rank']] \
            .add_suffix(f'_{src}')

    if len(frames) < 2:
        return pd.DataFrame(), pd.DataFrame()

    merged = pd.concat(frames.values(), axis=1, join='outer')
    inner  = pd.concat(frames.values(), axis=1, join='inner')

    rank_cols = [c for c in inner.columns if c.startswith('rank_')]
    corr = inner[rank_cols].corr(method='spearman') if len(inner) > 2 else pd.DataFrame()
    return merged.reset_index(), corr


# ---------------------------------------------------------------------------
# 3. DOES LINDDUN DIFFERENTIATE? (within-cell spread)
# ---------------------------------------------------------------------------

def differentiation(df, min_support=1):
    sc, _ = build_scenarios(df)
    sc = sc[sc['count'] >= min_support]
    g = (sc.groupby(['AssetTech', 'datacat'])
         .agg(n_linddun_subcells=('baseline_risk', 'size'),
              risk_min=('baseline_risk', 'min'),
              risk_max=('baseline_risk', 'max'),
              incidents=('count', 'sum'))
         .reset_index())
    g['risk_ratio'] = (g['risk_max'] / g['risk_min']).replace(np.inf, np.nan).round(2)
    g['share_in_largest_subcell'] = np.nan
    return g.sort_values('incidents', ascending=False)


def confounding(df):
    tabs = {}
    for col in ['AssetTech', 'datacat', 'Jurisdiction', 'Data Protection State']:
        if col in df.columns:
            t = pd.crosstab(df[col].fillna('Not reported'), df['Source'])
            t['pct_row'] = (t.max(axis=1) / t.sum(axis=1) * 100).round(1)
            tabs[col] = t.sort_values('pct_row', ascending=False)
    return tabs


# ---------------------------------------------------------------------------
# ENTRY POINT
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    df, attrition = load_and_filter(INPUT_FILE)

    print("\n--- Attrition ---")
    print(attrition.to_string(index=False))
    print("\n--- Incidents per source ---")
    print(df.groupby('Source')['Incident ID'].nunique().to_string())

    prev   = label_prevalence(df)
    combos = combination_overlap(df)
    sc_all, n_all = build_scenarios(df)
    merged, corr = rank_stability(df)
    diff   = differentiation(df)
    tabs   = confounding(df)

    print(f"\n--- LINDDUN prevalence (N={n_all}) ---")
    print(prev.to_string())
    print("\n--- Differentiation: LINDDUN sub-cells within (AssetTech, datacat) ---")
    print(diff.head(15).to_string(index=False))
    if not corr.empty:
        print("\n--- Spearman rank correlation across sources (shared scenarios) ---")
        print(corr.round(3).to_string())
    print(f"\nSource-exclusive LINDDUN combinations: "
          f"{int(combos['source_exclusive'].sum())} of {len(combos)}")

    with pd.ExcelWriter(OUTPUT_FILE, engine='openpyxl') as w:
        attrition.to_excel(w, sheet_name='attrition', index=False)
        prev.to_excel(w,      sheet_name='linddun_prevalence')
        combos.to_excel(w,    sheet_name='linddun_combos')
        sc_all.to_excel(w,    sheet_name='scenarios_all', index=False)
        merged.to_excel(w,    sheet_name='rank_by_source', index=False)
        if not corr.empty:
            corr.to_excel(w,  sheet_name='rank_correlation')
        diff.to_excel(w,      sheet_name='differentiation', index=False)
        for name, t in tabs.items():
            t.to_excel(w, sheet_name=f'src_{name[:24]}')

    print(f"\nSaved → {OUTPUT_FILE}")