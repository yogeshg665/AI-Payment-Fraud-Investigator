"""Blacklist and watchlist checks against enriched reference data."""

from __future__ import annotations

from typing import Optional

from fraud_investigator.models.case import InvestigationCase, RiskSignal
from fraud_investigator.skills.base import Skill


class BlacklistCheckSkill(Skill):
    """Flags entities present on enrichment-provided deny or watch lists.

    Enrichment may supply boolean flags ``card_blacklisted``,
    ``ip_blacklisted``, and ``merchant_watchlisted``. These are sourced from
    upstream reference services; this skill only interprets them.
    """

    name = "blacklist_check"

    def evaluate(self, case: InvestigationCase) -> Optional[RiskSignal]:
        enrichment = case.enrichment
        severity = 0.0
        reasons: list[str] = []
        evidence: dict[str, object] = {}
        critical = False

        if enrichment.get("card_blacklisted") is True:
            severity += 90.0
            critical = True
            reasons.append("Payment instrument appears on the card deny list.")
            evidence["card_blacklisted"] = True

        if enrichment.get("ip_blacklisted") is True:
            severity += 60.0
            reasons.append("Originating IP address appears on a threat-intelligence list.")
            evidence["ip_blacklisted"] = True

        if enrichment.get("merchant_watchlisted") is True:
            severity += 35.0
            reasons.append("Merchant is on an internal watchlist for elevated dispute rates.")
            evidence["merchant_watchlisted"] = True

        if severity == 0.0:
            return None

        return self._signal(
            name="watchlist_match",
            severity=severity,
            rationale=" ".join(reasons),
            evidence=evidence,
            critical=critical,
        )
