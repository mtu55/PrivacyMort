# scripts/assets.py
# v8 – Asset classification for PrivacyMort incident dataset
#
# Classifies each incident description along three dimensions:
#   AssetTech:    technical asset type (ISO 27005:2022 Annex A, Table A.11)
#   AssetContext: organizational/sectoral context (NIS2 Annex I/II + 2 empirical)
#   TargetType:   whether the attack targeted an individual directly
#
# Classification is performed via keyword matching on free-text descriptions.
# Design principles:
#   - Word boundary anchors (\b) prevent substring matches (e.g. "cia" in "Activision")
#   - Trailing s? allows simple plural forms without a full stemmer
#   - Only compound nouns or acronyms are used as keywords; single generic nouns
#     are avoided to minimize false positives
#   - "Unknown" is a valid outcome and is never overridden by a default assignment
#   - Priority lists act as a tiebreaker when multiple categories match;
#     more specific categories take precedence over broader ones

import re
import pandas as pd
from collections import Counter


# ---------------------------------------------------------------------------
# CORE MATCHING
#
# Iterates over all categories and their keyword lists. For each category,
# the first matching keyword is sufficient to include that category as a
# candidate. If multiple categories match, the priority list determines the
# winner by scanning from the highest-priority end.
# ---------------------------------------------------------------------------

def _match(text_lower: str, keyword_dict: dict, priority: list) -> str:
    matched = []
    for cat, kws in keyword_dict.items():
        for kw in kws:
            # Compile pattern on the fly; re.escape handles hyphens and dots
            pattern = r'\b' + re.escape(kw.lower()) + r's?\b'
            if re.search(pattern, text_lower):
                matched.append(cat)
                break  # One match per category is enough; move to the next

    if not matched:
        return "Unknown"

    # reversed(priority) starts at the highest-priority category.
    # The first hit in that order wins.
    for cat in reversed(priority):
        if cat in matched:
            return cat

    # Fallback: return the first matched category if it is not in the
    # priority list at all (should not occur in normal operation)
    return matched[0]


# ---------------------------------------------------------------------------
# ASSETTECH KEYWORDS
# Reference: ISO 27005:2022 Annex A, Table A.11
#
# Four categories cover the principal technical asset types found in the
# incident corpus. The priority order ensures that a specific hardware or
# software match is not overridden by a broader infrastructure match.
# ---------------------------------------------------------------------------

ASSET_TECH_KEYWORDS = {
    # Third-party or cloud-hosted services where the asset is not owned
    # or operated by the affected organization itself
    "Services provided by supplier": [
        # Existing
        "third-party provider", "third-party vendor",
        "third party provider", "third party vendor",
        "supply chain attack",
        "managed service provider", "msp",
        "it service provider", "hosting provider",
        "cloud service provider", "saas platform",
        "software-as-a-service", "outsourc",
        "service provider",
        "cloud storage",
        "cloud infrastructure",
        "file sharing service", "file transfer service",
        "file sharing platform",
        "backup service", "backup provider",
        "managed backup", "cloud backup",
        # Breach location: specific cloud/SaaS platforms
        "amazon web services", "aws",
        "microsoft azure", "azure",
        "google cloud",
        "salesforce",
        # Breach location: hosting indicators
        "hosted on", "hosted by",
        "hosted with",
        # Breach location: external platform indicators
        "third-party platform", "third-party system",
        "third-party service",
        "external platform", "external provider",
        "external system",
        # Breach location: specific SaaS platforms common in incidents
        "activepipe", "moveit", "accellion",
        "fortra", "globalscape",
    ],
    # Network-layer assets: routing, switching, remote access, and
    # industrial/operational technology infrastructure
    "Network Infrastructure": [
        "router", "firewall", "vpn",
        "soho router",
        "network device", "network infrastructure",
        "network",
        "switch", "gateway",
        "scada", "ot system", "operational technology",
        "industrial control system",
        "data centre", "data center",
        "telecommunications provider", "telecom operator",
        "internet service provider", "broadband provider",
        "satellite service", "isp",
        "botnet",
        "rdp",
        "remote desktop",
        "remote access server",
        "ssh tunnel",
        "remote access tool",
    ],
    # Physical endpoint devices; matched before Software to avoid a
    # laptop being classified as a web application via generic terms
    "Hardware / Device": [
        "mobile phone", "mobile device", "smartphone",
        "personal phone",
        "laptop", "workstation",
        "usb drive", "usb stick",
        "medical device", "atm",
        "semiconductor", "chip manufacturer",
        "iot device", "hardware manufacturer",
        "personal device",
    ],
    # Application-layer assets: web applications, databases, identity
    # systems, and any software platform accessed by end users
    "Software / Web Application": [
        "website", "web application", "web server",
        "web portal", "online portal", "customer portal",
        "email server", "email system", "webmail",
        "email account", "email inbox", "inbox",
        "database", "sql",
        "social media account", "facebook page",
        "erp", "crm",
        "management software", "booking system",
        "mobile app", "online platform",
        "software developer", "software provider",
        "information system", "it system",
        "server", "platform", "portal", "app",
        "cloud platform", "cloud environment",
        "it infrastructure",
        "site",
        "active directory",
        "user account",
        "online account",
        "hr system", "hr platform",
        "ticketing system", "ticketing platform",
        "patient portal",
    ],
}

