"""Case memory skill: turns recalled history into a contextual risk signal."""

from __future__ import annotations

from typing import Optional

from fraud_investigator.models.case import InvestigationCase, RiskSignal
from fraud_investigator.skills.base import Skill


class CaseMemorySkill(Skill):
    """Emits a signal when an account or card has adverse prior history.

    The skill reads a ``memory_recall`` summary injected during enrichment from
    the collective memory store. It only interprets that summary, so it stays
    deterministic and side-effect free like every other skill. Memory is treated
    as corroborating context, never as a definitive indicator, so it is never
    marked critical.
    """

    name = "case_memory"

    def evaluate(self, case: InvestigationCase) -> Optional[RiskSignal]:
        recall = case.enrichment.get("memory_recall")
        if not isinstance(recall, dict):
            return None

        confirmed_fraud = int(recall.get("confirmed_fraud_count", 0))
        prior_declines = int(recall.get("prior_decline_count", 0))
        prior_escalations = int(recall.get("prior_escalation_count", 0))
        total_prior = int(recall.get("total_prior_cases", 0))
        matched_on = recall.get("matched_on") or []

        if total_prior <= 0:
            return None

        if confirmed_fraud > 0:
            severity = min(75.0, 55.0 + 10.0 * confirmed_fraud)
            reason = (
                f"Account or card has {confirmed_fraud} confirmed-fraud case(s) in "
                f"prior history."
            )
        elif prior_declines > 0:
            severity = min(50.0, 35.0 + 5.0 * prior_declines)
            reason = f"Account or card was previously declined {prior_declines} time(s)."
        elif prior_escalations > 0:
            severity = min(30.0, 20.0 + 3.0 * prior_escalations)
            reason = f"Account or card was previously escalated {prior_escalations} time(s)."
        else:
            return None

        return self._signal(
            name="adverse_history",
            severity=severity,
            rationale=reason,
            confidence=0.85,
            evidence={
                "matched_on": list(matched_on),
                "total_prior_cases": total_prior,
                "confirmed_fraud_count": confirmed_fraud,
                "prior_decline_count": prior_declines,
                "prior_escalation_count": prior_escalations,
            },
        )
