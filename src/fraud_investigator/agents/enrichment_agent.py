"""Enrichment agent: augments the case with derived context features.

In production, enrichment would call external reference services (device
intelligence, threat feeds, watchlists). This implementation derives features
deterministically from the provided account history and merges any enrichment
supplied with the input, so the engine runs without external dependencies while
preserving the same downstream contract.
"""

from __future__ import annotations

from fraud_investigator.agents.base import Agent
from fraud_investigator.models.case import InvestigationCase


class EnrichmentAgent(Agent):
    """Computes contextual features used by downstream skills."""

    name = "enrichment"

    def run(self, case: InvestigationCase) -> InvestigationCase:
        txn = case.transaction
        derived: dict[str, object] = {}

        if txn.device_id is not None:
            account_devices = {
                prior.device_id
                for prior in case.account_history
                if prior.account_id == txn.account_id and prior.device_id is not None
            }
            derived["device_known"] = txn.device_id in account_devices

            accounts_on_device = {
                prior.account_id
                for prior in case.account_history
                if prior.device_id == txn.device_id
            }
            accounts_on_device.add(txn.account_id)
            derived["device_account_count"] = len(accounts_on_device)

        # Caller-supplied enrichment takes precedence over derived values.
        merged = {**derived, **case.enrichment}
        case.enrichment = merged
        self.logger.info("Enriched %s with %d feature(s)", case.case_id, len(merged))
        return case
