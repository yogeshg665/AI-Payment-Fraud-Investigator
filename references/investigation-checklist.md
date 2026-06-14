# Investigation Checklist

A pre-close control checklist for every fraud case. Used by the
`compliance-reviewer` persona and recommended before finalizing any decision.

## Data Handling

- [ ] The case uses a tokenized card reference, not a raw card number.
- [ ] The account identifier is pseudonymous.
- [ ] No personal or sensitive data beyond what the investigation requires is present.

## Process Integrity

- [ ] Intake validated the transaction schema.
- [ ] Enrichment ran and recorded unavailable features explicitly.
- [ ] All detection skills executed; none were skipped.
- [ ] The risk score is reproducible from the recorded inputs and configuration.

## Explainability

- [ ] Every triggered signal has a severity, a confidence, and a rationale.
- [ ] The decision cites the signals that produced it.
- [ ] The narrative is consistent with the decision outcome.

## Decision Controls

- [ ] The outcome matches the score and the configured thresholds.
- [ ] Declines and escalations include human-review provisions.
- [ ] Adverse-action notification requirements for the jurisdiction are noted.

## Fairness

- [ ] No signal or feature relies on a prohibited or proxy attribute.
- [ ] Borderline cases were escalated rather than auto-declined.

## Record Keeping

- [ ] The structured report is retained as the evidentiary record.
- [ ] The configuration version used for scoring is identifiable.
