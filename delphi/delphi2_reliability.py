#!/usr/bin/env python3
"""
Standard reliability analysis for Delphi Round 2.

Input:
    que_2.xlsx, sheet "Tabelle1"

Output:
    standard_reliability.md

Methods:
    - ICC(2,k) / ICC(A,k):
      Pingouin, two-way random effects, absolute agreement,
      average measures.

    - Gwet's AC2:
      Five pre-defined ordinal percentage bands with quadratic
      agreement weights:
          w_ij = 1 - ((i - j) / (K - 1))^2

      AC2 is calculated as:
          AC2 = (P_o - P_e) / (1 - P_e)

      where:
          P_e = sum_ij w_ij * p_i * (1 - p_j) / (K - 1)

Notes:
    - Q_T is retained for descriptive ICC reporting only.
    - Q_T is not included in AC2 because level 0 is a substantive
      "no effect at any maturity level" category rather than merely
      the lowest ordinal maturity level.
    - Only one Markdown file is written; no JSON or CSV files are created.
"""

from __future__ import annotations

import numbers
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import pingouin as pg


# ---------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent

INPUT_FILE = BASE_DIR / "que_2.xlsx"
SHEET_NAME = "Tabelle1"
OUTPUT_MD = BASE_DIR / "delphi2_reliability.md"

CONTROLS = [
    "A8.28", "A8.16", "A8.12", "A8.24", "A5.16",
    "A8.15", "A5.17", "A5.34", "A8.5", "A5.15",
]

DEPENDENCY_NAMES = [
    "A5.34 + A5.12",
    "A5.34 + A5.13",
    "A5.34 + A5.12 UND A5.13",
    "A5.34 + A5.17",
    "A5.34 + A5.26",
    "A8.16 + A8.15",
    "A8.16 + A8.15 UND A5.25",
]

BAND_LABELS = [
    "[0,10]",
    "(10,25]",
    "(25,50]",
    "(50,75]",
    "(75,100]",
]

N_CATEGORIES = len(BAND_LABELS)
TOLERANCE = 1e-6

N_BOOTSTRAP = 10_000
BOOTSTRAP_SEED = 20260826

NON_ASSESSABLE_PATTERNS = [
    "nicht pauschal",
    "nicht beurteilbar",
    "nicht bewertbar",
    "kann ich nicht",
    "keine angabe",
    "keine aussage",
    "weiss nicht",
    "weiß nicht",
    "unklar",
    "n/a",
    "k.a.",
]


# ---------------------------------------------------------------------
# Parsing helpers
# ---------------------------------------------------------------------

def is_blank(value) -> bool:
    """Return True for empty spreadsheet cells."""
    if value is None:
        return True

    try:
        missing = pd.isna(value)
        if isinstance(missing, (bool, np.bool_)) and missing:
            return True
    except (TypeError, ValueError):
        pass

    return str(value).strip() == ""


def is_non_assessable(value) -> bool:
    """Return True for textual non-assessable responses."""
    if is_blank(value):
        return False

    text = str(value).strip().lower()

    return any(
        pattern in text
        for pattern in NON_ASSESSABLE_PATTERNS
    )


def resolve_column(df: pd.DataFrame, wanted: str) -> str:
    """
    Resolve spreadsheet columns robustly.

    Order:
    1. Exact match
    2. Whitespace-normalised match
    3. Unique prefix match
    """
    if wanted in df.columns:
        return wanted

    def normalise(text: str) -> str:
        return " ".join(str(text).split())

    wanted_norm = normalise(wanted)

    exact_normalised = {
        normalise(column): column
        for column in df.columns
    }

    if wanted_norm in exact_normalised:
        return exact_normalised[wanted_norm]

    matches = [
        column
        for column in df.columns
        if normalise(column).startswith(wanted_norm)
    ]

    if len(matches) == 1:
        return matches[0]

    if len(matches) > 1:
        raise KeyError(
            f"Ambiguous column lookup for '{wanted}'. "
            f"Possible matches: {matches}"
        )

    raise KeyError(f"Column not found: {wanted}")


