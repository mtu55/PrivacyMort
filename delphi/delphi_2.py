#!/usr/bin/env python3
"""
Delphi round 2 evaluation.

Input:  que_2.xlsx, sheet "answer"
Output: delphi_2_results.md

Modelling decisions (agreed):
  * P5 rule A: prerequisites become active from maturity level >= 3.
  * Ordinal bands for percentage answers: 0-10 / 25 / 50 / 75 / 100.
  * Primary consensus criterion: 50 % of the raters in the modal band
    (4 of 7); reported together with three sensitivity variants.
  * Kendall's W is computed over atomic dependency items only, because
    composite AND items are logically derived from them.
  * Composite AND items are validated against the monotonicity bound
    residual effectiveness <= min(components).
  * Minimum rule and product rule predictions are compared via MAE.
  * Scenario blocks are reported separately from the core model.

Column mapping is derived from the workbook headers, so header typos do
not require any edit in Excel.
"""

from __future__ import annotations

import math
import re
from collections import Counter
from pathlib import Path

import pandas as pd

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
INPUT_FILE = BASE_DIR / "que_2.xlsx"
OUTPUT_FILE = BASE_DIR / "delphi_2_results.md"
ANSWER_SHEET = "Tabelle1"

MATURITY_LABELS = ["1", "2", "3", "4", "5"]

BAND_LABELS = ["0-10", "25", "50", "75", "100"]
BAND_CENTRES = [5.0, 25.0, 50.0, 75.0, 100.0]
BAND_UPPER_BOUNDS = [15.0, 37.5, 62.5, 87.5, math.inf]

CONSENSUS_VARIANTS = [
    {"label": "Consensus 50 % modal", "threshold": 0.50, "neighbours": False},
    {"label": "Consensus 50 % neighbours", "threshold": 0.50, "neighbours": True},
    {"label": "Consensus 75 % modal", "threshold": 0.75, "neighbours": False},
    {"label": "Consensus 75 % neighbours", "threshold": 0.75, "neighbours": True},
]

PREREQUISITE_MATURITY_THRESHOLD = 3
INCONSISTENCY_MATURITY_LEVEL = 3
REINTERPRETED_QT = PREREQUISITE_MATURITY_THRESHOLD - 1

CONSISTENCY_TOLERANCE = 1e-6

SCENARIO_BLOCKS = [
    {"name": "Dienstleister betreibt Umgebung", "keywords": ["dienstleister", "betreibt"]},
    {"name": "Umgebung unbekannt", "keywords": ["umgebung", "unbekannt"]},
]

CONTROL_PATTERN = re.compile(r"([A-Za-z]{0,2})\s*(\d{1,2})\.(\d{1,2})")


# ---------------------------------------------------------------------------
# Normalisation helpers
# ---------------------------------------------------------------------------

def normalize_header(text):
    """
    Normalise a header: lower case, umlauts folded, whitespace collapsed,
    known typos repaired.
    """
    if text is None:
        return ""

    value = str(text).replace("\n", " ").strip().lower()
    value = (
        value.replace("ae", "ae")
        .replace("ä", "ae")
        .replace("ö", "oe")
        .replace("ü", "ue")
        .replace("ß", "ss")
    )
    value = re.sub(r"\s+", " ", value)
    value = value.replace("wirskamkeit", "wirksamkeit")
    value = value.replace("abhaengikeit", "abhaengigkeit")
    return value


def extract_control_ids(text):
    """
    Extract control identifiers such as A5.34 from a header, preserving order.
    """
    ids = []

    for letters, major, minor in CONTROL_PATTERN.findall(str(text)):
        if int(major) == 0:
            continue

        prefix = letters.upper() if letters else "A"
        control = prefix + str(int(major)) + "." + minor

        if control not in ids:
            ids.append(control)

    return ids


def is_blank(value):
    if value is None:
        return True
    if isinstance(value, float) and math.isnan(value):
        return True
    return str(value).strip() == ""


def clamp_percentage(number):
    return max(0.0, min(100.0, float(number)))


