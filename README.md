# PrivacyMort

Empirically calibrated privacy risk metric based on 2,037 real-world privacy incidents. Derives baseline risk scores per scenario from  labeled incident data using GDPR data categories and LINDDUN threat  classifications.

---

## Data Pipeline
privacyrisq_export.csv (N = 8,464) │ │ Manual filtering (see below) ▼ privacyrisq_cleaned.xlsx (N = 2,037) │ │ scripts/label.py ▼ privacyrisq_labeled.xlsx (N = 2,037, with data category flags) │ │ scripts/scenarios.py ▼ mort_scenarios.xlsx (scenario-level baseline risk scores)

### Filtering Steps (raw → cleaned)

| Step | Action                                                                        | Remaining |
|------|-------------------------------------------------------------------------------|-----------|
| 1    | Remove GDPR enforcement/fine records (regulatory responses, not incidents)    | 3,798     |
| 2    | Remove incidents without LINDDUN mapping (not classified as privacy incident) | 3,389     |
| 3    | Remove incidents without personal data involvement (DDoS, defacements)        | 2,037     |
| 4    | Add labels following the data categories of the GDPR and remove 0             | 2,035     |

`privacyrisq_cleaned.xlsx` is the stable input for all subsequent scripts.

---

## Scripts

### `label.py`
Applies keyword-based regex labeling to classify each incident by
GDPR data category. Derives three binary flags per incident:

| Flag                     | Definition                     |
|--------------------------|--------------------------------|
| `has_personal_data`      | GDPR Art. 4(1) categories      |
| `has_special_categories` | GDPR Art. 9 categories         |
| `has_credentials`        | Authentication and access data |

Keywords use word-boundary regex (`\b`) to prevent partial matches.
Full taxonomy is documented inline in the script.

| Step | Action                                                                        | Remaining |
|------|-------------------------------------------------------------------------------|-----------|
| 4    | Add labels following the data categories of the GDPR and remove 0             | 2,035     |

**Run:**

python scripts/label.py

---
### `scenarios.py`
Constructs privacy risk scenarios as triples:
s = (AssetType, LINDDUN combination, DataCategory)

Computes per scenario:
- `count` – unique incidents
- `likelihood` – count / N (N = 2,037)
- `avg_severity` – mean severity score (1–4, GDPR-grounded)
- `baseline_risk` – likelihood × avg_severity

### `asssets.py`


**Run:**
python scripts/scenarios_combined.py

---

## Scripts for evaluation 

### `sensitivity_analysis.py`
Evaluates ranking stability across:
- Minimum incident thresholds: n >= 3, 5, 10, 15
- Severity weightings: current, exponential, compressed, flat, linear high

Reports Spearman rho for all comparisons.

**Run:**
python scripts/sensitivity_analysis.py
---

### `explore_keywords.py`
Identifies frequent data-related terms in unlabeled incidents.
Use this to iteratively extend the keyword taxonomy in `label.py`.

**Run:**
python scripts/explore_keywords.py
---

### `description_quality.py`
Measures data completeness per year across all relevant fields
(Asset Type, LINDDUN, Threat Actor, Data Protection State,
Techniques Used). Runs on the raw export.

**Run:**
python scripts/description_quality.py

---

## Requirements and installation
pip install pandas 
pip install openpyxl 
pip install scipyv



