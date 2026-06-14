"""Integration tests for the end-to-end investigation pipeline."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

from fraud_investigator.models.decision import DecisionOutcome
from fraud_investigator.pipeline.investigation_pipeline import (
    CaseInput,
    InvestigationPipeline,
    load_cases_from_json,
)
from tests.conftest import LONDON, NYC, make_transaction

SAMPLE_PATH = Path(__file__).resolve().parents[1] / "data" / "samples" / "sample_transactions.json"


def test_clean_transaction_is_approved():
    pipeline = InvestigationPipeline()
    txn = make_transaction(amount=25.0)
    result = pipeline.run_one(CaseInput(transaction=txn))
    assert result.decision.outcome is DecisionOutcome.APPROVE
    assert result.decision.risk_score < 45.0


def test_high_risk_transaction_is_declined():
    pipeline = InvestigationPipeline()
    base = datetime(2026, 5, 1, 3, 0, tzinfo=timezone.utc)
    prior = make_transaction(transaction_id="prior", timestamp=base, location=NYC)
    txn = make_transaction(
        transaction_id="suspicious",
        amount=9000.0,
        timestamp=base + timedelta(minutes=20),
        location=LONDON,
        device_id="dev_unknown",
    )
    result = pipeline.run_one(
        CaseInput(
            transaction=txn,
            account_history=[prior],
            enrichment={"card_blacklisted": True, "device_known": False},
        )
    )
    assert result.decision.outcome is DecisionOutcome.DECLINE
    assert result.decision.risk_score >= 75.0
    assert result.report["signals"]


def test_report_structure_is_complete():
    pipeline = InvestigationPipeline()
    result = pipeline.run_one(CaseInput(transaction=make_transaction()))
    report = result.report
    for key in ("case_id", "risk_score", "decision", "confidence", "narrative", "signals"):
        assert key in report


def test_batch_writes_reports(tmp_path):
    pipeline = InvestigationPipeline()
    cases = load_cases_from_json(SAMPLE_PATH)
    results = pipeline.run_batch(cases, output_dir=tmp_path)
    assert len(results) == len(cases)
    written = list(tmp_path.glob("*.json"))
    assert len(written) == len(cases)


def test_sample_file_loads():
    cases = load_cases_from_json(SAMPLE_PATH)
    assert len(cases) == 2
