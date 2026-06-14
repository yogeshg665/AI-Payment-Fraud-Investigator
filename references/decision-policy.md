# Decision Policy Reference

Defines how the aggregate risk score maps to an outcome, and the actions
associated with each outcome. Used by `fraud-decisioning`.

## Thresholds

| Parameter | Default | Description |
| --- | --- | --- |
| `decline_threshold` | 75 | Score at or above which the transaction is declined. |
| `escalate_threshold` | 45 | Score at or above which the case is escalated. |

Scores below the escalate threshold are approved.

## Outcomes and Actions

### Approve

- Allow the transaction to proceed.
- Continue passive monitoring of the account.

### Escalate

- Route the case to the manual review queue.
- Request step-up authentication before settlement.

### Decline

- Block the transaction.
- Place a temporary hold on the account pending review.
- Notify the cardholder through a verified channel.

## Confidence

Confidence reflects how far the score sits from the relevant threshold and how
strongly the signals agree. A score near a threshold yields lower confidence and
should bias toward escalation rather than an automated adverse action.

## Governance

- Declines and escalations are subject to human review.
- Apply jurisdiction-specific adverse-action and notification requirements.
- Retain the full report as the evidentiary record for each decision.
