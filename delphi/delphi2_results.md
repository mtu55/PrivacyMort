# Delphi Round 2 - Results
n = 11 experts, source: `que_2.xlsx`

Bands: 0-10, >10-25, >25-50, >50-75, >75-100 (half-open, no gaps/overlaps). Consensus reading: B, two-tier rule (tier 1: modal band alone >= 50%; tier 2: modal + adjacent band >= 70%), min n = 5, bimodality blocks consensus: True. Ordinal point estimates rounded up.

## Top-10 Confirmation (Round 2)
| Control | n valid | Confirmation % | Rejections | Missing |
|---|---|---|---|---|
| A8.28 | 11 | 100.0 | 0 | 0 |
| A8.16 | 11 | 100.0 | 0 | 0 |
| A8.12 | 11 | 100.0 | 0 | 0 |
| A8.24 | 11 | 100.0 | 0 | 0 |
| A5.16 | 11 | 90.9 | 0 | 0 |
| A8.15 | 11 | 100.0 | 0 | 0 |
| A5.17 | 11 | 90.9 | 0 | 0 |
| A5.34 | 11 | 100.0 | 0 | 0 |
| A8.5 | 11 | 100.0 | 0 | 0 |
| A5.15 | 11 | 100.0 | 0 | 0 |

## Control Effectiveness Anchors
| Control | Q_T | Q_T agr. | n(level 0) | Q_M % | Q_M agr. | Q_C % | Q_C agr. | Q_C bimodal |
|---|---|---|---|---|---|---|---|---|
| A8.28 | 2 | consensus | 0 | 50.0 | consensus | 80.0 | consensus | no |
| A8.16 | 2 | consensus | 1 | 15.0 | consensus | 25.0 | tendency | no |
| A8.12 | 3 | consensus | 0 | 50.0 | consensus | 80.0 | consensus | no |
| A8.24 | 2 | consensus | 0 | 50.0 | consensus | 75.0 | consensus | no |
| A5.16 | 3 | consensus | 0 | 45.0 | consensus | 60.0 | dissent | yes |
| A8.15 | 2 | consensus | 1 | 10.0 | consensus | 25.0 | tendency | no |
| A5.17 | 2 | consensus | 0 | 30.0 | consensus | 60.0 | dissent | yes |
| A5.34 | 2 | consensus | 0 | 25.0 | consensus | 50.0 | consensus | no |
| A8.5 | 3 | consensus | 0 | 50.0 | consensus | 70.0 | consensus | no |
| A5.15 | 2 | consensus | 0 | 40.0 | consensus | 60.0 | consensus | no |

## Round-number Anchoring (share of verbatim 50 %)
| Control | Q_M at 50 | Q_C at 50 |
|---|---|---|
| A8.28 | 5/11 | 0/11 |
| A8.16 | 0/11 | 0/11 |
| A8.12 | 6/11 | 1/11 |
| A8.24 | 2/11 | 0/11 |
| A5.16 | 5/11 | 2/11 |
| A8.15 | 1/11 | 1/11 |
| A5.17 | 2/11 | 4/11 |
| A5.34 | 2/11 | 3/11 |
| A8.5 | 6/11 | 1/11 |
| A5.15 | 3/11 | 1/11 |

