---
name: risk-scoring
description: Aggregates all triggered risk signals into a single explainable score from 0 to 100 using confidence weighting, a corroboration boost, and a critical-signal floor. WHEN: "score the risk", "calculate fraud score", "aggregate signals", "compute risk score", "combine fraud indicators".
---

# Risk Scoring

## Overview

Combines the individual risk signals into one aggregate score. The method blends
signal severities by their configured weight and confidence, applies a small
boost when multiple independent signals corroborate, and never lets the score
fall below a definitive critical signal.

## When to Use

- After all detection skills have run and before `fraud-decisioning`.

## Inputs

| Input | Required | Description |
| --- | --- | --- |
| `case.signals` | yes | The signals emitted during detection. |
| `skill_weights` | yes | Per-skill weights from configuration. |

## Process

1. Select the triggered signals. If none, the score is zero.
2. For each signal, compute a weight equal to its configured skill weight times
   its confidence.
3. Compute the weighted average of severities.
4. Apply a corroboration boost that grows with the number of independent
   triggers, capped to avoid runaway inflation.
5. Compute the critical floor as the maximum severity among critical signals.
6. The final score is the greater of the boosted blend and the critical floor,
   bounded to the range 0 to 100.

## Outputs

A `risk_score` on the case.

## Reference Implementation

`src/fraud_investigator/agents/risk_scoring_agent.py`.

## Rationalizations

| Excuse | Rebuttal |
| --- | --- |
| "Just take the maximum severity." | A pure maximum is brittle to a single noisy signal; blending is more robust. |
| "Ignore the critical floor to smooth results." | Definitive indicators must not be diluted; the floor is intentional. |

## Red Flags

- The score can be lower than a confirmed deny-list signal.
- Weights are applied without confidence.

## Verification

- A case with a critical deny-list signal scores at or above that signal's
  severity.
