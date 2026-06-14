---
name: investigation-reporting
description: Produces an audit-ready case report and a human-readable narrative summarizing the transaction, signals, score, decision, and recommended actions. WHEN: "write the case report", "summarize the investigation", "generate fraud report", "explain the decision", "audit trail", "case narrative".
---

# Investigation Reporting

## Overview

Generates the final deliverable: a structured JSON report and a narrative summary
suitable for an audit trail. The narrative is produced deterministically by
default; an optional language model may enrich it but must not alter the score or
decision.

## When to Use

- As the final phase of every investigation, after `fraud-decisioning`.

## Inputs

| Input | Required | Description |
| --- | --- | --- |
| `case` | yes | The scored case with its signals. |
| `decision` | yes | The recommendation from `fraud-decisioning`. |

## Process

1. Assemble the structured report: case identifier, transaction summary, risk
   score, decision, confidence, triggered signals with rationale and evidence,
   and recommended actions.
2. Build a deterministic narrative covering the transaction, the score, the
   recommendation, the contributing indicators, and the next actions.
3. If a language model is configured, request an enriched narrative using the
   deterministic version as the grounding context. On any failure, keep the
   deterministic narrative.
4. Attach the narrative to the decision and return the report.

## Outputs

A structured report dictionary and a narrative string.

## Reference Implementation

`src/fraud_investigator/agents/reporting_agent.py`.

## Rationalizations

| Excuse | Rebuttal |
| --- | --- |
| "Let the model decide the wording of the verdict." | The verdict comes from scoring and policy; the model only narrates. |
| "Omit evidence to keep the report short." | Evidence is what makes the report auditable; include it. |

## Red Flags

- The narrative states a different outcome than the decision.
- A model failure blocks report generation instead of falling back.

## Verification

- The report contains the score, the decision, the confidence, every triggered
  signal, and a narrative consistent with the decision.
