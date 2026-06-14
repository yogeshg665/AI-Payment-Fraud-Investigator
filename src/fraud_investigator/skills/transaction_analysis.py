"""Transaction-level heuristics: high value and unusual timing."""

from __future__ import annotations

from typing import Optional

from fraud_investigator.models.case import InvestigationCase, RiskSignal
from fraud_investigator.skills.base import Skill


class TransactionAnalysisSkill(Skill):
    """Flags high-value transactions and activity during unusual hours."""

    name = "transaction_analysis"

    def evaluate(self, case: InvestigationCase) -> Optional[RiskSignal]:
        settings = self.config.transaction_analysis
        txn = case.transaction

        severity = 0.0
        reasons: list[str] = []
        evidence: dict[str, object] = {}

        if txn.amount >= settings.high_value_amount:
            # Scale severity with how far the amount exceeds the threshold.
            ratio = txn.amount / max(settings.high_value_amount, 1.0)
            severity += min(60.0, 30.0 * ratio)
            reasons.append(
                f"High-value transaction of {txn.amount_label()} "
                f"exceeds threshold of {settings.high_value_amount:,.2f}."
            )
            evidence["amount"] = txn.amount

        hour = txn.timestamp.hour
        if hour in settings.unusual_hours:
            severity += 25.0
            reasons.append(f"Transaction occurred during unusual hour {hour:02d}:00 UTC.")
            evidence["hour"] = hour

        if severity == 0.0:
            return None

        return self._signal(
            name="suspicious_transaction_profile",
            severity=severity,
            rationale=" ".join(reasons),
            evidence=evidence,
        )
