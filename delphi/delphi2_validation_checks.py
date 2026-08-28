#!/usr/bin/env python3
"""
Delphi Round 2 - Validation Checks
====================================
Input : que_2.xlsx (sheet "Tabelle1"), delphi2_results.json (run
        results_builder.py first)
Output: delphi2_results.json (extended with a "validation" key),
        delphi2_validation_results.md

Aligned with results_builder.py:
  * identical half-open band definition (no gaps, no overlaps)
  * identical two-tier consensus rule (tier 1: modal band alone >= 50 %;
    tier 2: modal + one adjacent band >= 70 %), so both reports agree
  * maturity level 0 is a VALID category, so no rater is dropped from the
    Q_T ICC for answering 0
  * identical 3-way agreement label (consensus / tendency / dissent) and
    bimodality rule
  * band definition self-test (guards against re-introducing gaps)
  * no-effect-vote coherence check (level 0 vs. 0 % on both anchors)

Measures:
  * ICC(2,k) for Q_T, Q_M, Q_C (targets = controls, raters = experts),
    available-case, missingness reported, no imputation, no pooled number.
  * Fleiss' kappa (variable n per item) for dependency type, descriptive.
  * Gwet's AC1/AC2, appendix-only, descriptive.
  * Monotonicity: Q_M <= Q_C per rater; curve non-decreasing, with the
    structural onset step reported separately from genuine jumps.
  * Excluded: Krippendorff's alpha, van der Eijk's A, Kendall's W.
"""

from __future__ import annotations

import json
import math
import re
from collections import Counter
from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
INPUT_FILE = BASE_DIR / "que_2.xlsx"
SHEET = "Tabelle1"
RESULTS_JSON = BASE_DIR / "delphi2_results.json"
OUTPUT_MD = BASE_DIR / "delphi2_validation_results.md"

CONTROLS = ["A8.28", "A8.16", "A8.12", "A8.24", "A5.16",
            "A8.15", "A5.17", "A5.34", "A8.5", "A5.15"]

TOLERANCE = 1e-6

# ---- must stay identical to results_builder.py ---------------------------
BAND_EDGES = [10.0, 25.0, 50.0, 75.0]
BAND_LABELS = ["0-10", ">10-25", ">25-50", ">50-75", ">75-100"]
LEVEL_CODES = [0, 1, 2, 3, 4, 5]

MIN_VALID = 5
MODAL_ONLY_THRESHOLD = 0.50    # tier 1: modal band alone
WINDOW_THRESHOLD = 0.70        # tier 2: modal + one adjacent band (stricter)
CONSENSUS_READING = "B"
BIMODAL_BLOCKS_CONSENSUS = True
BIMODAL_MIN_SHARE = 0.25
TENDENCY_THRESHOLD = 0.40

CURVE_JUMP_THRESHOLD_PCT = 15.0   # applied only outside the onset step

DEPENDENCY_NAMES = [
    "A5.34 + A5.12", "A5.34 + A5.13", "A5.34 + A5.12 UND A5.13",
    "A5.34 + A5.17", "A5.34 + A5.26",
    "A8.16 + A8.15", "A8.16 + A8.15 UND A5.25",
]


# --------------------------------------------------------------------------
# Helpers (mirrored from results_builder.py for standalone use)
# --------------------------------------------------------------------------

def resolve_column(df, name):
    if name in df.columns:
        return name
    norm = {" ".join(str(c).split()): c for c in df.columns}
    key = " ".join(str(name).split())
    if key in norm:
        return norm[key]
    for c in df.columns:
        if str(c).startswith(str(name)[:30]):
            return c
    return None


def is_blank(value):
    if value is None:
        return True
    if isinstance(value, float) and math.isnan(value):
        return True
    return str(value).strip() == ""


NON_ASSESSABLE_PATTERNS = [
    "nicht pauschal", "nicht beurteilbar", "nicht bewertbar",
    "kann ich nicht", "keine angabe", "keine aussage",
    "weiss nicht", "weiß nicht", "unklar", "n/a", "k.a.",
]


def is_non_assessable(value):
    if is_blank(value):
        return False
    return any(p in str(value).strip().lower() for p in NON_ASSESSABLE_PATTERNS)


def clamp_pct(number):
    return max(0.0, min(100.0, float(number)))


