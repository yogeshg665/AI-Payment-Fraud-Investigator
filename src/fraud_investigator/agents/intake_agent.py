"""Intake agent: validates input and constructs the investigation case."""

from __future__ import annotations

import uuid

from fraud_investigator.agents.base import Agent
from fraud_investigator.models.case import InvestigationCase
from fraud_investigator.models.transaction import Transaction


class IntakeAgent(Agent):
    """Normalizes raw input into a validated :class:`InvestigationCase`."""

    name = "intake"

    def run(
        self,
        transaction: Transaction,
        account_history: list[Transaction] | None = None,
    ) -> InvestigationCase:
        """Create a case from a transaction and optional account history."""
        history = account_history or []
        case = InvestigationCase(
            case_id=f"case_{uuid.uuid4().hex[:12]}",
            transaction=transaction,
            account_history=sorted(history, key=lambda item: item.timestamp),
        )
        self.logger.info(
            "Opened %s for transaction %s on account %s",
            case.case_id,
            transaction.transaction_id,
            transaction.account_id,
        )
        return case
