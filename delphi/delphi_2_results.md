# Delphi Round 2 Results

## Overview

- Input file: `que_2.xlsx`
- Evaluated sheet: `Tabelle1`
- Number of evaluated responses: 11
- Controls detected: A8.28, A8.16, A8.12, A8.24, A5.16, A8.15, A5.17, A5.34, A8.5, A5.15
- Ordinal bands: 0-10 / 25 / 50 / 75 / 100
- Primary consensus criterion: Consensus 50 % modal
- Prerequisite activation threshold (P5, rule A): maturity level 3
- Atomic dependency items: D1, D2, D4, D5, D6
- Composite dependency items: D3, D7
- Q_T main reading: answers with maturity level >= 3 and a positive reduction at level 3 are reinterpreted as Q_T = 2
- Q_T literal reading: Q_T = answer - 1 for all answers

## Column Mapping

The mapping is derived from the workbook headers. Please verify that every row below points to the intended column.

| Role | Control or item | Workbook column |
| --- | --- | --- |
| Validation | A8.28 | A8.28 |
| Maturity | A8.28 | Reifegrad A8.28 |
| Reduction level 3 | A8.28 | Reduktion 3 A8.28 |
| Reduction level 5 | A8.28 | Reduktion 5 A8.28 |
| Validation | A8.16 | A8.16 |
| Maturity | A8.16 | Reifegrad A8.16 |
| Reduction level 3 | A8.16 | Reduktion 3 A8.16 |
| Reduction level 5 | A8.16 | Reduktion 5 A8.16 |
| Validation | A8.12 | A8.12 |
| Maturity | A8.12 | Reifegrad A8.12 |
| Reduction level 3 | A8.12 | Reduktion 3 A8.12 |
| Reduction level 5 | A8.12 | Reduktion 5 A8.12 |
| Validation | A8.24 | A8.24 |
| Maturity | A8.24 | Reifegrad A8.24 |
| Reduction level 3 | A8.24 | Reduktion 3 A8.24 |
| Reduction level 5 | A8.24 | Reduktion 5 A8.24 |
| Validation | A5.16 | A5.16 |
| Maturity | A5.16 | Reifegrad A5.16 |
| Reduction level 3 | A5.16 | Reduktion 3 A5.16 |
| Reduction level 5 | A5.16 | Reduktion 5 A5.16 |
| Validation | A8.15 | A8.15 |
| Maturity | A8.15 | Reifegrad A8.15 |
| Reduction level 3 | A8.15 | Reduktion 3 A8.15 |
| Reduction level 5 | A8.15 | Reduktion 5 A8.15 |
| Validation | A5.17 | A5.17 |
| Maturity | A5.17 | Reifegrad A5.17 |
| Reduction level 3 | A5.17 | Reduktion 3 A5.17 |
| Reduction level 5 | A5.17 | Reduktion 5 A5.17 |
| Validation | A5.34 | A5.34 |
| Maturity | A5.34 | Reifegrad A5.34 |
| Reduction level 3 | A5.34 | Reduktion 3 A5.34 |
| Reduction level 5 | A5.34 | Reduktion 5 A5.34 |
| Validation | A8.5 | A8.5 |
| Maturity | A8.5 | Reifegrad A8.5 |
| Reduction level 3 | A8.5 | Reduktion 3 A8.5 |
| Reduction level 5 | A8.5 | Reduktion 5 A8.5 |
| Validation | A5.15 | A5.15 |
| Maturity | A5.15 | Reifegrad A5.15 |
| Reduction level 3 | A5.15 | Reduktion 3 A5.15 |
| Reduction level 5 | A5.15 | Reduktion 5 A5.15 |
| Residual effectiveness | D1 | Verbleibende operative Wirskamkeit A5.34 + A5.12 |
| Dependency type | D1 | Art Abhängigkeit A5.34 + A5.12 |
| Residual effectiveness | D2 | Verbleibende operative Wirskamkeit A5.34 + A5.13 |
| Dependency type | D2 | Art Abhängigkeit A5.34 + A5.13 |
| Residual effectiveness | D3 | Verbleibende operative Wirskamkeit A5.34 + A5.12 UND A5.13 |
| Dependency type | D3 | Art Abhängigkeit A5.34 + A5.12 UND A5.13 |
| Residual effectiveness | D4 | Verbleibende operative Wirskamkeit A5.34 + A5.17 |
| Dependency type | D4 | Art Abhängigkeit A5.34 + A5.17 |
| Residual effectiveness | D5 | Verbleibende operative Wirskamkeit A5.34 + A5.26 |
| Dependency type | D5 | Art Abhängigkeit A5.34 + A5.26 |
| Residual effectiveness | D6 | Verbleibende operative Wirskamkeit A8.16 + A8.15 |
| Dependency type | D6 | Art Abhängigkeit A8.16 + A8.15 |
| Residual effectiveness | D7 | Verbleibende operative Wirskamkeit A8.16 + A8.15 UND A5.25 |
| Dependency type | D7 | Art Abhängigkeit A8.16 + A8.15 UND A5.25 |
| Scenario assessment | Dienstleister betreibt Umgebung | Dienstleister betreibt Umgebung Einschätzung |
| Scenario percentage | Dienstleister betreibt Umgebung | Dienstleister betreibt Umgebung Prozent |
| Scenario assessment | Umgebung unbekannt | Umgebung unbekannt Einschätzung |
| Scenario percentage | Umgebung unbekannt | DiUmgebung unbekannt  Prozent |