def normalize_percentage(value):
    """
    Parse a percentage answer.

    Rules:
      * numeric cells strictly between 0 and 1 are read as shares (0.5 -> 50)
      * "0,5" -> 50, while "1" stays 1
      * ranges such as "0-10" are reduced to their midpoint
    """
    if is_blank(value):
        return None

    if isinstance(value, (int, float)):
        number = float(value)
        if 0.0 < number < 1.0:
            number = number * 100.0
        return clamp_percentage(number)

    text = str(value).strip().replace("%", " ").strip()

    range_match = re.match(
        r"^(\d+(?:[.,]\d+)?)\s*(?:-|–|bis)\s*(\d+(?:[.,]\d+)?)$", text
    )
    if range_match:
        low = float(range_match.group(1).replace(",", "."))
        high = float(range_match.group(2).replace(",", "."))
        return clamp_percentage((low + high) / 2.0)

    match = re.search(r"-?\d+(?:[.,]\d+)?", text)
    if match is None:
        return None

    raw = match.group(0).replace(",", ".")
    number = float(raw)

    if "." in raw and 0.0 < number <= 1.0:
        number = number * 100.0

    return clamp_percentage(number)


def normalize_level(value):
    """
    Parse a maturity level answer into an integer between 1 and 5.
    """
    if is_blank(value):
        return None

    if isinstance(value, (int, float)):
        number = int(round(float(value)))
        return number if 1 <= number <= 5 else None

    match = re.search(r"[1-5]", str(value))
    return int(match.group(0)) if match else None


def normalize_category(value):
    if is_blank(value):
        return None
    return re.sub(r"\s+", " ", str(value)).strip()


def band_index(number):
    for position, upper in enumerate(BAND_UPPER_BOUNDS):
        if number <= upper:
            return position
    return len(BAND_UPPER_BOUNDS) - 1


# ---------------------------------------------------------------------------
# Column mapping
# ---------------------------------------------------------------------------

def classify_columns(columns):
    """
    Assign every workbook column to a role, based on the normalised header.
    """
    mapping = {
        "maturity": {},
        "reduction_3": {},
        "reduction_5": {},
        "validation": {},
        "effectiveness": [],
        "dependency_type": {},
        "scenario": {block["name"]: {"assessment": None, "percentage": None}
                     for block in SCENARIO_BLOCKS},
        "unmapped": [],
    }

    for column in columns:
        norm = normalize_header(column)
        ids = extract_control_ids(column)

        if not norm:
            mapping["unmapped"].append(column)
            continue

        if "reifegrad" in norm and ids:
            mapping["maturity"].setdefault(ids[0], column)
            continue

        if "reduktion" in norm and ids:
            level_match = re.search(r"reduktion\s*([0-9])", norm)
            level = level_match.group(1) if level_match else None
            if level == "3":
                mapping["reduction_3"].setdefault(ids[0], column)
                continue
            if level == "5":
                mapping["reduction_5"].setdefault(ids[0], column)
                continue
            mapping["unmapped"].append(column)
            continue

        if "wirksamkeit" in norm and len(ids) >= 2:
            mapping["effectiveness"].append((column, ids))
            continue

        if len(ids) >= 2 and ("art" in norm or "typ" in norm or "abhaengigkeit" in norm):
            mapping["dependency_type"].setdefault(frozenset(ids), column)
            continue

        scenario_hit = None
        for block in SCENARIO_BLOCKS:
            if all(keyword in norm for keyword in block["keywords"]):
                scenario_hit = block["name"]
                break

        if scenario_hit is not None:
            slot = "percentage" if ("prozent" in norm or "%" in str(column)) else "assessment"
            if mapping["scenario"][scenario_hit][slot] is None:
                mapping["scenario"][scenario_hit][slot] = column
            else:
                mapping["unmapped"].append(column)
            continue

        if len(ids) == 1:
            mapping["validation"].setdefault(ids[0], column)
            continue

        mapping["unmapped"].append(column)

    return mapping


def ordered_controls(mapping):
    controls = []
    for source in ("maturity", "reduction_3", "reduction_5", "validation"):
        for control in mapping[source]:
            if control not in controls:
                controls.append(control)
    return controls