# Supplier services rank highest because the breach location takes
# precedence over the type of service the affected organization provides.
# If data was exfiltrated from a third-party or cloud-hosted system,
# the asset is classified as supplier-managed regardless of whether
# the organization also operates its own web application.
# Hardware is matched before Network Infrastructure and Software to
# prevent endpoint descriptions from being subsumed by broader categories.
ASSET_TECH_PRIORITY = [
    "Hardware / Device",
    "Network Infrastructure",
    "Software / Web Application",
    "Services provided by supplier",
]


# ---------------------------------------------------------------------------
# ASSETCONTEXT KEYWORDS
# Reference: NIS2 Directive (EU 2022/2555) Annex I/II (structural reference
# only, not applied normatively) + 2 empirically derived categories
#
# Keyword selection follows a strict compound-noun rule: single generic nouns
# (e.g. "city", "county", "state") are not used because they produce too many
# false positives. Only multi-word phrases or unambiguous acronyms qualify.
#
# Priority order: more legally or contextually specific sectors rank higher.
# Defense/Military is highest because its incidents fall outside GDPR scope
# (Art. 2(2)(a)) and must not be conflated with other sectors.
# Corporate/Enterprise is lowest because it is a residual catch-all category.
# ---------------------------------------------------------------------------

ASSET_CONTEXT_KEYWORDS = {
    # Incidents involving defense establishments, military contractors, or
    # NATO-affiliated organizations. Data processing in this context falls
    # outside the material scope of the GDPR (Art. 2(2)(a)).
    # Keywords describe the TARGET organization only; attacker designations
    # such as GRU, FSB, or espionage-related terms are explicitly excluded.
    "Defense / Military": [
        "ministry of defense", "ministry of defence",
        "department of defense",
        "armed forces",
        "defense contractor", "defence contractor",
        "cleared defense contractor",
        "defense company", "defence company",
        "weapons manufacturer", "arms manufacturer",
        "aerospace company",
        "military base", "air force base",
        "pentagon",
        "missile manufacturer",
        "nuclear weapons facility",
        "nato",
    ],
    # Healthcare organizations, including hospitals, insurers, pharmacies,
    # and biotech. This category is relevant because health data constitutes
    # a special category under GDPR Art. 9, increasing incident severity.
    "Healthcare": [
        "hospital", "clinic", "medical center", "medical centre",
        "healthcare provider", "health care provider",
        "health system", "health network",
        "nhs", "health service", "health authority",
        "pharmacy", "pharmaceutical company",
        "patient", "nursing home", "care facility",
        "cancer center", "cancer centre",
        "biotech", "biotechnology",
        "health insurance",
        "medical clinic", "healthcare facility",
        "health department",
        "dental",
        "health record",
        "medical practice",
        "ambulance service",
        "blood bank",
        "rehabilitation center", "rehabilitation centre",
    ],
    # Government bodies at all levels (federal, regional, municipal) and
    # public administration. Only compound nouns are used to avoid matching
    # generic occurrences of "city", "county", or "state".
    "Government / Public Sector": [
        # Ministries and federal bodies
        "government agency", "government entity",
        "government organization",
        "ministry of",
        "interior ministry", "foreign ministry",
        "finance ministry", "justice ministry",
        "state department", "federal agency",
        "federal bureau",
        # Municipal and regional administration
        "municipal administration", "municipality",
        "city council", "city hall",
        "town hall", "town council", "town clerk",
        "county council", "county administration",
        "county government", "county sheriff",
        "county clerk", "county board",
        "local council", "local government",
        "district council", "district administration",
        "regional government",
        "state government",
        "prefecture",
        "magistrate",
        # Legislative and executive bodies
        "parliament", "senate",
        "public administration",
        "civil service",
        "local authority",
        "electoral commission",
        # Law enforcement and justice
        "police department", "law enforcement agency",
        "fire department",
        "immigration department", "customs authority",
        "tax authority",
        "sheriff",
        "mayor",
        # Diplomatic entities
        "embassy", "consulate", "diplomatic",
        # Broad but empirically reliable in context
        "government",
        "public sector",
        "public service",
    ],
    # Operators of essential services as defined in NIS2 Annex I, including
    # energy, water, transport, and telecommunications infrastructure
    "Critical Infrastructure": [
        "power grid", "electricity provider", "electricity grid",
        "energy company", "energy provider",
        "nuclear plant", "nuclear facility",
        "oil company", "gas company", "pipeline operator",
        "water utility", "water supplier", "wastewater",
        "sewage system", "water treatment",
        "railway company", "railroad", "public transport",
        "transportation authority",
        "port authority", "port operator",
        "airport operator", "air traffic",
        "shipping company", "logistics provider",
        "food supplier", "food distribution",
        "utility company", "utility provider",
        "telecom operator", "telecommunications company",
        "telecommunications provider",
        "electricity supplier",
        "wireless telecommunications",
        "power company",
        "gas provider",
        "water company",
        "waste management",
        "public utility",
    ],
    # Financial institutions and services as covered by NIS2 Annex I,
    # including banks, insurers, payment processors, and crypto exchanges
    "Finance": [
        "bank", "banking", "central bank",
        "financial institution", "financial service",
        "credit union", "stock exchange",
        "investment firm", "investment bank",
        "insurance company", "insurance provider",
        "mortgage company", "payment provider",
        "fintech", "crypto exchange",
        "cryptocurrency exchange",
        "trading platform", "brokerage",
        "lender", "lending firm",
        "investment platform",
        "tax reporting platform",
        "federal mortgage",
        "credit card company",
        "payment processor",
        "asset management",
        "hedge fund",
        "wealth management",
        "pension fund",
        "savings bank",
    ],
    # Educational institutions from primary to university level
    "Education": [
        "university", "college",
        "school district", "public school",
        "high school", "secondary school",
        "community college", "academic institution",
        "student", "education authority",
        "school board",
        "school",
        "primary school",
        "elementary school",
        "research institution",
        "research university",
        "vocational school",
        "training provider",
    ],
    # Empirically derived category covering consumer-facing digital platforms
    # not addressed by NIS2. Dominates the HIBP sub-corpus. Includes gaming,
    # social media, e-commerce, entertainment, and community platforms.
    "Consumer Platform": [
        # Gaming
        "gaming platform", "online game", "game developer",
        "video game", "game studio",
        "gaming website",
        "game portal",
        "games website",
        # Dating and social
        "dating app", "dating platform",
        "social media platform", "social media website",
        "social media company", "social network",
        # Commerce
        "e-commerce", "ecommerce", "online shop", "online store",
        "retail chain", "supermarket chain", "department store",
        "clothing store", "fashion retailer",
        "grocery platform", "retailer",
        # Entertainment
        "streaming service", "streaming platform",
        "music platform", "podcast platform",
        "video making service",
        "music streaming",
        # Photo and creative
        "stock photo", "photo sharing", "photo community",
        "photography community",
        # Community and forums
        "forum platform", "community platform",
        "torrent site", "anime",
        # Travel and food
        "food delivery", "restaurant chain",
        "hotel chain", "travel platform", "airline",
        # Sports and fitness
        "sports tracking",
        "fitness app", "fitness platform",
        # Miscellaneous consumer services
        "subscription service", "consumer app",
        "betting", "gambling", "casino",
        "coupon",
        "recipe platform", "cooking platform",
        "adult platform", "nsfw",
        "nft platform", "web3 platform",
        "coding platform",
        "marketplace",
        "crowdfunding",
        "app store",
        "friend search",
        "tracking app",
        "loyalty program", "rewards program",
        "job board", "job portal",
        "freelance platform",
        "ticket platform",
        "event platform",
        "ride sharing", "ridesharing",
        "car sharing",
    ],
    # Empirically derived residual category for commercial organizations
    # that do not fall within any NIS2 sector. Acts as a catch-all for
    # private-sector incidents not covered by the categories above.
    "Corporate / Enterprise": [
        "manufacturer", "manufacturing company",
        "automotive manufacturer", "car manufacturer",
        "technology company", "tech company", "technology firm",
        "it company", "it provider",
        "cybersecurity firm", "cybersecurity company",
        "security firm",
        "law firm", "consulting firm",
        "media company", "newspaper",
        "engineering firm", "industrial company",
        "multinational corporation",
        "corporation",
        "staffing company", "staffing firm",
        "recruitment company",
        "data aggregator",
        "accounting firm",
        "logistics company", "logistics firm",
        "real estate company", "real estate firm",
        "staffing agency",
        "media outlet",
        "publishing company", "publishing house",
        "marketing agency", "marketing firm",
        "advertising agency",
        "audit firm",
        "conglomerate",
    ],
}

