"""Decision agent: maps the risk score and signals to a recommended outcome."""

from __future__ import annotations

from fraud_investigator.agents.base import Agent
from fraud_investigator.models.case import InvestigationCase
from fraud_investigator.models.decision import Decision, DecisionOutcome


class DecisionAgent(Agent):
    """Applies the decision policy to produce an explainable recommendation."""

    name = "decision"

    def run(self, case: InvestigationCase) -> Decision:
        policy = self.config.decision_policy
        score = case.risk_score

        if score >= policy.decline_threshold:
            outcome = DecisionOutcome.DECLINE
            actions = [
                "Block the transaction.",
                "Place a temporary hold on the account pending review.",
                "Notify the cardholder through a verified channel.",
            ]
        elif score >= policy.escalate_threshold:
            outcome = DecisionOutcome.ESCALATE
            actions = [
                "Route the case to the manual review queue.",
                "Request step-up authentication before settlement.",
            ]
        else:
            outcome = DecisionOutcome.APPROVE
            actions = ["Allow the transaction to proceed.", "Continue passive monitoring."]

        reasons = [signal.rationale for signal in case.triggered_signals()]
        if not reasons:
            reasons = ["No fraud indicators were triggered for this transaction."]

        confidence = self._confidence(case, outcome)
        decision = Decision(
            case_id=case.case_id,
            outcome=outcome,
            risk_score=score,
            confidence=confidence,
            reasons=reasons,
            recommended_actions=actions,
        )
        self.logger.info(
            "Decided %s: %s (risk=%.1f, confidence=%.2f)",
            case.case_id,
            outcome.value,
            score,
            confidence,
        )
        return decision

    def _confidence(self, case: InvestigationCase, outcome: DecisionOutcome) -> float:
        """Derive a confidence value from signal agreement and score margin."""
        policy = self.config.decision_policy
        score = case.risk_score

        if outcome is DecisionOutcome.DECLINE:
            margin = (score - policy.decline_threshold) / max(100 - policy.decline_threshold, 1)
        elif outcome is DecisionOutcome.APPROVE:
            margin = (policy.escalate_threshold - score) / max(policy.escalate_threshold, 1)
        else:
            band = max(policy.decline_threshold - policy.escalate_threshold, 1)
            midpoint = (policy.decline_threshold + policy.escalate_threshold) / 2
            margin = 1.0 - abs(score - midpoint) / band

        base = 0.6 + 0.4 * max(0.0, min(1.0, margin))
        return round(max(0.0, min(1.0, base)), 2)
