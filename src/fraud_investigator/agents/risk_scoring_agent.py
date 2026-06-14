"""Risk scoring agent: runs all skills and aggregates a weighted risk score."""

from __future__ import annotations

from fraud_investigator.agents.base import Agent
from fraud_investigator.models.case import InvestigationCase
from fraud_investigator.skills.base import Skill
from fraud_investigator.skills.registry import default_skills


class RiskScoringAgent(Agent):
    """Executes the skill suite and computes the aggregate risk score.

    The aggregate score is a confidence-weighted, configuration-weighted blend
    of individual signal severities, bounded to the 0-100 range. Using a blend
    rather than a simple maximum keeps the score robust to single noisy signals
    while still reacting strongly to multiple corroborating indicators.
    """

    name = "risk_scoring"

    def __init__(self, config, skills: list[Skill] | None = None) -> None:
        super().__init__(config)
        self.skills = skills if skills is not None else default_skills(config)

    def run(self, case: InvestigationCase) -> InvestigationCase:
        for skill in self.skills:
            try:
                signal = skill.evaluate(case)
            except Exception:  # pragma: no cover - defensive isolation per skill
                self.logger.exception("Skill '%s' raised an error; skipping", skill.name)
                continue
            if signal is not None:
                case.add_signal(signal)

        case.risk_score = self._aggregate(case)
        self.logger.info(
            "Scored %s: risk=%.1f from %d signal(s)",
            case.case_id,
            case.risk_score,
            len(case.triggered_signals()),
        )
        return case

    def _aggregate(self, case: InvestigationCase) -> float:
        weights = self.config.skill_weights
        triggered = case.triggered_signals()
        if not triggered:
            return 0.0

        weighted_sum = 0.0
        weight_total = 0.0
        for signal in triggered:
            weight = weights.get(signal.skill, 0.1) * signal.confidence
            weighted_sum += signal.severity * weight
            weight_total += weight

        blended = weighted_sum / weight_total if weight_total else 0.0

        # Apply a corroboration boost: multiple independent triggers raise risk.
        corroboration = min(0.25, 0.05 * (len(triggered) - 1))
        score = blended * (1.0 + corroboration)

        # A definitive (critical) indicator, such as a deny-list hit, sets a
        # floor on the score so it cannot be diluted by weaker signals.
        critical_floor = max(
            (signal.severity for signal in triggered if signal.critical),
            default=0.0,
        )
        score = max(score, critical_floor)
        return round(max(0.0, min(100.0, score)), 1)
