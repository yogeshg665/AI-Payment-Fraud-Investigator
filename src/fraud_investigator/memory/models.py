"""Data models for collective case memory and the outcome feedback loop.

These models persist only pseudonymous account identifiers and tokenized card
references. No raw cardholder data is ever stored.
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel, Field


class FeedbackLabel(str, Enum):
    """Analyst-confirmed ground truth for a recorded investigation."""

    UNREVIEWED = "unreviewed"
    CONFIRMED_FRAUD = "confirmed_fraud"
    LEGITIMATE = "legitimate"


class CaseMemoryRecord(BaseModel):
    """A persisted summary of one completed investigation.

    Records form the collective memory the engine draws on to recognize repeat
    offenders and to calibrate thresholds from real outcomes.
    """

    case_id: str = Field(..., description="Unique case identifier.")
    account_id: str = Field(..., description="Pseudonymous account identifier.")
    card_token: str = Field(..., description="Tokenized payment instrument reference.")
    merchant_id: str = Field(..., description="Merchant identifier.")
    amount: float = Field(..., ge=0.0)
    currency: str = Field(default="USD", min_length=3, max_length=3)
    occurred_at: datetime = Field(..., description="When the transaction occurred (UTC).")
    risk_score: float = Field(..., ge=0.0, le=100.0)
    outcome: str = Field(..., description="Decision outcome value, e.g. 'decline'.")
    signal_names: list[str] = Field(default_factory=list)
    narrative: str = Field(default="")
    label: FeedbackLabel = Field(default=FeedbackLabel.UNREVIEWED)
    label_note: str | None = Field(default=None)
    recorded_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class RecallSummary(BaseModel):
    """Aggregate history for an account or card, injected during enrichment.

    The summary is deterministic: it is a pure function of the records already
    present in the store at recall time.
    """

    matched_on: list[str] = Field(
        default_factory=list,
        description="Which keys matched prior cases, e.g. ['account_id', 'card_token'].",
    )
    total_prior_cases: int = 0
    confirmed_fraud_count: int = 0
    legitimate_count: int = 0
    prior_decline_count: int = 0
    prior_escalation_count: int = 0
    most_recent_outcome: str | None = None
    most_recent_at: datetime | None = None

    @property
    def has_history(self) -> bool:
        return self.total_prior_cases > 0

    def as_enrichment(self) -> dict[str, object]:
        """Render the summary as a plain dict for case enrichment."""
        return {
            "matched_on": list(self.matched_on),
            "total_prior_cases": self.total_prior_cases,
            "confirmed_fraud_count": self.confirmed_fraud_count,
            "legitimate_count": self.legitimate_count,
            "prior_decline_count": self.prior_decline_count,
            "prior_escalation_count": self.prior_escalation_count,
            "most_recent_outcome": self.most_recent_outcome,
        }


class CalibrationReport(BaseModel):
    """Threshold recommendations derived from labeled feedback.

    The report is advisory only. It never mutates configuration so that scoring
    and decisioning remain deterministic and under human control.
    """

    labeled_cases: int = 0
    confirmed_fraud_cases: int = 0
    legitimate_cases: int = 0
    current_decline_threshold: float = 0.0
    current_escalate_threshold: float = 0.0
    suggested_decline_threshold: float | None = None
    suggested_escalate_threshold: float | None = None
    rationale: list[str] = Field(default_factory=list)
