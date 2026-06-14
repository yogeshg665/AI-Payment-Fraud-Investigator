---
name: velocity-analysis
description: Detects abnormal transaction frequency or cumulative spend on a single account within a short time window. WHEN: "check transaction velocity", "rapid transactions", "card testing", "too many charges", "burst of activity", "velocity check".
---

# Velocity Analysis

## Overview

Identifies bursts of activity that are characteristic of card testing and
account takeover: many transactions or a large cumulative spend within a short
window on the same account.

## When to Use

- During the detection phase, whenever account history is available.

## Inputs

| Input | Required | Description |
| --- | --- | --- |
| `transaction` | yes | The current transaction. |
| `account_history` | yes | Prior transactions for the same account. |

## Process

1. Define the window as `window_minutes` ending at the transaction timestamp.
2. Count transactions for the account within the window, including the current
   one. If the count exceeds `max_transactions`, add severity.
3. Sum the spend within the window. If it exceeds `max_amount`, add severity.
4. Emit a `high_velocity_activity` signal with the count, window, and cumulative
   amount as evidence.

## Outputs

Zero or one `RiskSignal`.

## Reference Implementation

`src/fraud_investigator/skills/velocity_check.py`.

## Rationalizations

| Excuse | Rebuttal |
| --- | --- |
| "The account has no history, so velocity is irrelevant." | A first transaction simply yields no velocity signal; do not infer safety. |
| "A few rapid purchases are normal." | The threshold encodes normal; exceeding it is the signal. |

## Red Flags

- The current transaction is excluded from the window count.
- The window is measured from the wrong anchor time.

## Verification

- When activity exceeds the configured limits, a signal reports the count and
  cumulative amount.