def normalize_percentage(value) -> float | None:
    """
    Convert values to percentages in [0,100].

    Examples:
        50       -> 50.0
        0.50     -> 50.0
        "50 %"   -> 50.0
        "25-50"  -> 37.5
    """
    if is_blank(value) or is_non_assessable(value):
        return None

    if isinstance(value, numbers.Real) and not isinstance(value, bool):
        number = float(value)

    else:
        text = str(value).strip().lower().replace("%", " ")

        range_match = re.match(
            r"^(\d+(?:[.,]\d+)?)\s*(?:-|–|bis)\s*(\d+(?:[.,]\d+)?)$",
            text,
        )

        if range_match:
            low = float(range_match.group(1).replace(",", "."))
            high = float(range_match.group(2).replace(",", "."))
            number = (low + high) / 2.0

        else:
            number_match = re.search(
                r"-?\d+(?:[.,]\d+)?",
                text,
            )

            if number_match is None:
                return None

            number = float(
                number_match.group(0).replace(",", ".")
            )

    if not np.isfinite(number):
        return None

    # Excel percentage cells may be stored as 0.50 for 50 %.
    if 0.0 < number < 1.0:
        number *= 100.0

    return float(np.clip(number, 0.0, 100.0))


def normalize_level(value) -> float | None:
    """
    Parse maturity levels 0--5.

    Level 0 remains valid because it represents:
    "no effect at any maturity level".
    """
    if is_blank(value) or is_non_assessable(value):
        return None

    if isinstance(value, numbers.Real) and not isinstance(value, bool):
        level = int(round(float(value)))

    else:
        match = re.search(r"-?\d+", str(value))

        if match is None:
            return None

        level = int(match.group(0))

    if level in range(0, 6):
        return float(level)

    return None


def percentage_to_band(value: float | None) -> float:
    """
    Map percentages to ordinal codes.

    0 = [0,10]
    1 = (10,25]
    2 = (25,50]
    3 = (50,75]
    4 = (75,100]
    """
    if value is None or pd.isna(value):
        return np.nan

    if value <= 10.0 + TOLERANCE:
        return 0.0

    if value <= 25.0 + TOLERANCE:
        return 1.0

    if value <= 50.0 + TOLERANCE:
        return 2.0

    if value <= 75.0 + TOLERANCE:
        return 3.0

    return 4.0


def band_definition_selftest() -> dict:
    """Verify boundary handling for the five pre-defined bands."""
    probes = {
        0.0: 0,
        10.0: 0,
        10.1: 1,
        25.0: 1,
        25.1: 2,
        50.0: 2,
        50.1: 3,
        75.0: 3,
        75.1: 4,
        100.0: 4,
    }

    failures = []

    for value, expected in probes.items():
        observed = percentage_to_band(value)

        if observed != expected:
            failures.append(
                f"{value}: expected {expected}, observed {observed}"
            )

    return {
        "passed": len(failures) == 0,
        "failures": failures,
    }


# ---------------------------------------------------------------------
# Matrix construction
# ---------------------------------------------------------------------

def build_matrix(
        df: pd.DataFrame,
        targets: list[str],
        column_prefix: str,
        parser,
) -> pd.DataFrame:
    """
    Build a target-by-rater matrix.

    Rows:
        Controls or dependency items.

    Columns:
        Delphi participants.
    """
    values = {}

    for target in targets:
        column = resolve_column(df, f"{column_prefix}{target}")

        values[target] = [
            parser(value)
            for value in df[column]
        ]

    matrix = pd.DataFrame(
        values,
        index=[f"expert_{i + 1}" for i in range(len(df))],
        dtype=float,
    ).T

    matrix.index.name = "target"
    matrix.columns.name = "rater"

    return matrix


def complete_case_targets(
        matrix: pd.DataFrame,
) -> tuple[pd.DataFrame, list[str]]:
    """
    Retain only targets with ratings from every rater.

    This creates a balanced target-by-rater matrix for both ICC
    and AC2 calculations.
    """
    complete_mask = matrix.notna().all(axis=1)

    complete = matrix.loc[complete_mask].copy()
    dropped = matrix.index[~complete_mask].tolist()

    return complete, dropped


