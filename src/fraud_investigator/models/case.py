"""Investigation case and risk signal models."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional

from pydantic import BaseModel, Field

from fraud_investigator.models.transaction import Transaction


class RiskSignal(BaseModel):
    """A single fraud indicator produced by a skill.

    Each signal carries a normalized severity (0-100), a confidence value, and
    a human-readable rationale so investigations remain explainable.
    """

    skill: str = Field(..., description="Name of the skill that emitted the signal.")
    name: str = Field(..., description="Short signal identifier.")
    severity: float = Field(..., ge=0.0, le=100.0, description="Risk contribution, 0-100.")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Signal confidence, 0-1.")
    rationale: str = Field(..., description="Explanation of why the signal fired.")
    critical: bool = Field(
        default=False,
        description="Definitive indicator that should set a floor on the aggregate score.",
    )
    evidence: dict[str, Any] = Field(default_factory=dict, description="Supporting data points.")

    @property
    def triggered(self) -> bool:
        """Whether this signal contributes meaningful risk."""
        return self.severity > 0.0


class InvestigationCase(BaseModel):
    """The unit of work that flows through the investigation pipeline."""

    case_id: str = Field(..., description="Unique case identifier.")
    transaction: Transaction = Field(..., description="Transaction under investigation.")
    account_history: list[Transaction] = Field(
        default_factory=list,
        description="Recent prior transactions for the same account, used for context.",
    )
    enrichment: dict[str, Any] = Field(
        default_factory=dict,
        description="Contextual data added during the enrichment stage.",
    )
    signals: list[RiskSignal] = Field(default_factory=list)
    risk_score: float = Field(default=0.0, ge=0.0, le=100.0)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    notes: Optional[str] = Field(default=None)

    def add_signal(self, signal: RiskSignal) -> None:
        """Attach a risk signal to the case."""
        self.signals.append(signal)

    def triggered_signals(self) -> list[RiskSignal]:
        """Return only the signals that contributed risk."""
        return [signal for signal in self.signals if signal.triggered]
