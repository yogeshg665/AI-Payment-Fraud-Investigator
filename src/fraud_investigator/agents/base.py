"""Base agent definition."""

from __future__ import annotations

from abc import ABC

from fraud_investigator.utils.config import EngineConfig
from fraud_investigator.utils.logging import get_logger


class Agent(ABC):
    """Common base for all investigation agents.

    Agents are stateless with respect to individual cases; all case state is
    carried on the :class:`InvestigationCase` passed between stages. This keeps
    the pipeline horizontally scalable and easy to reason about.
    """

    #: Human-readable agent name used in logs and reports.
    name: str = "agent"

    def __init__(self, config: EngineConfig) -> None:
        self.config = config
        self.logger = get_logger(f"agent.{self.name}")
