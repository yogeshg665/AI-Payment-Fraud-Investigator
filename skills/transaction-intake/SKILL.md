---
name: transaction-intake
description: Validates and normalizes a raw payment transaction into a structured investigation case, enforcing data minimization. WHEN: "open a fraud case", "intake this transaction", "validate transaction data", "start investigating this payment", "normalize transaction input".
---

# Transaction Intake

## Overview

Converts raw transaction input into a validated `InvestigationCase` that the rest
of the pipeline can trust. This is the first phase of every investigation.

## When to Use

- As the first step of any investigation, before enrichment or detection.
- When transaction input arrives from an external system and must be validated.

## Inputs

| Input | Required | Description |
| --- | --- | --- |
| `transaction` | yes | The payment event, including amount, currency, timestamp, merchant, and channel. |
| `account_history` | no | Recent prior transactions for the same account, used later for context. |

## Process

1. Validate the transaction against the schema. Reject negative amounts, invalid
   currency or country codes, and out-of-range coordinates.
2. Confirm the payload uses a tokenized card reference and a pseudonymous account
   identifier. If raw card data is present, stop and reject the input.
3. Sort any provided account history by timestamp ascending.
4. Open a new case with a unique identifier and attach the transaction and
   history.

## Outputs

A validated `InvestigationCase` ready for `data-enrichment`.

## Reference Implementation

`src/fraud_investigator/agents/intake_agent.py` and the `Transaction` and
`InvestigationCase` models in `src/fraud_investigator/models/`.

## Rationalizations

| Excuse | Rebuttal |
| --- | --- |
| "The data looks fine, skip validation." | Unvalidated input corrupts every downstream signal and the audit trail. |
| "Raw card data is convenient to keep." | It is never required here and creates compliance liability. Reject it. |

## Red Flags

- A case is opened with missing required fields.
- Raw cardholder data appears anywhere in the payload.

## Verification

- A case object exists with a unique identifier and a schema-valid transaction.
