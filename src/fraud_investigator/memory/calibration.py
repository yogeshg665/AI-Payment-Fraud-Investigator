"""Deterministic threshold calibration from labeled feedback.

This implements the engine's offline learning loop. It inspects analyst-confirmed
outcomes and recommends decline and escalate thresholds that best separate
confirmed fraud from legitimate activity. The recommendation is advisory only;
applying it remains a human decision so that runtime scoring stays deterministic.
"""

from __future__ import annotations

from fraud_investigator.memory.models import (
    CalibrationReport,
    CaseMemoryRecord,
    FeedbackLabel,
)
from fraud_investigator.utils.config import DecisionPolicy


def calibrate_thresholds(
    records: list[CaseMemoryRecord],
    policy: DecisionPolicy,
) -> CalibrationReport:
    """Recommend thresholds from labeled records.

    The decline threshold is placed at the midpoint between the lowest-scoring
    confirmed-fraud case and the highest-scoring legitimate case when they are
    separable, and at a conservative blend otherwise. The escalate threshold is
    placed at the highest legitimate score so likely-legitimate traffic is not
    escalated unnecessarily.
    """
    fraud_scores = sorted(
        r.risk_score for r in records if r.label is FeedbackLabel.CONFIRMED_FRAUD
    )
    legit_scores = sorted(
        r.risk_score for r in records if r.label is FeedbackLabel.LEGITIMATE
    )

    report = CalibrationReport(
        labeled_cases=len(fraud_scores) + len(legit_scores),
        confirmed_fraud_cases=len(fraud_scores),
        legitimate_cases=len(legit_scores),
        current_decline_threshold=policy.decline_threshold,
        current_escalate_threshold=policy.escalate_threshold,
    )

    if not fraud_scores or not legit_scores:
        report.rationale.append(
            "Need at least one confirmed-fraud and one legitimate labeled case to "
            "recommend thresholds. Record more feedback and retry."
        )
        return report

    lowest_fraud = fraud_scores[0]
    highest_legit = legit_scores[-1]

    if lowest_fraud > highest_legit:
        decline = (lowest_fraud + highest_legit) / 2.0
        report.rationale.append(
            f"Labeled cases are cleanly separable: lowest confirmed-fraud score "
            f"{lowest_fraud:.1f} exceeds highest legitimate score {highest_legit:.1f}. "
            f"Decline threshold set to their midpoint."
        )
    else:
        decline = max(lowest_fraud, highest_legit)
        report.rationale.append(
            f"Labeled cases overlap: lowest confirmed-fraud score {lowest_fraud:.1f} is "
            f"not above highest legitimate score {highest_legit:.1f}. Decline threshold "
            f"set conservatively to {decline:.1f}; expect residual error until more "
            f"feedback is collected."
        )

    escalate = min(decline, highest_legit)
    report.rationale.append(
        f"Escalate threshold set to the highest legitimate score {highest_legit:.1f} to "
        f"limit unnecessary escalations of likely-legitimate traffic."
    )

    report.suggested_decline_threshold = round(_clamp(decline), 1)
    report.suggested_escalate_threshold = round(_clamp(escalate), 1)
    return report


def _clamp(value: float) -> float:
    return max(0.0, min(100.0, value))
