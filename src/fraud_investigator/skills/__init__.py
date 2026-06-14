"""Fraud detection skills.

A skill is a single, focused, explainable fraud check. Each skill consumes an
investigation case and emits zero or one risk signal. Skills are composable and
independently testable, which keeps the engine transparent and auditable.
"""

from fraud_investigator.skills.anomaly_detection import AnomalyDetectionSkill
from fraud_investigator.skills.base import Skill
from fraud_investigator.skills.blacklist_check import BlacklistCheckSkill
from fraud_investigator.skills.device_fingerprint import DeviceFingerprintSkill
from fraud_investigator.skills.geolocation_check import GeolocationCheckSkill
from fraud_investigator.skills.registry import default_skills
from fraud_investigator.skills.transaction_analysis import TransactionAnalysisSkill
from fraud_investigator.skills.velocity_check import VelocityCheckSkill

__all__ = [
    "Skill",
    "TransactionAnalysisSkill",
    "VelocityCheckSkill",
    "GeolocationCheckSkill",
    "DeviceFingerprintSkill",
    "BlacklistCheckSkill",
    "AnomalyDetectionSkill",
    "default_skills",
]