def build_dependency_items(mapping):
    """
    Derive dependency items D1..Dn from the residual effectiveness columns.

    The first control identifier in a header is the dependent control, the
    remaining identifiers are its prerequisites. Items with more than one
    prerequisite are treated as composite AND items.
    """
    items = {}

    for position, (column, ids) in enumerate(mapping["effectiveness"], start=1):
        key = "D" + str(position)
        items[key] = {
            "column": column,
            "control": ids[0],
            "prerequisites": ids[1:],
            "kind": "atomic" if len(ids[1:]) == 1 else "composite",
            "type_column": mapping["dependency_type"].get(frozenset(ids)),
            "components": [],
            "bound_complete": True,
        }

    for key, item in items.items():
        if item["kind"] != "composite":
            continue

        components = []
        for other_key, other in items.items():
            if other_key == key or other["kind"] != "atomic":
                continue
            if other["control"] != item["control"]:
                continue
            if other["prerequisites"][0] in item["prerequisites"]:
                components.append(other_key)

        item["components"] = components
        item["bound_complete"] = len(components) == len(item["prerequisites"])

    return items


# ---------------------------------------------------------------------------
# Reading
# ---------------------------------------------------------------------------

def read_matrices(df, mapping, controls, items):
    """
    Build rater x item matrices for all answer groups.
    """
    rater_labels = ["R" + str(position) for position in range(1, len(df) + 1)]
    excel_rows = [position + 2 for position in range(len(df))]

    matrices = {
        "validation": pd.DataFrame(index=rater_labels, columns=controls, dtype="object"),
        "maturity": pd.DataFrame(index=rater_labels, columns=controls, dtype="object"),
        "reduction_3": pd.DataFrame(index=rater_labels, columns=controls, dtype="object"),
        "reduction_5": pd.DataFrame(index=rater_labels, columns=controls, dtype="object"),
        "dependency": pd.DataFrame(index=rater_labels, columns=list(items), dtype="object"),
        "dependency_type": pd.DataFrame(index=rater_labels, columns=list(items), dtype="object"),
    }

    unparsed = []

    def record(row_number, field, value):
        unparsed.append({"Row": row_number, "Field": field, "Value": str(value).strip()})

    for position, (_, row) in enumerate(df.iterrows()):
        rater = rater_labels[position]
        excel_row = excel_rows[position]

        for control in controls:
            column = mapping["validation"].get(control)
            if column is not None:
                matrices["validation"].at[rater, control] = normalize_category(row[column])

            column = mapping["maturity"].get(control)
            if column is not None:
                parsed = normalize_level(row[column])
                matrices["maturity"].at[rater, control] = parsed
                if parsed is None and not is_blank(row[column]):
                    record(excel_row, "Reifegrad " + control, row[column])

            for key, source in (("reduction_3", mapping["reduction_3"]),
                                ("reduction_5", mapping["reduction_5"])):
                column = source.get(control)
                if column is None:
                    continue
                parsed = normalize_percentage(row[column])
                matrices[key].at[rater, control] = parsed
                if parsed is None and not is_blank(row[column]):
                    record(excel_row, key + " " + control, row[column])

        for key, item in items.items():
            parsed = normalize_percentage(row[item["column"]])
            matrices["dependency"].at[rater, key] = parsed
            if parsed is None and not is_blank(row[item["column"]]):
                record(excel_row, key + " residual effectiveness", row[item["column"]])

            if item["type_column"] is not None:
                matrices["dependency_type"].at[rater, key] = normalize_category(
                    row[item["type_column"]]
                )

    return matrices, unparsed, rater_labels


def read_scenarios(df, mapping, rater_labels):
    scenarios = []

    for block in SCENARIO_BLOCKS:
        columns = mapping["scenario"][block["name"]]
        assessments = []
        percentages = []

        for _, row in df.iterrows():
            if columns["assessment"] is None:
                assessments.append(None)
            else:
                assessments.append(normalize_category(row[columns["assessment"]]))

            if columns["percentage"] is None:
                percentages.append(None)
            else:
                percentages.append(normalize_percentage(row[columns["percentage"]]))

        scenarios.append(
            {
                "name": block["name"],
                "assessments": pd.Series(assessments, index=rater_labels, dtype="object"),
                "percentages": pd.Series(percentages, index=rater_labels, dtype="object"),
            }
        )

    return scenarios


