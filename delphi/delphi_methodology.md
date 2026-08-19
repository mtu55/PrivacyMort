# Delphi Expert Selection

## Methodological Basis
Okoli & Pawlowski (2004). The Delphi method as a research tool: an example, design considerations and applications. Information & Management, 42, 15–29
doi:10.1016/j.im.2003.11.002

> "A Delphi study does not depend on a statistical sample. It is a group decision mechanism requiring qualified experts who have deep understanding of the issues." (Okoli & Pawlowski, 2004, p. 20)
---

## Inclusion Criteria

An expert must meet ALL THREE of the following criteria:

| Criterion | Specification |
|-----------|--------------|
| Professional experience ≥ 5 years | In IT security, privacy, or compliance/risk management |
| Active current role | Actively working in at least one of: ISO 27001/Controls, Data Protection, Risk Assessment |
| Decision-making responsibility | Currently makes or evaluates decisions related to privacy controls or risk (self-reported) |

---

## Screening Questionnaire (Round 0)

Four questions administered before Round 1.
Responses are used for qualification ranking, not as a test.

| # | Question | Format | Exclusion Criterion |
|---|----------|--------|-------------------|
| 1 | What is your current job title? | Free text | No active position recognizable |
| 2 | What is your primary area of work? | Multiple Choice: IT Security / Data Protection / Compliance / Risk Management / Other | No relevance to RQ |
| 3 | How many years of professional experience do you have in this field? | Dropdown: <2 / 2–5 / 5–10 / >10 | < 5 years |
| 4 | Do you currently make or evaluate decisions related to privacy controls or risks? | Yes / No / Partially | No |

**Hard exclusion:** Question 4 answered with "No" → excluded from study.

---

## 5-Step Expert Selection Process
### Following Okoli & Pawlowski (2004), Figure 1

### Step 1: Prepare Knowledge Resource Nomination Worksheet (KRNW)

| Disciplines or Skills | Organizations | Related Literature (→ find expert names) |
|-----------------------|---------------|------------------------------------------|
| IT Security Practitioner (CISO, Security Engineer) | ISACA | PETS – who publishes on Privacy Risk? |
| Data Protection Officer (DPO) | IAPP | IEEE Security & Privacy – who publishes on Controls? |
| Compliance & Risk Manager | BSI | USENIX Security – who publishes on Incident Analysis? |
| Privacy Engineer | ENISA | ENISA Reports – who are the authors? |
| Information Security Auditor | GDD | BSI Publications – who are the authors? |
| Academic Researcher (Privacy/Security) | BvD | ACM CCS – who publishes on Privacy Threats? |
| | TeleTrusT | ISO 27001/27002 Practitioner Guides – who are the authors? |
| | LinkedIn Groups: ISO 27001, CISO Network, Privacy Professionals | |

---

### Step 2: Populate KRNW with Names

Executed during recruitment phase, not documented in paper in detail.

**Strategy:**
- Personal network (first pass)
- LinkedIn/XING search by job title and field
- Organizations listed in KRNW
- Authors identified via Related Literature

---

### Step 3: Collect Nominations

Initial contacts from KRNW are asked to nominate additional experts.

Note: At this stage, individuals are NOT yet invited to the study.
Only biographical information and nominations are collected.

---

### Step 4: Rank Experts by Qualification

Based on screening questionnaire responses, each expert receives a score:

| Criterion | Points |
|-----------|--------|
| Experience 5–10 years | 1 |
| Experience > 10 years | 2 |
| Area directly relevant (IT Security, Privacy, Risk) | 1 |
| Decision responsibility: Partially | 1 |
| Decision responsibility: Yes | 2 |

**Thresholds:**

| Score | Decision |
|-------|----------|
| 4–5 | Invite |
| 2–3 | Waitlist |
| < 2 | Exclude |

---

### Step 5: Invite Until Panel Size Reached

| Step | Detail |
|------|--------|
| Invite | By score ranking, highest score first |
| Confirmation | Expert confirms participation + provides email |
| Immediately after | Round 1 questionnaire is sent |
| Stop | When 20–25 confirmations reached |

**Target panel size:** 10–18 experts (Okoli & Pawlowski, 2004)
**Invitations sent:** 20–25 (to account for ~20% attrition)

---

## Anonymity

Following Okoli & Pawlowski (2004, p. 19):
> "Respondents are always anonymous to each other, but never anonymous to the researcher."

- Experts do not know who else participates 
- Researcher knows all participants 
- Targeted re-invitation for Round 2 is possible 

