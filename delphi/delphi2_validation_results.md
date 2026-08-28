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
| Q_T | 0.333 | -0.15 | 0.851 | 10 | 11 | 0 |
| Q_M | 0.879 | 0.758 | 0.969 | 10 | 11 | 0 |
| Q_C | 0.909 | 0.831 | 0.978 | 10 | 11 | 0 |

*Pooling ICC(2,k) across Q_T, Q_M, Q_C into a single number is deliberately not reported: the three anchors differ substantially in target variance (Q_T shows range restriction across controls, most raters converge on level 2), which would make an unweighted average misleading. Reported separately per anchor instead. Maturity level 0 is now a valid category, so no rater is dropped for answering 0.*

## Fleiss' Kappa - Dependency Type
| Kappa | n items | Categories | p_bar | p_e |
|---|---|---|---|---|
| 0.429 | 7 | Harte Voraussetzung, Keine, Teilvoraussetzung, Wirkungsverstärker | 0.618 | 0.331 |

*Dependency type is descriptive only and does not enter the effectiveness model. Non-assessable answers excluded, consistent with results_builder.py.*

## Agreement Classification (Consensus / Tendency / Dissent)
*Same two-tier rule as results_builder.py; the 3-way label is descriptive, the binary criterion is tier1 OR tier2.*
| Item | n valid | Label | Modal band | Modal share | Window share | Bimodal |
|---|---|---|---|---|---|---|
| A8.28_Q_T | 11 | consensus | 2 | 54.5 % | 90.9 % | no |
| A8.28_Q_M | 11 | consensus | >25-50 | 90.9 % | 100.0 % | no |
| A8.28_Q_C | 11 | consensus | >75-100 | 54.5 % | 100.0 % | no |
| A8.16_Q_T | 11 | consensus | 2 | 72.7 % | 81.8 % | no |
| A8.16_Q_M | 11 | consensus | 0-10 | 36.4 % | 72.7 % | no |
| A8.16_Q_C | 11 | tendency | 0-10 | 36.4 % | 54.5 % | no |
| A8.12_Q_T | 11 | consensus | 3 | 63.6 % | 100.0 % | no |
| A8.12_Q_M | 11 | consensus | >25-50 | 81.8 % | 90.9 % | no |
| A8.12_Q_C | 11 | consensus | >75-100 | 54.5 % | 90.9 % | no |
| A8.24_Q_T | 11 | consensus | 2 | 63.6 % | 90.9 % | no |
| A8.24_Q_M | 11 | consensus | >25-50 | 54.5 % | 81.8 % | no |
| A8.24_Q_C | 11 | consensus | >50-75 | 63.6 % | 100.0 % | no |
| A5.16_Q_T | 11 | consensus | 2 | 45.5 % | 90.9 % | no |
| A5.16_Q_M | 11 | consensus | >25-50 | 72.7 % | 100.0 % | no |
| A5.16_Q_C | 11 | dissent | >25-50 | 36.4 % | 63.6 % | yes |
| A8.15_Q_T | 11 | consensus | 2 | 45.5 % | 81.8 % | no |
| A8.15_Q_M | 11 | consensus | 0-10 | 45.5 % | 81.8 % | no |
| A8.15_Q_C | 11 | tendency | 0-10 | 36.4 % | 63.6 % | no |
| A5.17_Q_T | 11 | consensus | 2 | 72.7 % | 90.9 % | no |
| A5.17_Q_M | 11 | consensus | >25-50 | 63.6 % | 100.0 % | no |
| A5.17_Q_C | 11 | dissent | >25-50 | 45.5 % | 63.6 % | yes |
| A5.34_Q_T | 11 | consensus | 2 | 45.5 % | 72.7 % | no |
| A5.34_Q_M | 11 | consensus | >10-25 | 54.5 % | 100.0 % | no |
| A5.34_Q_C | 11 | consensus | >25-50 | 45.5 % | 81.8 % | no |
| A8.5_Q_T | 11 | consensus | 3 | 54.5 % | 100.0 % | no |
| A8.5_Q_M | 11 | consensus | >25-50 | 72.7 % | 100.0 % | no |
| A8.5_Q_C | 11 | consensus | >50-75 | 54.5 % | 81.8 % | no |
| A5.15_Q_T | 11 | consensus | 2 | 54.5 % | 100.0 % | no |
| A5.15_Q_M | 11 | consensus | >25-50 | 54.5 % | 100.0 % | no |
| A5.15_Q_C | 11 | consensus | >50-75 | 63.6 % | 81.8 % | no |
| A5.34 + A5.12_residual | 11 | consensus | >25-50 | 54.5 % | 81.8 % | no |
| A5.34 + A5.13_residual | 11 | tendency | >25-50 | 36.4 % | 63.6 % | no |
| A5.34 + A5.12 UND A5.13_residual | 10 | consensus | >25-50 | 70.0 % | 90.0 % | no |
| A5.34 + A5.17_residual | 11 | consensus | >25-50 | 54.5 % | 72.7 % | no |
| A5.34 + A5.26_residual | 11 | consensus | >25-50 | 45.5 % | 72.7 % | no |
| A8.16 + A8.15_residual | 11 | consensus | 0-10 | 72.7 % | 81.8 % | no |
| A8.16 + A8.15 UND A5.25_residual | 11 | consensus | 0-10 | 72.7 % | 81.8 % | no |

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
| AC2, Q_T levels (ordinal) | 0.75 |
| AC2, Q_M bands (ordinal) | 0.756 |
| AC2, Q_C bands (ordinal) | 0.503 |
| AC2, residual effectiveness bands (ordinal) | 0.513 |
| AC1, dependency type (nominal) | 0.509 |

## Monotonicity Checks

### Q_M <= Q_C Violations (per rater, per control)
| Control | Row | Q_M | Q_C |
|---|---|---|---|
| A5.16 | 10 | 45.0 % | 40.0 % |

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
| A8.28 | 2 | 2 | 3 | 0.0 | 50.0 | 50.0 |
| A8.16 | 2 | 2 | 3 | 0.0 | 15.0 | 15.0 |
| A8.12 | 3 | 2 | 3 | 0.0 | 50.0 | 50.0 |
| A8.24 | 2 | 2 | 3 | 0.0 | 50.0 | 50.0 |
| A5.16 | 3 | 2 | 3 | 0.0 | 45.0 | 45.0 |
| A8.15 | 2 | 2 | 3 | 0.0 | 10.0 | 10.0 |
| A5.17 | 2 | 2 | 3 | 0.0 | 30.0 | 30.0 |
| A5.34 | 2 | 2 | 3 | 0.0 | 25.0 | 25.0 |
| A8.5 | 3 | 2 | 3 | 0.0 | 50.0 | 50.0 |
| A5.15 | 2 | 2 | 3 | 0.0 | 40.0 | 40.0 |

### Genuine Jump Warnings (outside the onset step, > 15.0 pct points)
| Control | Level from | Level to | Value from | Value to | Delta (pct) | Note |
|---|---|---|---|---|---|---|
| - | - | - | - | - | - | - |

## Excluded Measures
| Measure | Reason |
|---|---|
| krippendorffs_alpha | not used (prevalence paradox under skewed marginals in this dataset) |
| van_der_eijk_agreement_a | not used (unvalidated beyond edge-case self-tests) |
| kendalls_w | not used (no que_1.xlsx rater-level ranking data in scope of this script) |