def normalize_percentage(value):
    if is_blank(value) or is_non_assessable(value):
        return None
    if isinstance(value, (int, float)):
        n = float(value)
        if 0.0 < n < 1.0:
            n *= 100.0
        return clamp_pct(n)
    text = str(value).strip().replace("%", " ").strip()
    m = re.match(r"^(\d+(?:[.,]\d+)?)\s*(?:-|–|bis)\s*(\d+(?:[.,]\d+)?)$", text)
    if m:
        low = float(m.group(1).replace(",", "."))
        high = float(m.group(2).replace(",", "."))
        return clamp_pct((low + high) / 2.0)
    m = re.search(r"-?\d+(?:[.,]\d+)?", text)
    if m is None:
        return None
    raw = m.group(0).replace(",", ".")
    n = float(raw)
    if "." in raw and 0.0 < n <= 1.0:
        n *= 100.0
    return clamp_pct(n)


def normalize_level(value):
    """0..5 valid; 0 = 'no effect at any maturity level' (substantive)."""
    if is_blank(value) or is_non_assessable(value):
        return None
    if isinstance(value, (int, float)):
        n = int(round(float(value)))
        return n if n in LEVEL_CODES else None
    m = re.search(r"-?\d+", str(value))
    if m is None:
        return None
    n = int(m.group(0))
    return n if n in LEVEL_CODES else None


def normalize_category(value):
    if is_blank(value):
        return None
    return re.sub(r"\s+", " ", str(value)).strip()


def band_index(number):
    value = clamp_pct(number)
    for i, upper in enumerate(BAND_EDGES):
        if value <= upper + TOLERANCE:
            return i
    return len(BAND_EDGES)


def band_definition_selftest():
    """Guards against gaps/overlaps being re-introduced in BAND_EDGES."""
    problems = []
    if sorted(BAND_EDGES) != BAND_EDGES or len(set(BAND_EDGES)) != len(BAND_EDGES):
        problems.append("BAND_EDGES not strictly increasing")
    if len(BAND_LABELS) != len(BAND_EDGES) + 1:
        problems.append("BAND_LABELS length != len(BAND_EDGES) + 1")
    probes = [0.0, 10.0, 10.4, 10.5, 24.9, 25.0, 25.1, 50.0, 50.5,
              75.0, 75.5, 100.0]
    mapping = {}
    for p in probes:
        idx = band_index(p)
        if not 0 <= idx < len(BAND_LABELS):
            problems.append(f"probe {p} mapped outside label range")
        mapping[p] = BAND_LABELS[idx]
    # every probe just above an edge must land one band higher
    for i, edge in enumerate(BAND_EDGES):
        if band_index(edge) != i or band_index(edge + 0.1) != i + 1:
            problems.append(f"edge {edge} not handled half-open")
    return {"ok": not problems, "problems": problems, "probe_mapping": mapping}


def read_dependency_type_filtered(df, name):
    col = resolve_column(df, f"Art Abhängigkeit {name}")
    if col is None:
        return []
    out = []
    for v in df[col]:
        if is_non_assessable(v):
            continue
        cat = normalize_category(v)
        if cat is not None:
            out.append(cat)
    return out


# --------------------------------------------------------------------------
# ICC(2,k)
# --------------------------------------------------------------------------

def icc_2k(matrix):
    n, k = matrix.shape
    if n < 2 or k < 2:
        return None

    grand_mean = matrix.mean()
    row_means = matrix.mean(axis=1)
    col_means = matrix.mean(axis=0)

    ss_rows = k * np.sum((row_means - grand_mean) ** 2)
    ss_cols = n * np.sum((col_means - grand_mean) ** 2)
    ss_total = np.sum((matrix - grand_mean) ** 2)
    ss_error = ss_total - ss_rows - ss_cols

    df_r, df_c, df_e = n - 1, k - 1, (n - 1) * (k - 1)
    if df_r <= 0 or df_c <= 0 or df_e <= 0:
        return None

    ms_r, ms_c, ms_e = ss_rows / df_r, ss_cols / df_c, ss_error / df_e
    denom = ms_r + (ms_c - ms_e) / n
    if denom == 0:
        return None

    icc = (ms_r - ms_e) / denom
    f_stat = ms_r / ms_e if ms_e > 0 else np.inf
    try:
        from scipy import stats as sstats
        f_lower = f_stat / sstats.f.ppf(0.975, df_r, df_e)
        f_upper = f_stat * sstats.f.ppf(0.975, df_e, df_r)
        ci_lower = (f_lower - 1) / f_lower if f_lower not in (0, np.inf) else None
        ci_upper = (f_upper - 1) / f_upper if f_upper not in (0, np.inf) else None
    except Exception:
        ci_lower = ci_upper = None

    return {
        "icc": round(float(icc), 3),
        "ci_lower": None if ci_lower is None else round(float(ci_lower), 3),
        "ci_upper": None if ci_upper is None else round(float(ci_upper), 3),
        "n_targets": int(n), "k_raters": int(k),
    }