def matrix_summary(
        label: str,
        matrix: pd.DataFrame,
) -> dict:
    """Summarise matrix completeness."""
    return {
        "label": label,
        "n_targets": int(matrix.shape[0]),
        "n_raters": int(matrix.shape[1]),
        "n_total_cells": int(matrix.shape[0] * matrix.shape[1]),
        "n_valid_cells": int(matrix.notna().sum().sum()),
        "n_missing_cells": int(matrix.isna().sum().sum()),
        "n_complete_targets": int(
            matrix.notna().all(axis=1).sum()
        ),
    }


# ---------------------------------------------------------------------
# ICC(2,k): Pingouin
# ---------------------------------------------------------------------

def extract_ci(ci_value) -> tuple[float | None, float | None]:
    """Extract a two-element 95 % CI from Pingouin output."""
    if ci_value is None:
        return None, None

    if isinstance(ci_value, (list, tuple, np.ndarray, pd.Series)):
        if len(ci_value) >= 2:
            return float(ci_value[0]), float(ci_value[1])

    try:
        array = np.asarray(ci_value, dtype=float).ravel()

        if len(array) >= 2:
            return float(array[0]), float(array[1])

    except (TypeError, ValueError):
        pass

    matches = re.findall(
        r"-?\d+(?:\.\d+)?",
        str(ci_value),
    )

    if len(matches) >= 2:
        return float(matches[0]), float(matches[1])

    return None, None


def find_ci_column(result: pd.DataFrame) -> str | None:
    """Find Pingouin's confidence-interval column robustly."""
    for column in result.columns:
        normalised = re.sub(
            r"[^a-z0-9]",
            "",
            str(column).lower(),
        )

        if normalised.startswith("ci95"):
            return column

    return None


def select_icc2k_row(result: pd.DataFrame) -> pd.Series:
    """
    Select ICC(2,k), which Pingouin may label either as ICC2k
    or ICC(A,k), depending on the installed version.
    """
    if "Type" not in result.columns:
        raise RuntimeError(
            "Pingouin returned no 'Type' column.\n\n"
            f"Returned output:\n{result.to_string(index=False)}"
        )

    type_key = (
        result["Type"]
        .astype(str)
        .str.casefold()
        .str.replace(r"[^a-z0-9]", "", regex=True)
    )

    # Accept both older and newer Pingouin labels:
    # ICC2k    -> icc2k
    # ICC(A,k) -> iccak
    candidates = result.loc[
        type_key.isin({"icc2k", "iccak"})
    ]

    if len(candidates) != 1:
        visible_columns = [
            column
            for column in ["Type", "Description", "ICC", "CI95%"]
            if column in result.columns
        ]

        raise RuntimeError(
            "Could not uniquely identify ICC(2,k) / ICC(A,k) "
            "in Pingouin output.\n\n"
            f"Available rows:\n"
            f"{result[visible_columns].to_string(index=False)}"
        )

    return candidates.iloc[0]


def calculate_icc2k(
        matrix: pd.DataFrame,
        anchor: str,
) -> dict:
    """
    Calculate ICC(2,k) / ICC(A,k).

    Pingouin's ICC2k corresponds to:
        - two-way random effects,
        - absolute agreement,
        - average measures.
    """
    complete, dropped_targets = complete_case_targets(matrix)

    if complete.shape[0] < 2:
        raise ValueError(
            f"Too few complete targets for ICC(2,k): {anchor}"
        )

    complete = complete.copy()
    complete.index.name = "target"

    long_df = (
        complete.reset_index()
        .melt(
            id_vars="target",
            var_name="rater",
            value_name="rating",
        )
    )

    result = pg.intraclass_corr(
        data=long_df,
        targets="target",
        raters="rater",
        ratings="rating",
    )

    row = select_icc2k_row(result)

    ci_column = find_ci_column(result)
    ci_lower, ci_upper = extract_ci(
        row[ci_column] if ci_column is not None else None
    )

    return {
        "anchor": anchor,
        "measure": "ICC(2,k) / ICC(A,k)",
        "estimate": float(row["ICC"]),
        "ci_lower": ci_lower,
        "ci_upper": ci_upper,
        "pingouin_type": str(row.get("Type", "")),
        "description": str(row.get("Description", "")),
        "n_targets": int(complete.shape[0]),
        "k_raters": int(complete.shape[1]),
        "dropped_targets_missingness": dropped_targets,
    }


