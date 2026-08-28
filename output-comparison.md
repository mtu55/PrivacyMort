# Output Comparison

All xlsx files were checked with the xlsx comparator scripts: 
- [Comparison with last commited version](utils/xlsx-git-comparator.py).
- [Comparison with different file](utils/xlsx-local-comparator.py)

| Script                                        | Changes | If changed: Commmited | Comment                                                                              |
|-----------------------------------------------|---------|-----------------------|--------------------------------------------------------------------------------------|
| scripts/assets.py                             | Yes     | cb65a4b5              | At least label changes                                                               |
| scripts/label.py                              | No      |                       |                                                                                      |
| scripts/scenarios_final.py                    | No      |                       |                                                                                      |
| scripts/quality_check/adid_pattern.py         | No      |                       |                                                                                      |
| scripts/quality_check/databaseStability.py    | Yes     | 4abd3916              | n_incidents: 2037 => 2035                                                            |
| scripts/quality_check/description_quality.py  | No      |                       | File moved (not commmited)                                                           |
| scripts/quality_check/explore_keywords.py     | No      |                       |                                                                                      |
| scripts/quality_check/kfold_validation.py     | No      |                       |                                                                                      |
| scripts/quality_check/sampleCheck.py          | No      |                       |                                                                                      |
| scripts/quality_check/sensitivity_analysis.py | Yes     | bdf773b5              | At least label changes + tex                                                         |
| scripts/quality_check/severity_scale.py       | No      |                       | Result in results/archive/severity_sensitivity_v8.xlsx. Is this (archive) by design? |
| delphi/delphi2_reliability.py                 | Error   |                       | KeyError: 'Column not found: Verbleibende operative Wirksamkeit A5.34 + A5.12'       |
| delphi/delphi2_results_builder.py             | Yes     | 0859ab47              | see md/json                                                                          |
| delphi/delphi2_validation_checks.py           | Yes     | 768894a5              | see md/json                                                                          |
| delphi/delphi_1.py                            | No      |                       |                                                                                      |
| delphi/delphi_sample.py                       | No      |                       |                                                                                      |