# Delphi Scenario Descriptions 

## Core Scenario

**LINDDUN:** Linkability + Identifiability  
**DataCategory:** Personal Data + Credentials  
**AssetTech:** Software / Web Application  
**BaselineRisk:** 0.289 (n=147, avg_severity=4)

---## 2. Scenario Selection

### 2.1 Core Scenario Family

**LINDDUN:** Linkability + Identifiability (exact match)
**DataCategory:** Personal Data + Credentials (has_special_categories = 0)
**AssetTech:** varies (see anchors below)

### 2.2 Selection Method

Anchor scenarios were selected using Maximum Variation Sampling
(Patton, 1990) across AssetTech variants within the core scenario family.

For each AssetTech variant, the incident with the highest number of
detected data field types was selected as the most representative case.

**Script:** `delphi/delphi_sample.py`

> "For each AssetTech variant, the incident with the highest number of
> exposed data field types was selected as the most representative case,
> following Maximum Variation Sampling (Patton, 1990)."

### 2.3 Anchor Scenarios

| Anchor | AssetTech | Source Incident | n | BaselineRisk |
|--------|-----------|----------------|---|--------------|
| A1 | Software / Web Application | Spoutible (2024) | 150 | 0.295 |
| A2 | Network Infrastructure | LimeVPN (2020) | 5 | 0.010 |
| A3 | Services provided by supplier | Amart Furniture (2022) | 9 | 0.018 |

### 2.4 Scenario Descriptions

#### Anchor 1 – Software / Web Application
*n=150 | BaselineRisk=0.295*

> A consumer-facing web application with registered user accounts
> suffered a data breach through a misconfigured API that inadvertently
> returned excessive personal information. The exposed data included
> email addresses, usernames, IP addresses, names, phone numbers,
> genders, password hashes, two-factor authentication secrets, backup
> codes and password reset tokens.

#### Anchor 2 – Network Infrastructure
*n=5 | BaselineRisk=0.010*

> A network infrastructure provider suffered a data breach that exposed
> customer records. The exposed data included email addresses, IP and
> physical addresses, names, phone numbers, purchase histories and
> hashed passwords.

#### Anchor 3 – Services provided by supplier
*n=9 | BaselineRisk=0.018*

> A retailer's customer database hosted on a third-party cloud
> infrastructure was targeted in a cyber attack. The exposed data
> included email addresses, physical addresses, names, phone numbers
> and hashed passwords.

---

## 3. Round 1 – Questionnaire

### Instructions for Experts

> You will be presented with three scenario descriptions. Each scenario
> describes a real-world privacy incident that has been abstracted for
> this study. For each scenario, please answer the following questions
> as specifically as possible. There are no right or wrong answers –
> we are interested in your professional judgment and experience.

---

### Questions per Scenario

**Q1:** Which privacy or security controls should have been implemented
in this scenario – and how – to reduce the privacy risk?

*Please be as specific as possible: name the control, describe how it
should be implemented, and explain why it addresses the risk.*

> **Q1_var1:** Would your answer change if no credentials (e.g.
> passwords, tokens) were affected – only personal data? If yes, how?

> **Q1_var2:** Would your answer change if special categories of
> personal data (e.g. health data, sexual orientation) were
> additionally affected? If yes, how?

---

**Q2:** Which of the controls you named would have the greatest impact
on reducing privacy risk – and why?

> **Q2_var1:** Would your answer change if no credentials were affected
> – only personal data? If yes, how?

> **Q2_var2:** Would your answer change if special categories were
> additionally affected? If yes, how?

---

**Q3:** Are there controls in your answer that only make sense for this
specific type of asset – and would not apply to a different asset type?

> **Q3_var1:** Would your answer change if no credentials were affected
> – only personal data? If yes, how?

> **Q3_var2:** Would your answer change if special categories were
> additionally affected? If yes, how?

---

## 4. Round 2 – Design

*To be defined after Round 1 consolidation.*

Round 2 will present consolidated control lists from Round 1 and ask
experts to assess the degree of risk reduction per control.

**Consensus threshold:** ICC > 0.75 (Koo & Mae, 2016)

**Fallback:** If ICC < 0.75 after Round 2:
> "Expert disagreement on control effectiveness constitutes a finding
> in itself, indicating that practitioner consensus on privacy control
> efficacy is currently insufficient for reliable quantitative
> estimation." (PrivacyMort Fallback Plan)

---
