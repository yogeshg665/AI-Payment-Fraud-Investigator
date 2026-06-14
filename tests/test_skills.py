"""Unit tests for individual fraud detection skills."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fraud_investigator.models.case import InvestigationCase
from fraud_investigator.skills.anomaly_detection import AnomalyDetectionSkill
from fraud_investigator.skills.blacklist_check import BlacklistCheckSkill
from fraud_investigator.skills.geolocation_check import GeolocationCheckSkill
from fraud_investigator.skills.transaction_analysis import TransactionAnalysisSkill
from fraud_investigator.skills.velocity_check import VelocityCheckSkill
from tests.conftest import LONDON, NYC, make_transaction


def _case(transaction, history=None, enrichment=None) -> InvestigationCase:
    return InvestigationCase(
        case_id="case_test",
        transaction=transaction,
        account_history=history or [],
        enrichment=enrichment or {},
    )


def test_high_value_triggers_transaction_analysis(config):
    txn = make_transaction(amount=10000.0)
    signal = TransactionAnalysisSkill(config).evaluate(_case(txn))
    assert signal is not None
    assert signal.severity > 0


def test_low_value_normal_hour_no_signal(config):
    txn = make_transaction(amount=20.0)
    assert TransactionAnalysisSkill(config).evaluate(_case(txn)) is None


def test_velocity_check_detects_burst(config):
    base = datetime(2026, 5, 1, 12, 0, tzinfo=timezone.utc)
    history = [
        make_transaction(transaction_id=f"h{i}", amount=100.0, timestamp=base + timedelta(minutes=i))
        for i in range(6)
    ]
    current = make_transaction(amount=100.0, timestamp=base + timedelta(minutes=10))
    signal = VelocityCheckSkill(config).evaluate(_case(current, history=history))
    assert signal is not None
    assert signal.evidence["transaction_count"] >= 6


def test_geolocation_impossible_travel(config):
    base = datetime(2026, 5, 1, 12, 0, tzinfo=timezone.utc)
    prior = make_transaction(transaction_id="prior", timestamp=base, location=NYC)
    current = make_transaction(
        transaction_id="current",
        timestamp=base + timedelta(minutes=30),
        location=LONDON,
    )
    signal = GeolocationCheckSkill(config).evaluate(_case(current, history=[prior]))
    assert signal is not None
    assert "implied_speed_kmh" in signal.evidence


def test_blacklist_card_high_severity(config):
    txn = make_transaction()
    signal = BlacklistCheckSkill(config).evaluate(
        _case(txn, enrichment={"card_blacklisted": True})
    )
    assert signal is not None
    assert signal.severity >= 90.0


def test_anomaly_detection_requires_history(config):
    txn = make_transaction(amount=5000.0)
    assert AnomalyDetectionSkill(config).evaluate(_case(txn)) is None


def test_anomaly_detection_flags_outlier(config):
    history = [
        make_transaction(transaction_id=f"h{i}", amount=40.0 + i * 5.0) for i in range(8)
    ]
    current = make_transaction(amount=5000.0)
    signal = AnomalyDetectionSkill(config).evaluate(_case(current, history=history))
    assert signal is not None
    assert signal.evidence["zscore"] > 3.0
