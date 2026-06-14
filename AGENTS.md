# AGENTS.md

Operating guide for AI agents working in this repository. This file defines how
to discover, invoke, and extend the AI Payment Fraud Investigator skills.

## What This Repository Provides

A pack of Agent Skills that automate payment fraud investigations, plus a
deterministic Python engine that implements the same logic and serves as the
executable reference for every skill.

- `skills/` contains one folder per skill, each with a `SKILL.md`.
- `agents/` contains specialist personas.
- `references/` contains supporting checklists and rubrics.
- `src/fraud_investigator/` is the executable engine the skills describe.

## How to Start

1. Read `skills/using-fraud-investigator/SKILL.md`. It is the meta-skill that
   routes a request to the correct workflow and defines the shared rules.
2. Run the lifecycle in order: intake, enrichment, detection, scoring,
   decisioning, reporting.

## Operating Rules

1. Decisions must be explainable and cite their signals.
2. Scoring and decisions must be deterministic. A language model may enrich the
   narrative only; it must never change the score or the decision.
3. Use tokenized card references and pseudonymous account identifiers. Never
   request or store raw cardholder data.
4. Declines and escalations require human-review provisions.

## Running the Engine

```bash
python -m pip install -e ".[dev]"
fraud-investigator investigate data/samples/sample_transactions.json --output output
pytest -q
python scripts/validate_skills.py
```

## Adding a Skill

1. Copy `template/SKILL.md` into a new folder under `skills/`.
2. Set `name` to match the folder and write a complete `description` with trigger
   phrases.
3. Fill in Overview, When to Use, Process, and Verification at minimum.
4. If the skill is executable, add the implementation under
   `src/fraud_investigator/skills/` and register it in `registry.py`.
5. Run `python scripts/validate_skills.py` and `pytest -q`.

## Conventions

- Skill folder names are lowercase with hyphens and match the `name` field.
- Each skill emits at most one risk signal with a severity, confidence, and
  rationale.
- Configuration lives in `config/config.yaml`; do not hardcode thresholds.
