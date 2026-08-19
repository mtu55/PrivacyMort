"""
Privacy Incident Data Labeling Pipeline
========================================
Applies keyword-based GDPR data category labeling to cleaned incidents.

Input:  data/processed/privacyrisq_cleaned.xlsx
Output: data/processed/privacyrisq_labeled.xlsx
"""

import pandas as pd
import re
from pathlib import Path

# === CONFIGURATION ===
INPUT_FILE  = Path(__file__).parent.parent / "data" / "processed" / "privacyrisq_cleaned.xlsx"
OUTPUT_FILE = Path(__file__).parent.parent / "data" / "processed" / "privacyrisq_labeled_final.xlsx"


# === REGEX PATTERNS ===

personal_data_patterns = [
    # Identification Data
    r"\bfull\s?names?\b", r"\breal\s?names?\b", r"\bdisplay\s?names?\b",
    r"\busernames?\b", r"\bscreen\s?names?\b", r"\bplayer\s?names?\b",

    # Contact Data
    r"\bemails?\s?address\w*\b", r"\be-?mails?\b",
    r"\bphone\s?numbers?\b", r"\btelephone\b",
    r"\bhome\s?address\w*\b", r"\bphysical\s?address\w*\b",
    r"\bpostal\s?address\w*\b", r"\bmailing\s?address\w*\b",
    r"\bpost\s?codes?\b", r"\bzip\s?codes?\b",

    # Online Identifiers
    r"\bIP\s?address\w*\b",
    r"\bsocial\s?media\s?profiles?\b", r"\bsocial\s?media\s?accounts?\b",
    r"\bFacebook\s?(profile|account|data|ID)\w*\b",
    r"\bLinkedIn\s?(profile|account|data)\w*\b",
    r"\buser\s?IDs?\b", r"\baccount\s?IDs?\b",
    r"\bonline\s?identifiers?\b",
    r"\badvertising\s?(?:identifiers?|IDs?)\b",

    # Location Data
    r"\blocation\s?data\b", r"\bGPS\s?locations?\b",
    r"\bgeolocation\w*\b", r"\blatitudes?\b", r"\blongitudes?\b",
    r"\btime\s?zones?\b",

    # Demographic Data
    r"\bgenders?\b", r"\bdates?\s?of\s?birth\b", r"\bDOB\b",
    r"\bnationalit(y|ies)\b", r"\bmarital\s?status\w*\b",

    # Physical Characteristics
    r"\bphysical\s?attributes?\b",
    r"\bprofile\s?photos?\b",

    # Professional Data
    r"\bjob\s?titles?\b", r"\bemployers?\b", r"\bplaces?\s?of\s?employment\b",
    r"\bsalar(y|ies)\b", r"\bsalary\s?grades?\b",
    r"\bjob\s?applications?\b", r"\bcover\s?letters?\b",
    r"\bincome\s?levels?\b", r"\bincomes?\b", r"\bpayrolls?\b",

    # Financial Data
    r"\bcredit\s?cards?\s?(data|numbers?|details?)?\b",
    r"\blast\s?4\s?digits\b", r"\bexpiry\s?dates?\b",
    r"\bbank\s?account\s?numbers?\b", r"\bbank\s?accounts?\b",
    r"\bIBAN\w*\b", r"\border\s?histor(y|ies)\b",
    r"\baccount\s?balances?\b", r"\bdonation\s?amounts?\b",
    r"\bcryptocurrenc(y|ies)\s?wallet\w*\b", r"\bwallet\s?address\w*\b",

    # Identification Numbers
    r"\bsocial\s?security\s?numbers?\b", r"\bSSNs?\b",
    r"\bpassport\s?numbers?\b", r"\bpassports?\b",
    r"\bgovernment[\s-]?issued?\s?IDs?\b", r"\bgovernment\s?IDs?\b",
    r"\bAadhaar\s?numbers?\b", r"\bAadhaar\b",
    r"\bdriver.?s?\s?licen[cs]e\s?numbers?\b", r"\bdriver.?s?\s?licen[cs]es?\b",
    r"\bVIN\s?numbers?\b",
    r"\binsurance\s?numbers?\b", r"\bnational\s?IDs?\b",
    r"\btax\s?(ID|number|address)\w*\b",

    # Communication Data
    r"\bprivate\s?messages?\b", r"\bdirect\s?messages?\b",
    r"\bchat\s?logs?\b", r"\bchat\s?histor(y|ies)\b",
    r"\bforum\s?posts?\b", r"\bsupport\s?tickets?\b",

    # Device Data
    r"\bdevice\s?(information|make|model|IDs?|identifiers?)\b",
    r"\bIMSI\s?numbers?\b", r"\bIMSI\b", r"\bIMEI\b",
    r"\bserial\s?numbers?\b",
    r"\bbrowser\s?user\s?agents?\b", r"\buser\s?agents?\b",
    r"\bcomputer\s?names?\b",

    # Social and Cultural Data
    r"\bpolitical\s?views?\b", r"\beducation\s?levels?\b",
    r"\brelationship\s?status\w*\b",

    # Other Personal Data
    r"\bregistration\s?plates?\b", r"\blicen[cs]e\s?plates?\b",
    r"\btravel\s?histor(y|ies)\b",
    r"\bloyalty\s?program\w*\b",

    # General Personal Data References
    r"\bpersonal\s?(data|information|details)\b", r"\bPII\b",
    r"\bsensitive\s+(data|information)\b",
    r"\bcustomer\s?(data|records?|information|details|database)\b",
    r"\bcustomer\w*\b",
    r"\bemployee\s?(data|records?|information|details|database)\b",
    r"\bemployee\w*\b",
    r"\bcitizen\s?(data|records?|information)\b", r"\bcitizens?\b",
    r"\buser\s?(data|records?|information|details|database|profiles?)\b",
    r"\bvoter\s?(data|records?|information|rolls?)\b",
    r"\bsubscriber\s?(data|records?|information)\b",
    r"\bpatient\s?(data|records?|information)\b",
    r"\bpersonal\s?records?\b", r"\bcustomer\s?records?\b",
    r"\buser\s?records?\b", r"\bmedical\s?records?\b",
    r"\bexfiltrat\w*\b",
    r"\bidentit(y|ies)\s?(theft|fraud|data|information)\b",
]

