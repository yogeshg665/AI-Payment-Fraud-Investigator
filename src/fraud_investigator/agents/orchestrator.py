"""Orchestrator agent: composes all stages into one investigation workflow."""

from __future__ import annotations

from fraud_investigator.agents.base import Agent
from fraud_investigator.agents.decision_agent import DecisionAgent
from fraud_investigator.agents.enrichment_agent import EnrichmentAgent
from fraud_investigator.agents.intake_agent import IntakeAgent
from fraud_investigator.agents.reporting_agent import ReportingAgent
from fraud_investigator.agents.risk_scoring_agent import RiskScoringAgent
from fraud_investigator.llm.client import LLMClient
from fraud_investigator.memory.store import MemoryStore
from fraud_investigator.models.case import InvestigationCase
from fraud_investigator.models.decision import Decision
from fraud_investigator.models.transaction import Transaction
from fraud_investigator.utils.config import EngineConfig


class InvestigationResult:
    """Container bundling the outcome of a single investigation."""

    def __init__(self, decision: Decision, report: dict) -> None:
        self.decision = decision
        self.report = report


class OrchestratorAgent(Agent):
    """Runs intake, enrichment, scoring, decisioning, and reporting in order."""

    name = "orchestrator"

    def __init__(
        self,
        config: EngineConfig,
        llm_client: LLMClient | None = None,
        memory_store: MemoryStore | None = None,
    ) -> None:
        super().__init__(config)
        self.intake = IntakeAgent(config)
        self.enrichment = EnrichmentAgent(config)
        self.scoring = RiskScoringAgent(config)
        self.decision = DecisionAgent(config)
        self.reporting = ReportingAgent(config, llm_client=llm_client)
        self.memory_store = memory_store

    def investigate(
        self,
        transaction: Transaction,
        account_history: list[Transaction] | None = None,
        enrichment: dict | None = None,
    ) -> InvestigationResult:
        """Execute the full investigation workflow for one transaction."""
        case = self.intake.run(transaction, account_history)
        if enrichment:
            case.enrichment.update(enrichment)
        case = self.enrichment.run(case)
        self._recall_history(case)
        case = self.scoring.run(case)
        decision = self.decision.run(case)
        report = self.reporting.run(case, decision)
        self._remember(case, decision)
        return InvestigationResult(decision=decision, report=report)

    def _recall_history(self, case: InvestigationCase) -> None:
        """Inject prior-case history from collective memory, when available."""
        if self.memory_store is None:
            return
        summary = self.memory_store.recall_similar(case.transaction)
        if summary.has_history:
            case.enrichment["memory_recall"] = summary.as_enrichment()

    def _remember(self, case: InvestigationCase, decision: Decision) -> None:
        """Persist the completed investigation to collective memory."""
        if self.memory_store is None:
            return
        self.memory_store.record_investigation(case, decision)