### Unmapped Columns

| Workbook column |
| --- |
| Id |

## Dependency Item Definitions

| Item | Control | Prerequisites | Kind | Components | Bound |
| --- | --- | --- | --- | --- | --- |
| D1 | A5.34 | A5.12 | atomic | - | complete |
| D2 | A5.34 | A5.13 | atomic | - | complete |
| D3 | A5.34 | A5.12 and A5.13 | composite | D1, D2 | complete |
| D4 | A5.34 | A5.17 | atomic | - | complete |
| D5 | A5.34 | A5.26 | atomic | - | complete |
| D6 | A8.16 | A8.15 | atomic | - | complete |
| D7 | A8.16 | A8.15 and A5.25 | composite | D6 | partial |

## Validation of the Round 1 Top 10

| Control | Answer | Frequency | Missing |
| --- | --- | --- | --- |
| A8.28 | Ja, eindeutig | 7 | 4 |
| A8.16 | Ja, eindeutig | 6 | 4 |
| A8.16 | Eher ja | 1 | 4 |
| A8.12 | Ja, eindeutig | 7 | 4 |
| A8.24 | Ja, eindeutig | 6 | 4 |
| A8.24 | Eher ja | 1 | 4 |
| A5.16 | Ja, eindeutig | 7 | 4 |
| A8.15 | Ja, eindeutig | 6 | 4 |
| A8.15 | Eher ja | 1 | 4 |
| A5.17 | Ja, eindeutig | 7 | 4 |
| A5.34 | Ja, eindeutig | 7 | 4 |
| A8.5 | Ja, eindeutig | 7 | 4 |
| A5.15 | Ja, eindeutig | 6 | 4 |
| A5.15 | Eher ja | 1 | 4 |

## Maturity Onset Answers

| Control | n | Median | IQR | Min | Max | Modal band | Modal share | Neighbour share | Consensus 50 % modal | Consensus 50 % neighbours | Consensus 75 % modal | Consensus 75 % neighbours |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A8.28 | 7 | 3.0 | 1.0 | 2.0 | 4.0 | 2 | 42.9 % | 85.7 % | no | yes | no | yes |
| A8.16 | 6 | 2.0 | 0.8 | 2.0 | 4.0 | 2 | 66.7 % | 83.3 % | yes | yes | no | yes |
| A8.12 | 7 | 3.0 | 0.5 | 2.0 | 3.0 | 3 | 71.4 % | 100.0 % | yes | yes | no | yes |
| A8.24 | 7 | 2.0 | 1.0 | 2.0 | 3.0 | 2 | 57.1 % | 100.0 % | yes | yes | no | yes |
| A5.16 | 7 | 3.0 | 1.0 | 2.0 | 4.0 | 2 | 42.9 % | 85.7 % | no | yes | no | yes |
| A8.15 | 6 | 2.5 | 1.0 | 2.0 | 4.0 | 2 | 50.0 % | 83.3 % | yes | yes | no | yes |
| A5.17 | 7 | 2.0 | 1.0 | 2.0 | 4.0 | 2 | 57.1 % | 85.7 % | yes | yes | no | yes |
| A5.34 | 7 | 3.0 | 1.5 | 2.0 | 4.0 | 4 | 42.9 % | 71.4 % | no | yes | no | no |
| A8.5 | 7 | 3.0 | 1.0 | 2.0 | 3.0 | 3 | 57.1 % | 100.0 % | yes | yes | no | yes |
| A5.15 | 7 | 3.0 | 1.0 | 2.0 | 3.0 | 3 | 57.1 % | 100.0 % | yes | yes | no | yes |

