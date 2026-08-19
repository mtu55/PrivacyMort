#!/usr/bin/env python3
"""
Delphi Round 1 Analysis Script

This script reads an Excel workbook with a sheet named "answer".
It evaluates:
1. Ranked Top-10 control selections using rank-based scoring:
   - Top 1 = 10 points
   - Top 2 = 9 points
   - ...
   - Top 10 = 1 point

2. Dependency statements:
   - Dependencies are counted unweighted.
   - Each dependency statement counts as one mention.

Output:
- A Markdown report file.
"""

import re
from collections import Counter, defaultdict
from pathlib import Path

import pandas as pd


# ---------------------------------------------------------------------------
# File paths
# ---------------------------------------------------------------------------

INPUT_FILE = Path(__file__).parent / "que_1.xlsx"
OUTPUT_FILE = Path(__file__).parent / "Delphi_round_1_results.md"

ANSWER_SHEET = "answer"


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

TOP_COLUMNS = [f"Top {i}" for i in range(1, 11)]

RANK_POINTS = {
    "Top 1": 10,
    "Top 2": 9,
    "Top 3": 8,
    "Top 4": 7,
    "Top 5": 6,
    "Top 6": 5,
    "Top 7": 4,
    "Top 8": 3,
    "Top 9": 2,
    "Top 10": 1,
}


# ---------------------------------------------------------------------------
# Normalization helpers
# ---------------------------------------------------------------------------

def normalize_control_code(value):
    """
    Normalize a single control code.

    Examples:
    - "8.28" -> "A8.28"
    - "A8.28" -> "A8.28"
    - " 5.34 " -> "A5.34"
    """
    if pd.isna(value):
        return None

    text = str(value).strip().upper().replace(" ", "")

    if not text:
        return None

    match = re.fullmatch(r"A?(\d+)\.(\d+)", text)
    if match:
        return f"A{match.group(1)}.{match.group(2)}"

    return text


def normalize_dependency_text(value):
    """
    Normalize a dependency statement.

    Examples:
    - "8.16->8.15" -> "A8.16->A8.15"
    - "8.15 -> 5.17" -> "A8.15->A5.17"
    - "8.11->5.12+5.34" -> "A8.11->A5.12+A5.34"
    - "5.24-5.28->8.15/8.16" -> "A5.24-A5.28->A8.15/A8.16"
    """
    if pd.isna(value):
        return None

    text = str(value).strip().upper()

    if not text:
        return None

    text = text.replace(" ", "")

    # Normalize common arrow and dash variants
    text = text.replace("→", "->")
    text = text.replace("–", "-")
    text = text.replace("—", "-")

    # Add A before plain control numbers such as 8.16 or 5.24
    text = re.sub(r"(?<![A-Z])(?<!\d)(\d+\.\d+)", r"A\1", text)

    return text


def expand_control_range(source):
    """
    Expand a control range if possible.

    Example:
    - "A5.24-A5.28" -> ["A5.24", "A5.25", "A5.26", "A5.27", "A5.28"]
    """
    source = source.strip()

    match = re.fullmatch(r"A(\d+)\.(\d+)-A(\d+)\.(\d+)", source)

    if not match:
        return [source]

    chapter_start, number_start, chapter_end, number_end = match.groups()

    if chapter_start != chapter_end:
        return [source]

    start = int(number_start)
    end = int(number_end)

    if end < start:
        return [source]

    return [f"A{chapter_start}.{i}" for i in range(start, end + 1)]


# ---------------------------------------------------------------------------
# Dependency parsing
# ---------------------------------------------------------------------------

def parse_dependency_statement(statement):
    """
    Parse one dependency statement.

    Supported examples:
    - 8.16->8.15
    - 8.15 -> 5.17
    - 8.11->5.12+5.34
    - 5.26->5.24+5.25+8.15/8.16
    - 5.24-5.28->8.15/8.16

    Returns:
    - grouped_dependency
    - atomic_edges
    - or_groups
    """
    normalized = normalize_dependency_text(statement)

    if not normalized or "->" not in normalized:
        return None, [], []

    parts = normalized.split("->")

    if len(parts) != 2:
        return None, [], []

    left = parts[0].strip()
    right = parts[1].strip()

    if not left or not right:
        return None, [], []

    sources = expand_control_range(left)

    atomic_edges = []
    or_groups = []

    required_parts = [part.strip() for part in right.split("+") if part.strip()]

    for source in sources:
        for required_part in required_parts:
            if "/" in required_part:
                alternatives = [target.strip() for target in required_part.split("/") if target.strip()]

                if len(alternatives) < 2:
                    return None, [], []

                alternatives_string = "/".join(alternatives)

                or_groups.append((source, alternatives_string))

                for target in alternatives:
                    atomic_edges.append((source, target, "OR_PART"))
            else:
                atomic_edges.append((source, required_part, "REQUIRED"))

    return normalized, atomic_edges, or_groups