# ---------------------------------------------------------------------------
# Statistics
# ---------------------------------------------------------------------------

def describe_values(values):
    numeric = [float(value) for value in values if value is not None]

    if not numeric:
        return None

    series = pd.Series(numeric)
    q1 = series.quantile(0.25)
    q3 = series.quantile(0.75)

    return {
        "n": len(numeric),
        "Median": round(float(series.median()), 1),
        "IQR": round(float(q3 - q1), 1),
        "Min": round(float(series.min()), 1),
        "Max": round(float(series.max()), 1),
    }


def consensus_core(numeric, indices, labels):
    stats = describe_values(numeric)

    if stats is None:
        return None

    total = len(indices)
    counts = Counter(indices)
    modal_index = max(counts.items(), key=lambda entry: (entry[1], -entry[0]))[0]
    modal_count = counts[modal_index]
    neighbour_count = (
            modal_count + counts.get(modal_index - 1, 0) + counts.get(modal_index + 1, 0)
    )

    modal_share = modal_count / total
    neighbour_share = neighbour_count / total

    flags = []
    for variant in CONSENSUS_VARIANTS:
        share = neighbour_share if variant["neighbours"] else modal_share
        flags.append("yes" if share >= variant["threshold"] else "no")

    stats.update(
        {
            "Modal band": labels[modal_index],
            "Modal share": str(round(modal_share * 100.0, 1)) + " %",
            "Neighbour share": str(round(neighbour_share * 100.0, 1)) + " %",
            "Flags": flags,
        }
    )

    return stats


def evaluate_band_consensus(values):
    numeric = [float(value) for value in values if value is not None]
    if not numeric:
        return None
    return consensus_core(numeric, [band_index(value) for value in numeric], BAND_LABELS)


def evaluate_level_consensus(values):
    numeric = [float(value) for value in values if value is not None]
    if not numeric:
        return None
    return consensus_core(numeric, [int(value) - 1 for value in numeric], MATURITY_LABELS)


def summary_row(label, extra, summary):
    if summary is None:
        return [label] + list(extra) + [0] + ["n/a"] * 7 + ["n/a"] * len(CONSENSUS_VARIANTS)

    return (
            [label]
            + list(extra)
            + [
                summary["n"],
                summary["Median"],
                summary["IQR"],
                summary["Min"],
                summary["Max"],
                summary["Modal band"],
                summary["Modal share"],
                summary["Neighbour share"],
            ]
            + summary["Flags"]
    )


def kendalls_w(matrix):
    """
    Kendall's W with correction for ties, computed over complete raters only.
    """
    complete = matrix.dropna(axis=0, how="any")
    raters, items = complete.shape

    if raters < 2 or items < 2:
        return None

    ranks = complete.rank(axis=1, method="average")
    column_sums = ranks.sum(axis=0)
    mean_sum = column_sums.mean()
    deviation_sum = float(((column_sums - mean_sum) ** 2).sum())

    tie_correction = 0.0
    for _, row in ranks.iterrows():
        counts = Counter(row.values)
        tie_correction += sum(count ** 3 - count for count in counts.values())

    denominator = (raters ** 2) * (items ** 3 - items) - raters * tie_correction

    if denominator <= 0:
        return None

    w = 12.0 * deviation_sum / denominator
    excluded = [label for label in matrix.index if label not in complete.index]

    return {
        "Raters used": raters,
        "Items used": items,
        "Excluded raters": ", ".join(excluded) if excluded else "none",
        "W": round(w, 3),
        "Chi square": round(raters * (items - 1) * w, 2),
        "Degrees of freedom": items - 1,
    }


# ---------------------------------------------------------------------------
# Section builders
# ---------------------------------------------------------------------------

def frequency_rows(label, values):
    present = [value for value in values if value is not None]
    missing = len(values) - len(present)

    if not present:
        return [[label, "no valid answer", 0, missing]]

    counts = Counter(present)
    rows = []
    for answer, frequency in sorted(counts.items(), key=lambda entry: (-entry[1], entry[0])):
        rows.append([label, answer, frequency, missing])

    return rows


