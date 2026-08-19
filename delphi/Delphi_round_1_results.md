# Delphi Round 1 Results

## Overview

- Input file: `que_1.xlsx`
- Evaluated sheet: `answer`
- Number of evaluated responses: 11
- Top-10 scoring method: rank-based scoring
  - Top 1 = 10 points
  - Top 2 = 9 points
  - Top 3 = 8 points
  - Top 4 = 7 points
  - Top 5 = 6 points
  - Top 6 = 5 points
  - Top 7 = 4 points
  - Top 8 = 3 points
  - Top 9 = 2 points
  - Top 10 = 1 point
- Dependency scoring method: unweighted frequency count

## Weighted Top Controls

| Rank | Control | Weighted score | Mentions | Average rank score |
| --- | --- | --- | --- | --- |
| 1 | A8.28 | 56 | 7 | 8.0 |
| 2 | A8.16 | 52 | 9 | 5.78 |
| 3 | A8.12 | 49 | 7 | 7.0 |
| 4 | A8.24 | 40 | 6 | 6.67 |
| 5 | A5.16 | 39 | 6 | 6.5 |
| 6 | A8.15 | 38 | 8 | 4.75 |
| 7 | A5.17 | 37 | 4 | 9.25 |
| 8 | A5.34 | 33 | 6 | 5.5 |
| 9 | A8.5 | 29 | 4 | 7.25 |
| 10 | A5.15 | 23 | 3 | 7.67 |
| 11 | A8.9 | 22 | 3 | 7.33 |
| 12 | A8.26 | 20 | 4 | 5.0 |
| 13 | A5.26 | 20 | 2 | 10.0 |
| 14 | A5.18 | 19 | 3 | 6.33 |
| 15 | A8.29 | 13 | 3 | 4.33 |
| 16 | A8.8 | 9 | 2 | 4.5 |
| 17 | A5.12 | 9 | 1 | 9.0 |
| 18 | A5.27 | 8 | 1 | 8.0 |
| 19 | A8.25 | 7 | 1 | 7.0 |
| 20 | A8.2 | 6 | 1 | 6.0 |
| 21 | A8.27 | 5 | 1 | 5.0 |
| 22 | A8.7 | 4 | 1 | 4.0 |
| 23 | A8.11 | 3 | 1 | 3.0 |
| 24 | A8.3 | 3 | 1 | 3.0 |
| 25 | A5.28 | 2 | 1 | 2.0 |


## Grouped Dependency Statements

| Rank | Dependency | Frequency |
| --- | --- | --- |
| 1 | A8.16->A8.15 | 6 |
| 2 | A5.34->A5.12 | 3 |
| 3 | A8.28->A5.15 | 3 |
| 4 | A8.24->A8.25 | 2 |
| 5 | A8.28->A8.8 | 2 |
| 6 | A5.15->A5.16 | 1 |
| 7 | A5.15->A5.16+A5.18 | 1 |
| 8 | A5.16->A5.18 | 1 |
| 9 | A5.16->A5.7+A5.25+A5.26 | 1 |
| 10 | A5.17->A5.16 | 1 |
| 11 | A5.18->A5.15 | 1 |
| 12 | A5.24->A5.25 | 1 |
| 13 | A5.24-A5.28->A8.15/A8.16 | 1 |
| 14 | A5.26->A5.24+A5.25+A8.15/A8.16 | 1 |
| 15 | A5.27->A5.24+A6.3 | 1 |
| 16 | A5.28->A8.15 | 1 |
| 17 | A5.28->A8.15+A8.16 | 1 |
| 18 | A5.34->A5.12+A5.13 | 1 |
| 19 | A5.34->A5.26 | 1 |
| 20 | A5.8->A5.16 | 1 |
| 21 | A8.11->A5.12 | 1 |
| 22 | A8.11->A5.12+A5.34 | 1 |
| 23 | A8.11->A8.24 | 1 |
| 24 | A8.12->A5.12 | 1 |
| 25 | A8.12->A5.12+A5.13+A5.34 | 1 |
| 26 | A8.12->A5.15 | 1 |
| 27 | A8.12->A5.3+A8.1 | 1 |
| 28 | A8.12->A8.16 | 1 |
| 29 | A8.15->A5.17 | 1 |
| 30 | A8.15->A8.16 | 1 |
| 31 | A8.15->A8.26 | 1 |
| 32 | A8.16->A8.15+A5.25 | 1 |
| 33 | A8.2->A5.18+A5.17 | 1 |
| 34 | A8.24->A5.17+A5.31 | 1 |
| 35 | A8.24->A8.5 | 1 |
| 36 | A8.24->A8.9 | 1 |
| 37 | A8.25->A5.8 | 1 |
| 38 | A8.26->A5.8 | 1 |
| 39 | A8.27->A5.8 | 1 |
| 40 | A8.28->A5.8 | 1 |
| 41 | A8.28->A8.29 | 1 |
| 42 | A8.28->A8.9 | 1 |
| 43 | A8.29->A5.8 | 1 |
| 44 | A8.29->A8.25 | 1 |
| 45 | A8.5->A5.16 | 1 |
| 46 | A8.5->A5.17 | 1 |
| 47 | A8.8->A5.8 | 1 |


## Atomic Dependency Edges

