"""Shared pytest fixtures and builders."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from fraud_investigator.models.transaction import GeoPoint, Transaction
from fraud_investigator.utils.config import load_config

NYC = GeoPoint(latitude=40.7128, longitude=-74.006, country_code="US")
LONDON = GeoPoint(latitude=51.5074, longitude=-0.1278, country_code="GB")


def make_transaction(
    transaction_id: str = "txn_test",
    account_id: str = "acct_test",
    amount: float = 50.0,
    timestamp: datetime | None = None,
    device_id: str | None = "dev_primary",
    location: GeoPoint | None = NYC,
) -> Transaction:
    """Construct a transaction with sensible defaults for tests."""
    return Transaction(
        transaction_id=transaction_id,
        account_id=account_id,
        card_token="tok_test",
        amount=amount,
        currency="USD",
        timestamp=timestamp or datetime(2026, 5, 1, 14, 0, tzinfo=timezone.utc),
        merchant_id="merch_test",
        channel="ecommerce",
        device_id=device_id,
        location=location,
    )


@pytest.fixture()
def config():
    return load_config()
