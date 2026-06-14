"""Batch investigation pipeline."""

from fraud_investigator.pipeline.investigation_pipeline import (
    InvestigationPipeline,
    load_cases_from_json,
)

__all__ = ["InvestigationPipeline", "load_cases_from_json"]
