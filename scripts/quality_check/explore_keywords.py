"""
Keyword Explorer
================
Identifies frequent data-related terms in unlabeled incidents
to iteratively extend the keyword taxonomy in label.py.

Input:  data/processed/privacyrisq_labeled.xlsx
Output: prints ranked term frequencies to console
"""

import pandas as pd
import re
from collections import Counter
from pathlib import Path

# === CONFIGURATION ===
INPUT_FILE = Path(__file__).parent.parent.parent / "data" / "processed" / "privacyrisq_labeled_final.xlsx"
# todo privacyrisq_cleaned according to readme which leads to errors.
#  Path problem was fixed => now: either change code below to match privacyrisq_cleaned or update readme

# Terms to scan for in unlabeled descriptions
TARGETS = [
    'record', 'records', 'customer', 'customers', 'employee', 'employees',
    'user', 'users', 'citizen', 'citizens', 'client', 'clients',
    'account', 'accounts', 'database', 'databases', 'leaked', 'leak',
    'exfiltrated', 'stolen', 'exposed', 'breach', 'breached',
    'sensitive', 'confidential', 'SSN', 'DOB', 'PII',
    'voter', 'taxpayer', 'subscriber', 'member', 'identity',
    'identities', 'document', 'documents', 'file', 'files',
]

if __name__ == "__main__":
    df = pd.read_excel(INPUT_FILE)
    df = df[df['Description'].notna()]

    unlabeled = df[
        (df['has_personal_data'] == 0) &
        (df['has_special_categories'] == 0) &
        (df['has_credentials'] == 0)
    ]
    print(f"Unlabeled incidents: {len(unlabeled)}\n")

    counts = Counter()
    for text in unlabeled['Description']:
        text_lower = str(text).lower()
        for term in TARGETS:
            if re.search(r'\b' + term.lower() + r'\b', text_lower):
                counts[term] += 1

    print(f"{'Count':>6}  Term")
    print("-" * 20)
    for term, count in counts.most_common():
        print(f"{count:>6}  {term}")