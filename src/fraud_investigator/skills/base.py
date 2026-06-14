"""Base class shared by all fraud detection skills."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

from fraud_investigator.models.case import InvestigationCase, RiskSignal
from fraud_investigator.utils.config import EngineConfig


class Skill(ABC):
    """Abstract base for a single fraud check.

    Subclasses implement :meth:`evaluate` and return a :class:`RiskSignal` when
    the check fires, or ``None`` when there is nothing to report. Skills must be
    deterministic and side-effect free so investigations remain reproducible.
    """

    #: Stable identifier used for configuration, weighting, and reporting.
    name: str = "skill"

    def __init__(self, config: EngineConfig) -> None:
        self.config = config

    @abstractmethod
    def evaluate(self, case: InvestigationCase) -> Optional[RiskSignal]:
        """Inspect the case and optionally emit a risk signal."""
        raise NotImplementedError

    def _signal(
        self,
        name: str,
        severity: float,
        rationale: str,
        confidence: float = 1.0,
        evidence: dict | None = None,
        critical: bool = False,
    ) -> RiskSignal:
        """Helper to build a well-formed risk signal for this skill."""
        return RiskSignal(
            skill=self.name,
            name=name,
            severity=max(0.0, min(100.0, severity)),
            confidence=confidence,
            rationale=rationale,
            critical=critical,
            evidence=evidence or {},
        )