# ---------------------------------------------------------------------
# Gwet's AC2: quadratic ordinal weighting
# ---------------------------------------------------------------------

def quadratic_weights(
        n_categories: int,
) -> np.ndarray:
    """
    Quadratic agreement weights.

    Exact agreement = 1.
    Maximum category distance = 0.
    """
    categories = np.arange(n_categories)

    return 1.0 - (
            (
                    categories[:, None]
                    - categories[None, :]
            )
            / (n_categories - 1)
    ) ** 2


def ac2_from_complete_matrix(
        complete: pd.DataFrame,
        n_categories: int = N_CATEGORIES,
) -> dict:
    """
    Calculate weighted Gwet's AC2 for a complete matrix.

    The matrix must contain ordinal category codes 0--K-1 and no
    missing values.
    """
    if complete.shape[0] < 2 or complete.shape[1] < 2:
        raise ValueError(
            "At least two targets and two raters are required for AC2."
        )

    values = complete.to_numpy(dtype=float)

    if not np.isfinite(values).all():
        raise ValueError(
            "AC2 requires a complete matrix after filtering."
        )

    codes = np.rint(values).astype(int)

    if not np.allclose(values, codes, atol=TOLERANCE):
        raise ValueError(
            "AC2 input contains non-integer category codes."
        )

    if np.any(codes < 0) or np.any(codes >= n_categories):
        raise ValueError(
            "AC2 input contains category codes outside 0..K-1."
        )

    n_targets, n_raters = codes.shape
    weights = quadratic_weights(n_categories)

    total_weighted_pairs = 0.0
    category_counts = np.zeros(n_categories, dtype=float)

    for ratings in codes:
        counts = np.bincount(
            ratings,
            minlength=n_categories,
        ).astype(float)

        category_counts += counts

        # counts @ W @ counts includes self-comparisons.
        # Each self-comparison has weight 1 and must be removed.
        weighted_pairs = (
                counts @ weights @ counts
                - n_raters
        )

        total_weighted_pairs += weighted_pairs

    observed_agreement = total_weighted_pairs / (
            n_targets * n_raters * (n_raters - 1)
    )

    category_proportions = category_counts / (
            n_targets * n_raters
    )

    chance_agreement = np.sum(
        weights
        * np.outer(
            category_proportions,
            1.0 - category_proportions,
            )
    ) / (n_categories - 1)

    if abs(1.0 - chance_agreement) < TOLERANCE:
        raise ValueError(
            "AC2 is undefined because expected agreement is 1."
        )

    ac2 = (
                  observed_agreement - chance_agreement
          ) / (
                  1.0 - chance_agreement
          )

    return {
        "ac2": float(ac2),
        "observed_agreement": float(observed_agreement),
        "chance_agreement": float(chance_agreement),
        "category_proportions": category_proportions,
        "n_targets": int(n_targets),
        "k_raters": int(n_raters),
        "n_valid_ratings": int(n_targets * n_raters),
    }


def bootstrap_ac2_ci(
        complete: pd.DataFrame,
        n_categories: int,
        n_bootstrap: int,
        seed: int,
) -> tuple[float | None, float | None, int]:
    """
    Target-level non-parametric percentile bootstrap CI for AC2.

    This is supplementary descriptive uncertainty reporting.
    """
    if complete.shape[0] < 2:
        return None, None, 0

    rng = np.random.default_rng(seed)
    estimates = []

    for _ in range(n_bootstrap):
        indices = rng.integers(
            low=0,
            high=len(complete),
            size=len(complete),
        )

        sample = complete.iloc[indices]

        try:
            estimate = ac2_from_complete_matrix(
                sample,
                n_categories=n_categories,
            )["ac2"]

            if np.isfinite(estimate):
                estimates.append(estimate)

        except ValueError:
            continue

    if len(estimates) < 100:
        return None, None, len(estimates)

    ci_lower, ci_upper = np.quantile(
        estimates,
        [0.025, 0.975],
    )

    return float(ci_lower), float(ci_upper), len(estimates)