def build_icc_matrix(per_control_raw, controls, n_raters):
    data = {c: per_control_raw[c] for c in controls}
    keep = [ri for ri in range(n_raters)
            if all(data[c][ri] is not None for c in controls)]
    n_dropped = n_raters - len(keep)
    if len(keep) < 2:
        return None, n_dropped
    matrix = np.array([[data[c][ri] for ri in keep] for c in controls],
                      dtype=float)
    return matrix, n_dropped


# --------------------------------------------------------------------------
# Fleiss' kappa (variable n per subject)
# --------------------------------------------------------------------------

def fleiss_kappa_variable_n(item_ratings):
    categories = sorted({c for ratings in item_ratings for c in ratings})
    if len(categories) < 2:
        return None
    cat_index = {c: i for i, c in enumerate(categories)}

    rows = []
    for ratings in item_ratings:
        if len(ratings) < 2:
            continue
        counts = np.zeros(len(categories))
        for r in ratings:
            counts[cat_index[r]] += 1
        rows.append((len(ratings), counts))
    if not rows:
        return None

    p_i_list, p_j_num, n_total = [], np.zeros(len(categories)), 0
    for n_i, counts in rows:
        p_i_list.append((np.sum(counts ** 2) - n_i) / (n_i * (n_i - 1)))
        p_j_num += counts
        n_total += n_i

    p_bar = float(np.mean(p_i_list))
    p_j = p_j_num / n_total
    p_e = float(np.sum(p_j ** 2))
    if p_e >= 1.0:
        return {"kappa": None, "note": "p_e == 1, kappa undefined",
                "n_items": len(rows), "categories": categories}

    return {
        "kappa": round((p_bar - p_e) / (1.0 - p_e), 3),
        "n_items": len(rows), "categories": categories,
        "p_bar": round(p_bar, 3), "p_e": round(p_e, 3),
    }


# --------------------------------------------------------------------------
# Gwet's AC1 / AC2
# --------------------------------------------------------------------------

def gwet(item_ratings, k, ordinal):
    if k < 2:
        return None
    if ordinal:
        w = np.array([[1 - abs(a - b) / (k - 1) for b in range(k)]
                      for a in range(k)])
    else:
        w = np.eye(k)

    pa_list, pi_sum, n_items = [], np.zeros(k), 0
    for ratings in item_ratings:
        n = len(ratings)
        if n < 2:
            continue
        counts = np.zeros(k)
        for r in ratings:
            counts[r] += 1
        pa = sum(counts[a] * (w[a] @ counts - w[a, a]) for a in range(k)) / (n * (n - 1))
        pa_list.append(pa)
        pi_sum += counts / n
        n_items += 1

    if not n_items:
        return None
    pi = pi_sum / n_items
    p_e = (w.sum() / (k * (k - 1))) * float(pi @ (1 - pi))
    if p_e >= 1.0:
        return None
    return round((float(np.mean(pa_list)) - p_e) / (1 - p_e), 3)


# --------------------------------------------------------------------------
# Agreement classification (identical logic to results_builder.py)
# --------------------------------------------------------------------------

def detect_bimodality(freq):
    n = sum(freq)
    if n == 0:
        return False, ""
    peaks = [i for i, f in enumerate(freq) if f / n >= BIMODAL_MIN_SHARE]
    for a, b in combinations(peaks, 2):
        if b - a >= 2 and min(freq[a + 1:b]) < min(freq[a], freq[b]):
            return True, (f"two separate peaks >= {BIMODAL_MIN_SHARE:.0%} "
                          f"(index {a} and {b})")
    return False, ""


