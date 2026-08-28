# Delphi Round 2 - Validation Results

Bands: 0-10, >10-25, >25-50, >50-75, >75-100 (half-open). Maturity levels 0-5, level 0 valid. Two-tier consensus rule: tier 1 modal band alone >= 50%, tier 2 modal + adjacent band >= 70%. Consensus reading: B.

## Band Definition Self-test
Status: **OK**
| Probe value | Assigned band |
|---|---|
| 0.0 | 0-10 |
| 10.0 | 0-10 |
| 10.4 | >10-25 |
| 10.5 | >10-25 |
| 24.9 | >10-25 |
| 25.0 | >10-25 |
| 25.1 | >25-50 |
| 50.0 | >25-50 |
| 50.5 | >50-75 |
| 75.0 | >50-75 |
| 75.5 | >75-100 |
| 100.0 | >75-100 |

## ICC(2,k) per Effectiveness Anchor
| Anchor | ICC | CI lower | CI upper | n targets | k raters | Raters dropped (missing) |
|---|---|---|---|---|---|---|
| Q_T | 0.233 | -0.439 | 0.824 | 10 | 7 | 4 |
| Q_M | 0.836 | 0.638 | 0.956 | 10 | 7 | 4 |
| Q_C | 0.875 | 0.746 | 0.969 | 10 | 7 | 4 |

*Pooling ICC(2,k) across Q_T, Q_M, Q_C into a single number is deliberately not reported: the three anchors differ substantially in target variance (Q_T shows range restriction across controls, most raters converge on level 2), which would make an unweighted average misleading. Reported separately per anchor instead. Maturity level 0 is now a valid category, so no rater is dropped for answering 0.*

## Fleiss' Kappa - Dependency Type
| Kappa | n items | Categories | p_bar | p_e |
|---|---|---|---|---|
| 0.585 | 7 | Harte Voraussetzung, Teilvoraussetzung, Wrikungsverstärker | 0.728 | 0.344 |

*Dependency type is descriptive only and does not enter the effectiveness model. Non-assessable answers excluded, consistent with results_builder.py.*

## Agreement Classification (Consensus / Tendency / Dissent)
*Same two-tier rule as results_builder.py; the 3-way label is descriptive, the binary criterion is tier1 OR tier2.*
| Item | n valid | Label | Modal band | Modal share | Window share | Bimodal |
|---|---|---|---|---|---|---|
| A8.28_Q_T | 7 | consensus | 2 | 42.9 % | 85.7 % | no |
| A8.28_Q_M | 7 | consensus | >25-50 | 85.7 % | 100.0 % | no |
| A8.28_Q_C | 7 | consensus | >75-100 | 71.4 % | 100.0 % | no |
| A8.16_Q_T | 7 | consensus | 2 | 57.1 % | 71.4 % | no |
| A8.16_Q_M | 7 | consensus | 0-10 | 42.9 % | 71.4 % | no |
| A8.16_Q_C | 7 | tendency | 0-10 | 42.9 % | 57.1 % | no |
| A8.12_Q_T | 7 | consensus | 3 | 71.4 % | 100.0 % | no |
| A8.12_Q_M | 7 | consensus | >25-50 | 85.7 % | 100.0 % | no |
| A8.12_Q_C | 7 | consensus | >75-100 | 71.4 % | 100.0 % | no |
| A8.24_Q_T | 7 | consensus | 2 | 57.1 % | 100.0 % | no |
| A8.24_Q_M | 7 | consensus | >25-50 | 42.9 % | 85.7 % | no |
| A8.24_Q_C | 7 | consensus | >75-100 | 57.1 % | 100.0 % | no |
| A5.16_Q_T | 7 | consensus | 2 | 42.9 % | 85.7 % | no |
| A5.16_Q_M | 7 | consensus | >25-50 | 85.7 % | 100.0 % | no |
| A5.16_Q_C | 7 | consensus | >50-75 | 42.9 % | 85.7 % | no |
| A8.15_Q_T | 7 | consensus | 2 | 42.9 % | 71.4 % | no |
| A8.15_Q_M | 7 | dissent | 0-10 | 57.1 % | 71.4 % | yes |
| A8.15_Q_C | 7 | dissent | 0-10 | 42.9 % | 57.1 % | yes |
| A5.17_Q_T | 7 | consensus | 2 | 57.1 % | 85.7 % | no |
| A5.17_Q_M | 7 | consensus | >25-50 | 85.7 % | 100.0 % | no |
| A5.17_Q_C | 7 | consensus | >75-100 | 57.1 % | 85.7 % | no |
| A5.34_Q_T | 7 | consensus | 4 | 42.9 % | 71.4 % | no |
| A5.34_Q_M | 7 | consensus | >25-50 | 57.1 % | 100.0 % | no |
| A5.34_Q_C | 7 | dissent | >25-50 | 57.1 % | 71.4 % | yes |
| A8.5_Q_T | 7 | consensus | 3 | 57.1 % | 100.0 % | no |
| A8.5_Q_M | 7 | consensus | >25-50 | 85.7 % | 100.0 % | no |
| A8.5_Q_C | 7 | consensus | >50-75 | 42.9 % | 85.7 % | no |
| A5.15_Q_T | 7 | consensus | 3 | 57.1 % | 100.0 % | no |
| A5.15_Q_M | 7 | consensus | >25-50 | 71.4 % | 100.0 % | no |
| A5.15_Q_C | 7 | consensus | >50-75 | 57.1 % | 85.7 % | no |
| A5.34 + A5.12_residual | 0 | - | - | - | - | - |
| A5.34 + A5.13_residual | 0 | - | - | - | - | - |
| A5.34 + A5.12 UND A5.13_residual | 0 | - | - | - | - | - |
| A5.34 + A5.17_residual | 0 | - | - | - | - | - |
| A5.34 + A5.26_residual | 0 | - | - | - | - | - |
| A8.16 + A8.15_residual | 0 | - | - | - | - | - |
| A8.16 + A8.15 UND A5.25_residual | 0 | - | - | - | - | - |

