# scripts/check_adid_patterns.py
# Testet Kandidaten-Regex fuer Advertising Identifier auf Ueber-Matching
# Zeigt Trefferzahlen + Beispiel-Incidents direkt in der Kommandozeile.

import pandas as pd
import re
from pathlib import Path

INPUT_FILE = Path("/Users/mev61324/IdeaProjects/PrivacyMort/data/processed/privacyrisq_cleaned.xlsx")

# Kandidaten: sichere (SAFE) vs. riskante (RISK)
CANDIDATES = {
    "advertising identifier/ID [SAFE]": r"\badvertising\s?(identifiers?|IDs?)\b",
    "IDFA [SAFE]":                      r"\bIDFA\b",
    "GAID/AAID [SAFE]":                 r"\b(GAID|AAID)\b",
    "mobile advertising ID [SAFE]":     r"\bmobile\s?advertising\s?IDs?\b",
    "unique identifier [RISK]":         r"\bunique\s?identifiers?\b",
    "tracking ID [RISK]":               r"\btracking\s?IDs?\b",
    "cookie ID [RISK]":                 r"\bcookie\s?IDs?\b",
    "ad ID (nackt) [RISK]":             r"\bad\s?IDs?\b",
}

ID_COL   = "Incident ID"
DESC_COL = "Description"

print("=" * 70)
print(f"Lade: {INPUT_FILE}")
df = pd.read_excel(INPUT_FILE)
print(f"Zeilen gesamt: {len(df)}")
print("=" * 70)

# --- Trefferuebersicht ---
print(f"\n{'Muster':<34} {'Treffer':>7}")
print("-" * 44)
results = {}
for name, pat in CANDIDATES.items():
    mask = df[DESC_COL].fillna("").str.contains(pat, case=True, regex=True)
    results[name] = mask
    print(f"{name:<34} {mask.sum():>7}")

# --- Beispiel-Incidents pro Muster (max. 3) ---
print("\n" + "=" * 70)
print("BEISPIELE (max. 3 pro Muster)")
print("=" * 70)

for name, mask in results.items():
    hits = df[mask]
    print(f"\n### {name}  ({mask.sum()} Treffer)")
    if hits.empty:
        print("   (keine)")
        continue
    for _, row in hits.head(3).iterrows():
        inc = row.get(ID_COL, "?")
        desc = str(row.get(DESC_COL, ""))[:160].replace("\n", " ")
        print(f"   - {inc}: {desc}...")

print("\nFERTIG.")