def classify_distribution(raw_values, labels, coder):
    numeric = [v for v in raw_values if v is not None]
    n = len(numeric)
    if n == 0:
        return None
    k = len(labels)
    freq = [0] * k
    for v in numeric:
        freq[coder(v)] += 1

    modal_idx = max(range(k), key=lambda i: (freq[i], -i))
    modal_share = freq[modal_idx] / n
    neighbours = [i for i in (modal_idx - 1, modal_idx + 1) if 0 <= i < k]
    best_adjacent = (max(neighbours, key=lambda i: (freq[i], -i))
                     if neighbours else None)
    if CONSENSUS_READING == "A" or best_adjacent is None:
        window = [modal_idx]
    else:
        window = sorted({modal_idx, best_adjacent})
    window_share = sum(freq[i] for i in window) / n

    bimodal, note = detect_bimodality(freq)

    tier1 = modal_share >= MODAL_ONLY_THRESHOLD
    tier2 = (window_share >= WINDOW_THRESHOLD) and (len(window) > 1)

    if n < MIN_VALID:
        label = "insufficient_n"
    elif bimodal:
        label = "dissent"
    elif tier1 or tier2:
        label = "consensus"
    elif window_share >= TENDENCY_THRESHOLD:
        label = "tendency"
    else:
        label = "dissent"

    return {
        "n_valid": n, "label": label,
        "modal_label": labels[modal_idx],
        "modal_share_pct": round(modal_share * 100, 1),
        "window_labels": [labels[i] for i in window],
        "window_share_pct": round(window_share * 100, 1),
        "bimodal": bimodal, "bimodal_note": note,
        "consensus_tier": "modal" if tier1 else ("window" if tier2 else None),
        "note": "same two-tier rule as results_builder.py; the 3-way label "
                "is descriptive, the binary criterion is tier1 OR tier2",
    }


# --------------------------------------------------------------------------
# Coherence check: no-effect votes
# --------------------------------------------------------------------------

def no_effect_votes(df, q_t_raw, q_m_raw, q_c_raw):
    """
    Level 0 means 'no effect at any maturity level'. Cross-check it against
    the two percentage anchors: a coherent no-effect vote is level 0 AND
    0 % on both anchors. Incoherent combinations are reported, not fixed.
    """
    rows = []
    for control in CONTROLS:
        for ri in range(len(df)):
            level = q_t_raw[control][ri]
            r3 = q_m_raw[control][ri]
            r5 = q_c_raw[control][ri]
            zero_pct = (r3 is not None and r5 is not None
                        and abs(r3) < TOLERANCE and abs(r5) < TOLERANCE)
            if level == 0 or zero_pct:
                rows.append({
                    "control": control, "row": ri, "level": level,
                    "reduction_3_pct": r3, "reduction_5_pct": r5,
                    "coherent": bool(level == 0 and zero_pct),
                })
    return {
        "n_votes": len(rows),
        "n_coherent": sum(1 for r in rows if r["coherent"]),
        "n_incoherent": sum(1 for r in rows if not r["coherent"]),
        "detail": rows,
        "note": "level 0 is treated as a substantive category, not as "
                "missing data; incoherent rows are reported for the paper, "
                "not silently corrected",
    }


# --------------------------------------------------------------------------
# Monotonicity checks
# --------------------------------------------------------------------------

def monotonicity_qm_qc(df):
    violations = []
    for control in CONTROLS:
        col3 = resolve_column(df, f"Reduktion 3 {control}")
        col5 = resolve_column(df, f"Reduktion 5 {control}")
        if col3 is None or col5 is None:
            continue
        for i in range(len(df)):
            q_m = normalize_percentage(df[col3].iloc[i])
            q_c = normalize_percentage(df[col5].iloc[i])
            if q_m is None or q_c is None:
                continue
            if q_c + TOLERANCE < q_m:
                violations.append({"control": control, "row": i,
                                   "q_m_pct": q_m, "q_c_pct": q_c})
    return violations


