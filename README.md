# PrivacyMort

PrivacyMort is an empirically calibrated privacy risk metric based on real-world privacy incidents. It constructs privacy risk scenarios from incident data and estimates baseline and residual risk.

## Overview

The workflow consists of four main phases:

1. Corpus construction and labeling
2. Asset classification and scenario generation
3. Control-effectiveness elicitation
4. Baseline and residual risk estimation

## Data Pipeline

```text
privacyrisq_export.csv
        │
        │ Manual cleaning and filtering
        ▼
privacyrisq_cleaned.xlsx
        │
        │ scripts/label.py
        ▼
privacyrisq_labeled.xlsx
        │
        │ scripts/assets.py
        ▼
privacyrisq_assets.xlsx
        │
        │ scripts/scenarios.py
        ▼
mort_scenarios.xlsx
        │
        │ scripts/delphi_sample.py
        ▼
Delphi example scenarios
```

## Main Workflow

Run the scripts in the following order.
### 1. Data labeling

Labels the 2,037 cleaned incidents and retains 2,035 incidents with at least one detected data category.

- **Input:** `data/processed/privacyrisq_cleaned.xlsx`
- **Output:** `data/processed/privacyrisq_labeled_final.xlsx`

```bash
python scripts/label.py
```

### 2. Asset classification

Classifies incidents by technical asset, organizational context, and target type.

- **Input:** `data/processed/privacyrisq_labeled_final.xlsx`
- **Output:** `data/processed/privacyrisq_assets_final.xlsx`

```bash
python scripts/assets.py
```

### 3. Scenario construction

Constructs risk scenarios and calculates likelihood, severity, and baseline risk.

- **Input:** `data/processed/privacyrisq_assets_final.xlsx`
- **Output:** `results/mort_scenarios_final.xlsx`

```bash
python scripts/scenarios_final.py
```


## Delphi

Run the Delphi scripts from the project root.

### Scenario selection

Selects three anchor scenarios from the core scenario family using maximum variation sampling. The scenarios share the same LINDDUN and data-category characteristics but vary by technical asset type. Within each asset group, the incident containing the largest number of detected data fields is selected as the representative case.

- **Method:** Maximum Variation Sampling according to Patton (1990)
- **Input:** `data/processed/privacyrisq_assets_final.xlsx`
- **Outputs:**
  - `results/delphi_scenario_selection.csv`
  - `results/delphi_scenario_selection.txt`

```bash
python scripts/delphi_sample.py
```

### Delphi Round 1

Evaluates the first Delphi round. The ten ranked control selections are scored from 10 points for rank 1 to 1 point for rank 10. Dependency statements are normalized, parsed, and counted without weighting.

- **Input:** `scripts/que_1.xlsx`, sheet `answer`
- **Output:** `scripts/Delphi_round_1_results.md`

```bash
python scripts/delphi_1.py
```

### Delphi Round 2

Builds the final quantitative model from the second Delphi round. The analysis covers control confirmation, maturity thresholds, effectiveness estimates, consensus, dependency effects, effectiveness curves, composite dependency rules, and contextual responses.

The consensus assessment uses a predefined two-tier rule:

- At least five valid responses are required.
- Consensus is reached if the modal response band contains at least 50% of valid responses.
- Alternatively, the modal band and its strongest adjacent band must contain at least 70% of valid responses.
- Detected bimodality prevents consensus.
- Maturity level `0` is treated as a valid substantive response indicating no effect at any maturity level.

- **Input:** `scripts/que_2.xlsx`, sheet `Tabelle1`
- **Outputs:**
  - `scripts/delphi2_results.json`
  - `scripts/delphi2_results.md`

```bash
python scripts/delphi_results.builder.py
```

## Validation

Run the validation scripts from the project root.

### Corpus Validation

#### Description quality

Checks the completeness of relevant incident fields over time.

- **Input:** `data/raw/privacyrisq_export.csv`
- **Output:** `results/description_quality.xlsx`

```bash
python scripts/quality_check/description_quality.py
```