def build_mapping_section(mapping, controls, items):
    rows = []

    for control in controls:
        rows.append(["Validation", control, mapping["validation"].get(control, "not found")])
        rows.append(["Maturity", control, mapping["maturity"].get(control, "not found")])
        rows.append(["Reduction level 3", control, mapping["reduction_3"].get(control, "not found")])
        rows.append(["Reduction level 5", control, mapping["reduction_5"].get(control, "not found")])

    for key, item in items.items():
        rows.append(["Residual effectiveness", key, item["column"]])
        rows.append(["Dependency type", key, item["type_column"] or "not found"])

    for block in SCENARIO_BLOCKS:
        columns = mapping["scenario"][block["name"]]
        rows.append(["Scenario assessment", block["name"], columns["assessment"] or "not found"])
        rows.append(["Scenario percentage", block["name"], columns["percentage"] or "not found"])

    return rows


def build_item_overview_section(items):
    rows = []

    for key, item in items.items():
        rows.append(
            [
                key,
                item["control"],
                " and ".join(item["prerequisites"]),
                item["kind"],
                ", ".join(item["components"]) if item["components"] else "-",
                "complete" if item["bound_complete"] else "partial",
            ]
        )

    return rows


def build_validation_section(matrices, controls):
    rows = []
    for control in controls:
        rows.extend(frequency_rows(control, list(matrices["validation"][control])))
    return rows


def build_maturity_section(matrices, controls):
    rows = []
    for control in controls:
        summary = evaluate_level_consensus(list(matrices["maturity"][control]))
        rows.append(summary_row(control, [], summary))
    return rows


def derive_qt(maturity, reduction_at_level_3):
    if maturity is None:
        return None, None

    literal = maturity - 1

    reinterpreted = (
            maturity >= INCONSISTENCY_MATURITY_LEVEL
            and reduction_at_level_3 is not None
            and reduction_at_level_3 > 0.0
    )

    return literal, (REINTERPRETED_QT if reinterpreted else literal)


def build_qt_sections(matrices, controls):
    qt_rows = []
    inconsistency_rows = []

    for control in controls:
        literal_values = []
        main_values = []

        for rater in matrices["maturity"].index:
            maturity = matrices["maturity"].at[rater, control]
            reduction = matrices["reduction_3"].at[rater, control]

            literal, main = derive_qt(maturity, reduction)

            if literal is None:
                continue

            literal_values.append(literal)
            main_values.append(main)

            if literal != main:
                inconsistency_rows.append(
                    [
                        rater,
                        control,
                        maturity,
                        "n/a" if reduction is None else str(round(reduction)) + " %",
                        literal,
                        main,
                    ]
                )

        literal_summary = describe_values(literal_values)
        main_summary = describe_values(main_values)

        if literal_summary is None or main_summary is None:
            qt_rows.append([control, "n/a", "n/a", "n/a"])
            continue

        difference = round(main_summary["Median"] - literal_summary["Median"], 1)
        qt_rows.append([control, main_summary["Median"], literal_summary["Median"], difference])

    return qt_rows, inconsistency_rows


def build_reduction_section(matrices, controls, key):
    rows = []
    for control in controls:
        summary = evaluate_band_consensus(list(matrices[key][control]))
        rows.append(summary_row(control, [], summary))
    return rows


def build_reduction_monotonicity_section(matrices, controls):
    rows = []

    for rater in matrices["reduction_3"].index:
        for control in controls:
            level_3 = matrices["reduction_3"].at[rater, control]
            level_5 = matrices["reduction_5"].at[rater, control]

            if level_3 is None or level_5 is None:
                continue

            if level_5 + CONSISTENCY_TOLERANCE < level_3:
                rows.append(
                    [
                        rater,
                        control,
                        str(round(level_3)) + " %",
                        str(round(level_5)) + " %",
                        "violation",
                        ]
                )

    return rows


def build_dependency_section(matrices, items):
    rows = []

    for key, item in items.items():
        summary = evaluate_band_consensus(list(matrices["dependency"][key]))
        extra = [item["control"], " and ".join(item["prerequisites"]), item["kind"]]
        rows.append(summary_row(key, extra, summary))

    return rows


