# Delphi Round 2: Standard Reliability Analysis

Generated: 2026-08-26 19:10:29 UTC

## Scope and Methods

- Source file: `que_2.xlsx`
- Sheet: `Tabelle1`
- Python: `3.14.0`
- pandas: `3.0.3`
- NumPy: `2.5.1`
- Pingouin: `0.6.1`

### ICC

ICC(2,k), also denoted ICC(A,k), is calculated with `pingouin.intraclass_corr()` using a two-way random-effects model, absolute agreement, and average measures.

`Q_T` is included only as a descriptive numeric ICC result. It is an ordinal maturity threshold and category 0 has the special substantive meaning "no effect at any maturity level."

### Gwet's AC2

AC2 is calculated for the five pre-defined ordinal percentage bands using quadratic agreement weights:

- `[0,10]`
- `(10,25]`
- `(25,50]`
- `(50,75]`
- `(75,100]`

The AC2 analyses use complete target-by-rater rows only. Targets containing missing ratings are reported explicitly and excluded only from the respective AC2 calculation.

## Internal Checks

| Check | Status | Detail |
|---|---|---|
| Band-boundary self-test | passed | All boundary values map to the intended band. |
| AC2 implementation self-test | passed | Perfect agreement produced AC2 = 1. |

## Input Completeness

| Matrix | Targets | Raters | Valid cells | Missing cells | Complete targets |
|---|---|---|---|---|---|
| Q_T | 10 | 11 | 110 | 0 | 10 |
| Q_M | 10 | 11 | 110 | 0 | 10 |
| Q_C | 10 | 11 | 110 | 0 | 10 |
| Residual effectiveness | 7 | 11 | 76 | 1 | 6 |

## ICC(2,k) / ICC(A,k) Results

| Anchor | ICC | 95% CI | Targets | Raters | Dropped targets | Pingouin type |
|---|---|---|---|---|---|---|
| Q_T (ordinal; descriptive only) | 0.333 | [-0.080, 0.750] | 10 | 11 | none | ICC(A,k) |
| Q_M (raw percentage estimates) | 0.879 | [0.730, 0.960] | 10 | 11 | none | ICC(A,k) |
| Q_C (raw percentage estimates) | 0.909 | [0.800, 0.970] | 10 | 11 | none | ICC(A,k) |

## Gwet's AC2 Results

| Measure | AC2 | Bootstrap 95% CI | P_o | P_e | Targets | Raters | Dropped targets |
|---|---|---|---|---|---|---|---|
| Q_M (five ordinal percentage bands) | 0.784 | [0.735, 0.839] | 0.958 | 0.807 | 10 | 11 | none |
| Q_C (five ordinal percentage bands) | 0.637 | [0.435, 0.798] | 0.905 | 0.737 | 10 | 11 | none |
| Residual effectiveness (five ordinal percentage bands) | 0.568 | [0.486, 0.677] | 0.899 | 0.767 | 6 | 11 | A5.34 + A5.12 UND A5.13 |

The AC2 confidence intervals are target-level percentile bootstrap intervals based on 10000 resamples and are reported as supplementary descriptive uncertainty estimates.

## Category Proportions Used for AC2

| Band | Q_M (five ordinal percentage bands) | Q_C (five ordinal percentage bands) | Residual effectiveness (five ordinal percentage bands) |
|---|---|---|---|
| [0,10] | 0.082 | 0.073 | 0.242 |
| (10,25] | 0.291 | 0.045 | 0.136 |
| (25,50] | 0.582 | 0.209 | 0.364 |
| (50,75] | 0.045 | 0.382 | 0.182 |
| (75,100] | 0 | 0.291 | 0.076 |

## Interpretation Notes

- `Q_M` and `Q_C` ICC values are based on raw percentage estimates.
- AC2 is based on the five a-priori percentage bands, not raw percentages.
- `Q_T` is not included in the AC2 analysis because its zero category is semantically distinct.
- No p-values are reported for ICC or AC2 in this file.
- The Markdown appendix below contains the exact matrices used for the analyses.

## Appendix A: Raw ICC Input Matrices

### Q_T: Maturity Threshold

