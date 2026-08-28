"""
Precision-Stichprobe für die Datenkategorie-Flags
==================================================
1. Lauf: erzeugt precision_sample.xlsx (Spalte true_label leer)
2. true_label manuell mit 1 / 0 befüllen
3. Lauf: rechnet Precision inkl. Wilson-95%-CI

Overwrite-Schutz: eine vorhandene Datei wird nur mit --new-sample ersetzt.
"""

import sys
import re
import argparse
from pathlib import Path

import pandas as pd

# label.py liegt eine Ebene höher -> Pattern-Listen importieren statt kopieren
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from label import (
    personal_data_patterns,
    special_categories_patterns,
    credentials_patterns,
)

# === KONFIGURATION ===
ROOT        = Path(__file__).resolve().parent.parent.parent
INPUT_FILE  = ROOT / "data" / "processed" / "privacyrisq_labeled_final.xlsx"
SAMPLE_FILE = ROOT / "scripts" / "quality_check" / "precision_sample.xlsx"

FLAGS = {
    "has_personal_data":      personal_data_patterns,
    "has_special_categories": special_categories_patterns,
    "has_credentials":        credentials_patterns,
}

N_PER_STRATUM = 8
SEED = 42
DESC_CHARS = 1200


# === STICHPROBE ZIEHEN ===

def build_sample(df):
    rows = []
    for flag, pats in FLAGS.items():
        comp = [(p, re.compile(p, re.I)) for p in pats]
        hits = df[df[flag] == 1]
        if hits.empty:
            print(f"  WARNUNG: keine Treffer für {flag}")
            continue
        for src, g in hits.groupby("Source"):
            n_take = min(N_PER_STRATUM, len(g))
            if n_take < N_PER_STRATUM:
                print(f"  Hinweis: {flag} / {src} hat nur {len(g)} Treffer")
            for idx, r in g.sample(n_take, random_state=SEED).iterrows():
                text = str(r["Description"]) if pd.notna(r["Description"]) else ""
                matched = [p for p, c in comp if c.search(text)]
                rows.append({
                    "row_id": idx,
                    "flag": flag,
                    "Source": src,
                    "n_patterns": len(matched),
                    "matched_patterns": " | ".join(matched[:6]),
                    "Description": text[:DESC_CHARS],
                    "true_label": "",
                    "note": "",
                })
    # Zufallsreihenfolge: verhindert Urteilsmuster beim Kodieren
    return pd.DataFrame(rows).sample(frac=1, random_state=SEED).reset_index(drop=True)


# === AUSWERTUNG ===

def wilson(k, n, z=1.96):
    if n == 0:
        return (float("nan"), float("nan"))
    p = k / n
    d = 1 + z**2 / n
    c = p + z**2 / (2 * n)
    h = z * ((p * (1 - p) / n + z**2 / (4 * n**2)) ** 0.5)
    return ((c - h) / d, (c + h) / d)


def precision(g):
    k, n = int(g["true_label"].sum()), len(g)
    lo, hi = wilson(k, n)
    return pd.Series({
        "n": n,
        "korrekt": k,
        "precision": round(k / n, 2),
        "ci_low": round(lo, 2),
        "ci_high": round(hi, 2),
    })


def evaluate(s):
    valid = pd.to_numeric(s["true_label"], errors="coerce")
    done = s.assign(true_label=valid).dropna(subset=["true_label"])
    done["true_label"] = done["true_label"].astype(int)

    offen = len(s) - len(done)
    print(f"Kodiert: {len(done)} / {len(s)}" + (f"  ({offen} offen)" if offen else ""))
    if done.empty:
        print("\nNoch nichts kodiert. true_label in der Excel mit 1 / 0 befüllen.")
        return

    print("\n--- Precision je Flag ---")
    print(done.groupby("flag").apply(precision, include_groups=False))

    print("\n--- Precision je Flag x Quelle ---")
    print(done.groupby(["flag", "Source"]).apply(precision, include_groups=False))

    print("\n--- Einzel- vs. Mehrfachtreffer ---")
    bucket = done["n_patterns"].apply(lambda x: "1 Pattern" if x == 1 else ">1 Pattern")
    print(done.groupby(bucket).apply(precision, include_groups=False))

    fp = done[done["true_label"] == 0]
    if not fp.empty:
        print(f"\n--- Häufigste Pattern in Falsch-Positiven (n={len(fp)}) ---")
        print(fp["matched_patterns"].str.split(" | ", regex=False).explode()
              .value_counts().head(10))


# === MAIN ===

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--new-sample", action="store_true",
                    help="vorhandene Stichprobe überschreiben")
    args = ap.parse_args()

    if SAMPLE_FILE.exists() and not args.new_sample:
        print(f"Auswertung: {SAMPLE_FILE}\n")
        evaluate(pd.read_excel(SAMPLE_FILE))
    else:
        print(f"Laden: {INPUT_FILE}")
        df = pd.read_excel(INPUT_FILE)
        print(f"{len(df)} Vorfälle\n")

        sample = build_sample(df)
        SAMPLE_FILE.parent.mkdir(parents=True, exist_ok=True)
        sample.to_excel(SAMPLE_FILE, index=False)

        print(f"\n{len(sample)} Fälle -> {SAMPLE_FILE}")
        print(sample.groupby(["flag", "Source"]).size())
        print("\nJetzt true_label (1/0) befüllen und Skript erneut starten.")