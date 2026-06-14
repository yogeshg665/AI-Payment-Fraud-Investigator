"""Decision model representing the final investigation outcome."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel, Field


class DecisionOutcome(str, Enum):
    """Terminal outcomes for an investigated case."""

    APPROVE = "approve"
    ESCALATE = "escalate"
    DECLINE = "decline"


class Decision(BaseModel):
    """The recommendation produced by the decision agent.

    A decision is fully explainable: it references the aggregate risk score, the
    triggering signals, and a narrative summary suitable for an audit trail.
    """

    case_id: str
    outcome: DecisionOutcome
    risk_score: float = Field(..., ge=0.0, le=100.0)
    confidence: float = Field(..., ge=0.0, le=1.0)
    reasons: list[str] = Field(default_factory=list)
    recommended_actions: list[str] = Field(default_factory=list)
    narrative: str = Field(default="")
    decided_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def is_actionable_by_human(self) -> bool:
        """Whether the case should be routed to a human review queue."""
        return self.outcome is DecisionOutcome.ESCALATE