def calculate_ac2(
        matrix: pd.DataFrame,
        anchor: str,
        seed: int,
) -> dict:
    """
    Calculate Gwet's AC2 after complete-target filtering.

    Complete-target filtering is used so every retained target has the
    same number of raters.
    """
    complete, dropped_targets = complete_case_targets(matrix)

    result = ac2_from_complete_matrix(
        complete,
        n_categories=N_CATEGORIES,
    )

    ci_lower, ci_upper, n_bootstrap_valid = bootstrap_ac2_ci(
        complete,
        n_categories=N_CATEGORIES,
        n_bootstrap=N_BOOTSTRAP,
        seed=seed,
    )

    return {
        "anchor": anchor,
        "measure": "Gwet's AC2",
        "weights": "quadratic ordinal weights",
        "ac2": result["ac2"],
        "ci_lower": ci_lower,
        "ci_upper": ci_upper,
        "ci_method": (
            f"target-level percentile bootstrap "
            f"({N_BOOTSTRAP} resamples)"
        ),
        "n_bootstrap_valid": n_bootstrap_valid,
        "observed_agreement": result["observed_agreement"],
        "chance_agreement": result["chance_agreement"],
        "n_targets": result["n_targets"],
        "k_raters": result["k_raters"],
        "n_valid_ratings": result["n_valid_ratings"],
        "dropped_targets_missingness": dropped_targets,
        "category_proportions": {
            BAND_LABELS[i]: float(
                result["category_proportions"][i]
            )
            for i in range(N_CATEGORIES)
        },
    }


def ac2_selftest() -> dict:
    """Basic internal check: perfect agreement must yield AC2 = 1."""
    failures = []

    weights = quadratic_weights(N_CATEGORIES)

    if not np.allclose(weights, weights.T):
        failures.append("Quadratic weight matrix is not symmetric.")

    if not np.allclose(np.diag(weights), 1.0):
        failures.append(
            "Quadratic weight matrix diagonal is not equal to 1."
        )

    if np.any(weights < -TOLERANCE) or np.any(weights > 1.0 + TOLERANCE):
        failures.append(
            "Quadratic weights lie outside the expected [0,1] range."
        )

    perfect = pd.DataFrame(
        [
            [0, 0, 0, 0],
            [2, 2, 2, 2],
            [4, 4, 4, 4],
        ],
        index=["target_1", "target_2", "target_3"],
        columns=["rater_1", "rater_2", "rater_3", "rater_4"],
    )

    perfect_ac2 = ac2_from_complete_matrix(
        perfect,
        n_categories=N_CATEGORIES,
    )["ac2"]

    if not np.isclose(perfect_ac2, 1.0, atol=TOLERANCE):
        failures.append(
            f"Perfect agreement returned AC2={perfect_ac2}, not 1.0."
        )

    return {
        "passed": len(failures) == 0,
        "perfect_agreement_ac2": float(perfect_ac2),
        "failures": failures,
    }


# ---------------------------------------------------------------------
# Markdown helpers
# ---------------------------------------------------------------------

def format_number(
        value,
        decimals: int = 3,
) -> str:
    """Format scalar values safely for Markdown."""
    if value is None:
        return "—"

    try:
        if pd.isna(value):
            return "—"
    except (TypeError, ValueError):
        pass

    if isinstance(value, numbers.Real) and not isinstance(value, bool):
        value = float(value)

        if abs(value - round(value)) < TOLERANCE:
            return str(int(round(value)))

        return f"{value:.{decimals}f}"

    return str(value)


def format_ci(
        lower: float | None,
        upper: float | None,
) -> str:
    """Format a confidence interval."""
    if lower is None or upper is None:
        return "—"

    return (
        f"[{format_number(lower)}, "
        f"{format_number(upper)}]"
    )


def format_dropped(
        dropped: list[str],
) -> str:
    """Format dropped target names."""
    if not dropped:
        return "none"

    return ", ".join(dropped)


def escape_markdown(value) -> str:
    """Escape basic Markdown table characters."""
    return str(value).replace("|", r"\|").replace("\n", "<br>")


