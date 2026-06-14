"""Velocity checks: rapid bursts of activity on a single account."""

from __future__ import annotations

from datetime import timedelta
from typing import Optional

from fraud_investigator.models.case import InvestigationCase, RiskSignal
from fraud_investigator.skills.base import Skill


class VelocityCheckSkill(Skill):
    """Detects abnormal transaction count or spend within a short window."""

    name = "velocity_check"

    def evaluate(self, case: InvestigationCase) -> Optional[RiskSignal]:
        settings = self.config.velocity_check
        txn = case.transaction
        window_start = txn.timestamp - timedelta(minutes=settings.window_minutes)

        recent = [
            prior
            for prior in case.account_history
            if prior.account_id == txn.account_id
            and window_start <= prior.timestamp <= txn.timestamp
        ]
        # Include the current transaction in the counts.
        count = len(recent) + 1
        total_amount = sum(prior.amount for prior in recent) + txn.amount

        severity = 0.0
        reasons: list[str] = []

        if count > settings.max_transactions:
            severity += min(60.0, 15.0 * (count - settings.max_transactions) + 30.0)
            reasons.append(
                f"{count} transactions in {settings.window_minutes} minutes "
                f"exceeds limit of {settings.max_transactions}."
            )

        if total_amount > settings.max_amount:
            severity += 40.0
            reasons.append(
                f"Cumulative spend {total_amount:,.2f} in window exceeds "
                f"limit of {settings.max_amount:,.2f}."
            )

        if severity == 0.0:
            return None

        return self._signal(
            name="high_velocity_activity",
            severity=severity,
            rationale=" ".join(reasons),
            evidence={
                "transaction_count": count,
                "window_minutes": settings.window_minutes,
                "cumulative_amount": round(total_amount, 2),
            },
        )