special_categories_patterns = [
    # Health Data
    r"\bmedical\s?(information|data|records?|histor(y|ies))?\b",
    r"\bpatient\s?(conditions?|data|records?|information)\b",
    r"\bpatients?\b",
    r"\bdiagnos\w*\b", r"\bclinical\s?data\b", r"\bclinical\b",
    r"\bpsychotherap(y|ist|ists)\b", r"\bpsychotherapy\s?session\w*\b",
    r"\bhealth[\s-]?related\s?(data|information)\b",
    r"\bhealth\s?(data|information|records?|conditions?)\b",
    r"\bhealthcare\s?(data|records?|information)\b",
    r"\bprescriptions?\b", r"\bmedication\w*\b",

    # Biometric Data
    r"\bfacial\s?(images?|recognition|scans?|data)\b",
    r"\bbiometric\s?(data|identifiers?|information)?\b",
    r"\bfingerprints?\b", r"\bface\s?scans?\b",
    r"\biris\s?scans?\b", r"\bretina\s?scans?\b",

    # Genetic Data
    r"\bDNA\b", r"\bgenetic\s?(data|information|testing)\b",

    # Sexual Orientation / Sex Life
    r"\bsexual\s?orientations?\b",
    r"\bLGBTQ\w*\b",
    r"\bescort\s?(data|services?|site)\b",

    # Political Opinions
    r"\bpolitical\s?(views?|opinions?|beliefs?|party|parties|membership|affiliation)\b",

    # Religious or Philosophical Beliefs
    r"\breligious\s?(beliefs?|views?|affiliation)?\b",
    r"\breligions?\b",

    # Trade Union Membership
    r"\btrade\s?union\s?(membership|data|affiliation)\b",
    r"\btrade\s?unions?\b",

    # Racial or Ethnic Origin
    r"\bethnicit(y|ies)\b", r"\bethnic\s?(origins?|data|background)\b",
    r"\bracial\s?(data|origins?|background)?\b", r"\bracial\b",
]