def find_dependency_columns(df):
    """
    Find dependency columns.

    The first dependency column is expected to be named "Dependencies".
    All columns to the right of it are treated as dependency columns too.
    """
    columns = list(df.columns)

    dependency_start_index = None

    for index, column in enumerate(columns):
        if str(column).strip().lower() == "dependencies":
            dependency_start_index = index
            break

    if dependency_start_index is None:
        raise ValueError('Could not find a column named "Dependencies" in the answer sheet.')

    return columns[dependency_start_index:]


# ---------------------------------------------------------------------------
# Analysis
# ---------------------------------------------------------------------------

def analyze_top_controls(df):
    """
    Analyze Top 1 to Top 10 columns using rank-based scoring.
    """
    weighted_scores = defaultdict(int)
    mentions = Counter()

    missing_columns = [column for column in TOP_COLUMNS if column not in df.columns]

    if missing_columns:
        raise ValueError(f"Missing Top columns in answer sheet: {missing_columns}")

    for _, row in df.iterrows():
        for column in TOP_COLUMNS:
            control = normalize_control_code(row[column])

            if control is None:
                continue

            weighted_scores[control] += RANK_POINTS[column]
            mentions[control] += 1

    results = []

    for control in sorted(weighted_scores.keys()):
        score = weighted_scores[control]
        mention_count = mentions[control]
        average_score = score / mention_count if mention_count else 0

        results.append(
            {
                "Control": control,
                "Weighted score": score,
                "Mentions": mention_count,
                "Average rank score": round(average_score, 2),
            }
        )

    results.sort(
        key=lambda item: (
            -item["Weighted score"],
            -item["Mentions"],
            item["Control"],
    )
)

    return results


def analyze_dependencies(df):
    """
    Analyze dependency columns.
    """
    dependency_columns = find_dependency_columns(df)

    grouped_counter = Counter()
    atomic_counter = Counter()
    or_counter = Counter()

    invalid_dependencies = []

    for row_index, row in df.iterrows():
        for column in dependency_columns:
            value = row[column]

            if pd.isna(value):
                continue

            raw_statement = str(value).strip()

            if not raw_statement:
                continue

            grouped_dependency, atomic_edges, or_groups = parse_dependency_statement(raw_statement)

            if grouped_dependency is None:
                invalid_dependencies.append(
                    {
                        "Row": row_index + 2,
                        "Value": raw_statement,
                    }
                )
                continue

            grouped_counter[grouped_dependency] += 1

            for edge in atomic_edges:
                atomic_counter[edge] += 1

            for or_group in or_groups:
                or_counter[or_group] += 1

    grouped_results = [
        {
            "Dependency": dependency,
            "Frequency": frequency,
        }
        for dependency, frequency in grouped_counter.items()
    ]

    grouped_results.sort(
        key=lambda item: (
            -item["Frequency"],
            item["Dependency"],
        )
    )

    atomic_results = [
        {
            "Source": source,
            "Target": target,
            "Type": dependency_type,
            "Frequency": frequency,
        }
        for (source, target, dependency_type), frequency in atomic_counter.items()
    ]

    atomic_results.sort(
        key=lambda item: (
            -item["Frequency"],
            item["Source"],
            item["Target"],
            item["Type"],
        )
    )

    or_results = [
        {
            "Source": source,
            "Alternative targets": alternatives,
            "Frequency": frequency,
        }
        for (source, alternatives), frequency in or_counter.items()
    ]

    or_results.sort(
        key=lambda item: (
            -item["Frequency"],
            item["Source"],
            item["Alternative targets"],
        )
    )

    return grouped_results, atomic_results, or_results, invalid_dependencies