## No-effect Votes (maturity level 0 / 0 % on both anchors)
4 votes total, 2 coherent, 2 incoherent.

*level 0 is treated as a substantive category, not as missing data; incoherent rows are reported for the paper, not silently corrected*
| Control | Row | Level | Reduktion 3 % | Reduktion 5 % | Coherent |
|---|---|---|---|---|---|
| A8.16 | 1 | 2 | 0.0 | 0.0 | no |
| A8.16 | 4 | 0 | 0.0 | 0.0 | yes |
| A8.15 | 1 | 2 | 0.0 | 0.0 | no |
| A8.15 | 4 | 0 | 0.0 | 0.0 | yes |

## Appendix: Gwet's AC1 / AC2 (Descriptive Only)
*No true value exists in a Delphi panel; not interpreted as a reliability criterion.*
| Measure | Value |
|---|---|
| AC2, Q_T levels (ordinal) | 0.686 |
| AC2, Q_M bands (ordinal) | 0.777 |
| AC2, Q_C bands (ordinal) | 0.51 |
| AC2, residual effectiveness bands (ordinal) |  |
| AC1, dependency type (nominal) | 0.596 |

## Monotonicity Checks

### Q_M <= Q_C Violations (per rater, per control)
| Control | Row | Q_M | Q_C |
|---|---|---|---|
| - | - | - | - |

### Curve Non-monotonicity (hard violations)
| Control | Level from | Level to | Value from | Value to |
|---|---|---|---|---|
| - | - | - | - | - |

### Flat-zero Curves (Q_T = 0)
| Control | Q_T | Note |
|---|---|---|
| - | - | - |

### Structural Onset Jumps (informational, not a warning)
*The single-integer step in which the curve leaves 0 carries the full 0 -> Q_M increase, because maturity is only defined on integer levels.*
| Control | Q_T | Level from | Level to | Value from | Value to | Delta (pct) |
|---|---|---|---|---|---|---|
| A8.28 | 3 | 2 | 3 | 0.0 | 50.0 | 50.0 |
| A8.16 | 2 | 2 | 3 | 0.0 | 10.0 | 10.0 |
| A8.12 | 3 | 2 | 3 | 0.0 | 50.0 | 50.0 |
| A8.24 | 2 | 2 | 3 | 0.0 | 55.0 | 55.0 |
| A5.16 | 3 | 2 | 3 | 0.0 | 50.0 | 50.0 |
| A8.15 | 2 | 2 | 3 | 0.0 | 10.0 | 10.0 |
| A5.17 | 2 | 2 | 3 | 0.0 | 30.0 | 30.0 |
| A5.34 | 4 | 3 | 4 | 0.0 | 40.0 | 40.0 |
| A8.5 | 3 | 2 | 3 | 0.0 | 50.0 | 50.0 |
| A5.15 | 3 | 2 | 3 | 0.0 | 40.0 | 40.0 |

### Genuine Jump Warnings (outside the onset step, > 15.0 pct points)
| Control | Level from | Level to | Value from | Value to | Delta (pct) | Note |
|---|---|---|---|---|---|---|
| A5.17 | 3 | 4 | 30.0 | 55.0 | 25.0 | large increase outside the onset step; check the Q_M/Q_C spread or curve construction |
| A5.17 | 4 | 5 | 55.0 | 80.0 | 25.0 | large increase outside the onset step; check the Q_M/Q_C spread or curve construction |

## Excluded Measures
| Measure | Reason |
|---|---|
| krippendorffs_alpha | not used (prevalence paradox under skewed marginals in this dataset) |
| van_der_eijk_agreement_a | not used (unvalidated beyond edge-case self-tests) |
| kendalls_w | not used (no que_1.xlsx rater-level ranking data in scope of this script) |