def monotonicity_curve(model, jump_threshold_pct=CURVE_JUMP_THRESHOLD_PCT):
    """
    (a) violations   : curve decreases - never expected
    (b) onset_jumps  : the single step in which the curve leaves 0 (structural,
                       because maturity is only defined on integer levels)
    (c) jump_warnings: any other step above the threshold
    Flat-zero curves (Q_T = 0) are reported separately, not as violations.
    """
    violations, jump_warnings, onset_jumps, flat_zero = [], [], [], []

    for control, d in model["controls"].items():
        curve = d.get("curve_pct")
        q_t = d.get("q_t", {}).get("point_estimate")
        if not curve:
            continue
        values = [curve[str(m)] for m in range(1, 6)]

        if all(v <= TOLERANCE for v in values):
            flat_zero.append({
                "control": control, "q_t": q_t,
                "note": "flat zero curve (Q_T = 0: no effect at any maturity "
                        "level); monotonicity trivially satisfied",
            })
            continue

        onset_done = False
        for i in range(1, len(values)):
            level_from, level_to = i, i + 1
            delta = values[i] - values[i - 1]

            if delta < -TOLERANCE:
                violations.append({
                    "control": control, "level_from": level_from,
                    "level_to": level_to, "value_from": values[i - 1],
                    "value_to": values[i],
                })
                continue
            if delta <= TOLERANCE:
                continue

            is_onset = (not onset_done) and values[i - 1] <= TOLERANCE
            if is_onset:
                onset_done = True
                onset_jumps.append({
                    "control": control, "level_from": level_from,
                    "level_to": level_to, "value_from": values[i - 1],
                    "value_to": values[i], "delta_pct": round(delta, 1),
                    "q_t": q_t,
                    "note": "structural: single-integer-step onset from Q_T to "
                            "the first level with effect; expected by "
                            "construction",
                })
            elif delta > jump_threshold_pct:
                jump_warnings.append({
                    "control": control, "level_from": level_from,
                    "level_to": level_to, "value_from": values[i - 1],
                    "value_to": values[i], "delta_pct": round(delta, 1),
                    "note": "large increase outside the onset step; check the "
                            "Q_M/Q_C spread or curve construction",
                })

    return violations, jump_warnings, onset_jumps, flat_zero


# --------------------------------------------------------------------------
# Markdown report
# --------------------------------------------------------------------------

def md_table(headers, rows):
    if not rows:
        rows = [["-"] * len(headers)]
    lines = ["| " + " | ".join(headers) + " |",
             "|" + "|".join(["---"] * len(headers)) + "|"]
    for r in rows:
        lines.append("| " + " | ".join("" if v is None else str(v) for v in r) + " |")
    return "\n".join(lines) + "\n"