#### Keyword exploration

Identifies potentially relevant terms in incidents without a detected data category.

- **Input:** `data/processed/privacyrisq_labeled.xlsx`
- **Output:** Console output

```bash
python scripts/quality_check/explore_keywords.py
```

#### Advertising identifier patterns

Tests candidate regular expressions for advertising identifiers and displays example matches.

- **Input:** `data/processed/privacyrisq_cleaned.xlsx`
- **Output:** Console output

```bash
python scripts/quality_check/adid_pattern.py
```

#### Label precision sample

Creates a stratified sample for manually checking the precision of the data-category labels. After completing `true_label`, run the script again to calculate precision and Wilson confidence intervals.

- **Input:** `data/processed/privacyrisq_labeled_final.xlsx`
- **Output:** `scripts/quality_check/precision_sample.xlsx`

```bash
python scripts/quality_check/sampleCheck.py
```

#### Database stability

Examines source heterogeneity, LINDDUN prevalence, and scenario-ranking stability across data sources.

- **Input:** `data/processed/privacyrisq_assets_final.xlsx`
- **Output:** `scripts/quality_check/source_diagnostics.xlsx`

```bash
python scripts/quality_check/databaseStability.py
```

### Metric Validation

#### Severity-scale check

Tests whether alternative severity scales change the scenario ranking.

- **Input:** Asset-classified incident data
- **Output:** Severity-sensitivity results as an Excel file

```bash
python scripts/quality_check/severity_scale.py
```

#### Sensitivity analysis

Evaluates ranking stability across alternative scenario thresholds and severity weightings.

- **Input:** `results/mort_scenarios_final.xlsx`
- **Output:** `results/sensitivity_analysis.xlsx`
- **Additional output:** `results/severity_sens_table.tex`

```bash
python scripts/quality_check/sensitivity_analysis.py
```

#### K-fold validation

Tests the stability of the scenario ranking across five incident-level folds.

- **Input:** `data/processed/privacyrisq_assets_final.xlsx`
- **Output:** `results/kfold_validation_results.xlsx`

```bash
python scripts/quality_check/kfold_validation.py
```

### Delphi Validation

#### Delphi validation checks

Checks consensus, agreement, coherence, and monotonicity for Delphi Round 2.

- **Input:** `que_2.xlsx` and `delphi2_results.json`
- **Output:** Updated `delphi2_results.json`
- **Additional output:** `delphi2_validation_results.md`

```bash
python scripts/quality_check/delphi2_validation_checks.py
```

#### Delphi reliability

Calculates ICC(2,k) and Gwet’s AC2 for Delphi Round 2.

- **Input:** `que_2.xlsx`
- **Output:** `delphi2_reliability.md`

```bash
python scripts/quality_check/delphi2_reliability.py
```

# Dockerized Quarto Report

The research findings of this project are presented with Quarto.
If you are interested in understanding the data, the procedure, the findings, and their evaluation, make sure you have installed [Docker](https://www.docker.com/get-started/) and run:

```shell
docker compose up -d
```

This will open a web browser to view the rendered Quarto document on http://localhost:8080.

## Writing the report

While editing `quarto/story.qmd`, use the `preview` service instead. It re-renders on
every save and reloads the browser by itself:

```shell
docker compose up preview
```

The document is served on http://localhost:4200. `quarto/`, `data/` and `scripts/` are
mounted from the host, so edits take effect without rebuilding the image.

Both `preview` and `quarto` belong to the `dev` profile, so `docker compose up` on its
own starts only the `web` service above.

Notes for editing:

- Editing an imported script under `scripts/` does not retrigger a render on its own.
  Save the `.qmd` afterwards; the re-render then picks up the changed module.
- The `.qmd` extension is mandatory for documents with executable code, so the file
  cannot be renamed to `.md`. PyCharm has no Quarto plugin, but registering `*.qmd`
  under Settings → Editor → File Types → Markdown gives it Markdown editing support.

To render once without a server, writing the HTML to `_site/` on the host:

```shell
docker compose run --rm quarto
```
