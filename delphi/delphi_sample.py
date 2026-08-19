"""
Delphi Scenario Selection – Maximum Variation Sampling
========================================================
Selects three anchor scenarios from the core scenario family:
  LINDDUN      = exactly "Linkability, Identifiability"
  DataCategory = Personal Data + Credentials (no Special Categories)
  AssetTech    = varies: Software/Web App / Unknown /
                         Services provided by supplier

Method: Patton (1990) – Maximum Variation Sampling
Input:  data/processed/privacyrisq_assetsv8.xlsx
Output: results/delphi_scenario_selection.csv
        results/delphi_scenario_selection.txt
"""

import re
import pandas as pd
from pathlib import Path

# ── CONFIGURATION ─────────────────────────────────────────────────────────────
INPUT_FILE = Path(__file__).parent.parent / "data" / "processed" / "privacyrisq_assets_final.xlsx"
OUTPUT_CSV = Path(__file__).parent.parent / "results" / "delphi_scenario_selection.csv"
OUTPUT_TXT = Path(__file__).parent.parent / "results" / "delphi_scenario_selection.txt"

ASSET_TECH_VARIANTS = [
    "Software / Web Application",
    "Unknown",                        # Rank 2 in Daten (n=120)
    "Services provided by supplier",
]

# ── DATA FIELD PATTERNS (precompiled) ─────────────────────────────────────────
_RAW_PATTERNS: dict[str, list[str]] = {
    "Email Address":            [r"\bemails?\s?address\w*\b", r"\be-?mails?\b"],
    "Password (any form)":      [r"\bpasswords?\b", r"\bMD5\b", r"\bbcrypt\b",
                                 r"\bPBKDF2\b", r"\bargon2\b", r"\bSHA-?\d+\b"],
    "IP Address":               [r"\bIP\s?address\w*\b"],
    "Username":                 [r"\busernames?\b", r"\bscreen\s?names?\b",
                                 r"\bplayer\s?names?\b", r"\bdisplay\s?names?\b"],
    "Name (full/real)":         [r"\bfull\s?names?\b", r"\breal\s?names?\b", r"\bnames?\b"],
    "Date of Birth":            [r"\bdates?\s?of\s?birth\b", r"\bDOB\b", r"\bbirthdays?\b"],
    "Phone Number":             [r"\bphone\s?numbers?\b", r"\btelephone\b"],
    "Physical Address":         [r"\bphysical\s?address\w*\b", r"\bhome\s?address\w*\b",
                                 r"\bpostal\s?address\w*\b"],
    "Gender":                   [r"\bgenders?\b"],
    "Geographic Location":      [r"\bgeolocation\w*\b", r"\blocation\s?data\b",
                                 r"\blatitudes?\b", r"\blongitudes?\b", r"\bcit(y|ies)\b"],
    "Private Messages":         [r"\bprivate\s?messages?\b", r"\bchat\s?logs?\b"],
    "Purchase / Transaction":   [r"\border\s?histor(y|ies)\b", r"\bpurchases?\b"],
    "Partial Credit Card Data": [r"\bcredit\s?card\w*\b", r"\blast\s?4\s?digits\b"],
    "Security Questions":       [r"\bsecurity\s?questions?\b"],
    "2FA / Auth Token":         [r"\b2FA\b", r"\bauth\s?tokens?\b",
                                 r"\bbackup\s?codes?\b", r"\breset\s?tokens?\b"],
}

DATA_FIELD_PATTERNS: dict[str, list[re.Pattern]] = {
    field: [re.compile(p, re.IGNORECASE) for p in patterns]
    for field, patterns in _RAW_PATTERNS.items()
}

# ── FUNCTIONS ──────────────────────────────────────────────────────────────────

def compute_severity(row) -> int:
    pd_ = row["has_personal_data"]
    sc  = row["has_special_categories"]
    cr  = row["has_credentials"]
    if pd_ == 0:            return 0
    if sc == 0 and cr == 0: return 1
    if sc == 1 and cr == 1: return 6
    if sc == 1 or  cr == 1: return 4
    return 0


def detect_fields(text: str | float) -> dict[str, int]:
    """Gibt {Feldname: 0/1} für jeden Datentyp zurück."""
    if pd.isna(text):
        return {field: 0 for field in DATA_FIELD_PATTERNS}
    text = str(text)
    return {
        field: int(any(p.search(text) for p in patterns))
        for field, patterns in DATA_FIELD_PATTERNS.items()
    }