## Derived Q_T Values

| Control | Median Q_T main | Median Q_T literal | Difference |
| --- | --- | --- | --- |
| A8.28 | 2.0 | 2.0 | 0.0 |
| A8.16 | 1.0 | 1.0 | 0.0 |
| A8.12 | 2.0 | 2.0 | 0.0 |
| A8.24 | 1.0 | 1.0 | 0.0 |
| A5.16 | 2.0 | 2.0 | 0.0 |
| A8.15 | 1.5 | 1.5 | 0.0 |
| A5.17 | 1.0 | 1.0 | 0.0 |
| A5.34 | 2.0 | 2.0 | 0.0 |
| A8.5 | 2.0 | 2.0 | 0.0 |
| A5.15 | 2.0 | 2.0 | 0.0 |

### Inconsistent Maturity and Reduction Combinations

| Rater | Control | Maturity answer | Reduction at level 3 | Q_T literal | Q_T main |
| --- | --- | --- | --- | --- | --- |
| R7 | A8.28 | 4 | 40 % | 3 | 2 |
| R7 | A8.16 | 4 | 20 % | 3 | 2 |
| R7 | A5.16 | 4 | 50 % | 3 | 2 |
| R1 | A8.15 | 4 | 50 % | 3 | 2 |
| R7 | A5.17 | 4 | 40 % | 3 | 2 |
| R1 | A5.34 | 4 | 20 % | 3 | 2 |
| R5 | A5.34 | 4 | 20 % | 3 | 2 |
| R7 | A5.34 | 4 | 40 % | 3 | 2 |

## Risk Reduction at Maturity Level 3

| Control | n | Median | IQR | Min | Max | Modal band | Modal share | Neighbour share | Consensus 50 % modal | Consensus 50 % neighbours | Consensus 75 % modal | Consensus 75 % neighbours |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A8.28 | 7 | 50.0 | 7.5 | 40.0 | 60.0 | 50 | 100.0 % | 100.0 % | yes | yes | yes | yes |
| A8.16 | 7 | 20.0 | 20.0 | 0.0 | 30.0 | 25 | 57.1 % | 100.0 % | yes | yes | no | yes |
| A8.12 | 7 | 50.0 | 5.0 | 35.0 | 70.0 | 50 | 71.4 % | 100.0 % | yes | yes | no | yes |
| A8.24 | 7 | 50.0 | 27.5 | 20.0 | 75.0 | 50 | 42.9 % | 100.0 % | no | yes | no | yes |
| A5.16 | 7 | 50.0 | 10.0 | 25.0 | 50.0 | 50 | 85.7 % | 100.0 % | yes | yes | yes | yes |
| A8.15 | 7 | 10.0 | 20.0 | 0.0 | 50.0 | 0-10 | 57.1 % | 85.7 % | yes | yes | no | yes |
| A5.17 | 7 | 30.0 | 15.0 | 20.0 | 50.0 | 25 | 57.1 % | 100.0 % | yes | yes | no | yes |
| A5.34 | 7 | 30.0 | 22.5 | 20.0 | 50.0 | 25 | 57.1 % | 100.0 % | yes | yes | no | yes |
| A8.5 | 7 | 50.0 | 10.0 | 20.0 | 50.0 | 50 | 71.4 % | 100.0 % | yes | yes | no | yes |
| A5.15 | 7 | 40.0 | 20.0 | 20.0 | 50.0 | 50 | 71.4 % | 100.0 % | yes | yes | no | yes |

## Risk Reduction at Maturity Level 5