def markdown_table(
        headers: list[str],
        rows: list[list],
) -> str:
    """Create a Markdown table."""
    lines = [
        "| " + " | ".join(
            escape_markdown(header)
            for header in headers
        ) + " |",
        "|" + "|".join("---" for _ in headers) + "|",
        ]

    for row in rows:
        lines.append(
            "| " + " | ".join(
                escape_markdown(cell)
                for cell in row
            ) + " |"
        )

    return "\n".join(lines)


def raw_matrix_rows(
        matrix: pd.DataFrame,
) -> list[list[str]]:
    """Render a raw numeric target-by-rater matrix."""
    rows = []

    for target, row in matrix.iterrows():
        rows.append(
            [str(target)]
            + [
                format_number(value, decimals=1)
                for value in row
            ]
        )

    return rows


def band_matrix_rows(
        matrix: pd.DataFrame,
) -> list[list[str]]:
    """Render AC2 band codes as readable interval labels."""
    rows = []

    for target, row in matrix.iterrows():
        converted = []

        for value in row:
            if pd.isna(value):
                converted.append("—")
            else:
                converted.append(
                    BAND_LABELS[int(round(float(value)))]
                )

        rows.append([str(target), *converted])

    return rows


def append_matrix(
        lines: list[str],
        heading: str,
        matrix: pd.DataFrame,
        rows: list[list[str]],
) -> None:
    """Append one matrix table to the Markdown report."""
    lines.extend(
        [
            f"### {heading}",
            "",
            markdown_table(
                ["Target", *matrix.columns.tolist()],
                rows,
            ),
            "",
        ]
    )


# ---------------------------------------------------------------------
# Markdown report
# ---------------------------------------------------------------------