| Rank | Source | Target | Type | Frequency |
| --- | --- | --- | --- | --- |
| 1 | A8.16 | A8.15 | REQUIRED | 7 |
| 2 | A5.34 | A5.12 | REQUIRED | 4 |
| 3 | A8.28 | A5.15 | REQUIRED | 3 |
| 4 | A5.15 | A5.16 | REQUIRED | 2 |
| 5 | A5.26 | A8.15 | OR_PART | 2 |
| 6 | A5.26 | A8.16 | OR_PART | 2 |
| 7 | A5.28 | A8.15 | REQUIRED | 2 |
| 8 | A8.11 | A5.12 | REQUIRED | 2 |
| 9 | A8.12 | A5.12 | REQUIRED | 2 |
| 10 | A8.24 | A8.25 | REQUIRED | 2 |
| 11 | A8.28 | A8.8 | REQUIRED | 2 |
| 12 | A5.15 | A5.18 | REQUIRED | 1 |
| 13 | A5.16 | A5.18 | REQUIRED | 1 |
| 14 | A5.16 | A5.25 | REQUIRED | 1 |
| 15 | A5.16 | A5.26 | REQUIRED | 1 |
| 16 | A5.16 | A5.7 | REQUIRED | 1 |
| 17 | A5.17 | A5.16 | REQUIRED | 1 |
| 18 | A5.18 | A5.15 | REQUIRED | 1 |
| 19 | A5.24 | A5.25 | REQUIRED | 1 |
| 20 | A5.24 | A8.15 | OR_PART | 1 |
| 21 | A5.24 | A8.16 | OR_PART | 1 |
| 22 | A5.25 | A8.15 | OR_PART | 1 |
| 23 | A5.25 | A8.16 | OR_PART | 1 |
| 24 | A5.26 | A5.24 | REQUIRED | 1 |
| 25 | A5.26 | A5.25 | REQUIRED | 1 |
| 26 | A5.27 | A5.24 | REQUIRED | 1 |
| 27 | A5.27 | A6.3 | REQUIRED | 1 |
| 28 | A5.27 | A8.15 | OR_PART | 1 |
| 29 | A5.27 | A8.16 | OR_PART | 1 |
| 30 | A5.28 | A8.15 | OR_PART | 1 |
| 31 | A5.28 | A8.16 | OR_PART | 1 |
| 32 | A5.28 | A8.16 | REQUIRED | 1 |
| 33 | A5.34 | A5.13 | REQUIRED | 1 |
| 34 | A5.34 | A5.26 | REQUIRED | 1 |
| 35 | A5.8 | A5.16 | REQUIRED | 1 |
| 36 | A8.11 | A5.34 | REQUIRED | 1 |
| 37 | A8.11 | A8.24 | REQUIRED | 1 |
| 38 | A8.12 | A5.13 | REQUIRED | 1 |
| 39 | A8.12 | A5.15 | REQUIRED | 1 |
| 40 | A8.12 | A5.3 | REQUIRED | 1 |
| 41 | A8.12 | A5.34 | REQUIRED | 1 |
| 42 | A8.12 | A8.1 | REQUIRED | 1 |
| 43 | A8.12 | A8.16 | REQUIRED | 1 |
| 44 | A8.15 | A5.17 | REQUIRED | 1 |
| 45 | A8.15 | A8.16 | REQUIRED | 1 |
| 46 | A8.15 | A8.26 | REQUIRED | 1 |
| 47 | A8.16 | A5.25 | REQUIRED | 1 |
| 48 | A8.2 | A5.17 | REQUIRED | 1 |
| 49 | A8.2 | A5.18 | REQUIRED | 1 |
| 50 | A8.24 | A5.17 | REQUIRED | 1 |
| 51 | A8.24 | A5.31 | REQUIRED | 1 |
| 52 | A8.24 | A8.5 | REQUIRED | 1 |
| 53 | A8.24 | A8.9 | REQUIRED | 1 |
| 54 | A8.25 | A5.8 | REQUIRED | 1 |
| 55 | A8.26 | A5.8 | REQUIRED | 1 |
| 56 | A8.27 | A5.8 | REQUIRED | 1 |
| 57 | A8.28 | A5.8 | REQUIRED | 1 |
| 58 | A8.28 | A8.29 | REQUIRED | 1 |
| 59 | A8.28 | A8.9 | REQUIRED | 1 |
| 60 | A8.29 | A5.8 | REQUIRED | 1 |
| 61 | A8.29 | A8.25 | REQUIRED | 1 |
| 62 | A8.5 | A5.16 | REQUIRED | 1 |
| 63 | A8.5 | A5.17 | REQUIRED | 1 |
| 64 | A8.8 | A5.8 | REQUIRED | 1 |


## OR Dependencies

| Rank | Source | Alternative targets | Frequency |
| --- | --- | --- | --- |
| 1 | A5.26 | A8.15/A8.16 | 2 |
| 2 | A5.24 | A8.15/A8.16 | 1 |
| 3 | A5.25 | A8.15/A8.16 | 1 |
| 4 | A5.27 | A8.15/A8.16 | 1 |
| 5 | A5.28 | A8.15/A8.16 | 1 |


## Invalid or Unparsed Dependency Entries

_No entries found._