| Target | expert_1 | expert_2 | expert_3 | expert_4 | expert_5 | expert_6 | expert_7 | expert_8 | expert_9 | expert_10 | expert_11 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| A8.28 | 3 | 3 | 3 | 2 | 2 | 2 | 4 | 2 | 3 | 2 | 2 |
| A8.16 | 2 | 2 | 3 | 2 | 0 | 2 | 4 | 2 | 2 | 2 | 2 |
| A8.12 | 3 | 3 | 3 | 2 | 3 | 2 | 3 | 2 | 3 | 3 | 2 |
| A8.24 | 2 | 3 | 3 | 2 | 2 | 2 | 3 | 2 | 2 | 1 | 2 |
| A5.16 | 3 | 3 | 3 | 2 | 2 | 2 | 4 | 2 | 3 | 3 | 2 |
| A8.15 | 4 | 2 | 3 | 2 | 0 | 2 | 3 | 3 | 3 | 2 | 2 |
| A5.17 | 2 | 3 | 3 | 2 | 2 | 2 | 4 | 2 | 2 | 2 | 2 |
| A5.34 | 4 | 3 | 3 | 2 | 4 | 2 | 4 | 2 | 3 | 2 | 2 |
| A8.5 | 3 | 3 | 3 | 2 | 2 | 2 | 3 | 3 | 3 | 2 | 2 |
| A5.15 | 3 | 3 | 3 | 2 | 2 | 2 | 3 | 3 | 2 | 2 | 2 |

### Q_M: Reduction at Maturity Level 3 (%)

| Target | expert_1 | expert_2 | expert_3 | expert_4 | expert_5 | expert_6 | expert_7 | expert_8 | expert_9 | expert_10 | expert_11 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| A8.28 | 60 | 50 | 50 | 40 | 50 | 45 | 40 | 50 | 50 | 45 | 30 |
| A8.16 | 30 | 0 | 10 | 20 | 0 | 30 | 20 | 5 | 25 | 30 | 25 |
| A8.12 | 70 | 50 | 50 | 40 | 50 | 35 | 50 | 50 | 50 | 25 | 35 |
| A8.24 | 20 | 75 | 70 | 40 | 60 | 35 | 50 | 25 | 50 | 40 | 45 |
| A5.16 | 40 | 50 | 50 | 40 | 50 | 25 | 50 | 50 | 25 | 15 | 45 |
| A8.15 | 50 | 0 | 10 | 10 | 0 | 30 | 20 | 5 | 25 | 15 | 20 |
| A5.17 | 30 | 50 | 30 | 20 | 50 | 30 | 40 | 15 | 25 | 30 | 15 |
| A5.34 | 20 | 50 | 50 | 25 | 20 | 30 | 40 | 20 | 25 | 20 | 30 |
| A8.5 | 50 | 50 | 50 | 20 | 50 | 30 | 50 | 50 | 25 | 25 | 40 |
| A5.15 | 40 | 50 | 50 | 20 | 50 | 40 | 20 | 15 | 25 | 15 | 40 |

### Q_C: Reduction at Maturity Level 5 (%)

| Target | expert_1 | expert_2 | expert_3 | expert_4 | expert_5 | expert_6 | expert_7 | expert_8 | expert_9 | expert_10 | expert_11 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| A8.28 | 90 | 95 | 80 | 80 | 80 | 70 | 75 | 80 | 75 | 70 | 55 |
| A8.16 | 80 | 0 | 10 | 30 | 0 | 60 | 20 | 10 | 25 | 55 | 35 |
| A8.12 | 85 | 95 | 80 | 70 | 99 | 60 | 80 | 90 | 75 | 50 | 65 |
| A8.24 | 80 | 95 | 80 | 70 | 80 | 70 | 60 | 75 | 75 | 60 | 70 |
| A5.16 | 85 | 95 | 80 | 60 | 60 | 60 | 50 | 85 | 50 | 30 | 40 |
| A8.15 | 60 | 0 | 10 | 30 | 0 | 70 | 20 | 10 | 50 | 25 | 25 |
| A5.17 | 85 | 95 | 80 | 60 | 60 | 50 | 80 | 50 | 50 | 50 | 45 |
| A5.34 | 40 | 95 | 80 | 50 | 50 | 60 | 50 | 75 | 75 | 40 | 65 |
| A8.5 | 90 | 95 | 80 | 60 | 60 | 50 | 70 | 55 | 75 | 45 | 55 |
| A5.15 | 70 | 95 | 80 | 50 | 60 | 60 | 70 | 75 | 75 | 30 | 60 |

## Appendix B: Banded AC2 Input Matrices

### Q_M Bands