## Effectiveness Curves E(m), m=1..5 (%)
| Control | m1 | m2 | m3 | m4 | m5 | Note |
|---|---|---|---|---|---|---|
| A8.28 | 0.0 | 0.0 | 50.0 | 65.0 | 80.0 | monotonic |
| A8.16 | 0.0 | 0.0 | 15.0 | 20.0 | 25.0 | monotonic |
| A8.12 | 0.0 | 0.0 | 50.0 | 65.0 | 80.0 | monotonic (Q_T >= 3 edge case: effect starts exactly at m=3) |
| A8.24 | 0.0 | 0.0 | 50.0 | 62.5 | 75.0 | monotonic |
| A5.16 | 0.0 | 0.0 | 45.0 | 52.5 | 60.0 | monotonic (Q_T >= 3 edge case: effect starts exactly at m=3) |
| A8.15 | 0.0 | 0.0 | 10.0 | 17.5 | 25.0 | monotonic |
| A5.17 | 0.0 | 0.0 | 30.0 | 45.0 | 60.0 | monotonic |
| A5.34 | 0.0 | 0.0 | 25.0 | 37.5 | 50.0 | monotonic |
| A8.5 | 0.0 | 0.0 | 50.0 | 60.0 | 70.0 | monotonic (Q_T >= 3 edge case: effect starts exactly at m=3) |
| A5.15 | 0.0 | 0.0 | 40.0 | 50.0 | 60.0 | monotonic |

## Dependencies
| Item | Dependent | Prerequisites | Kind | Residual % | Agreement | at 50 | Type distribution |
|---|---|---|---|---|---|---|---|
| A5.34 + A5.12 | A5.34 | A5.12 | atomic | 50.0 | consensus | 6/11 | Teilvoraussetzung:9, Harte Voraussetzung:1, Wirkungsverstärker:1 |
| A5.34 + A5.13 | A5.34 | A5.13 | atomic | 75.0 | tendency | 4/11 | Wirkungsverstärker:5, Teilvoraussetzung:5, Keine:1 |
| A5.34 + A5.12 UND A5.13 | A5.34 | A5.12 + A5.13 | composite | 50.0 | consensus | 5/10 | Teilvoraussetzung:9, Wirkungsverstärker:1 |
| A5.34 + A5.17 | A5.34 | A5.17 | atomic | 50.0 | consensus | 6/11 | Teilvoraussetzung:2, Wirkungsverstärker:8, Keine:1 |
| A5.34 + A5.26 | A5.34 | A5.26 | atomic | 50.0 | consensus | 5/11 | Wirkungsverstärker:7, Teilvoraussetzung:4 |
| A8.16 + A8.15 | A8.16 | A8.15 | atomic | 10.0 | consensus | 1/11 | Harte Voraussetzung:10, Teilvoraussetzung:1 |
| A8.16 + A8.15 UND A5.25 | A8.16 | A8.15 + A5.25 | composite | 10.0 | consensus | 0/11 | Harte Voraussetzung:9, Teilvoraussetzung:2 |

## Minimum vs. Product Rule (composite items)
| Item | n | MAE min rule | MAE product rule | Closer |
|---|---|---|---|---|
| A5.34 + A5.12 UND A5.13 | 10 | 7.5 | 14.9 | minimum |
| A8.16 + A8.15 UND A5.25 | n/a | n/a | n/a | not all single-prerequisite failures were elicited individually |

## Context Items (descriptive only)
| Item | Answer | Frequency |
|---|---|---|
| Dienstleister betreibt Umgebung Einschätzung | Nicht pauschal beurteilbar | 9 |
| Dienstleister betreibt Umgebung Einschätzung | Nein, meine Einschätzung bleibt gleich | 1 |
| Dienstleister betreibt Umgebung Einschätzung | Ja, im Durschschnitt schwächer | 1 |
| Dienstleister betreibt Umgebung Prozent | Nicht pauschal beurteilbar | 9 |
| Dienstleister betreibt Umgebung Prozent | Nein, meine Einschätzung bleibt gleich | 1 |
| Dienstleister betreibt Umgebung Prozent | Spürbar (10-25) | 1 |
| Umgebung unbekannt Einschätzung | Ja, im Durchschnitt eher schwächer | 2 |
| Umgebung unbekannt Einschätzung | Nicht pauschal beurteilbar | 9 |
| DiUmgebung unbekannt  Prozent | Spürbar (10-25) | 2 |
| DiUmgebung unbekannt  Prozent | Nicht pauschal beurteilbar | 9 |
