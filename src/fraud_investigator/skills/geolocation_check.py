"""Geolocation checks: high-risk geographies and impossible travel."""

from __future__ import annotations

import math
from typing import Optional

from fraud_investigator.models.case import InvestigationCase, RiskSignal
from fraud_investigator.models.transaction import GeoPoint
from fraud_investigator.skills.base import Skill

_EARTH_RADIUS_KM = 6371.0


def haversine_km(origin: GeoPoint, destination: GeoPoint) -> float:
    """Return the great-circle distance between two points in kilometers."""
    lat1, lon1 = math.radians(origin.latitude), math.radians(origin.longitude)
    lat2, lon2 = math.radians(destination.latitude), math.radians(destination.longitude)
    delta_lat = lat2 - lat1
    delta_lon = lon2 - lon1
    a = (
        math.sin(delta_lat / 2) ** 2
        + math.cos(lat1) * math.cos(lat2) * math.sin(delta_lon / 2) ** 2
    )
    return 2 * _EARTH_RADIUS_KM * math.asin(math.sqrt(a))


class GeolocationCheckSkill(Skill):
    """Flags high-risk countries and physically impossible travel patterns."""

    name = "geolocation_check"

    def evaluate(self, case: InvestigationCase) -> Optional[RiskSignal]:
        settings = self.config.geolocation_check
        txn = case.transaction
        if txn.location is None:
            return None

        severity = 0.0
        reasons: list[str] = []
        evidence: dict[str, object] = {}

        country = (txn.location.country_code or "").upper()
        if country and country in {c.upper() for c in settings.high_risk_countries}:
            severity += 40.0
            reasons.append(f"Transaction originates from high-risk country '{country}'.")
            evidence["country_code"] = country

        prior_located = [
            prior
            for prior in case.account_history
            if prior.account_id == txn.account_id and prior.location is not None
        ]
        if prior_located:
            last = max(prior_located, key=lambda item: item.timestamp)
            if last.location is not None:
                hours = abs((txn.timestamp - last.timestamp).total_seconds()) / 3600.0
                distance = haversine_km(last.location, txn.location)
                speed = distance / hours if hours > 0 else float("inf")
                if speed > settings.impossible_travel_kmh:
                    severity += 55.0
                    reasons.append(
                        f"Implied travel speed {speed:,.0f} km/h between consecutive "
                        f"transactions exceeds feasible limit."
                    )
                    evidence["implied_speed_kmh"] = round(speed, 1)
                    evidence["distance_km"] = round(distance, 1)

        if severity == 0.0:
            return None

        return self._signal(
            name="geolocation_risk",
            severity=severity,
            rationale=" ".join(reasons),
            evidence=evidence,
        )
