---
name: data-enrichment
description: Augments an investigation case with derived context features such as device familiarity and account history signals, and merges external reference data. WHEN: "enrich the case", "add context to transaction", "look up device history", "gather reference data", "prepare case for scoring".
---

# Data Enrichment

## Overview

Adds the contextual features that detection skills depend on. Enrichment derives
features deterministically from account history and merges any externally
supplied reference data, such as deny-list flags from upstream services.

## When to Use

- Immediately after `transaction-intake`, before any detection skill runs.
- When detection skills require context that is not present on the raw event.

## Inputs

| Input | Required | Description |
| --- | --- | --- |
| `case` | yes | The validated investigation case. |
| `enrichment` | no | Externally supplied flags, for example `card_blacklisted`, `ip_blacklisted`, `device_known`. |

## Process

1. For the transaction device, determine whether it has prior history for this
   account and set `device_known`.
2. Count the distinct accounts that have transacted on the same device and set
   `device_account_count`.
3. Merge externally supplied enrichment. External values take precedence over
   derived values.
4. Record which features could not be derived as unavailable rather than guessing.

## Outputs

The same case with a populated `enrichment` map.

## Reference Implementation

`src/fraud_investigator/agents/enrichment_agent.py`.

## Rationalizations

| Excuse | Rebuttal |
| --- | --- |
| "There is no history, so skip enrichment." | Absence of history is itself a feature. Record it explicitly. |
| "Guess a value to fill the gap." | Guessing corrupts the score. Mark unknowns as unavailable. |

## Red Flags

- Derived features silently overwrite authoritative external reference data.
- Missing data is filled with assumed defaults.

## Verification

- The case enrichment map reflects either derived values or an explicit
  unavailable marker for each expected feature.
