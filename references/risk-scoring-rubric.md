# Risk Scoring Rubric

Reference for how individual signal severities map to risk and how the aggregate
score is interpreted. Used by `risk-scoring` and `fraud-decisioning`.

## Severity Bands (per signal, 0-100)

| Band | Range | Meaning |
| --- | --- | --- |
| Low | 1-25 | Weak indicator; meaningful only with corroboration. |
| Moderate | 26-50 | Notable indicator; contributes materially to the score. |
| High | 51-80 | Strong indicator; likely to drive escalation on its own. |
| Definitive | 81-100 | Near-certain indicator; marked critical and floors the score. |

## Confidence

Each signal carries a confidence from 0 to 1. The scoring step multiplies a
signal's configured weight by its confidence, so a low-confidence signal
contributes proportionally less.

## Aggregate Score Interpretation

| Score | Interpretation | Typical Decision |
| --- | --- | --- |
| 0-44 | Low risk | Approve with passive monitoring. |
| 45-74 | Elevated risk | Escalate to human review or step-up authentication. |
| 75-100 | High risk | Decline and notify through a verified channel. |

Thresholds are configurable in `config/config.yaml` and via the
`RISK_DECLINE_THRESHOLD` and `RISK_ESCALATE_THRESHOLD` environment variables.

## Aggregation Method

1. Weighted average of triggered signal severities, weighted by configured skill
   weight times confidence.
2. Corroboration boost up to 25 percent as the number of independent triggers
   grows.
3. Critical floor: the score is never lower than the highest-severity critical
   signal.

## Worked Example

- Signals: deny-list card hit (severity 90, critical), high value (severity 55),
  unknown device (severity 30).
- Weighted blend lands near 70, corroboration raises it slightly, but the
  critical floor of 90 dominates.
- Final score: 90. Decision: decline.
