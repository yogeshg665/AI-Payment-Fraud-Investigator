---
name: case-memory
description: Recalls prior investigations for the same account or tokenized card from collective memory and emits a contextual risk signal when adverse history exists. WHEN: "repeat offender", "prior fraud history", "seen this account before", "recall past cases", "account has chargebacks", "card previously declined", "collective memory".
---

# Case Memory

## Overview

Reads a `memory_recall` summary injected during enrichment from the collective
memory store and converts adverse prior history into a corroborating risk
signal. Memory is contextual, not definitive: the signal is never marked
critical and never sets a score floor. Recall is exact-match on the pseudonymous
account identifier and the tokenized card reference, so it stays deterministic
and privacy-preserving.

## When to Use

- During the detection phase, when collective memory is enabled and the engine
  has injected a `memory_recall` summary for the case.

## Inputs

| Input | Required | Description |
| --- | --- | --- |
| `enrichment.memory_recall.total_prior_cases` | no | Count of prior cases for this account or card. |
| `enrichment.memory_recall.confirmed_fraud_count` | no | Prior cases analysts labeled as fraud. |
| `enrichment.memory_recall.prior_decline_count` | no | Prior cases that were declined. |
| `enrichment.memory_recall.prior_escalation_count` | no | Prior cases that were escalated. |
| `enrichment.memory_recall.matched_on` | no | Which keys matched: account, card, or both. |

## Process

1. Return nothing when no recall summary or no prior cases are present.
2. If there is confirmed-fraud history, emit a high-severity signal.
3. Otherwise, if there are prior declines, emit a moderate signal.
4. Otherwise, if there are prior escalations, emit a low-moderate signal.
5. Attach the matched keys and counts as evidence.

## Outputs

Zero or one `RiskSignal` named `adverse_history`. The signal is never critical.

## Reference Implementation

`src/fraud_investigator/skills/case_memory.py`. The store and recall logic live
in `src/fraud_investigator/memory/`.

## Rationalizations

| Excuse | Rebuttal |
| --- | --- |
| "Past fraud proves this transaction is fraud." | History is corroborating context only; it informs, it does not decide. |
| "Store the raw card number to match better." | Only tokenized card references and pseudonymous accounts are ever persisted. |
| "Let memory override the score." | Memory contributes a weighted signal; it never floors or overrides the score. |

## Red Flags

- The skill marks the memory signal as critical.
- Raw cardholder data is written to the store.
- Recall is non-deterministic or depends on wall-clock time.

## Verification

- With no prior history, the skill returns no signal.
- With a confirmed-fraud prior case on the same account, the skill emits an
  `adverse_history` signal with elevated severity and the matched keys as
  evidence.