# Defense/Military is highest priority: most specific and legally distinct.
# Corporate/Enterprise is lowest: residual category with broad keywords.
ASSET_CONTEXT_PRIORITY = [
    "Corporate / Enterprise",
    "Consumer Platform",
    "Education",
    "Finance",
    "Critical Infrastructure",
    "Government / Public Sector",
    "Healthcare",
    "Defense / Military",
]


# ---------------------------------------------------------------------------
# TARGETTYPE KEYWORDS
#
# Captures incidents where an individual person is the direct target of an
# attack, as opposed to an organization. Relevant for GDPR Art. 4(1) and
# ISO 27005 personnel asset classification.
#
# Because there are only two possible outcomes (Individual / Unknown),
# no priority list is needed. The first matching keyword returns "Individual"
# immediately.
# ---------------------------------------------------------------------------

INDIVIDUAL_KEYWORDS = [
    "pegasus",
    "predator spyware",
    "spyware on the phone",
    "infected the mobile phone of",
    "compromised the phone of",
    "personal phone of",
    "email account of a member",
    "email account of the president",
    "email account of a staff member",
    "email account of an employee",
    "personal email account",
    "private email",
    "sim swapping",
    "targeted individual",
    "socially engineered an",
    "social engineering of",
    "phone of",
    "devices of executives",
    "account of a",
    "spear-phishing against",
]


