# Rating Mapping Documentation

## Keyword Tiers

Both data sources use the same three keyword lists to classify exposed data types.
Each `DataClass` / description term is matched case-insensitively against these tiers:

| Tier | Examples |
|---|---|
| **High** | `email addresses`, `names`, `phone numbers`, `physical addresses`, `social security numbers`, `credit cards`, `government issued ids`, `auth tokens`, `passport numbers`, `ip addresses` |
| **Medium** | `passwords`, `dates of birth`, `geographic location`, `financial transactions`, `profile photos`, `historical passwords`, `marital statuses`, `races` |
| **Low** | `genders`, `occupations`, `purchasing habits`, `account balances`, `payment methods`, `job applications`, `vehicle details`, `time zones` |

Additionally, `sensitiveKeywords` covers special-category data:
`physical attributes`, `private messages`, `sexual orientations`, `nationalities`, `ethnicities`, `races`, `personal health data`, `health insurance information`

---

## HIBP

### Level of Identification

Based on keyword tier matches in `DataClasses`.

| Condition | Grade |
|---|---|
| `high > 2` | `2` |
| `high >= 1` or `medium > 2` | `1` |
| `medium >= 1` or `low >= 1` | `0` |
| No matches | `-1` |

### Level of Data Exposure

Based on HIBP flags.

| Condition | Grade |
|---|---|
| `IsSubscriptionFree` | `2` |
| None of `IsSpamList`, `IsMalware`, `IsStealerLog` | `0` |
| 1–2 of those flags set | `1` |
| All 3 flags set | `2` |

### Data Sensitivity

Based on `IsSensitive` flag and `sensitiveKeywords` matches.

| Condition | Grade |
|---|---|
| `IsSensitive === false` | `0` |
| `IsSensitive` and ≥ 1 sensitive keyword match | `1` |
| `IsSensitive` and no sensitive keyword match | `2` |

---

## EuRepoC

### Level of Identification

Based on keyword tier matches in the entry description.

| Condition | Grade |
|---|---|
| `high >= 2` | `2` |
| `high >= 1` or `medium >= 2` | `1` |
| `medium >= 1` or `low >= 1` | `0` |
| No matches | `-1` |

### Data Sensitivity

Based on the `data_theft` field string.

| Condition | Grade |
|---|---|
| `data_theft === 'none'` | `0` |
| Contains `'incident scores 1 points in intensity'` | `1` |
| Contains `'incident scores 2 points in intensity'` | `2` |
| Anything else | `-1` |