# Contributing

Thank you for contributing to the AI Payment Fraud Investigator. This guide
covers how to add or change skills and the engine.

## Principles

Skills should be:

- **Specific.** Actionable steps, not vague advice.
- **Verifiable.** Clear exit criteria with evidence requirements.
- **Minimal.** Only what is needed to guide the agent.
- **Explainable.** Every risk contribution carries a rationale.

## Adding or Changing a Skill

1. Copy `template/SKILL.md` into a new folder under `skills/`. The folder name
   must be lowercase with hyphens and must match the `name` in the frontmatter.
2. Write a complete `description` that states the capability and lists trigger
   phrases after `WHEN:`.
3. Fill in the body. The Overview, Process, and Verification sections are
   required and enforced by the validator.
4. If the skill is executable, implement it under
   `src/fraud_investigator/skills/`, register it in `registry.py`, and add a
   weight in `config/config.yaml`.

## Quality Gates

Run all of the following before opening a pull request:

```bash
python scripts/validate_skills.py
ruff check src/fraud_investigator tests
mypy src/fraud_investigator
pytest -q
```

## Testing

- Add unit tests for new skills under `tests/test_skills.py`.
- Add or update integration coverage in `tests/test_pipeline.py` when behavior
  changes.
- Do not weaken the critical-floor or determinism guarantees without tests that
  justify the new behavior.

## Commit and Review

- Keep changes small and focused, roughly one skill or one concern per change.
- Describe the trade-off for any threshold or weight change: its expected effect
  on fraud capture and false positives.

## Security and Data Handling

- Never add code paths that accept or store raw cardholder data.
- Do not include real personal data in samples or tests; use synthetic values.
- Follow the OWASP Top 10 when handling input and external integrations.