# ---------------------------------------------------------------------------
# CLASSIFICATION FUNCTIONS
#
# Each function normalizes the input to lowercase before matching.
# NaN values from Excel are caught by the isinstance check and returned
# as "Unknown" rather than raising a TypeError.
# ---------------------------------------------------------------------------

def classify_asset_tech(text: str) -> str:
    if not isinstance(text, str):
        return "Unknown"
    return _match(text.lower(), ASSET_TECH_KEYWORDS, ASSET_TECH_PRIORITY)


def classify_asset_context(text: str) -> str:
    if not isinstance(text, str):
        return "Unknown"
    return _match(text.lower(), ASSET_CONTEXT_KEYWORDS, ASSET_CONTEXT_PRIORITY)


def classify_target_type(text: str) -> str:
    if not isinstance(text, str):
        return "Unknown"
    text_lower = text.lower()
    for kw in INDIVIDUAL_KEYWORDS:
        pattern = r'\b' + re.escape(kw.lower()) + r's?\b'
        if re.search(pattern, text_lower):
            return "Individual"
    return "Unknown"


# ---------------------------------------------------------------------------
# DEBUG UTILITY: explain()
#
# Prints all keyword matches for a given text across all three dimensions.
# Useful for inspecting unexpected classifications or testing new keywords
# before adding them to the main dictionaries.
# ---------------------------------------------------------------------------

