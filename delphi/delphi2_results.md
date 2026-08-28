# Delphi Round 2 - Results
n = 11 experts, source: `que_2.xlsx`

Bands: 0-10, >10-25, >25-50, >50-75, >75-100 (half-open, no gaps/overlaps). Consensus reading: B, two-tier rule (tier 1: modal band alone >= 50%; tier 2: modal + adjacent band >= 70%), min n = 5, bimodality blocks consensus: True. Ordinal point estimates rounded up.

## Top-10 Confirmation (Round 2)
| Control | n valid | Confirmation % | Rejections | Missing |
|---|---|---|---|---|
| A8.28 | 7 | 100.0 | 0 | 4 |
| A8.16 | 7 | 100.0 | 0 | 4 |
| A8.12 | 7 | 100.0 | 0 | 4 |
| A8.24 | 7 | 100.0 | 0 | 4 |
| A5.16 | 7 | 100.0 | 0 | 4 |
| A8.15 | 7 | 100.0 | 0 | 4 |
| A5.17 | 7 | 100.0 | 0 | 4 |
| A5.34 | 7 | 100.0 | 0 | 4 |
| A8.5 | 7 | 100.0 | 0 | 4 |
| A5.15 | 7 | 100.0 | 0 | 4 |

## Control Effectiveness Anchors
| Control | Q_T | Q_T agr. | n(level 0) | Q_M % | Q_M agr. | Q_C % | Q_C agr. | Q_C bimodal |
|---|---|---|---|---|---|---|---|---|
| A8.28 | 3 | consensus | 0 | 50.0 | consensus | 80.0 | consensus | no |
| A8.16 | 2 | consensus | 1 | 10.0 | consensus | 20.0 | tendency | no |
| A8.12 | 3 | consensus | 0 | 50.0 | consensus | 80.0 | consensus | no |
| A8.24 | 2 | consensus | 0 | 55.0 | consensus | 80.0 | consensus | no |
| A5.16 | 3 | consensus | 0 | 50.0 | consensus | 70.0 | consensus | no |
| A8.15 | 2 | consensus | 1 | 10.0 | dissent | 20.0 | dissent | yes |
| A5.17 | 2 | consensus | 0 | 30.0 | consensus | 80.0 | consensus | no |
| A5.34 | 4 | consensus | 0 | 30.0 | consensus | 50.0 | dissent | yes |
| A8.5 | 3 | consensus | 0 | 50.0 | consensus | 75.0 | consensus | no |
| A5.15 | 3 | consensus | 0 | 40.0 | consensus | 70.0 | consensus | no |

## Round-number Anchoring (share of verbatim 50 %)
| Control | Q_M at 50 | Q_C at 50 |
|---|---|---|
| A8.28 | 3/7 | 0/7 |
| A8.16 | 0/7 | 0/7 |
| A8.12 | 4/7 | 0/7 |
| A8.24 | 1/7 | 0/7 |
| A5.16 | 4/7 | 1/7 |
| A8.15 | 1/7 | 0/7 |
| A5.17 | 2/7 | 1/7 |
| A5.34 | 2/7 | 3/7 |
| A8.5 | 5/7 | 1/7 |
| A5.15 | 3/7 | 1/7 |

## Effectiveness Curves E(m), m=1..5 (%)
| Control | m1 | m2 | m3 | m4 | m5 | Note |
|---|---|---|---|---|---|---|
| A8.28 | 0.0 | 0.0 | 50.0 | 65.0 | 80.0 | monotonic (Q_T >= 3 edge case: effect starts exactly at m=3) |
| A8.16 | 0.0 | 0.0 | 10.0 | 15.0 | 20.0 | monotonic |
| A8.12 | 0.0 | 0.0 | 50.0 | 65.0 | 80.0 | monotonic (Q_T >= 3 edge case: effect starts exactly at m=3) |
| A8.24 | 0.0 | 0.0 | 55.0 | 67.5 | 80.0 | monotonic |
| A5.16 | 0.0 | 0.0 | 50.0 | 60.0 | 70.0 | monotonic (Q_T >= 3 edge case: effect starts exactly at m=3) |
| A8.15 | 0.0 | 0.0 | 10.0 | 15.0 | 20.0 | monotonic |
| A5.17 | 0.0 | 0.0 | 30.0 | 55.0 | 80.0 | monotonic |
| A5.34 | 0.0 | 0.0 | 0.0 | 40.0 | 50.0 | monotonic (Q_T >= 3 edge case: effect starts exactly at m=3) |
| A8.5 | 0.0 | 0.0 | 50.0 | 62.5 | 75.0 | monotonic (Q_T >= 3 edge case: effect starts exactly at m=3) |
| A5.15 | 0.0 | 0.0 | 40.0 | 55.0 | 70.0 | monotonic (Q_T >= 3 edge case: effect starts exactly at m=3) |

