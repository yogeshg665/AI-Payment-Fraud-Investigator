"""Reporting agent: produces an explainable, audit-ready investigation report."""

from __future__ import annotations

from fraud_investigator.agents.base import Agent
from fraud_investigator.llm.client import LLMClient
from fraud_investigator.models.case import InvestigationCase
from fraud_investigator.models.decision import Decision

_SYSTEM_PROMPT = (
    "You are a senior payment fraud investigator. Write a concise, factual case "
    "summary for an audit trail. Use neutral, professional language. Do not "
    "invent facts beyond the provided signals and decision."
)


class ReportingAgent(Agent):
    """Generates a structured report and a human-readable narrative."""

    name = "reporting"

    def __init__(self, config, llm_client: LLMClient | None = None) -> None:
        super().__init__(config)
        self.llm = llm_client or LLMClient()

    def run(self, case: InvestigationCase, decision: Decision) -> dict:
        narrative = self._build_narrative(case, decision)
        decision.narrative = narrative

        report = {
            "case_id": case.case_id,
            "created_at": case.created_at.isoformat(),
            "transaction": {
                "transaction_id": case.transaction.transaction_id,
                "account_id": case.transaction.account_id,
                "amount": case.transaction.amount,
                "currency": case.transaction.currency,
                "merchant_id": case.transaction.merchant_id,
                "channel": case.transaction.channel,
                "timestamp": case.transaction.timestamp.isoformat(),
            },
            "risk_score": case.risk_score,
            "decision": decision.outcome.value,
            "confidence": decision.confidence,
            "signals": [
                {
                    "skill": signal.skill,
                    "name": signal.name,
                    "severity": signal.severity,
                    "confidence": signal.confidence,
                    "rationale": signal.rationale,
                    "evidence": signal.evidence,
                }
                for signal in case.triggered_signals()
            ],
            "recommended_actions": decision.recommended_actions,
            "narrative": narrative,
        }
        self.logger.info("Generated report for %s", case.case_id)
        return report

    def _build_narrative(self, case: InvestigationCase, decision: Decision) -> str:
        """Use the LLM when available; otherwise build a deterministic summary."""
        deterministic = self._deterministic_narrative(case, decision)
        generated = self.llm.summarize(_SYSTEM_PROMPT, deterministic)
        return generated or deterministic

    @staticmethod
    def _deterministic_narrative(case: InvestigationCase, decision: Decision) -> str:
        txn = case.transaction
        lines = [
            f"Case {case.case_id} reviewed transaction {txn.transaction_id} for "
            f"{txn.amount_label()} at merchant {txn.merchant_id} via {txn.channel}.",
            f"Aggregate risk score: {case.risk_score:.1f}/100. "
            f"Recommendation: {decision.outcome.value.upper()} "
            f"(confidence {decision.confidence:.0%}).",
        ]
        triggered = case.triggered_signals()
        if triggered:
            lines.append("Contributing indicators:")
            for signal in triggered:
                lines.append(f"- {signal.rationale}")
        else:
            lines.append("No fraud indicators were triggered.")
        lines.append("Recommended actions:")
        for action in decision.recommended_actions:
            lines.append(f"- {action}")
        return "\n".join(lines)