| Target | expert_1 | expert_2 | expert_3 | expert_4 | expert_5 | expert_6 | expert_7 | expert_8 | expert_9 | expert_10 | expert_11 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| A8.28 | (50,75] | (25,50] | (25,50] | (25,50] | (25,50] | (25,50] | (25,50] | (25,50] | (25,50] | (25,50] | (25,50] |
| A8.16 | (25,50] | [0,10] | [0,10] | (10,25] | [0,10] | (25,50] | (10,25] | [0,10] | (10,25] | (25,50] | (10,25] |
| A8.12 | (50,75] | (25,50] | (25,50] | (25,50] | (25,50] | (25,50] | (25,50] | (25,50] | (25,50] | (10,25] | (25,50] |
| A8.24 | (10,25] | (50,75] | (50,75] | (25,50] | (50,75] | (25,50] | (25,50] | (10,25] | (25,50] | (25,50] | (25,50] |
| A5.16 | (25,50] | (25,50] | (25,50] | (25,50] | (25,50] | (10,25] | (25,50] | (25,50] | (10,25] | (10,25] | (25,50] |
| A8.15 | (25,50] | [0,10] | [0,10] | [0,10] | [0,10] | (25,50] | (10,25] | [0,10] | (10,25] | (10,25] | (10,25] |
| A5.17 | (25,50] | (25,50] | (25,50] | (10,25] | (25,50] | (25,50] | (25,50] | (10,25] | (10,25] | (25,50] | (10,25] |
| A5.34 | (10,25] | (25,50] | (25,50] | (10,25] | (10,25] | (25,50] | (25,50] | (10,25] | (10,25] | (10,25] | (25,50] |
| A8.5 | (25,50] | (25,50] | (25,50] | (10,25] | (25,50] | (25,50] | (25,50] | (25,50] | (10,25] | (10,25] | (25,50] |
| A5.15 | (25,50] | (25,50] | (25,50] | (10,25] | (25,50] | (25,50] | (10,25] | (10,25] | (10,25] | (10,25] | (25,50] |

### Q_C Bands

| Target | expert_1 | expert_2 | expert_3 | expert_4 | expert_5 | expert_6 | expert_7 | expert_8 | expert_9 | expert_10 | expert_11 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| A8.28 | (75,100] | (75,100] | (75,100] | (75,100] | (75,100] | (50,75] | (50,75] | (75,100] | (50,75] | (50,75] | (50,75] |
| A8.16 | (75,100] | [0,10] | [0,10] | (25,50] | [0,10] | (50,75] | (10,25] | [0,10] | (10,25] | (50,75] | (25,50] |
| A8.12 | (75,100] | (75,100] | (75,100] | (50,75] | (75,100] | (50,75] | (75,100] | (75,100] | (50,75] | (25,50] | (50,75] |
| A8.24 | (75,100] | (75,100] | (75,100] | (50,75] | (75,100] | (50,75] | (50,75] | (50,75] | (50,75] | (50,75] | (50,75] |
| A5.16 | (75,100] | (75,100] | (75,100] | (50,75] | (50,75] | (50,75] | (25,50] | (75,100] | (25,50] | (25,50] | (25,50] |
| A8.15 | (50,75] | [0,10] | [0,10] | (25,50] | [0,10] | (50,75] | (10,25] | [0,10] | (25,50] | (10,25] | (10,25] |
| A5.17 | (75,100] | (75,100] | (75,100] | (50,75] | (50,75] | (25,50] | (75,100] | (25,50] | (25,50] | (25,50] | (25,50] |
| A5.34 | (25,50] | (75,100] | (75,100] | (25,50] | (25,50] | (50,75] | (25,50] | (50,75] | (50,75] | (25,50] | (50,75] |
| A8.5 | (75,100] | (75,100] | (75,100] | (50,75] | (50,75] | (25,50] | (50,75] | (50,75] | (50,75] | (25,50] | (50,75] |
| A5.15 | (50,75] | (75,100] | (75,100] | (25,50] | (50,75] | (50,75] | (50,75] | (50,75] | (50,75] | (25,50] | (50,75] |

### Residual Effectiveness Bands

| Target | expert_1 | expert_2 | expert_3 | expert_4 | expert_5 | expert_6 | expert_7 | expert_8 | expert_9 | expert_10 | expert_11 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| A5.34 + A5.12 | (25,50] | (50,75] | (50,75] | (10,25] | (25,50] | (25,50] | (25,50] | (10,25] | (25,50] | (25,50] | (50,75] |
| A5.34 + A5.13 | (10,25] | (50,75] | (75,100] | (25,50] | (75,100] | (50,75] | (25,50] | (25,50] | (25,50] | (50,75] | (75,100] |
| A5.34 + A5.12 UND A5.13 | (25,50] | (50,75] | (25,50] | — | (25,50] | (25,50] | (25,50] | (10,25] | (25,50] | (25,50] | (50,75] |
| A5.34 + A5.17 | (25,50] | (25,50] | (25,50] | (25,50] | (25,50] | (50,75] | (25,50] | (10,25] | (10,25] | (50,75] | (75,100] |
| A5.34 + A5.26 | (25,50] | (50,75] | (25,50] | (10,25] | (75,100] | (25,50] | (25,50] | (10,25] | (25,50] | (50,75] | (50,75] |
| A8.16 + A8.15 | (25,50] | [0,10] | [0,10] | [0,10] | (10,25] | [0,10] | [0,10] | [0,10] | [0,10] | [0,10] | (25,50] |
| A8.16 + A8.15 UND A5.25 | (50,75] | [0,10] | [0,10] | [0,10] | (10,25] | [0,10] | [0,10] | [0,10] | [0,10] | [0,10] | (25,50] |

