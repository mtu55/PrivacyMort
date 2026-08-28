#!/usr/bin/env python3
"""
Delphi Round 2 - Results Builder
==================================
Input : que_2.xlsx, sheet "Tabelle1"
Output: delphi2_results.json, delphi2_results.md

Scope (final spec, agreed):
  * Only que_2.xlsx is used. No que_1.xlsx, no incident corpus.
  * Maturity scale is 0-5. Level 0 ("kein Prozess") is a VALID substantive
    category meaning "no effect at any maturity level" - see below.
  * Percentage answers are banded on half-open intervals with no gaps and
    no overlaps: [0,10], (10,25], (25,50], (50,75], (75,100].
  * Consensus rule (a priori, two-tier): >= MIN_VALID valid answers AND
    EITHER (a) the modal band alone holds >= 50 % of answers (tier 1,
    strong plurality), OR (b) the modal band plus ONE adjacent band (the
    adjacent band with the higher count) holds >= 70 % of answers (tier 2,
    broader but stricter window). A weak plurality (e.g. 36 % modal) can no
    longer reach consensus merely by padding a moderately populated
    neighbour to 50 %; it must clear 70 % across the two-band window
    instead. The earlier single-threshold rule (>= 50 % window share) is
    superseded by this two-tier rule.
  * Bimodality blocks consensus: if two peaks of >= 25 % each are separated
    by at least one strictly lower band, the panel is split and no
    consensus is claimed regardless of the window share.
  * Point estimate: if tier 1 (modal alone) is met but tier 2 is not, the
    median is restricted to the modal band only. If tier 2 is met, the
    median is restricted to the full two-band window (more conservative,
    uses more data points). If neither tier is met, the raw median of all
    valid answers is used. Ordinal items (Q_T) are rounded UP (ceil) -
    decided a priori, conservative: no effectiveness credit is granted at
    a lower maturity level when the panel is tied.
  * Q_T = 0 (panel point estimate) means "no effect at any maturity level"
    and yields a flat zero effectiveness curve.
  * Dependency type ("Art Abhaengigkeit") is descriptive only; it does NOT
    enter the gating formula. Gating uses the elicited residual
    effectiveness r_i in [0,1]:
        G_i(m_j) = 1   if prerequisite active
                 = r_i otherwise
  * Round-number anchoring (share of verbatim "50" answers) is reported for
    all percentage items, for the limitations section.
  * Minimum vs. product comparison only for composite (AND) items whose
    components were elicited individually.
  * Context items are reported descriptively (raw text frequencies).
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

# --------------------------------------------------------------------------
# Configuration
# --------------------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
INPUT_FILE = BASE_DIR / "que_2.xlsx"
SHEET = "Tabelle1"
OUTPUT_JSON = BASE_DIR / "delphi2_results.json"
OUTPUT_MD = BASE_DIR / "delphi2_results.md"

CONTROLS = ["A8.28", "A8.16", "A8.12", "A8.24", "A5.16",
            "A8.15", "A5.17", "A5.34", "A8.5", "A5.15"]

VALIDATION_SCALE = ["Ja, eindeutig", "Eher ja", "Unsicher", "Eher nein", "Nein"]

TOLERANCE = 1e-6

# ---- Maturity scale ------------------------------------------------------
# Level 0 is VALID: raters who answered 0 also answered 0 % reduction on
# both maturity anchors, i.e. "this control has no privacy effect at any
# level". Dropping it would silently discard a substantive minority vote.
LEVEL_CODES = [0, 1, 2, 3, 4, 5]
MATURITY_WORDING = {
    0: "kein Prozess / keine Wirkung auf keiner Stufe",
    1: "geplant",
    2: "teilweise umgesetzt",
    3: "umgesetzt und dokumentiert",
    4: "zusaetzlich mit Wirksamkeitspruefung",
    5: "zusaetzlich mit laufender Verbesserung",
}

# ---- Percentage bands (half-open, no gaps, no overlaps) ------------------
# [0,10] (10,25] (25,50] (50,75] (75,100]
BAND_EDGES = [10.0, 25.0, 50.0, 75.0]
BAND_LABELS = ["0-10", ">10-25", ">25-50", ">50-75", ">75-100"]

# ---- Consensus rule (two-tier, see module docstring) ---------------------
MIN_VALID = 5
MODAL_ONLY_THRESHOLD = 0.50    # tier 1: modal band alone
WINDOW_THRESHOLD = 0.70        # tier 2: modal + one adjacent band (stricter)
CONSENSUS_READING = "B"        # "A" = modal band only, "B" = modal + one adjacent band
BIMODAL_BLOCKS_CONSENSUS = True
BIMODAL_MIN_SHARE = 0.25
TENDENCY_THRESHOLD = 0.40      # for the 3-way descriptive label only

ROUND_NUMBER_MARKER = 50.0     # anchoring diagnostic, independent of consensus rule

DEPENDENCIES = [
    {"name": "A5.34 + A5.12", "dependent": "A5.34",
     "prerequisites": ["A5.12"], "kind": "atomic"},
    {"name": "A5.34 + A5.13", "dependent": "A5.34",
     "prerequisites": ["A5.13"], "kind": "atomic"},
    {"name": "A5.34 + A5.12 UND A5.13", "dependent": "A5.34",
     "prerequisites": ["A5.12", "A5.13"], "kind": "composite",
     "components": ["A5.34 + A5.12", "A5.34 + A5.13"]},
    {"name": "A5.34 + A5.17", "dependent": "A5.34",
     "prerequisites": ["A5.17"], "kind": "atomic"},
    {"name": "A5.34 + A5.26", "dependent": "A5.34",
     "prerequisites": ["A5.26"], "kind": "atomic"},
    {"name": "A8.16 + A8.15", "dependent": "A8.16",
     "prerequisites": ["A8.15"], "kind": "atomic"},
    {"name": "A8.16 + A8.15 UND A5.25", "dependent": "A8.16",
     "prerequisites": ["A8.15", "A5.25"], "kind": "composite",
     "components": ["A8.16 + A8.15"]},   # A5.25 alone never elicited
]

CONTEXT_ITEMS = [
    "Dienstleister betreibt Umgebung Einschätzung",
    "Dienstleister betreibt Umgebung Prozent",
    "Umgebung unbekannt Einschätzung",
    "DiUmgebung unbekannt  Prozent",
]

WARNINGS = []


# --------------------------------------------------------------------------
# Generic helpers
# --------------------------------------------------------------------------

def resolve_column(df, name):
    """Tolerant column lookup: exact -> whitespace-normalised -> prefix."""
    if name in df.columns:
        return name
    norm = {" ".join(str(c).split()): c for c in df.columns}
    key = " ".join(str(name).split())
    if key in norm:
        return norm[key]
    for c in df.columns:
        if str(c).startswith(str(name)[:30]):
            return c
    WARNINGS.append(f"column not found: {name}")
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
    text = str(value).strip().lower()
    return any(p in text for p in NON_ASSESSABLE_PATTERNS)


def clamp_pct(number):
    return max(0.0, min(100.0, float(number)))


def normalize_percentage(value):
    if is_blank(value) or is_non_assessable(value):
        return None
    if isinstance(value, (int, float)):
        number = float(value)
        if 0.0 < number < 1.0:
            number *= 100.0
        return clamp_pct(number)
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
    number = float(raw)
    if "." in raw and 0.0 < number <= 1.0:
        number *= 100.0
    return clamp_pct(number)


def normalize_level(value):
    """Maturity level 0..5 valid (0 = 'no effect at any level'), else None."""
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
    """Half-open bands: [0,10] (10,25] (25,50] (50,75] (75,100]."""
    value = clamp_pct(number)
    for i, upper in enumerate(BAND_EDGES):
        if value <= upper + TOLERANCE:
            return i
    return len(BAND_EDGES)


# --------------------------------------------------------------------------
# Consensus evaluation
# --------------------------------------------------------------------------

def describe(values):
    numeric = [float(v) for v in values if v is not None]
    if not numeric:
        return None
    s = pd.Series(numeric)
    return {
        "n_valid": len(numeric),
        "median": round(float(s.median()), 2),
        "iqr": round(float(s.quantile(0.75) - s.quantile(0.25)), 2),
        "min": round(float(s.min()), 1),
        "max": round(float(s.max()), 1),
    }


def detect_bimodality(freq):
    """Two peaks of >= BIMODAL_MIN_SHARE separated by a strictly lower band."""
    n = sum(freq)
    if n == 0:
        return False, ""
    peaks = [i for i, f in enumerate(freq) if f / n >= BIMODAL_MIN_SHARE]
    for a, b in combinations(peaks, 2):
        if b - a >= 2 and min(freq[a + 1:b]) < min(freq[a], freq[b]):
            return True, (f"two separate peaks >= {BIMODAL_MIN_SHARE:.0%} "
                          f"(index {a} and {b})")
    return False, ""


def classify_agreement(modal_share, window_share, n, bimodal):
    """Descriptive 3-way label, aligned with the two-tier spec_consensus
    rule: 'consensus' requires the same tier-1/tier-2 condition; 'tendency'
    is a softer, purely descriptive middle category not used for any
    quantitative decision."""
    if n < MIN_VALID:
        return "insufficient_n"
    if bimodal:
        return "dissent"
    if modal_share >= MODAL_ONLY_THRESHOLD or window_share >= WINDOW_THRESHOLD:
        return "consensus"
    if window_share >= TENDENCY_THRESHOLD:
        return "tendency"
    return "dissent"


def evaluate_consensus(raw_values, coder, labels, integer_rounding=None):
    """
    coder: raw numeric value -> band/level index.
    integer_rounding: None or "ceil" (for ordinal items such as Q_T).

    Two-tier consensus rule:
      tier 1: modal band alone holds >= MODAL_ONLY_THRESHOLD of answers.
      tier 2: modal band + best adjacent band holds >= WINDOW_THRESHOLD.
    Either tier reaching its threshold (and no bimodality) yields consensus.
    """
    numeric = [float(v) for v in raw_values if v is not None]
    n_total = len(raw_values)
    stats = describe(numeric)
    k = len(labels)

    if stats is None:
        return {
            "n_valid": 0, "n_missing": n_total, "median": None, "iqr": None,
            "modal_label": None, "modal_share": None, "window_share": None,
            "window_labels": [], "spec_consensus": False,
            "consensus_tier": None, "consensus_value": None,
            "bimodal": False, "bimodal_note": "",
            "agreement_label": "insufficient_n",
            "integer_rounding": integer_rounding,
            "modal_only_threshold": MODAL_ONLY_THRESHOLD,
            "window_threshold": WINDOW_THRESHOLD,
            "distribution": {label: 0 for label in labels},
        }

    indices = [coder(v) for v in numeric]
    counts = Counter(indices)
    freq = [counts.get(i, 0) for i in range(k)]
    n = len(indices)

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

    bimodal, bimodal_note = detect_bimodality(freq)

    tier1 = modal_share >= MODAL_ONLY_THRESHOLD
    tier2 = (window_share >= WINDOW_THRESHOLD) and (len(window) > 1)
    consensus_tier = "modal" if tier1 else ("window" if tier2 else None)

    spec_consensus = bool(
        n >= MIN_VALID
        and (tier1 or tier2)
        and not (BIMODAL_BLOCKS_CONSENSUS and bimodal)
    )

    if spec_consensus:
        # If only tier 1 is met, restrict the median to the modal band
        # alone; if tier 2 is met (with or without tier 1), use the wider,
        # more conservative two-band window.
        selection_idx = [modal_idx] if (tier1 and not tier2) else window
        selected = [v for v, i in zip(numeric, indices) if i in selection_idx]
        consensus_value = round(float(pd.Series(selected).median()), 2)
    else:
        consensus_value = None

    stats.update({
        "n_missing": n_total - n,
        "modal_label": labels[modal_idx],
        "modal_share": round(modal_share * 100.0, 1),
        "window_share": round(window_share * 100.0, 1),
        "window_labels": [labels[i] for i in window],
        "spec_consensus": spec_consensus,
        "consensus_tier": consensus_tier,
        "consensus_value": consensus_value,
        "bimodal": bimodal,
        "bimodal_note": bimodal_note,
        "agreement_label": classify_agreement(modal_share, window_share, n, bimodal),
        "integer_rounding": integer_rounding,
        "consensus_reading": CONSENSUS_READING,
        "modal_only_threshold": MODAL_ONLY_THRESHOLD,
        "window_threshold": WINDOW_THRESHOLD,
        "distribution": {labels[i]: freq[i] for i in range(k)},
    })
    return stats


def evaluate_band_consensus(values):
    return evaluate_consensus(values, band_index, BAND_LABELS)


def evaluate_level_consensus(values):
    labels = [str(m) for m in LEVEL_CODES]
    return evaluate_consensus(values, lambda v: LEVEL_CODES.index(int(round(v))),
                              labels, integer_rounding="ceil")


def point_estimate(summary):
    """Consensus value if reached, else raw median; ceil for ordinal items."""
    if summary is None or summary.get("n_valid", 0) == 0:
        return None
    if summary["spec_consensus"] and summary["consensus_value"] is not None:
        value = summary["consensus_value"]
    else:
        value = summary["median"]
    if value is None:
        return None
    if summary.get("integer_rounding") == "ceil":
        return int(math.ceil(value - TOLERANCE))
    return round(float(value), 1)


def round_number_anchoring(values):
    """Share of verbatim ROUND_NUMBER_MARKER answers (anchoring diagnostic).
    Independent of the consensus rule; retained unchanged for the
    limitations section."""
    numeric = [float(v) for v in values if v is not None]
    if not numeric:
        return {"n_valid": 0, "n_at_marker": 0, "share_pct": None,
                "marker": ROUND_NUMBER_MARKER}
    hits = sum(1 for v in numeric if abs(v - ROUND_NUMBER_MARKER) < TOLERANCE)
    return {
        "n_valid": len(numeric),
        "n_at_marker": hits,
        "share_pct": round(hits / len(numeric) * 100.0, 1),
        "marker": ROUND_NUMBER_MARKER,
    }


# --------------------------------------------------------------------------
# Reading que_2.xlsx
# --------------------------------------------------------------------------

def read_validation(df, control):
    col = resolve_column(df, control)
    return [normalize_category(v) for v in df[col]] if col else []


def read_maturity(df, control):
    col = resolve_column(df, f"Reifegrad {control}")
    return [normalize_level(v) for v in df[col]] if col else []


def read_reduction(df, control, level):
    col = resolve_column(df, f"Reduktion {level} {control}")
    return [normalize_percentage(v) for v in df[col]] if col else []


def read_dependency_type(df, name):
    col = resolve_column(df, f"Art Abhängigkeit {name}")
    if col is None:
        return []
    out = []
    for v in df[col]:
        out.append(None if is_non_assessable(v) else normalize_category(v))
    return out


def read_dependency_residual(df, name):
    col = resolve_column(df, f"Verbleibende operative Wirksamkeit {name}")
    return [normalize_percentage(v) for v in df[col]] if col else []


def read_context(df, item):
    col = resolve_column(df, item)
    return [normalize_category(v) for v in df[col]] if col else []


# --------------------------------------------------------------------------
# Control effectiveness curve
# --------------------------------------------------------------------------

def build_curve(q_t, q_m, q_c):
    """
    Piecewise-linear effectiveness curve E(m), m = 1..5.
      Q_T = 0  -> flat zero (panel: no effect at any maturity level)
      Q_T >= 3 -> effect starts exactly at m = 3, E(3) = Q_M
      otherwise linear 0 -> Q_M over [Q_T, 3], then Q_M -> Q_C over [3, 5]
    """
    if q_m is None or q_c is None:
        return None, "Q_M or Q_C missing"

    if q_t == 0:
        return ({str(m): 0.0 for m in range(1, 6)},
                "Q_T=0: panel point estimate is 'no effect at any maturity "
                "level'; curve is flat zero")

    if q_t is None:
        q_t = 3  # fallback: no measurable effect below the reference level

    q_t_note = " (Q_T >= 3 edge case: effect starts exactly at m=3)" if q_t >= 3 else ""

    clamped = q_c < q_m - TOLERANCE
    q_c_eff = max(q_c, q_m)

    curve = {}
    for m in range(1, 6):
        if m < q_t:
            value = 0.0
        elif m <= 3:
            span = 3 - q_t
            value = q_m if span <= 0 else q_m * (m - q_t) / span
        else:
            value = q_m + (q_c_eff - q_m) * (m - 3) / 2.0
        curve[str(m)] = round(clamp_pct(value), 1)

    note = ("Q_C raised to Q_M (monotonicity)" if clamped else "monotonic") + q_t_note
    return curve, note


# --------------------------------------------------------------------------
# Section builders
# --------------------------------------------------------------------------

def build_controls(df):
    controls_out = {}
    for control in CONTROLS:
        validation_vals = read_validation(df, control)
        valid_counts = Counter(v for v in validation_vals if v is not None)
        n_val = sum(valid_counts.values())
        confirm = sum(valid_counts.get(l, 0) for l in VALIDATION_SCALE[:2])
        reject = sum(valid_counts.get(l, 0) for l in VALIDATION_SCALE[3:])
        confirmation_rate = round(confirm / n_val * 100.0, 1) if n_val else None

        maturity_raw = read_maturity(df, control)
        reduction3_raw = read_reduction(df, control, 3)
        reduction5_raw = read_reduction(df, control, 5)

        n_level_zero = sum(1 for v in maturity_raw if v == 0)
        n_zero_both = sum(
            1 for a, b in zip(reduction3_raw, reduction5_raw)
            if a is not None and b is not None
            and abs(a) < TOLERANCE and abs(b) < TOLERANCE
        )

        q_t_summary = evaluate_level_consensus(maturity_raw)
        q_t_point = point_estimate(q_t_summary)

        q_m_summary = evaluate_band_consensus(reduction3_raw)
        q_c_summary = evaluate_band_consensus(reduction5_raw)
        q_m_point = point_estimate(q_m_summary)
        q_c_point = point_estimate(q_c_summary)

        curve, curve_note = build_curve(q_t_point, q_m_point, q_c_point)

        controls_out[control] = {
            "validation": {
                "distribution": dict(valid_counts),
                "n_valid": n_val,
                "n_missing": len(validation_vals) - n_val,
                "confirmation_rate_pct": confirmation_rate,
                "rejection_count": reject,
                "scale": VALIDATION_SCALE,
            },
            "q_t": {
                "point_estimate": q_t_point,
                "wording": MATURITY_WORDING.get(q_t_point),
                "consensus": q_t_summary,
                "n_level_zero_votes": n_level_zero,
                "n_zero_reduction_on_both_anchors": n_zero_both,
                "level_zero_note": "level 0 counted as a valid substantive "
                                   "category ('no effect at any maturity "
                                   "level'), not as missing data",
            },
            "q_m": {
                "point_estimate": q_m_point,
                "consensus": q_m_summary,
                "round_number_anchoring": round_number_anchoring(reduction3_raw),
            },
            "q_c": {
                "point_estimate": q_c_point,
                "consensus": q_c_summary,
                "round_number_anchoring": round_number_anchoring(reduction5_raw),
            },
            "curve_pct": curve,
            "curve_note": curve_note,
        }
    return controls_out


def build_dependencies(df, controls_out):
    deps_out = {}

    residual_raw = {item["name"]: read_dependency_residual(df, item["name"])
                    for item in DEPENDENCIES}

    for item in DEPENDENCIES:
        name = item["name"]

        type_vals_raw = read_dependency_type(df, name)
        type_vals = [v for v in type_vals_raw if v is not None]
        type_counts = dict(Counter(type_vals))

        residual_summary = evaluate_band_consensus(residual_raw[name])
        r_point = point_estimate(residual_summary)
        r_fraction = None if r_point is None else round(r_point / 100.0, 3)

        dependent = item["dependent"]
        dep_curve = controls_out.get(dependent, {}).get("curve_pct")

        gated_inactive = None
        if dep_curve is not None and r_fraction is not None:
            gated_inactive = {m: round(v * r_fraction, 1)
                              for m, v in dep_curve.items()}

        entry = {
            "dependent": dependent,
            "prerequisites": item["prerequisites"],
            "kind": item["kind"],
            "dependency_type_distribution": type_counts,
            "dependency_type_n_valid": len(type_vals),
            "dependency_type_n_missing": len(type_vals_raw) - len(type_vals),
            "dependency_type_note": (
                "descriptive only; does not enter the gating formula; "
                "non-assessable answers excluded, consistent with "
                "percentage items"
            ),
            "residual_effectiveness": {
                "point_estimate_pct": r_point,
                "consensus": residual_summary,
                "round_number_anchoring": round_number_anchoring(residual_raw[name]),
            },
            "gating_rule": "G_i(m_j)=1 if active else r_i (residual effectiveness)",
            "gated_curve_pct": {
                "prerequisite_active": dep_curve,
                "prerequisite_inactive": gated_inactive,
            },
        }

        if item["kind"] == "composite":
            entry["components"] = item["components"]
            entry["components_complete"] = (
                    all(c in residual_raw for c in item["components"])
                    and len(item["components"]) == len(item["prerequisites"])
            )

        deps_out[name] = entry

    # rule comparison for composite items with complete components
    for item in DEPENDENCIES:
        if item["kind"] != "composite":
            continue
        name = item["name"]
        entry = deps_out[name]
        if not entry.get("components_complete"):
            entry["rule_comparison"] = {
                "comparable": False,
                "reason": "not all single-prerequisite failures were elicited "
                          "individually",
            }
            continue

        obs = residual_raw[name]
        comps = [residual_raw[c] for c in item["components"]]

        min_errors, prod_errors, bound_violations, n_obs = [], [], 0, 0
        detail = []
        for i in range(len(obs)):
            o = obs[i]
            c_vals = [c[i] for c in comps]
            if o is None or any(v is None for v in c_vals):
                continue
            n_obs += 1
            minimum = min(c_vals)
            product = 100.0
            for v in c_vals:
                product *= v / 100.0
            min_errors.append(abs(o - minimum))
            prod_errors.append(abs(o - product))
            if o > minimum + TOLERANCE:
                bound_violations += 1
            detail.append({
                "components_pct": c_vals, "observed_pct": o,
                "minimum_rule_pct": round(minimum, 1),
                "product_rule_pct": round(product, 1),
            })

        if min_errors:
            mae_min = round(sum(min_errors) / len(min_errors), 1)
            mae_prod = round(sum(prod_errors) / len(prod_errors), 1)
            closer = ("minimum" if mae_min < mae_prod else
                      "product" if mae_prod < mae_min else "equivalent")
        else:
            mae_min = mae_prod = closer = None

        entry["rule_comparison"] = {
            "comparable": True, "n_observations": n_obs,
            "mae_minimum_rule": mae_min, "mae_product_rule": mae_prod,
            "closer_rule": closer, "bound_violations": bound_violations,
            "detail": detail,
        }

    return deps_out


def build_context(df):
    out = {}
    for item in CONTEXT_ITEMS:
        values = [v for v in read_context(df, item) if v is not None]
        out[item] = {
            "n_valid": len(values),
            "distribution": dict(Counter(values)),
            "note": "descriptive only, no banding or consensus rule applied "
                    "(panel consensus itself is 'not assessable in general')",
        }
    return out


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


def write_markdown(model, path):
    meta = model["meta"]
    L = ["# Delphi Round 2 - Results\n",
         f"n = {meta['n_responses']} experts, source: `{meta['source_file']}`\n",
         f"\nBands: {', '.join(BAND_LABELS)} (half-open, no gaps/overlaps). "
         f"Consensus reading: {CONSENSUS_READING}, two-tier rule "
         f"(tier 1: modal band alone >= {MODAL_ONLY_THRESHOLD:.0%}; "
         f"tier 2: modal + adjacent band >= {WINDOW_THRESHOLD:.0%}), "
         f"min n = {MIN_VALID}, "
         f"bimodality blocks consensus: {BIMODAL_BLOCKS_CONSENSUS}. "
         f"Ordinal point estimates rounded up.\n"]

    L.append("\n## Top-10 Confirmation (Round 2)\n")
    rows = [[c, d["validation"]["n_valid"],
             d["validation"]["confirmation_rate_pct"],
             d["validation"]["rejection_count"],
             d["validation"]["n_missing"]]
            for c, d in model["controls"].items()]
    L.append(md_table(["Control", "n valid", "Confirmation %", "Rejections",
                       "Missing"], rows))

    L.append("\n## Control Effectiveness Anchors\n")
    rows = []
    for c, d in model["controls"].items():
        rows.append([
            c,
            d["q_t"]["point_estimate"], d["q_t"]["consensus"]["agreement_label"],
            d["q_t"]["n_level_zero_votes"],
            d["q_m"]["point_estimate"], d["q_m"]["consensus"]["agreement_label"],
            d["q_c"]["point_estimate"], d["q_c"]["consensus"]["agreement_label"],
            "yes" if d["q_c"]["consensus"]["bimodal"] else "no",
        ])
    L.append(md_table(["Control", "Q_T", "Q_T agr.", "n(level 0)",
                       "Q_M %", "Q_M agr.", "Q_C %", "Q_C agr.",
                       "Q_C bimodal"], rows))

    L.append("\n## Round-number Anchoring (share of verbatim 50 %)\n")
    rows = []
    for c, d in model["controls"].items():
        rows.append([c,
                     f"{d['q_m']['round_number_anchoring']['n_at_marker']}/"
                     f"{d['q_m']['round_number_anchoring']['n_valid']}",
                     f"{d['q_c']['round_number_anchoring']['n_at_marker']}/"
                     f"{d['q_c']['round_number_anchoring']['n_valid']}"])
    L.append(md_table(["Control", "Q_M at 50", "Q_C at 50"], rows))

    L.append("\n## Effectiveness Curves E(m), m=1..5 (%)\n")
    rows = []
    for c, d in model["controls"].items():
        curve = d["curve_pct"] or {}
        rows.append([c] + [curve.get(str(m), "-") for m in range(1, 6)]
                    + [d["curve_note"]])
    L.append(md_table(["Control", "m1", "m2", "m3", "m4", "m5", "Note"], rows))

    L.append("\n## Dependencies\n")
    rows = []
    for name, d in model["dependencies"].items():
        r = d["residual_effectiveness"]
        rows.append([
            name, d["dependent"], " + ".join(d["prerequisites"]), d["kind"],
            r["point_estimate_pct"], r["consensus"]["agreement_label"],
            f"{r['round_number_anchoring']['n_at_marker']}/"
            f"{r['round_number_anchoring']['n_valid']}",
            ", ".join(f"{k}:{v}" for k, v in
                      d["dependency_type_distribution"].items()),
        ])
    L.append(md_table(["Item", "Dependent", "Prerequisites", "Kind",
                       "Residual %", "Agreement", "at 50",
                       "Type distribution"], rows))

    L.append("\n## Minimum vs. Product Rule (composite items)\n")
    rows = []
    for name, d in model["dependencies"].items():
        rc = d.get("rule_comparison")
        if rc is None:
            continue
        if not rc["comparable"]:
            rows.append([name, "n/a", "n/a", "n/a", rc["reason"]])
        else:
            rows.append([name, rc["n_observations"], rc["mae_minimum_rule"],
                         rc["mae_product_rule"], rc["closer_rule"]])
    L.append(md_table(["Item", "n", "MAE min rule", "MAE product rule",
                       "Closer"], rows))

    L.append("\n## Context Items (descriptive only)\n")
    rows = []
    for item, d in model["context"].items():
        for label, freq in d["distribution"].items():
            rows.append([item, label, freq])
    L.append(md_table(["Item", "Answer", "Frequency"], rows))

    if model.get("warnings"):
        L.append("\n## Warnings\n")
        for w in model["warnings"]:
            L.append(f"- {w}\n")

    path.write_text("".join(L), encoding="utf-8")


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------

def main():
    df = pd.read_excel(INPUT_FILE, sheet_name=SHEET)

    controls_out = build_controls(df)
    dependencies_out = build_dependencies(df, controls_out)
    context_out = build_context(df)

    model = {
        "meta": {
            "source_file": INPUT_FILE.name,
            "sheet": SHEET,
            "n_responses": len(df),
            "point_estimate_rule": "median inside winning window if consensus "
                                   "(modal band alone if tier 1 only, else the "
                                   "two-band window), else raw median; ordinal "
                                   "items rounded up (ceil)",
            "consensus_rule": {
                "min_valid": MIN_VALID,
                "modal_only_threshold": MODAL_ONLY_THRESHOLD,
                "window_threshold": WINDOW_THRESHOLD,
                "reading": CONSENSUS_READING,
                "window": ("modal band only" if CONSENSUS_READING == "A"
                           else "modal band + one adjacent band"),
                "description": "two-tier rule: consensus if modal band alone "
                               ">= modal_only_threshold, OR modal + adjacent "
                               "band >= window_threshold",
                "bimodality_blocks_consensus": BIMODAL_BLOCKS_CONSENSUS,
                "bimodal_min_share": BIMODAL_MIN_SHARE,
                "tendency_threshold": TENDENCY_THRESHOLD,
            },
            "bands": {"edges": BAND_EDGES, "labels": BAND_LABELS,
                      "definition": "half-open intervals, no gaps, no overlaps"},
            "maturity_scale": MATURITY_WORDING,
            "maturity_zero_treatment": "valid substantive category ('no effect "
                                       "at any maturity level'); Q_T = 0 yields "
                                       "a flat zero curve",
            "gating_rule": "G_i(m_j) = 1 if prerequisite active else r_i "
                           "(elicited residual effectiveness, NOT binary)",
        },
        "controls": controls_out,
        "dependencies": dependencies_out,
        "context": context_out,
        "warnings": WARNINGS,
    }

    OUTPUT_JSON.write_text(json.dumps(model, indent=2, ensure_ascii=False),
                           encoding="utf-8")
    write_markdown(model, OUTPUT_MD)

    print(f"written: {OUTPUT_JSON.name}, {OUTPUT_MD.name}")
    for w in WARNINGS:
        print(f"  WARNING: {w}")


if __name__ == "__main__":
    main()