def write_markdown(validation, path):
    L = ["# Delphi Round 2 - Validation Results\n",
         f"\nBands: {', '.join(BAND_LABELS)} (half-open). Maturity levels "
         f"{LEVEL_CODES[0]}-{LEVEL_CODES[-1]}, level 0 valid. Two-tier "
         f"consensus rule: tier 1 modal band alone >= "
         f"{MODAL_ONLY_THRESHOLD:.0%}, tier 2 modal + adjacent band >= "
         f"{WINDOW_THRESHOLD:.0%}. Consensus reading: {CONSENSUS_READING}.\n"]

    # ---- band self-test ---------------------------------------------------
    L.append("\n## Band Definition Self-test\n")
    st = validation["band_definition_selftest"]
    L.append(f"Status: **{'OK' if st['ok'] else 'FAILED'}**\n")
    if st["problems"]:
        for p in st["problems"]:
            L.append(f"- {p}\n")
    L.append(md_table(["Probe value", "Assigned band"],
                      [[k, v] for k, v in st["probe_mapping"].items()]))

    # ---- ICC(2,k) ---------------------------------------------------------
    L.append("\n## ICC(2,k) per Effectiveness Anchor\n")
    rows = []
    for label in ("q_t", "q_m", "q_c"):
        r = validation["icc_2k"].get(label, {})
        rows.append([label.upper(), r.get("icc"), r.get("ci_lower"),
                     r.get("ci_upper"), r.get("n_targets"), r.get("k_raters"),
                     r.get("n_raters_dropped_for_missingness")])
    L.append(md_table(["Anchor", "ICC", "CI lower", "CI upper", "n targets",
                       "k raters", "Raters dropped (missing)"], rows))
    L.append(f"\n*{validation['icc_2k'].get('pooled_summary_note', '')}*\n")

    # ---- Fleiss' kappa ----------------------------------------------------
    L.append("\n## Fleiss' Kappa - Dependency Type\n")
    fk = validation.get("fleiss_kappa_dependency_type")
    if fk is None:
        L.append("Not computable (fewer than 2 categories after filtering).\n")
    else:
        L.append(md_table(["Kappa", "n items", "Categories", "p_bar", "p_e"],
                          [[fk.get("kappa"), fk.get("n_items"),
                            ", ".join(fk.get("categories", [])),
                            fk.get("p_bar"), fk.get("p_e")]]))
        if fk.get("note"):
            L.append(f"\n*Note: {fk['note']}*\n")
    L.append("\n*Dependency type is descriptive only and does not enter the "
             "effectiveness model. Non-assessable answers excluded, "
             "consistent with results_builder.py.*\n")

    # ---- Agreement classification -----------------------------------------
    L.append("\n## Agreement Classification (Consensus / Tendency / Dissent)\n")
    L.append("*Same two-tier rule as results_builder.py; the 3-way label is "
             "descriptive, the binary criterion is tier1 OR tier2.*\n")
    rows = []
    for item, r in validation["agreement_classification"].items():
        if r is None:
            rows.append([item, 0, "-", "-", "-", "-", "-"])
            continue
        rows.append([item, r["n_valid"], r["label"], r["modal_label"],
                     f"{r['modal_share_pct']} %", f"{r['window_share_pct']} %",
                     "yes" if r["bimodal"] else "no"])
    L.append(md_table(["Item", "n valid", "Label", "Modal band", "Modal share",
                       "Window share", "Bimodal"], rows))

    # ---- No-effect votes ---------------------------------------------------
    L.append("\n## No-effect Votes (maturity level 0 / 0 % on both anchors)\n")
    ne = validation["no_effect_votes"]
    L.append(f"{ne['n_votes']} votes total, {ne['n_coherent']} coherent, "
             f"{ne['n_incoherent']} incoherent.\n\n*{ne['note']}*\n")
    rows = [[r["control"], r["row"], r["level"], r["reduction_3_pct"],
             r["reduction_5_pct"], "yes" if r["coherent"] else "no"]
            for r in ne["detail"]]
    L.append(md_table(["Control", "Row", "Level", "Reduktion 3 %",
                       "Reduktion 5 %", "Coherent"], rows))

    # ---- Gwet appendix -----------------------------------------------------
    L.append("\n## Appendix: Gwet's AC1 / AC2 (Descriptive Only)\n")
    L.append("*No true value exists in a Delphi panel; not interpreted as a "
             "reliability criterion.*\n")
    gw = validation["gwet_appendix"]
    L.append(md_table(["Measure", "Value"], [
        ["AC2, Q_T levels (ordinal)", gw.get("AC2_Q_T_levels")],
        ["AC2, Q_M bands (ordinal)", gw.get("AC2_Q_M_bands")],
        ["AC2, Q_C bands (ordinal)", gw.get("AC2_Q_C_bands")],
        ["AC2, residual effectiveness bands (ordinal)", gw.get("AC2_residual_bands")],
        ["AC1, dependency type (nominal)", gw.get("AC1_dependency_type")],
    ]))

    # ---- Monotonicity ------------------------------------------------------
    L.append("\n## Monotonicity Checks\n")
    mono = validation["monotonicity"]

    L.append("\n### Q_M <= Q_C Violations (per rater, per control)\n")
    L.append(md_table(["Control", "Row", "Q_M", "Q_C"],
                      [[v["control"], v["row"], f"{v['q_m_pct']} %",
                        f"{v['q_c_pct']} %"]
                       for v in mono["q_m_le_q_c_violations"]]))

    L.append("\n### Curve Non-monotonicity (hard violations)\n")
    L.append(md_table(["Control", "Level from", "Level to", "Value from",
                       "Value to"],
                      [[v["control"], v["level_from"], v["level_to"],
                        v["value_from"], v["value_to"]]
                       for v in mono["curve_violations"]]))

    L.append("\n### Flat-zero Curves (Q_T = 0)\n")
    L.append(md_table(["Control", "Q_T", "Note"],
                      [[v["control"], v["q_t"], v["note"]]
                       for v in mono["flat_zero_curves"]]))

    L.append("\n### Structural Onset Jumps (informational, not a warning)\n"
             "*The single-integer step in which the curve leaves 0 carries the "
             "full 0 -> Q_M increase, because maturity is only defined on "
             "integer levels.*\n")
    L.append(md_table(["Control", "Q_T", "Level from", "Level to",
                       "Value from", "Value to", "Delta (pct)"],
                      [[v["control"], v["q_t"], v["level_from"], v["level_to"],
                        v["value_from"], v["value_to"], v["delta_pct"]]
                       for v in mono["onset_jumps"]]))

    L.append(f"\n### Genuine Jump Warnings (outside the onset step, "
             f"> {CURVE_JUMP_THRESHOLD_PCT} pct points)\n")
    L.append(md_table(["Control", "Level from", "Level to", "Value from",
                       "Value to", "Delta (pct)", "Note"],
                      [[v["control"], v["level_from"], v["level_to"],
                        v["value_from"], v["value_to"], v["delta_pct"],
                        v["note"]]
                       for v in mono["curve_jump_warnings"]]))

    # ---- Excluded measures --------------------------------------------------
    L.append("\n## Excluded Measures\n")
    L.append(md_table(["Measure", "Reason"],
                      [[k, v] for k, v in validation["excluded_measures"].items()]))

    path.write_text("".join(L), encoding="utf-8")


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------

