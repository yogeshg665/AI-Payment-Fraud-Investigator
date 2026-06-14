"""Statistical anomaly detection on transaction amount versus account history."""

from __future__ import annotations

import statistics
from typing import Optional

from fraud_investigator.models.case import InvestigationCase, RiskSignal
from fraud_investigator.skills.base import Skill


class AnomalyDetectionSkill(Skill):
    """Flags transaction amounts that are statistical outliers for the account.

    A z-score is computed against the account's historical spend. Accounts with
    insufficient history are skipped to avoid unreliable signals.
    """

    name = "anomaly_detection"
    _MIN_HISTORY = 5

    def evaluate(self, case: InvestigationCase) -> Optional[RiskSignal]:
        txn = case.transaction
        amounts = [
            prior.amount
            for prior in case.account_history
            if prior.account_id == txn.account_id
        ]
        if len(amounts) < self._MIN_HISTORY:
            return None

        mean = statistics.fmean(amounts)
        stdev = statistics.pstdev(amounts)
        if stdev == 0.0:
            return None

        zscore = (txn.amount - mean) / stdev
        threshold = self.config.anomaly_detection.zscore_threshold
        if zscore < threshold:
            return None

        severity = min(70.0, 20.0 + 15.0 * (zscore - threshold + 1))
        return self._signal(
            name="amount_outlier",
            severity=severity,
            rationale=(
                f"Transaction amount {txn.amount:,.2f} is {zscore:,.1f} standard "
                f"deviations above the account mean of {mean:,.2f}."
            ),
            confidence=0.9,
            evidence={"zscore": round(zscore, 2), "account_mean": round(mean, 2)},
        )
