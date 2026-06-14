---
name: fraud-decisioning
description: Maps the aggregate risk score and signals to an explainable recommendation of approve, escalate, or decline, with a confidence value and recommended actions. WHEN: "make a fraud decision", "approve or decline", "should I block this", "decision policy", "escalate to review", "final fraud verdict".
---

# Fraud Decisioning

## Overview

Applies the configurable decision policy to the scored case and produces a
recommendation with a confidence value, the reasons behind it, and the actions to
take next.

## When to Use

- After `risk-scoring`, once the case has an aggregate score.

## Inputs

| Input | Required | Description |
| --- | --- | --- |
| `case.risk_score` | yes | The aggregate score. |
| `decision_policy.decline_threshold` | yes | Score at or above which to decline. |
| `decision_policy.escalate_threshold` | yes | Score at or above which to escalate. |

## Process

1. If the score is at or above `decline_threshold`, recommend **decline** and
   list blocking and notification actions.
2. Else if the score is at or above `escalate_threshold`, recommend **escalate**
   to manual review and request step-up authentication.
3. Otherwise recommend **approve** with continued passive monitoring.
4. Derive confidence from the margin between the score and the relevant threshold
   and from signal agreement.
5. Attach the triggered signal rationales as the reasons for the decision.

## Outputs

A `Decision` with outcome, confidence, reasons, and recommended actions.

## Reference Implementation

`src/fraud_investigator/agents/decision_agent.py`.

## Rationalizations

| Excuse | Rebuttal |
| --- | --- |
| "Auto-decline borderline cases to be safe." | Borderline cases belong in the escalate band for human review. |
| "Skip the reasons to save space." | A decision without cited reasons is not auditable and must not ship. |

## Red Flags

- A decline is issued with no triggered signals.
- Thresholds are inverted so that low scores decline.

## Verification

- The outcome is consistent with the score and the configured thresholds, and the
  decision lists its reasons.