def build_dependency_type_section(matrices, items):
    rows = []
    for key in items:
        rows.extend(frequency_rows(key, list(matrices["dependency_type"][key])))
    return rows


def build_concordance_section(matrices, atomic_items):
    if len(atomic_items) < 2:
        return [["n/a", len(atomic_items), "n/a", "n/a", "n/a", "n/a"]]

    numeric = matrices["dependency"][atomic_items].apply(pd.to_numeric, errors="coerce")
    result = kendalls_w(numeric)

    if result is None:
        return [["n/a", len(atomic_items), "n/a", "n/a", "n/a", "n/a"]]

    return [
        [
            result["Raters used"],
            result["Items used"],
            result["Excluded raters"],
            result["W"],
            result["Chi square"],
            result["Degrees of freedom"],
        ]
    ]


def build_composite_sections(matrices, items, composite_items):
    consistency_rows = []
    rule_rows = []
    minimum_errors = []
    product_errors = []

    for key in composite_items:
        item = items[key]
        bound_label = "complete" if item["bound_complete"] else "partial"
        prerequisites = " and ".join(item["prerequisites"])

        for rater in matrices["dependency"].index:
            observed = matrices["dependency"].at[rater, key]
            component_values = [
                matrices["dependency"].at[rater, component] for component in item["components"]
            ]

            if observed is None or not component_values:
                continue
            if any(value is None for value in component_values):
                continue

            upper_bound = min(component_values)
            status = "ok" if observed <= upper_bound + CONSISTENCY_TOLERANCE else "violation"

            consistency_rows.append(
                [
                    key,
                    prerequisites,
                    rater,
                    ", ".join(str(round(value)) + " %" for value in component_values),
                    str(round(upper_bound)) + " %",
                    str(round(observed)) + " %",
                    bound_label,
                    status,
                    ]
            )

            if len(component_values) < 2:
                continue

            minimum_prediction = upper_bound
            product_prediction = 100.0
            for value in component_values:
                product_prediction = product_prediction * (value / 100.0)

            error_minimum = abs(observed - minimum_prediction)
            error_product = abs(observed - product_prediction)

            minimum_errors.append(error_minimum)
            product_errors.append(error_product)

            rule_rows.append(
                [
                    key,
                    rater,
                    str(round(observed)) + " %",
                    str(round(minimum_prediction)) + " %",
                    str(round(product_prediction)) + " %",
                    round(error_minimum, 1),
                    round(error_product, 1),
                    ]
            )

    if minimum_errors:
        summary_rows = [
            [
                len(minimum_errors),
                round(sum(minimum_errors) / len(minimum_errors), 1),
                round(sum(product_errors) / len(product_errors), 1),
            ]
        ]
    else:
        summary_rows = [[0, "n/a", "n/a"]]

    return consistency_rows, rule_rows, summary_rows


def build_scenario_sections(scenarios):
    assessment_rows = []
    percentage_rows = []

    for scenario in scenarios:
        assessment_rows.extend(frequency_rows(scenario["name"], list(scenario["assessments"])))
        summary = evaluate_band_consensus(list(scenario["percentages"]))
        percentage_rows.append(summary_row(scenario["name"], [], summary))

    return assessment_rows, percentage_rows


def build_unparsed_section(unparsed):
    return [[entry["Row"], entry["Field"], entry["Value"]] for entry in unparsed]


# ---------------------------------------------------------------------------
# Markdown output
# ---------------------------------------------------------------------------

