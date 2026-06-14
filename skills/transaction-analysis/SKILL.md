---
name: transaction-analysis
description: Evaluates a single transaction for high-value amounts and unusual timing, emitting an explainable risk signal. WHEN: "analyze this transaction", "is this amount suspicious", "check transaction timing", "high value transaction check", "unusual hour transaction".
---

# Transaction Analysis

## Overview

Inspects the transaction in isolation for two classic indicators: an amount that
materially exceeds the high-value threshold, and activity during hours that are
unusual for legitimate behavior.

## When to Use

- During the detection phase of every investigation.

## Inputs

| Input | Required | Description |
| --- | --- | --- |
| `transaction.amount` | yes | Transaction amount. |
| `transaction.timestamp` | yes | UTC time of the transaction. |

## Process

1. Compare the amount to the configured `high_value_amount`. If it meets or
   exceeds the threshold, add severity proportional to how far it exceeds it.
2. Check whether the transaction hour falls within the configured
   `unusual_hours`. If so, add severity.
3. If any severity accrued, emit a `suspicious_transaction_profile` signal with a
   rationale and the supporting evidence. Otherwise emit nothing.

## Outputs

Zero or one `RiskSignal`.

## Reference Implementation

`src/fraud_investigator/skills/transaction_analysis.py`.

## Rationalizations

| Excuse | Rebuttal |
| --- | --- |
| "Large purchases are normal for some users." | The signal contributes risk; it does not decide alone. Let scoring weigh it. |
| "Time of day is irrelevant." | Off-hours activity is a well-established fraud correlate; keep the check. |

## Red Flags

- Severity is emitted without a corresponding rationale.
- Thresholds are hardcoded instead of read from configuration.

## Verification

- When the amount exceeds the threshold, a signal with non-zero severity exists.