def select_typical_incident(df_group: pd.DataFrame) -> pd.Series:
    """Wählt den Incident mit den meisten erkannten Datenfeldern."""
    df_group = df_group.copy()
    fields_series           = df_group["Description"].apply(detect_fields)
    df_group["field_count"] = fields_series.apply(lambda d: sum(d.values()))  # ← Fix
    df_group["_fields"]     = fields_series
    return df_group.sort_values(
        ["field_count", "Title (Company)"],
        ascending=[False, True]
    ).iloc[0]


def compute_scenario_stats(df_family: pd.DataFrame) -> dict[str, dict]:
    """Berechnet n und BaselineRisk pro AssetTech-Gruppe aus den Daten."""
    total = len(df_family)
    stats = {}
    for asset_tech, group in df_family.groupby("AssetTech"):
        n = len(group)
        stats[asset_tech] = {
            "n":             n,
            "baseline_risk": round(n / total, 6) if total > 0 else 0.0,
        }
    return stats


def format_incident(incident: pd.Series, fields: dict[str, int]) -> str:
    detected = [f"  ✓ {f}" for f, v in fields.items() if v]
    return "\n".join([
        f"Title:        {incident['Title (Company)']}",
        f"Date:         {incident['Date of occurrence']}",
        f"Severity:     {incident['Severity']}",
        f"AssetTech:    [not disclosed]",
        f"Field Count:  {incident['field_count']}",
        f"n (scenario): {incident['scenario_n']}",
        f"BaselineRisk: {incident['baseline_risk']}",
        "",
        "Description:",
        str(incident["Description"]),
        "",
        "Detected Data Fields:",
        *detected,
    ])


# ── MAIN ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_TXT.parent.mkdir(parents=True, exist_ok=True)

    print(f"Loading: {INPUT_FILE}")
    df = pd.read_excel(INPUT_FILE)
    print(f"Loaded {len(df)} incidents\n")

    df["Severity"] = df.apply(compute_severity, axis=1)

    df_family = df[
        (df["LINDDUN categories"]     == "Linkability, Identifiability") &
        (df["has_personal_data"]      == 1) &
        (df["has_credentials"]        == 1) &
        (df["has_special_categories"] == 0)
        ].copy()

    print(f"Core family (LI+ID | P+C): {len(df_family)} incidents")
    print(df_family["AssetTech"].value_counts(), "\n")

    scenario_stats = compute_scenario_stats(df_family)

    output_lines = [
        "=" * 70,
        "DELPHI ANCHOR SCENARIO SELECTION",
        "Family: LI+ID | P+C | AssetTech varies (incl. unclassified)",
        "Method: Patton (1990) – Maximum Variation Sampling",
        "=" * 70,
        "",
        "VARIATION QUESTIONS (DataCategory) – per anchor:",
        "  Q_var1: Would your answers change if only Personal Data "
        "(no Credentials) were affected?",
        "  Q_var2: Would your answers change if Special Categories "
        "were additionally affected?",
        "=" * 70,
        ]

    selected_incidents = []

    for i, asset_tech in enumerate(ASSET_TECH_VARIANTS, start=1):
        df_asset = df_family[df_family["AssetTech"] == asset_tech]

        if df_asset.empty:
            print(f"WARNING: Keine Incidents für AssetTech='{asset_tech}'")
            continue

        print(f"AssetTech '{asset_tech}': {len(df_asset)} incidents")

        selected = select_typical_incident(df_asset)
        fields   = selected["_fields"]

        stats = scenario_stats.get(asset_tech, {"n": 0, "baseline_risk": 0.0})
        selected["scenario_n"]    = stats["n"]
        selected["baseline_risk"] = stats["baseline_risk"]

        selected_incidents.append({
            "anchor":        i,
            "asset_tech":    asset_tech,
            "title":         selected["Title (Company)"],
            "date":          selected["Date of occurrence"],
            "severity":      selected["Severity"],
            "field_count":   selected["field_count"],
            "scenario_n":    stats["n"],
            "baseline_risk": stats["baseline_risk"],
            "description":   selected["Description"],
            **{f"field_{k}": v for k, v in fields.items()},
        })

        output_lines += [
            "",
            "─" * 70,
            f"ANCHOR {i} – AssetTech: {asset_tech}",
            "─" * 70,
            format_incident(selected, fields),
            ]

    pd.DataFrame(selected_incidents).to_csv(OUTPUT_CSV, index=False)
    print(f"\nSaved CSV → {OUTPUT_CSV}")

    OUTPUT_TXT.write_text("\n".join(output_lines), encoding="utf-8")
    print(f"Saved TXT → {OUTPUT_TXT}")