def markdown_table(headers, rows):
    if not rows:
        rows = [["no entries"] + [""] * (len(headers) - 1)]

    lines = [
        "| " + " | ".join(str(header) for header in headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
        ]

    for row in rows:
        cells = ["" if cell is None else str(cell) for cell in row]
        lines.append("| " + " | ".join(cells) + " |")

    return "\n".join(lines) + "\n"


def write_markdown_report(output_path, input_path, number_of_responses, sections, meta):
    consensus_headers = [
                            "n",
                            "Median",
                            "IQR",
                            "Min",
                            "Max",
                            "Modal band",
                            "Modal share",
                            "Neighbour share",
                        ] + [variant["label"] for variant in CONSENSUS_VARIANTS]

    parts = []

    def add_heading(text, level=2):
        parts.append("#" * level + " " + text + "\n")

    def add_text(text):
        parts.append(text + "\n")

    def add_table(headers, rows):
        parts.append(markdown_table(headers, rows))

    add_heading("Delphi Round 2 Results", level=1)

    add_heading("Overview")
    add_text(
        "\n".join(
            [
                "- Input file: `" + input_path.name + "`",
                "- Evaluated sheet: `" + ANSWER_SHEET + "`",
                "- Number of evaluated responses: " + str(number_of_responses),
                "- Controls detected: " + ", ".join(meta["controls"]),
                "- Ordinal bands: " + " / ".join(BAND_LABELS),
                "- Primary consensus criterion: " + CONSENSUS_VARIANTS[0]["label"],
                "- Prerequisite activation threshold (P5, rule A): maturity level "
                + str(PREREQUISITE_MATURITY_THRESHOLD),
                "- Atomic dependency items: " + (", ".join(meta["atomic_items"]) or "none"),
                "- Composite dependency items: " + (", ".join(meta["composite_items"]) or "none"),
                "- Q_T main reading: answers with maturity level >= "
                + str(INCONSISTENCY_MATURITY_LEVEL)
                + " and a positive reduction at level 3 are reinterpreted as Q_T = "
                + str(REINTERPRETED_QT),
                "- Q_T literal reading: Q_T = answer - 1 for all answers",
                ]
        )
    )

    add_heading("Column Mapping")
    add_text(
        "The mapping is derived from the workbook headers. Please verify that every "
        "row below points to the intended column."
    )
    add_table(["Role", "Control or item", "Workbook column"], sections["mapping"])

    add_heading("Unmapped Columns", level=3)
    add_table(["Workbook column"], sections["unmapped_columns"])

    add_heading("Dependency Item Definitions")
    add_table(
        ["Item", "Control", "Prerequisites", "Kind", "Components", "Bound"],
        sections["items"],
    )

    add_heading("Validation of the Round 1 Top 10")
    add_table(["Control", "Answer", "Frequency", "Missing"], sections["validation"])

    add_heading("Maturity Onset Answers")
    add_table(["Control"] + consensus_headers, sections["maturity"])

    add_heading("Derived Q_T Values")
    add_table(
        ["Control", "Median Q_T main", "Median Q_T literal", "Difference"],
        sections["qt"],
    )

    add_heading("Inconsistent Maturity and Reduction Combinations", level=3)
    add_table(
        ["Rater", "Control", "Maturity answer", "Reduction at level 3",
         "Q_T literal", "Q_T main"],
        sections["inconsistencies"],
    )

    add_heading("Risk Reduction at Maturity Level 3")
    add_table(["Control"] + consensus_headers, sections["reduction_3"])

    add_heading("Risk Reduction at Maturity Level 5")
    add_table(["Control"] + consensus_headers, sections["reduction_5"])

    add_heading("Monotonicity Violations between Level 3 and Level 5", level=3)
    add_table(
        ["Rater", "Control", "Reduction at level 3", "Reduction at level 5", "Status"],
        sections["reduction_monotonicity"],
    )

    add_heading("Residual Effectiveness per Dependency Item")
    add_table(
        ["Item", "Control", "Prerequisites", "Kind"] + consensus_headers,
        sections["dependency"],
        )

    add_heading("Reported Dependency Types")
    add_text(
        "The two transfer options were presented as a single answer option in the "
        "questionnaire. The categories are therefore reported as elicited and are "
        "not separated further."
    )
    add_table(["Item", "Answer", "Frequency", "Missing"], sections["dependency_types"])

    add_heading("Concordance over Atomic Dependency Items")
    add_text(
        "Kendall's W is computed over the atomic items only, because composite AND "
        "items are logically derived from them."
    )
    add_table(
        ["Raters used", "Items used", "Excluded raters", "W", "Chi square",
         "Degrees of freedom"],
        sections["concordance"],
    )

    add_heading("Consistency Check for Composite AND Items")
    add_text(
        "The residual effectiveness of a combined prerequisite loss must not exceed "
        "the minimum of its parts. Where a prerequisite was not elicited "
        "individually, the bound is only partial."
    )
    add_table(
        ["Item", "Prerequisites", "Rater", "Components", "Upper bound", "Observed",
         "Bound", "Status"],
        sections["composite_consistency"],
    )

    add_heading("Aggregation Rule Comparison")
    add_table(
        ["Item", "Rater", "Observed", "Minimum rule", "Product rule",
         "Error minimum", "Error product"],
        sections["rules"],
    )

    add_heading("Aggregation Rule Summary", level=3)
    add_table(["Comparisons", "MAE minimum rule", "MAE product rule"], sections["rule_summary"])

    add_heading("Scenario Analysis")
    add_text(
        "The following results describe context variants and are reported separately "
        "from the core model."
    )

    add_heading("Qualitative Assessments", level=3)
    add_table(["Scenario", "Answer", "Frequency", "Missing"], sections["scenario_assessments"])

    add_heading("Quantitative Assessments", level=3)
    add_table(["Scenario"] + consensus_headers, sections["scenario_percentages"])

    add_heading("Invalid or Unparsed Entries")
    add_table(["Excel row", "Field", "Raw value"], sections["unparsed"])

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(parts), encoding="utf-8")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    if not INPUT_FILE.exists():
        raise FileNotFoundError("Input file not found: " + str(INPUT_FILE))

    df = pd.read_excel(INPUT_FILE, sheet_name=ANSWER_SHEET)
    df = df.dropna(axis=0, how="all")

    mapping = classify_columns(list(df.columns))
    controls = ordered_controls(mapping)
    items = build_dependency_items(mapping)

    atomic_items = [key for key, item in items.items() if item["kind"] == "atomic"]
    composite_items = [key for key, item in items.items() if item["kind"] == "composite"]

    matrices, unparsed, rater_labels = read_matrices(df, mapping, controls, items)
    scenarios = read_scenarios(df, mapping, rater_labels)

    qt_rows, inconsistency_rows = build_qt_sections(matrices, controls)
    composite_rows, rule_rows, rule_summary_rows = build_composite_sections(
        matrices, items, composite_items
    )
    scenario_assessment_rows, scenario_percentage_rows = build_scenario_sections(scenarios)

    sections = {
        "mapping": build_mapping_section(mapping, controls, items),
        "unmapped_columns": [[column] for column in mapping["unmapped"]],
        "items": build_item_overview_section(items),
        "validation": build_validation_section(matrices, controls),
        "maturity": build_maturity_section(matrices, controls),
        "qt": qt_rows,
        "inconsistencies": inconsistency_rows,
        "reduction_3": build_reduction_section(matrices, controls, "reduction_3"),
        "reduction_5": build_reduction_section(matrices, controls, "reduction_5"),
        "reduction_monotonicity": build_reduction_monotonicity_section(matrices, controls),
        "dependency": build_dependency_section(matrices, items),
        "dependency_types": build_dependency_type_section(matrices, items),
        "concordance": build_concordance_section(matrices, atomic_items),
        "composite_consistency": composite_rows,
        "rules": rule_rows,
        "rule_summary": rule_summary_rows,
        "scenario_assessments": scenario_assessment_rows,
        "scenario_percentages": scenario_percentage_rows,
        "unparsed": build_unparsed_section(unparsed),
    }

    meta = {
        "controls": controls,
        "atomic_items": atomic_items,
        "composite_items": composite_items,
    }

    write_markdown_report(OUTPUT_FILE, INPUT_FILE, len(df), sections, meta)

    print("Report written to: " + str(OUTPUT_FILE))
    print("Responses evaluated: " + str(len(df)))
    print("Controls detected: " + str(len(controls)))
    print("Dependency items detected: " + str(len(items))
          + " (atomic " + str(len(atomic_items))
          + ", composite " + str(len(composite_items)) + ")")
    print("Unmapped columns: " + str(len(mapping["unmapped"])))
    print("Unparsed entries: " + str(len(unparsed)))


if __name__ == "__main__":
    main()