"""Transaction and supporting value objects."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class GeoPoint(BaseModel):
    """A geographic coordinate with an optional ISO country code."""

    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)
    country_code: Optional[str] = Field(
        default=None,
        description="ISO 3166-1 alpha-2 country code, for example 'US'.",
        min_length=2,
        max_length=2,
    )


class Transaction(BaseModel):
    """A single payment transaction submitted for investigation.

    The model intentionally avoids storing raw payment instrument data. Only a
    tokenized card reference and a coarse account identifier are retained so the
    engine can operate without handling sensitive cardholder data.
    """

    transaction_id: str = Field(..., description="Unique transaction identifier.")
    account_id: str = Field(..., description="Pseudonymous account identifier.")
    card_token: str = Field(..., description="Tokenized payment instrument reference.")
    amount: float = Field(..., ge=0.0, description="Transaction amount in minor-to-major units.")
    currency: str = Field(default="USD", min_length=3, max_length=3)
    timestamp: datetime = Field(..., description="UTC time the transaction occurred.")
    merchant_id: str = Field(..., description="Merchant identifier.")
    merchant_category: str = Field(default="unknown", description="Merchant category descriptor.")
    channel: str = Field(default="ecommerce", description="card_present, ecommerce, or mobile.")
    device_id: Optional[str] = Field(default=None, description="Device fingerprint identifier.")
    ip_address: Optional[str] = Field(default=None, description="Originating IP address.")
    location: Optional[GeoPoint] = Field(default=None, description="Transaction geolocation.")

    def amount_label(self) -> str:
        """Return a human-readable amount with currency for reporting."""
        return f"{self.amount:,.2f} {self.currency}"
