"""Tests for collective memory, recall, the feedback loop, and calibration."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fraud_investigator.memory import FeedbackLabel, MemoryStore, calibrate_thresholds
from fraud_investigator.models.decision import DecisionOutcome
from fraud_investigator.pipeline.investigation_pipeline import CaseInput, InvestigationPipeline
from fraud_investigator.utils.config import load_config
from tests.conftest import make_transaction


def _enable_memory(tmp_path):
    config = load_config()
    config.memory.enabled = True
    config.memory.path = str(tmp_path / "memory.db")
    return config


def test_store_records_and_recalls_history(tmp_path):
    store = MemoryStore(tmp_path / "memory.db")
    config = load_config()
    pipeline = InvestigationPipeline(config=config, memory_store=store)

    first = make_transaction(transaction_id="txn_a", amount=9000.0)
    pipeline.run_one(
        CaseInput(transaction=first, enrichment={"card_blacklisted": True})
    )

    follow_up = make_transaction(transaction_id="txn_b", amount=120.0)
    summary = store.recall_similar(follow_up)
    assert summary.has_history
    assert summary.total_prior_cases == 1
    assert "account_id" in summary.matched_on
    store.close()


def test_recall_excludes_own_pending_case(tmp_path):
    store = MemoryStore(tmp_path / "memory.db")
    txn = make_transaction(transaction_id="txn_solo")
    summary = store.recall_similar(txn)
    assert not summary.has_history
    store.close()


def test_adverse_history_raises_score(tmp_path):
    config = _enable_memory(tmp_path)
    pipeline = InvestigationPipeline(config=config)

    # Seed a confirmed-fraud case for the account.
    seed = make_transaction(transaction_id="txn_seed", amount=9000.0)
    seed_result = pipeline.run_one(
        CaseInput(transaction=seed, enrichment={"card_blacklisted": True})
    )
    pipeline.record_feedback(
        seed_result.decision.case_id, FeedbackLabel.CONFIRMED_FRAUD
    )

    # A later, otherwise-clean transaction on the same account inherits context.
    clean = make_transaction(transaction_id="txn_later", amount=40.0)
    result = pipeline.run_one(CaseInput(transaction=clean))

    signal_names = [s["name"] for s in result.report["signals"]]
    assert "adverse_history" in signal_names
    assert result.decision.risk_score > 0.0


def test_feedback_returns_false_for_unknown_case(tmp_path):
    store = MemoryStore(tmp_path / "memory.db")
    assert store.record_feedback("missing", FeedbackLabel.LEGITIMATE) is False
    store.close()


def test_calibration_recommends_separable_thresholds(tmp_path):
    config = _enable_memory(tmp_path)
    pipeline = InvestigationPipeline(config=config)
    store = pipeline.memory_store
    assert store is not None

    base = datetime(2026, 5, 1, 12, 0, tzinfo=timezone.utc)
    fraud_txn = make_transaction(
        transaction_id="txn_fraud",
        account_id="acct_fraud",
        amount=9000.0,
        timestamp=base,
    )
    fraud_result = pipeline.run_one(
        CaseInput(transaction=fraud_txn, enrichment={"card_blacklisted": True})
    )
    pipeline.record_feedback(fraud_result.decision.case_id, FeedbackLabel.CONFIRMED_FRAUD)

    legit_txn = make_transaction(
        transaction_id="txn_legit",
        account_id="acct_legit",
        amount=20.0,
        timestamp=base + timedelta(hours=1),
    )
    legit_result = pipeline.run_one(CaseInput(transaction=legit_txn))
    pipeline.record_feedback(legit_result.decision.case_id, FeedbackLabel.LEGITIMATE)

    report = calibrate_thresholds(store.all_records(), config.decision_policy)
    assert report.confirmed_fraud_cases == 1
    assert report.legitimate_cases == 1
    assert report.suggested_decline_threshold is not None
    assert report.suggested_decline_threshold > report.suggested_escalate_threshold - 0.01


def test_calibration_needs_both_labels(tmp_path):
    store = MemoryStore(tmp_path / "memory.db")
    config = load_config()
    report = calibrate_thresholds(store.all_records(), config.decision_policy)
    assert report.suggested_decline_threshold is None
    assert report.rationale
    store.close()


def test_memory_disabled_by_default():
    pipeline = InvestigationPipeline(config=load_config())
    assert pipeline.memory_store is None


def test_pipeline_without_memory_is_unchanged():
    pipeline = InvestigationPipeline(config=load_config())
    result = pipeline.run_one(CaseInput(transaction=make_transaction(amount=25.0)))
    assert result.decision.outcome is DecisionOutcome.APPROVE
