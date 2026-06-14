"""Registry that assembles the default skill set from configuration."""

from __future__ import annotations

from fraud_investigator.skills.anomaly_detection import AnomalyDetectionSkill
from fraud_investigator.skills.base import Skill
from fraud_investigator.skills.blacklist_check import BlacklistCheckSkill
from fraud_investigator.skills.device_fingerprint import DeviceFingerprintSkill
from fraud_investigator.skills.geolocation_check import GeolocationCheckSkill
from fraud_investigator.skills.transaction_analysis import TransactionAnalysisSkill
from fraud_investigator.skills.velocity_check import VelocityCheckSkill
from fraud_investigator.utils.config import EngineConfig

_SKILL_TYPES: list[type[Skill]] = [
    TransactionAnalysisSkill,
    VelocityCheckSkill,
    GeolocationCheckSkill,
    DeviceFingerprintSkill,
    BlacklistCheckSkill,
    AnomalyDetectionSkill,
]


def default_skills(config: EngineConfig) -> list[Skill]:
    """Instantiate the standard skill set bound to the given configuration."""
    return [skill_type(config) for skill_type in _SKILL_TYPES]