credentials_patterns = [
    # Hashed Passwords
    r"\bMD5\s?hash\w*\b", r"\bMD5\b", r"\bsalted\s?MD5\b",
    r"\bSHA-?1\b", r"\bsalted\s?SHA-?1\b",
    r"\bSHA-?256\b", r"\bSHA-?512\b", r"\bSHA-?\d+\b",
    r"\bbcrypt\s?hash\w*\b", r"\bbcrypt\b",
    r"\bPBKDF2\b", r"\bargon2\b", r"\bphpass\b",
    r"\bscrypt\b", r"\bmd5crypt\b",
    r"\bNTLM\s?hash\w*\b", r"\bNTLM\b",
    r"\bhashed\s?passwords?\b",

    # Plaintext Passwords
    r"\bplain\s?text\s?passwords?\b", r"\bplaintext\s?passwords?\b",
    r"\bcracked\s?passwords?\b",
    r"\bpasswords?\b",

    # Authentication Tokens
    r"\bauth\s?tokens?\b", r"\bauthentication\s?tokens?\b",
    r"\baccess\s?tokens?\b", r"\breset\s?tokens?\b",
    r"\bpassword\s?reset\s?tokens?\b",

    # Two-Factor Authentication Data
    r"\b2FA\s?(secrets?|codes?|data)?\b", r"\b2FA\b",
    r"\btwo[\s-]?factor\b", r"\bbackup\s?codes?\b", r"\bMFA\b",

    # Security Questions
    r"\bsecurity\s?questions?\b",

    # API and Cryptographic Keys
    r"\bmnemonic\s?phrases?\b", r"\bmnemonics?\b",
    r"\bencrypted\s?master\s?keys?\b", r"\bmaster\s?keys?\b",
    r"\bencrypted\s?recovery\s?keys?\b", r"\brecovery\s?keys?\b",
    r"\bAPI\s?keys?\b", r"\bprivate\s?keys?\b",

    # Stealer Logs
    r"\bstealer\s?logs?\b", r"\bstealers?\b", r"\binfostealers?\b",
    r"\bcredentials?\b", r"\bbrowser\s?fingerprints?\b",
    r"\blogins?\b",
]


# === FUNCTIONS ===

def has_keyword_regex(text, patterns):
    if pd.isna(text):
        return 0
    return 1 if any(re.search(p, str(text), re.IGNORECASE) for p in patterns) else 0


def label_data(df):
    df = df.copy()
    df['has_personal_data'] = df['Description'].apply(
        lambda x: has_keyword_regex(x, personal_data_patterns)
    )
    df['has_special_categories'] = df['Description'].apply(
        lambda x: has_keyword_regex(x, special_categories_patterns)
    )
    df['has_credentials'] = df['Description'].apply(
        lambda x: has_keyword_regex(x, credentials_patterns)
    )
    return df


# === MAIN ===

if __name__ == "__main__":
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    print(f"Loading: {INPUT_FILE}")
    df = pd.read_excel(INPUT_FILE)
    print(f"Loaded {len(df)} incidents\n")

    df = label_data(df)

    print(f"--- Label Distribution ---")
    print(f"has_personal_data=1:      {df['has_personal_data'].sum():>6}")
    print(f"has_special_categories=1: {df['has_special_categories'].sum():>6}")
    print(f"has_credentials=1:        {df['has_credentials'].sum():>6}")

    # === FILTER: incdidents with at least one datacategory ===
    before = len(df)
    df = df[
        (df['has_personal_data'] == 1) |
        (df['has_special_categories'] == 1) |
        (df['has_credentials'] == 1)
        ].reset_index(drop=True)
    removed = before - len(df)
    print(f"\n--- Data Category Filter ---")
    print(f"Removed {removed} incidents with no data category")
    print(f"Remaining: {len(df)} incidents")

    df.to_excel(OUTPUT_FILE, index=False)
    print(f"\nSaved to: {OUTPUT_FILE}")