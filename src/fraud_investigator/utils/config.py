"""Typed configuration model and loader for the investigation engine."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field


class DecisionPolicy(BaseModel):
    decline_threshold: float = 75.0
    escalate_threshold: float = 45.0


class EngineSettings(BaseModel):
    max_batch_size: int = 1000
    persist_reports: bool = True


class VelocityCheckConfig(BaseModel):
    window_minutes: int = 60
    max_transactions: int = 5
    max_amount: float = 5000.0


class GeolocationCheckConfig(BaseModel):
    impossible_travel_kmh: float = 900.0
    high_risk_countries: list[str] = Field(default_factory=list)


class TransactionAnalysisConfig(BaseModel):
    high_value_amount: float = 2500.0
    unusual_hours: list[int] = Field(default_factory=lambda: [0, 1, 2, 3, 4])


class AnomalyDetectionConfig(BaseModel):
    zscore_threshold: float = 3.0


class MemoryConfig(BaseModel):
    # When enabled, investigations are persisted and prior history is recalled.
    enabled: bool = False
    # Filesystem path to the SQLite memory database.
    path: str = ".fraud_memory/memory.db"


class EngineConfig(BaseModel):
    """Aggregate, strongly typed engine configuration."""

    engine: EngineSettings = Field(default_factory=EngineSettings)
    decision_policy: DecisionPolicy = Field(default_factory=DecisionPolicy)
    skill_weights: dict[str, float] = Field(default_factory=dict)
    velocity_check: VelocityCheckConfig = Field(default_factory=VelocityCheckConfig)
    geolocation_check: GeolocationCheckConfig = Field(default_factory=GeolocationCheckConfig)
    transaction_analysis: TransactionAnalysisConfig = Field(
        default_factory=TransactionAnalysisConfig
    )
    anomaly_detection: AnomalyDetectionConfig = Field(default_factory=AnomalyDetectionConfig)
    memory: MemoryConfig = Field(default_factory=MemoryConfig)

    def _apply_env_overrides(self) -> None:
        """Allow critical thresholds to be overridden via environment variables."""
        decline = os.getenv("RISK_DECLINE_THRESHOLD")
        escalate = os.getenv("RISK_ESCALATE_THRESHOLD")
        if decline is not None:
            self.decision_policy.decline_threshold = float(decline)
        if escalate is not None:
            self.decision_policy.escalate_threshold = float(escalate)
        memory_enabled = os.getenv("MEMORY_ENABLED")
        memory_path = os.getenv("MEMORY_PATH")
        if memory_enabled is not None:
            self.memory.enabled = memory_enabled.strip().lower() in {"1", "true", "yes", "on"}
        if memory_path is not None:
            self.memory.path = memory_path


def _default_config_path() -> Path:
    return Path(__file__).resolve().parents[3] / "config" / "config.yaml"


def load_config(path: str | Path | None = None) -> EngineConfig:
    """Load engine configuration from YAML, applying environment overrides.

    Falls back to built-in defaults when no configuration file is present.
    """
    config_path = Path(path) if path else _default_config_path()
    data: dict[str, Any] = {}
    if config_path.exists():
        with config_path.open("r", encoding="utf-8") as handle:
            data = yaml.safe_load(handle) or {}

    config = EngineConfig(**data)
    config._apply_env_overrides()
    return config
