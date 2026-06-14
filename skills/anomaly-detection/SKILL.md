---
name: anomaly-detection
description: Flags transaction amounts that are statistical outliers relative to the account's own spending history using a z-score. WHEN: "detect anomaly", "statistical outlier", "unusual spend for this account", "amount anomaly", "z-score check", "deviation from normal".
---

# Anomaly Detection

## Overview

Compares the transaction amount to the account's historical spend distribution.
Amounts that are several standard deviations above the account mean are flagged
as outliers. Accounts with insufficient history are skipped to avoid noise.

## When to Use

- During the detection phase, when the account has enough history to be reliable.

## Inputs

| Input | Required | Description |
| --- | --- | --- |
| `transaction.amount` | yes | The amount under review. |
| `account_history` | yes | At least five prior transactions for the account. |

## Process

1. Collect prior amounts for the account. If there are fewer than five, stop.
2. Compute the mean and population standard deviation. If the deviation is zero,
   stop, because no meaningful outlier can be defined.
3. Compute the z-score of the current amount.
4. If the z-score meets or exceeds `zscore_threshold`, emit an `amount_outlier`
   signal with the z-score and account mean as evidence.

## Outputs

Zero or one `RiskSignal`.

## Reference Implementation

`src/fraud_investigator/skills/anomaly_detection.py`.

## Rationalizations

| Excuse | Rebuttal |
| --- | --- |
| "Two prior transactions are enough." | Small samples produce unstable z-scores; require a minimum history. |
| "A high amount is always fraud." | Outlier status is relative to the account, not absolute; let scoring decide. |

## Red Flags

- A z-score is computed on a zero-variance history.
- The minimum-history guard is removed.

## Verification

- A clear outlier with adequate history yields a signal whose z-score exceeds the
  threshold.