def explain(text: str):
    if not isinstance(text, str):
        return
    text_lower = text.lower()
    print(f"\nText: {text[:160]}\n")

    for label, kd in [
        ("AssetTech",    ASSET_TECH_KEYWORDS),
        ("AssetContext", ASSET_CONTEXT_KEYWORDS),
    ]:
        print(f"  [{label}]")
        for cat, kws in kd.items():
            hits = [
                kw for kw in kws
                if re.search(r'\b' + re.escape(kw.lower()) + r's?\b',
                             text_lower)
            ]
            if hits:
                print(f"    ✓ {cat}: {hits}")

    ind_hits = [
        kw for kw in INDIVIDUAL_KEYWORDS
        if re.search(r'\b' + re.escape(kw.lower()) + r's?\b', text_lower)
    ]
    print(f"\n  [TargetType]")
    if ind_hits:
        print(f"    ✓ Individual: {ind_hits}")

    print(f"\n  → AssetTech:    {classify_asset_tech(text)}")
    print(f"  → AssetContext: {classify_asset_context(text)}")
    print(f"  → TargetType:   {classify_target_type(text)}")


# ---------------------------------------------------------------------------
# VOCABULARY ANALYSIS: analyze_unknowns_vocab()
#
# Computes word frequencies across all descriptions that remain "Unknown"
# for a given classification column. Used to identify candidate keywords
# for the next iteration. A stopword list filters out terms that appear
# frequently but carry no classification signal (dates, incident boilerplate,
# common verbs, etc.).
# ---------------------------------------------------------------------------

STOPWORDS = {
    "the", "a", "an", "of", "in", "to", "and", "on", "by",
    "was", "were", "that", "which", "with", "from", "its",
    "has", "had", "have", "been", "is", "are", "at", "for",
    "as", "it", "this", "their", "into", "be", "or", "not",
    "also", "but", "after", "when", "according", "data",
    "breach", "attack", "hacker", "group", "unknown", "actors",
    "accessed", "stole", "gained", "access", "systems", "company",
    "information", "personal", "reported", "incident", "cyber",
    "ransomware", "threat", "actor", "via", "against", "over",
    "including", "during", "following", "related", "more", "than",
    "between", "about", "some", "other", "several", "further",
    "such", "may", "affected", "disclosed", "stated", "claimed",
    "would", "could", "did", "its", "one", "two", "three",
    "new", "based", "used", "use", "using", "made", "said",
    "while", "well", "later", "early", "late", "first", "then",
    "same", "both", "where", "what", "these", "those",
    "million", "thousand", "number", "record", "unique",
    "email", "address", "password", "name", "phone",
    "north", "south", "east", "west",
}


def analyze_unknowns_vocab(input_path: str,
                           column: str = "AssetContext",
                           source_filter: str = None,
                           top_n: int = 50):
    # Re-classify on load so results always reflect the current keyword lists
    df = pd.read_excel(input_path)
    df["AssetTech"]    = df["Description"].apply(classify_asset_tech)
    df["AssetContext"] = df["Description"].apply(classify_asset_context)
    df["TargetType"]   = df["Description"].apply(classify_target_type)

    mask = df[column] == "Unknown"
    if source_filter:
        mask &= df["Source"].str.upper() == source_filter.upper()

    texts = df[mask]["Description"].dropna()
    label = f"'{column}' Unknown"
    if source_filter:
        label += f" [{source_filter}]"
    print(f"\n=== Vocabulary analysis: {label} ({len(texts)} incidents) ===\n")

    counter = Counter()
    for text in texts:
        words = re.findall(r'[a-z]{4,}', text.lower())
        counter.update(w for w in words if w not in STOPWORDS)

    for word, count in counter.most_common(top_n):
        print(f"  {count:4d}  {word}")


# ---------------------------------------------------------------------------
# TEXT INSPECTION: analyze_unknowns()
#
# Prints raw description texts for Unknown incidents. Used alongside
# analyze_unknowns_vocab() to manually verify whether a frequency signal
# actually corresponds to a classifiable pattern.
# ---------------------------------------------------------------------------