def main():
    df = pd.read_excel(INPUT_FILE, sheet_name=SHEET)
    n_raters = len(df)

    if not RESULTS_JSON.exists():
        raise FileNotFoundError(
            f"{RESULTS_JSON.name} not found. Run results_builder.py first.")
    model = json.loads(RESULTS_JSON.read_text(encoding="utf-8"))

    selftest = band_definition_selftest()
    if not selftest["ok"]:
        print("  WARNING: band definition self-test FAILED")
        for p in selftest["problems"]:
            print(f"    - {p}")

    # ---- raw matrices -----------------------------------------------------
    q_t_raw, q_m_raw, q_c_raw = {}, {}, {}
    for control in CONTROLS:
        col_t = resolve_column(df, f"Reifegrad {control}")
        col_m = resolve_column(df, f"Reduktion 3 {control}")
        col_c = resolve_column(df, f"Reduktion 5 {control}")
        q_t_raw[control] = ([normalize_level(v) for v in df[col_t]]
                            if col_t else [None] * n_raters)
        q_m_raw[control] = ([normalize_percentage(v) for v in df[col_m]]
                            if col_m else [None] * n_raters)
        q_c_raw[control] = ([normalize_percentage(v) for v in df[col_c]]
                            if col_c else [None] * n_raters)

    # ---- ICC(2,k) ---------------------------------------------------------
    icc_results = {}
    for label, raw in (("q_t", q_t_raw), ("q_m", q_m_raw), ("q_c", q_c_raw)):
        matrix, n_dropped = build_icc_matrix(raw, CONTROLS, n_raters)
        if matrix is None:
            icc_results[label] = {"icc": None,
                                  "note": "insufficient complete-case data"}
        else:
            result = icc_2k(matrix)
            if result is None:
                icc_results[label] = {"icc": None, "note": "ICC not computable"}
            else:
                result["n_raters_dropped_for_missingness"] = n_dropped
                icc_results[label] = result

    icc_results["pooled_summary_note"] = (
        "Pooling ICC(2,k) across Q_T, Q_M, Q_C into a single number is "
        "deliberately not reported: the three anchors differ substantially in "
        "target variance (Q_T shows range restriction across controls, most "
        "raters converge on level 2), which would make an unweighted average "
        "misleading. Reported separately per anchor instead. Maturity level 0 "
        "is now a valid category, so no rater is dropped for answering 0."
    )

    # ---- Fleiss' kappa ----------------------------------------------------
    dep_type_ratings = [read_dependency_type_filtered(df, name)
                        for name in DEPENDENCY_NAMES]
    fleiss_result = fleiss_kappa_variable_n(dep_type_ratings)

    # ---- Agreement classification ----------------------------------------
    level_labels = [str(m) for m in LEVEL_CODES]
    level_coder = lambda v: LEVEL_CODES.index(int(round(v)))

    agreement = {}
    for control in CONTROLS:
        agreement[f"{control}_Q_T"] = classify_distribution(
            q_t_raw[control], level_labels, level_coder)
        agreement[f"{control}_Q_M"] = classify_distribution(
            q_m_raw[control], BAND_LABELS, band_index)
        agreement[f"{control}_Q_C"] = classify_distribution(
            q_c_raw[control], BAND_LABELS, band_index)

    residual_raw_by_name = {}
    for name in DEPENDENCY_NAMES:
        col = resolve_column(df, f"Verbleibende operative Wirksamkeit {name}")
        raw = [normalize_percentage(v) for v in df[col]] if col else []
        residual_raw_by_name[name] = raw
        agreement[f"{name}_residual"] = classify_distribution(
            raw, BAND_LABELS, band_index)

    # ---- Gwet -------------------------------------------------------------
    level_ratings = [[level_coder(v) for v in q_t_raw[c] if v is not None]
                     for c in CONTROLS]
    band_ratings_qm = [[band_index(v) for v in q_m_raw[c] if v is not None]
                       for c in CONTROLS]
    band_ratings_qc = [[band_index(v) for v in q_c_raw[c] if v is not None]
                       for c in CONTROLS]
    band_ratings_residual = [
        [band_index(v) for v in residual_raw_by_name[name] if v is not None]
        for name in DEPENDENCY_NAMES]

    all_categories = sorted({c for r in dep_type_ratings for c in r})
    cat_index = {c: i for i, c in enumerate(all_categories)}
    dep_type_codes = [[cat_index[c] for c in r] for r in dep_type_ratings]

    gwet_results = {
        "AC2_Q_T_levels": gwet(level_ratings, len(LEVEL_CODES), ordinal=True),
        "AC2_Q_M_bands": gwet(band_ratings_qm, len(BAND_LABELS), ordinal=True),
        "AC2_Q_C_bands": gwet(band_ratings_qc, len(BAND_LABELS), ordinal=True),
        "AC2_residual_bands": gwet(band_ratings_residual, len(BAND_LABELS),
                                   ordinal=True),
        "AC1_dependency_type": gwet(dep_type_codes,
                                    max(len(all_categories), 2), ordinal=False),
        "note": "appendix only, descriptive; no true value exists in a Delphi "
                "panel, so this is not interpreted as a reliability criterion",
    }

    # ---- Coherence + monotonicity ----------------------------------------
    no_effect = no_effect_votes(df, q_t_raw, q_m_raw, q_c_raw)
    qm_qc_violations = monotonicity_qm_qc(df)
    (curve_violations, curve_jump_warnings,
     onset_jumps, flat_zero) = monotonicity_curve(model)

    # ---- Assemble ---------------------------------------------------------
    model["validation"] = {
        "band_definition_selftest": selftest,
        "icc_2k": icc_results,
        "fleiss_kappa_dependency_type": fleiss_result,
        "agreement_classification": agreement,
        "no_effect_votes": no_effect,
        "gwet_appendix": gwet_results,
        "monotonicity": {
            "q_m_le_q_c_violations": qm_qc_violations,
            "curve_violations": curve_violations,
            "flat_zero_curves": flat_zero,
            "onset_jumps": onset_jumps,
            "curve_jump_warnings": curve_jump_warnings,
        },
        "excluded_measures": {
            "krippendorffs_alpha": "not used (prevalence paradox under skewed "
                                   "marginals in this dataset)",
            "van_der_eijk_agreement_a": "not used (unvalidated beyond edge-case "
                                        "self-tests)",
            "kendalls_w": "not used (no que_1.xlsx rater-level ranking data in "
                          "scope of this script)",
        },
    }

    RESULTS_JSON.write_text(json.dumps(model, indent=2, ensure_ascii=False),
                            encoding="utf-8")
    write_markdown(model["validation"], OUTPUT_MD)

    print(f"validation appended to {RESULTS_JSON.name}")
    print(f"validation report written to {OUTPUT_MD.name}")
    print(f"band self-test: {'OK' if selftest['ok'] else 'FAILED'}")
    print(f"ICC(2,k): Q_T={icc_results['q_t'].get('icc')}, "
          f"Q_M={icc_results['q_m'].get('icc')}, "
          f"Q_C={icc_results['q_c'].get('icc')}")
    print(f"Fleiss' kappa (dependency type): "
          f"{fleiss_result.get('kappa') if fleiss_result else None}")
    print(f"No-effect votes: {no_effect['n_votes']} "
          f"({no_effect['n_incoherent']} incoherent)")
    print(f"Q_M/Q_C monotonicity violations: {len(qm_qc_violations)}")
    print(f"Curve monotonicity violations: {len(curve_violations)}")
    print(f"Flat-zero curves: {len(flat_zero)}")
    print(f"Structural onset jumps: {len(onset_jumps)}")
    print(f"Genuine jump warnings: {len(curve_jump_warnings)}")


if __name__ == "__main__":
    main()