## Dependencies
| Item | Dependent | Prerequisites | Kind | Residual % | Agreement | at 50 | Type distribution |
|---|---|---|---|---|---|---|---|
| A5.34 + A5.12 | A5.34 | A5.12 | atomic |  | insufficient_n | 0/0 | Teilvoraussetzung:6, Harte Voraussetzung:1 |
| A5.34 + A5.13 | A5.34 | A5.13 | atomic |  | insufficient_n | 0/0 | Wrikungsverstärker:3, Teilvoraussetzung:4 |
| A5.34 + A5.12 UND A5.13 | A5.34 | A5.12 + A5.13 | composite |  | insufficient_n | 0/0 | Teilvoraussetzung:6 |
| A5.34 + A5.17 | A5.34 | A5.17 | atomic |  | insufficient_n | 0/0 | Teilvoraussetzung:1, Wrikungsverstärker:6 |
| A5.34 + A5.26 | A5.34 | A5.26 | atomic |  | insufficient_n | 0/0 | Wrikungsverstärker:5, Teilvoraussetzung:2 |
| A8.16 + A8.15 | A8.16 | A8.15 | atomic |  | insufficient_n | 0/0 | Harte Voraussetzung:7 |
| A8.16 + A8.15 UND A5.25 | A8.16 | A8.15 + A5.25 | composite |  | insufficient_n | 0/0 | Harte Voraussetzung:6, Teilvoraussetzung:1 |

## Minimum vs. Product Rule (composite items)
| Item | n | MAE min rule | MAE product rule | Closer |
|---|---|---|---|---|
| A5.34 + A5.12 UND A5.13 | 0 |  |  |  |
| A8.16 + A8.15 UND A5.25 | n/a | n/a | n/a | not all single-prerequisite failures were elicited individually |

## Context Items (descriptive only)
| Item | Answer | Frequency |
|---|---|---|
| Dienstleister betreibt Umgebung Einschätzung | Nicht pauschal beurteilbar | 5 |
| Dienstleister betreibt Umgebung Einschätzung | Nein, meine Einschätzung bleibt gleich | 1 |
| Dienstleister betreibt Umgebung Einschätzung | Ja, im Durschschnitt schwächer | 1 |
| Dienstleister betreibt Umgebung Prozent | Nicht pauschal beurteilbar | 5 |
| Dienstleister betreibt Umgebung Prozent | Nein, meine Einschätzung bleibt gleich | 1 |
| Dienstleister betreibt Umgebung Prozent | Spürbar (10-25) | 1 |
| Umgebung unbekannt Einschätzung | Ja, im Durchschnitt eher schwächer | 2 |
| Umgebung unbekannt Einschätzung | Nicht pauschal beurteilbar | 5 |
| DiUmgebung unbekannt  Prozent | Spürbar (10-25) | 2 |
| DiUmgebung unbekannt  Prozent | Nicht pauschal beurteilbar | 5 |

## Warnings
- column not found: Verbleibende operative Wirksamkeit A5.34 + A5.12
- column not found: Verbleibende operative Wirksamkeit A5.34 + A5.13
- column not found: Verbleibende operative Wirksamkeit A5.34 + A5.12 UND A5.13
- column not found: Verbleibende operative Wirksamkeit A5.34 + A5.17
- column not found: Verbleibende operative Wirksamkeit A5.34 + A5.26
- column not found: Verbleibende operative Wirksamkeit A8.16 + A8.15
- column not found: Verbleibende operative Wirksamkeit A8.16 + A8.15 UND A5.25