def analyze_unknowns(input_path: str,
                     column: str = "AssetContext",
                     source_filter: str = None,
                     n: int = 25):
    df = pd.read_excel(input_path)
    df["AssetTech"]    = df["Description"].apply(classify_asset_tech)
    df["AssetContext"] = df["Description"].apply(classify_asset_context)
    df["TargetType"]   = df["Description"].apply(classify_target_type)

    mask = df[column] == "Unknown"
    if source_filter:
        mask &= df["Source"].str.upper() == source_filter.upper()

    unknowns = df[mask][["Source", "Description"]].dropna().head(n)
    label = f"'{column}' Unknown"
    if source_filter:
        label += f" [{source_filter}]"
    print(f"\n=== {label} ({len(unknowns)} shown) ===")
    for _, row in unknowns.iterrows():
        print(f"\n[{row['Source']}] {row['Description'][:180]}")


# ---------------------------------------------------------------------------
# PIPELINE: classify_dataset()
#
# Applies all three classifiers to the full dataset, prints a distribution
# summary per source, and writes the result to an Excel file.
# The three new columns (AssetTech, AssetContext, TargetType) are appended
# to the existing columns from the labeled input file.
# ---------------------------------------------------------------------------

def classify_dataset(input_path: str, output_path: str):
    df = pd.read_excel(input_path)
    print(f"Loaded {len(df)} rows.\n")

    df["AssetTech"]    = df["Description"].apply(classify_asset_tech)
    df["AssetContext"] = df["Description"].apply(classify_asset_context)
    df["TargetType"]   = df["Description"].apply(classify_target_type)

    for col in ["AssetTech", "AssetContext", "TargetType"]:
        print(f"=== {col} ===")
        print(df.groupby("Source")[col].value_counts().to_string())
        n = (df[col] == "Unknown").sum()
        print(f"→ Unknown: {n} ({n / len(df) * 100:.1f}%)\n")

    df.to_excel(output_path, index=False)
    print(f"Saved → {output_path}")


# ---------------------------------------------------------------------------
# ENTRY POINT
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    INPUT  = "../data/processed/privacyrisq_labeled_final.xlsx"
    OUTPUT = "../data/processed/privacyrisq_assets_final.xlsx"

    classify_dataset(INPUT, OUTPUT)

    print("\n── Spot checks ──")
    explain("In December 2022, attackers socially engineered an Activision "
            "HR employee into disclosing information which led to the breach "
            "of almost 20k employee records.")
    explain("gained access to the network of the hospital")
    explain("the stock photo site 123RF suffered a data breach which impacted "
            "over 8 million subscribers. The breach included email, IP and "
            "physical addresses, names, phone numbers and passwords.")
    explain("An unnamed hacker group compromised SOHO routers "
            "using Cuttlefish malware")
    explain("The LockBit ransomware group attacked the German "
            "defense contractor Rheinmetall")
    explain("Unknown threat actors targeted the municipal "
            "administration of Morón in Argentina")
    explain("On 23 October 2025, Freedom Mobile, a Canadian wireless "
            "telecommunications provider, detected unauthorized activity")
    explain("Delta Dental of Virginia, a dental benefits provider "
            "offering insurance plans, affecting approximately 146,000 people")
    explain("the gaming website dedicated to classic DOS games Abandonia "
            "suffered a data breach")
    explain("the crowdfunding platform APOIA.se was posted to an online forum")
    # Regression tests for known false-positive risks
    explain("City of Hope cancer center suffered a data breach")
    explain("Attackers used RDP to compromise the county council of Sacramento")
    explain("A logistics company reported unauthorized access to its cloud storage")
    explain("The city council of Dallas confirmed ransomware encrypted its "
            "Active Directory")
    explain("A freelance platform for designers exposed 2 million user accounts")
    print("\n── Regression tests: Supplier fixes ──")
explain(
    "In April 2026, the ultra-luxury hotel brand Aman was named by "
    "ShinyHunters as the target of a 'pay or leak' extortion campaign, "
    "with the data allegedly obtained from their Salesforce CRM."
)
explain(
    "In May 2022, the Australian retailer Amart Furniture advised that "
    "their warranty claims database hosted on Amazon Web Services had "
    "been the target of a cyber attack."
)