| Control | n | Median | IQR | Min | Max | Modal band | Modal share | Neighbour share | Consensus 50 % modal | Consensus 50 % neighbours | Consensus 75 % modal | Consensus 75 % neighbours |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A8.28 | 7 | 80.0 | 7.5 | 70.0 | 95.0 | 75 | 71.4 % | 100.0 % | yes | yes | no | yes |
| A8.16 | 7 | 20.0 | 40.0 | 0.0 | 80.0 | 0-10 | 42.9 % | 71.4 % | no | yes | no | no |
| A8.12 | 7 | 80.0 | 15.0 | 60.0 | 99.0 | 75 | 57.1 % | 100.0 % | yes | yes | no | yes |
| A8.24 | 7 | 80.0 | 10.0 | 60.0 | 95.0 | 75 | 71.4 % | 100.0 % | yes | yes | no | yes |
| A5.16 | 7 | 60.0 | 22.5 | 50.0 | 95.0 | 50 | 57.1 % | 85.7 % | yes | yes | no | yes |
| A8.15 | 7 | 20.0 | 40.0 | 0.0 | 70.0 | 0-10 | 42.9 % | 71.4 % | no | yes | no | no |
| A5.17 | 7 | 80.0 | 22.5 | 50.0 | 95.0 | 50 | 42.9 % | 85.7 % | no | yes | no | yes |
| A5.34 | 7 | 50.0 | 20.0 | 40.0 | 95.0 | 50 | 71.4 % | 85.7 % | yes | yes | no | yes |
| A8.5 | 7 | 70.0 | 25.0 | 50.0 | 95.0 | 50 | 42.9 % | 71.4 % | no | yes | no | no |
| A5.15 | 7 | 70.0 | 15.0 | 50.0 | 95.0 | 50 | 42.9 % | 85.7 % | no | yes | no | yes |

### Monotonicity Violations between Level 3 and Level 5

| Rater | Control | Reduction at level 3 | Reduction at level 5 | Status |
| --- | --- | --- | --- | --- |
| no entries |  |  |  |  |

## Residual Effectiveness per Dependency Item

| Item | Control | Prerequisites | Kind | n | Median | IQR | Min | Max | Modal band | Modal share | Neighbour share | Consensus 50 % modal | Consensus 50 % neighbours | Consensus 75 % modal | Consensus 75 % neighbours |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| D1 | A5.34 | A5.12 | atomic | 7 | 50.0 | 12.5 | 25.0 | 75.0 | 50 | 57.1 % | 100.0 % | yes | yes | no | yes |
| D2 | A5.34 | A5.13 | atomic | 7 | 75.0 | 27.5 | 25.0 | 80.0 | 75 | 57.1 % | 85.7 % | yes | yes | no | yes |
| D3 | A5.34 | A5.12 and A5.13 | composite | 6 | 50.0 | 0.0 | 40.0 | 75.0 | 50 | 83.3 % | 100.0 % | yes | yes | yes | yes |
| D4 | A5.34 | A5.17 | atomic | 7 | 50.0 | 0.0 | 50.0 | 75.0 | 50 | 85.7 % | 100.0 % | yes | yes | yes | yes |
| D5 | A5.34 | A5.26 | atomic | 7 | 50.0 | 12.5 | 25.0 | 80.0 | 50 | 57.1 % | 100.0 % | yes | yes | no | yes |
| D6 | A8.16 | A8.15 | atomic | 7 | 10.0 | 5.0 | 0.0 | 50.0 | 0-10 | 71.4 % | 85.7 % | yes | yes | no | yes |
| D7 | A8.16 | A8.15 and A5.25 | composite | 7 | 10.0 | 5.0 | 0.0 | 75.0 | 0-10 | 71.4 % | 85.7 % | yes | yes | no | yes |

## Reported Dependency Types

The two transfer options were presented as a single answer option in the questionnaire. The categories are therefore reported as elicited and are not separated further.

| Item | Answer | Frequency | Missing |
| --- | --- | --- | --- |
| D1 | Teilvoraussetzung | 6 | 4 |
| D1 | Harte Voraussetzung | 1 | 4 |
| D2 | Teilvoraussetzung | 4 | 4 |
| D2 | Wrikungsverstärker | 3 | 4 |
| D3 | Teilvoraussetzung | 6 | 4 |
| D3 | Nicht beurteilbar | 1 | 4 |
| D4 | Wrikungsverstärker | 6 | 4 |
| D4 | Teilvoraussetzung | 1 | 4 |
| D5 | Wrikungsverstärker | 5 | 4 |
| D5 | Teilvoraussetzung | 2 | 4 |
| D6 | Harte Voraussetzung | 7 | 4 |
| D7 | Harte Voraussetzung | 6 | 4 |
| D7 | Teilvoraussetzung | 1 | 4 |

## Concordance over Atomic Dependency Items

Kendall's W is computed over the atomic items only, because composite AND items are logically derived from them.

