# Fraud Typologies Reference

A concise catalog of common payment fraud patterns and the skills that detect
them. Skills pull this in when classifying a case.

## Card Testing

Attackers validate stolen card numbers with many small transactions in a short
period. Detected primarily by `velocity-analysis`, supported by
`anomaly-detection`.

- Indicators: rapid low-value transactions, many declines, new merchant.
- Primary skill: velocity-analysis.

## Account Takeover (ATO)

A legitimate account is compromised and used by an attacker.

- Indicators: new or shared device, impossible travel, changed behavior.
- Primary skills: device-fingerprinting, geolocation-risk, anomaly-detection.

## Stolen Card / Counterfeit

A physical or digital card is used without authorization.

- Indicators: high-value purchases, unusual geography, deny-list match.
- Primary skills: watchlist-screening, transaction-analysis, geolocation-risk.

## Friendly Fraud / Chargeback Abuse

A genuine cardholder disputes a legitimate purchase.

- Indicators: history of disputes, watchlisted merchant category.
- Primary skill: watchlist-screening (merchant signal), supported by history.

## Bust-Out Fraud

An account builds trust over time, then makes large unauthorized purchases.

- Indicators: sudden spend spike after stable history, velocity burst.
- Primary skills: anomaly-detection, velocity-analysis.

## Triangulation

A fraudulent storefront harvests card data used elsewhere.

- Indicators: merchant watchlist match, mismatched geography.
- Primary skills: watchlist-screening, geolocation-risk.

## Mapping Summary

| Typology | Primary Skills |
| --- | --- |
| Card testing | velocity-analysis, anomaly-detection |
| Account takeover | device-fingerprinting, geolocation-risk, anomaly-detection |
| Stolen card | watchlist-screening, transaction-analysis, geolocation-risk |
| Friendly fraud | watchlist-screening |
| Bust-out | anomaly-detection, velocity-analysis |
| Triangulation | watchlist-screening, geolocation-risk |
