"""Device fingerprint checks: new or shared devices across accounts."""

from __future__ import annotations

from typing import Optional

from fraud_investigator.models.case import InvestigationCase, RiskSignal
from fraud_investigator.skills.base import Skill


class DeviceFingerprintSkill(Skill):
    """Flags unrecognized devices and devices shared across many accounts.

    Enrichment may supply ``device_account_count`` (the number of distinct
    accounts that have used the device) and ``device_known`` (whether the device
    has prior history for this account).
    """

    name = "device_fingerprint"

    def evaluate(self, case: InvestigationCase) -> Optional[RiskSignal]:
        txn = case.transaction
        if txn.device_id is None:
            return None

        severity = 0.0
        reasons: list[str] = []
        evidence: dict[str, object] = {}

        device_known = case.enrichment.get("device_known")
        if device_known is False:
            severity += 30.0
            reasons.append("Device has no prior history for this account.")
            evidence["device_known"] = False

        shared_count = case.enrichment.get("device_account_count")
        if isinstance(shared_count, (int, float)) and shared_count >= 3:
            severity += min(50.0, 15.0 * (shared_count - 2))
            reasons.append(
                f"Device is shared across {int(shared_count)} distinct accounts, "
                f"a common pattern in account-takeover fraud."
            )
            evidence["device_account_count"] = int(shared_count)

        if severity == 0.0:
            return None

        return self._signal(
            name="device_risk",
            severity=severity,
            rationale=" ".join(reasons),
            evidence=evidence,
        )
