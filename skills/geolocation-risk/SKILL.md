---
name: geolocation-risk
description: Flags transactions from high-risk geographies and physically impossible travel between consecutive transactions. WHEN: "check transaction location", "impossible travel", "high risk country", "geolocation fraud", "location mismatch", "geo velocity".
---

# Geolocation Risk

## Overview

Evaluates where a transaction originates. It flags high-risk countries and
computes whether the implied travel speed between consecutive transactions is
physically impossible.

## When to Use

- During the detection phase, whenever the transaction carries a location.

## Inputs

| Input | Required | Description |
| --- | --- | --- |
| `transaction.location` | yes | Latitude, longitude, and country code. |
| `account_history` | no | Prior located transactions for impossible-travel checks. |

## Process

1. If the transaction country is on the `high_risk_countries` list, add severity.
2. Find the most recent prior located transaction for the account.
3. Compute the great-circle distance and divide by the elapsed time to get the
   implied speed.
4. If the implied speed exceeds `impossible_travel_kmh`, add severity and record
   the speed and distance as evidence.
5. Emit a `geolocation_risk` signal when any severity accrued.

## Outputs

Zero or one `RiskSignal`.

## Reference Implementation

`src/fraud_investigator/skills/geolocation_check.py`, including the
`haversine_km` distance function.

## Rationalizations

| Excuse | Rebuttal |
| --- | --- |
| "VPNs make location unreliable." | Treat it as one signal among many; scoring weighs uncertainty via confidence. |
| "The two transactions are close in time, so ignore distance." | Close time plus large distance is exactly the impossible-travel case. |

## Red Flags

- Distance is computed with a flat-earth approximation instead of haversine.
- Elapsed time of zero is divided without guarding against it.

## Verification

- An impossible-travel case yields a signal containing the implied speed.
