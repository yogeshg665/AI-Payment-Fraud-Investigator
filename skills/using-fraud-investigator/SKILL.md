---
name: using-fraud-investigator
description: Meta-skill that maps an incoming fraud investigation request to the correct skill workflow and defines the shared operating rules every fraud skill follows. WHEN: "investigate a transaction", "is this payment fraud", "review this charge", "start a fraud case", "which fraud check applies", "run a fraud investigation".
---

# Using the Fraud Investigator

## Overview

This is the entry point for the AI Payment Fraud Investigator skill pack. It
routes a request to the right skill and establishes the rules that keep every
investigation explainable, reproducible, and auditable.

## When to Use

- At the start of any fraud investigation, before invoking a specific skill.
- When it is unclear which skill applies to the request.

## The Investigation Lifecycle

Every investigation follows the same ordered pipeline. Each phase maps to one or
more skills.

| Phase | Skill | Purpose |
| --- | --- | --- |
| Intake | `transaction-intake` | Validate and normalize the transaction into a case. |
| Enrich | `data-enrichment` | Add device, history, and reference context. |
| Detect | `transaction-analysis` | Flag high value and unusual timing. |
| Detect | `velocity-analysis` | Flag rapid bursts of activity or spend. |
| Detect | `geolocation-risk` | Flag high-risk geography and impossible travel. |
| Detect | `device-fingerprinting` | Flag unknown or shared devices. |
| Detect | `watchlist-screening` | Flag deny-list and watchlist matches. |
| Detect | `anomaly-detection` | Flag statistical outliers versus account history. |
| Score | `risk-scoring` | Aggregate signals into a single risk score. |
| Decide | `fraud-decisioning` | Apply the policy to approve, escalate, or decline. |
| Report | `investigation-reporting` | Produce the audit-ready case report. |

## Shared Operating Rules

1. **Explainability is mandatory.** Every risk contribution must carry a
   severity, a confidence, and a written rationale. A decision must cite the
   signals that produced it.
2. **Determinism first.** Produce the same score and decision for the same input
   and configuration. A language model may enrich the narrative but must never
   change the score or the decision.
3. **Never fabricate evidence.** Only use data present in the case or supplied by
   enrichment. If a data point is missing, record it as unavailable.
4. **Respect data minimization.** Operate on tokenized card references and
   pseudonymous account identifiers. Never request or store raw cardholder data.
5. **Human oversight on adverse actions.** Declines and escalations are subject
   to human review and jurisdiction-specific compliance controls.

## Process

1. Confirm the request is a fraud investigation. If not, stop and redirect.
2. Run the lifecycle skills in order. Do not skip the detection phase.
3. Hand the scored case to `fraud-decisioning`, then `investigation-reporting`.
4. Return the decision and the report together.

## Red Flags

- A decision is produced without any cited signals.
- A skill is skipped because the transaction "looks fine."
- Raw card numbers or personal data appear in the case payload.

## Verification

- The final output contains a risk score, a decision, and a narrative that
  references every triggered signal.