def write_markdown_report(
        path: Path,
        icc_results: list[dict],
        ac2_results: list[dict],
        matrices: dict[str, pd.DataFrame],
        band_matrices: dict[str, pd.DataFrame],
        band_test: dict,
        ac2_test: dict,
) -> None:
    """Write the complete analysis into one Markdown file."""
    generated_at = datetime.now(timezone.utc).strftime(
        "%Y-%m-%d %H:%M:%S UTC"
    )

    input_summaries = [
        matrix_summary(label, matrix)
        for label, matrix in matrices.items()
    ]

    lines = [
        "# Delphi Round 2: Standard Reliability Analysis",
        "",
        f"Generated: {generated_at}",
        "",
        "## Scope and Methods",
        "",
        f"- Source file: `{INPUT_FILE.name}`",
        f"- Sheet: `{SHEET_NAME}`",
        f"- Python: `{sys.version.split()[0]}`",
        f"- pandas: `{pd.__version__}`",
        f"- NumPy: `{np.__version__}`",
        f"- Pingouin: `{getattr(pg, '__version__', 'unknown')}`",
        "",
        "### ICC",
        "",
        "ICC(2,k), also denoted ICC(A,k), is calculated with "
        "`pingouin.intraclass_corr()` using a two-way random-effects "
        "model, absolute agreement, and average measures.",
        "",
        "`Q_T` is included only as a descriptive numeric ICC result. "
        "It is an ordinal maturity threshold and category 0 has the "
        "special substantive meaning \"no effect at any maturity level.\"",
        "",
        "### Gwet's AC2",
        "",
        "AC2 is calculated for the five pre-defined ordinal percentage "
        "bands using quadratic agreement weights:",
        "",
        "- `[0,10]`",
        "- `(10,25]`",
        "- `(25,50]`",
        "- `(50,75]`",
        "- `(75,100]`",
        "",
        "The AC2 analyses use complete target-by-rater rows only. "
        "Targets containing missing ratings are reported explicitly and "
        "excluded only from the respective AC2 calculation.",
        "",
        "## Internal Checks",
        "",
        markdown_table(
            ["Check", "Status", "Detail"],
            [
                [
                    "Band-boundary self-test",
                    "passed" if band_test["passed"] else "failed",
                    (
                        "All boundary values map to the intended band."
                        if band_test["passed"]
                        else "; ".join(band_test["failures"])
                    ),
                ],
                [
                    "AC2 implementation self-test",
                    "passed" if ac2_test["passed"] else "failed",
                    (
                        "Perfect agreement produced "
                        f"AC2 = {format_number(ac2_test['perfect_agreement_ac2'])}."
                        if ac2_test["passed"]
                        else "; ".join(ac2_test["failures"])
                    ),
                ],
            ],
        ),
        "",
        "## Input Completeness",
        "",
        markdown_table(
            [
                "Matrix",
                "Targets",
                "Raters",
                "Valid cells",
                "Missing cells",
                "Complete targets",
            ],
            [
                [
                    result["label"],
                    result["n_targets"],
                    result["n_raters"],
                    result["n_valid_cells"],
                    result["n_missing_cells"],
                    result["n_complete_targets"],
                ]
                for result in input_summaries
            ],
        ),
        "",
        "## ICC(2,k) / ICC(A,k) Results",
        "",
        markdown_table(
            [
                "Anchor",
                "ICC",
                "95% CI",
                "Targets",
                "Raters",
                "Dropped targets",
                "Pingouin type",
            ],
            [
                [
                    result["anchor"],
                    format_number(result["estimate"]),
                    format_ci(
                        result["ci_lower"],
                        result["ci_upper"],
                    ),
                    result["n_targets"],
                    result["k_raters"],
                    format_dropped(
                        result["dropped_targets_missingness"]
                    ),
                    result["pingouin_type"],
                ]
                for result in icc_results
            ],
        ),
        "",
        "## Gwet's AC2 Results",
        "",
        markdown_table(
            [
                "Measure",
                "AC2",
                "Bootstrap 95% CI",
                "P_o",
                "P_e",
                "Targets",
                "Raters",
                "Dropped targets",
            ],
            [
                [
                    result["anchor"],
                    format_number(result["ac2"]),
                    format_ci(
                        result["ci_lower"],
                        result["ci_upper"],
                    ),
                    format_number(result["observed_agreement"]),
                    format_number(result["chance_agreement"]),
                    result["n_targets"],
                    result["k_raters"],
                    format_dropped(
                        result["dropped_targets_missingness"]
                    ),
                ]
                for result in ac2_results
            ],
        ),
        "",
        "The AC2 confidence intervals are target-level percentile "
        f"bootstrap intervals based on {N_BOOTSTRAP} resamples and are "
        "reported as supplementary descriptive uncertainty estimates.",
        "",
        "## Category Proportions Used for AC2",
        "",
        markdown_table(
            [
                "Band",
                *[
                    result["anchor"]
                    for result in ac2_results
                ],
            ],
            [
                [
                    band,
                    *[
                        format_number(
                            result["category_proportions"][band]
                        )
                        for result in ac2_results
                    ],
                ]
                for band in BAND_LABELS
            ],
        ),
        "",
        "## Interpretation Notes",
        "",
        "- `Q_M` and `Q_C` ICC values are based on raw percentage estimates.",
        "- AC2 is based on the five a-priori percentage bands, not raw percentages.",
        "- `Q_T` is not included in the AC2 analysis because its zero category is semantically distinct.",
        "- No p-values are reported for ICC or AC2 in this file.",
        "- The Markdown appendix below contains the exact matrices used for the analyses.",
        "",
        "## Appendix A: Raw ICC Input Matrices",
        "",
    ]

    append_matrix(
        lines,
        "Q_T: Maturity Threshold",
        matrices["Q_T"],
        raw_matrix_rows(matrices["Q_T"]),
    )

    append_matrix(
        lines,
        "Q_M: Reduction at Maturity Level 3 (%)",
        matrices["Q_M"],
        raw_matrix_rows(matrices["Q_M"]),
    )

    append_matrix(
        lines,
        "Q_C: Reduction at Maturity Level 5 (%)",
        matrices["Q_C"],
        raw_matrix_rows(matrices["Q_C"]),
    )

    lines.extend(
        [
            "## Appendix B: Banded AC2 Input Matrices",
            "",
        ]
    )

    append_matrix(
        lines,
        "Q_M Bands",
        band_matrices["Q_M"],
        band_matrix_rows(band_matrices["Q_M"]),
    )

    append_matrix(
        lines,
        "Q_C Bands",
        band_matrices["Q_C"],
        band_matrix_rows(band_matrices["Q_C"]),
    )

    append_matrix(
        lines,
        "Residual Effectiveness Bands",
        band_matrices["Residual effectiveness"],
        band_matrix_rows(
            band_matrices["Residual effectiveness"]
        ),
    )

    path.write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8",
        )