| Raters used | Items used | Excluded raters | W | Chi square | Degrees of freedom |
| --- | --- | --- | --- | --- | --- |
| 7 | 5 | R8, R9, R10, R11 | 0.468 | 13.1 | 4 |

## Consistency Check for Composite AND Items

The residual effectiveness of a combined prerequisite loss must not exceed the minimum of its parts. Where a prerequisite was not elicited individually, the bound is only partial.

| Item | Prerequisites | Rater | Components | Upper bound | Observed | Bound | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| D3 | A5.12 and A5.13 | R1 | 50 %, 25 % | 25 % | 50 % | complete | violation |
| D3 | A5.12 and A5.13 | R2 | 75 %, 75 % | 75 % | 75 % | complete | ok |
| D3 | A5.12 and A5.13 | R3 | 75 %, 80 % | 75 % | 50 % | complete | ok |
| D3 | A5.12 and A5.13 | R5 | 50 %, 80 % | 50 % | 50 % | complete | ok |
| D3 | A5.12 and A5.13 | R6 | 50 %, 75 % | 50 % | 40 % | complete | ok |
| D3 | A5.12 and A5.13 | R7 | 50 %, 50 % | 50 % | 50 % | complete | ok |
| D7 | A8.15 and A5.25 | R1 | 50 % | 50 % | 75 % | partial | violation |
| D7 | A8.15 and A5.25 | R2 | 0 % | 0 % | 0 % | partial | ok |
| D7 | A8.15 and A5.25 | R3 | 10 % | 10 % | 10 % | partial | ok |
| D7 | A8.15 and A5.25 | R4 | 10 % | 10 % | 10 % | partial | ok |
| D7 | A8.15 and A5.25 | R5 | 20 % | 20 % | 20 % | partial | ok |
| D7 | A8.15 and A5.25 | R6 | 10 % | 10 % | 10 % | partial | ok |
| D7 | A8.15 and A5.25 | R7 | 10 % | 10 % | 10 % | partial | ok |

## Aggregation Rule Comparison

| Item | Rater | Observed | Minimum rule | Product rule | Error minimum | Error product |
| --- | --- | --- | --- | --- | --- | --- |
| D3 | R1 | 50 % | 25 % | 12 % | 25.0 | 37.5 |
| D3 | R2 | 75 % | 75 % | 56 % | 0.0 | 18.8 |
| D3 | R3 | 50 % | 75 % | 60 % | 25.0 | 10.0 |
| D3 | R5 | 50 % | 50 % | 40 % | 0.0 | 10.0 |
| D3 | R6 | 40 % | 50 % | 38 % | 10.0 | 2.5 |
| D3 | R7 | 50 % | 50 % | 25 % | 0.0 | 25.0 |

### Aggregation Rule Summary

| Comparisons | MAE minimum rule | MAE product rule |
| --- | --- | --- |
| 6 | 10.0 | 17.3 |

## Scenario Analysis

The following results describe context variants and are reported separately from the core model.

### Qualitative Assessments

| Scenario | Answer | Frequency | Missing |
| --- | --- | --- | --- |
| Dienstleister betreibt Umgebung | Nicht pauschal beurteilbar | 5 | 4 |
| Dienstleister betreibt Umgebung | Ja, im Durschschnitt schwächer | 1 | 4 |
| Dienstleister betreibt Umgebung | Nein, meine Einschätzung bleibt gleich | 1 | 4 |
| Umgebung unbekannt | Nicht pauschal beurteilbar | 5 | 4 |
| Umgebung unbekannt | Ja, im Durchschnitt eher schwächer | 2 | 4 |

### Quantitative Assessments

| Scenario | n | Median | IQR | Min | Max | Modal band | Modal share | Neighbour share | Consensus 50 % modal | Consensus 50 % neighbours | Consensus 75 % modal | Consensus 75 % neighbours |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Dienstleister betreibt Umgebung | 1 | 10.0 | 0.0 | 10.0 | 10.0 | 0-10 | 100.0 % | 100.0 % | yes | yes | yes | yes |
| Umgebung unbekannt | 2 | 10.0 | 0.0 | 10.0 | 10.0 | 0-10 | 100.0 % | 100.0 % | yes | yes | yes | yes |

## Invalid or Unparsed Entries

| Excel row | Field | Raw value |
| --- | --- | --- |
| 5 | D3 residual effectiveness | Nicht beurteilbar |
| 6 | Reifegrad A8.16 | 0.0 |
| 6 | Reifegrad A8.15 | 0.0 |
