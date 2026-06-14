---
name: watchlist-screening
description: Screens the card, IP, and merchant against deny lists and watchlists, emitting a critical signal for confirmed deny-list matches. WHEN: "check blacklist", "watchlist screening", "deny list match", "is this card blocked", "sanctioned IP", "merchant watchlist".
---

# Watchlist Screening

## Overview

Interprets deny-list and watchlist flags supplied by upstream reference services.
A confirmed card deny-list match is a definitive indicator and is marked critical
so it sets a floor on the aggregate risk score.

## When to Use

- During the detection phase, after enrichment has merged reference data.

## Inputs

| Input | Required | Description |
| --- | --- | --- |
| `enrichment.card_blacklisted` | no | Card is on the deny list. Critical when true. |
| `enrichment.ip_blacklisted` | no | Originating IP is on a threat-intelligence list. |
| `enrichment.merchant_watchlisted` | no | Merchant is on an internal watchlist. |

## Process

1. If `card_blacklisted` is true, add high severity and mark the signal critical.
2. If `ip_blacklisted` is true, add severity.
3. If `merchant_watchlisted` is true, add severity.
4. Emit a `watchlist_match` signal with the matched lists as evidence.

## Outputs

Zero or one `RiskSignal`. The signal is critical when a card deny-list match is
present.

## Reference Implementation

`src/fraud_investigator/skills/blacklist_check.py`.

## Rationalizations

| Excuse | Rebuttal |
| --- | --- |
| "The list might be stale." | List hygiene is an upstream concern; act on the match and record the source. |
| "Let scoring dilute the deny-list hit." | A confirmed deny-list match is definitive; it floors the score by design. |

## Red Flags

- A card deny-list match is emitted as a non-critical signal.
- The skill infers list membership rather than reading authoritative flags.

## Verification

- A `card_blacklisted` input yields a critical signal with severity at or above
  the decline threshold.