# ---------------------------------------------------------------------------
# Markdown output
# ---------------------------------------------------------------------------

def markdown_table(headers, rows):
    """
    Create a Markdown table.
    """
    if not rows:
        return "_No entries found._\n"

    lines = []

    lines.append("| " + " | ".join(headers) + " |")
    lines.append("| " + " | ".join(["---"] * len(headers)) + " |")

    for row in rows:
        formatted_row = [str(value).replace("|", "\\|") for value in row]
        lines.append("| " + " | ".join(formatted_row) + " |")

    return "\n".join(lines) + "\n"


def write_markdown_report(
        output_path,
        input_path,
        number_of_responses,
        top_control_results,
        grouped_dependency_results,
        atomic_dependency_results,
        or_dependency_results,
        invalid_dependencies,
):
    """
    Write the final Markdown report.
    """
    top_rows = []

    for rank, item in enumerate(top_control_results, start=1):
        top_rows.append(
            [
                rank,
                item["Control"],
                item["Weighted score"],
                item["Mentions"],
                item["Average rank score"],
            ]
        )

    grouped_rows = []

    for rank, item in enumerate(grouped_dependency_results, start=1):
        grouped_rows.append(
            [
                rank,
                item["Dependency"],
                item["Frequency"],
            ]
        )

    atomic_rows = []

    for rank, item in enumerate(atomic_dependency_results, start=1):
        atomic_rows.append(
            [
                rank,
                item["Source"],
                item["Target"],
                item["Type"],
                item["Frequency"],
            ]
        )

    or_rows = []

    for rank, item in enumerate(or_dependency_results, start=1):
        or_rows.append(
            [
                rank,
                item["Source"],
                item["Alternative targets"],
                item["Frequency"],
            ]
        )

    invalid_rows = []

    for item in invalid_dependencies:
        invalid_rows.append(
            [
                item["Row"],
                item["Value"],
            ]
        )

    content = f"""# Delphi Round 1 Results

## Overview

- Input file: `{input_path.name}`
- Evaluated sheet: `{ANSWER_SHEET}`
- Number of evaluated responses: {number_of_responses}
- Top-10 scoring method: rank-based scoring
  - Top 1 = 10 points
  - Top 2 = 9 points
  - Top 3 = 8 points
  - Top 4 = 7 points
  - Top 5 = 6 points
  - Top 6 = 5 points
  - Top 7 = 4 points
  - Top 8 = 3 points
  - Top 9 = 2 points
  - Top 10 = 1 point
- Dependency scoring method: unweighted frequency count

## Weighted Top Controls

{markdown_table(
        ["Rank", "Control", "Weighted score", "Mentions", "Average rank score"],
        top_rows,
    )}

## Grouped Dependency Statements

{markdown_table(
        ["Rank", "Dependency", "Frequency"],
        grouped_rows,
    )}

## Atomic Dependency Edges

{markdown_table(
        ["Rank", "Source", "Target", "Type", "Frequency"],
        atomic_rows,
    )}

## OR Dependencies

{markdown_table(
        ["Rank", "Source", "Alternative targets", "Frequency"],
        or_rows,
    )}

## Invalid or Unparsed Dependency Entries

{markdown_table(
        ["Excel row", "Raw value"],
        invalid_rows,
    )}
"""

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content, encoding="utf-8")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    if not INPUT_FILE.exists():
        raise FileNotFoundError(f"Input file does not exist: {INPUT_FILE}")

    df = pd.read_excel(INPUT_FILE, sheet_name=ANSWER_SHEET)

    number_of_responses = len(df)

    top_control_results = analyze_top_controls(df)

    (
        grouped_dependency_results,
        atomic_dependency_results,
        or_dependency_results,
        invalid_dependencies,
    ) = analyze_dependencies(df)

    write_markdown_report(
        output_path=OUTPUT_FILE,
        input_path=INPUT_FILE,
        number_of_responses=number_of_responses,
        top_control_results=top_control_results,
        grouped_dependency_results=grouped_dependency_results,
        atomic_dependency_results=atomic_dependency_results,
        or_dependency_results=or_dependency_results,
        invalid_dependencies=invalid_dependencies,
    )

    print("Analysis completed successfully.")
    print(f"Input file: {INPUT_FILE}")
    print(f"Markdown report written to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()