# ---------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------

def main() -> None:
    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Input file not found: {INPUT_FILE}"
        )

    band_test = band_definition_selftest()
    ac2_test = ac2_selftest()

    if not band_test["passed"]:
        raise RuntimeError(
            "Band-definition self-test failed:\n"
            + "\n".join(band_test["failures"])
        )

    if not ac2_test["passed"]:
        raise RuntimeError(
            "AC2 implementation self-test failed:\n"
            + "\n".join(ac2_test["failures"])
        )

    df = pd.read_excel(
        INPUT_FILE,
        sheet_name=SHEET_NAME,
    )

    # Raw matrices for ICC.
    q_t = build_matrix(
        df=df,
        targets=CONTROLS,
        column_prefix="Reifegrad ",
        parser=normalize_level,
    )

    q_m = build_matrix(
        df=df,
        targets=CONTROLS,
        column_prefix="Reduktion 3 ",
        parser=normalize_percentage,
    )

    q_c = build_matrix(
        df=df,
        targets=CONTROLS,
        column_prefix="Reduktion 5 ",
        parser=normalize_percentage,
    )

    residual = build_matrix(
        df=df,
        targets=DEPENDENCY_NAMES,
        column_prefix="Verbleibende operative Wirksamkeit ",
        parser=normalize_percentage,
    )

    # Banded matrices for AC2.
    q_m_bands = q_m.apply(
        lambda column: column.map(percentage_to_band)
    )

    q_c_bands = q_c.apply(
        lambda column: column.map(percentage_to_band)
    )

    residual_bands = residual.apply(
        lambda column: column.map(percentage_to_band)
    )

    # ICC(2,k).
    icc_results = [
        calculate_icc2k(
            q_t,
            "Q_T (ordinal; descriptive only)",
        ),
        calculate_icc2k(
            q_m,
            "Q_M (raw percentage estimates)",
        ),
        calculate_icc2k(
            q_c,
            "Q_C (raw percentage estimates)",
        ),
    ]

    # Gwet's AC2.
    ac2_results = [
        calculate_ac2(
            q_m_bands,
            "Q_M (five ordinal percentage bands)",
            seed=BOOTSTRAP_SEED,
        ),
        calculate_ac2(
            q_c_bands,
            "Q_C (five ordinal percentage bands)",
            seed=BOOTSTRAP_SEED + 1,
        ),
        calculate_ac2(
            residual_bands,
            "Residual effectiveness (five ordinal percentage bands)",
            seed=BOOTSTRAP_SEED + 2,
        ),
    ]

    matrices = {
        "Q_T": q_t,
        "Q_M": q_m,
        "Q_C": q_c,
        "Residual effectiveness": residual,
    }

    band_matrices = {
        "Q_M": q_m_bands,
        "Q_C": q_c_bands,
        "Residual effectiveness": residual_bands,
    }

    write_markdown_report(
        path=OUTPUT_MD,
        icc_results=icc_results,
        ac2_results=ac2_results,
        matrices=matrices,
        band_matrices=band_matrices,
        band_test=band_test,
        ac2_test=ac2_test,
    )

    print(f"Markdown report written to: {OUTPUT_MD}")
    print("\nICC(2,k):")

    for result in icc_results:
        print(
            f"  {result['anchor']}: "
            f"{result['estimate']:.3f} "
            f"{format_ci(result['ci_lower'], result['ci_upper'])}"
        )

    print("\nGwet's AC2:")

    for result in ac2_results:
        print(
            f"  {result['anchor']}: "
            f"{result['ac2']:.3f} "
            f"{format_ci(result['ci_lower'], result['ci_upper'])}"
        )


if __name__ == "__main__":
    main()