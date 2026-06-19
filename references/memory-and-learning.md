# Memory and Learning

The engine supports an optional collective-memory and feedback loop that lets
investigations build on past outcomes without compromising determinism. All
three capabilities are off by default; enable them in `config/config.yaml` or
with the `--memory` CLI flag.

## Capabilities

### 1. Collective case memory

Every completed investigation is persisted to a local SQLite store
(`src/fraud_investigator/memory/store.py`). Records hold only pseudonymous
account identifiers and tokenized card references. No raw cardholder data is
ever written.

### 2. Retrieval (RAG-style recall)

Before scoring, the orchestrator recalls prior cases that share the account or
card and injects a `memory_recall` summary into case enrichment. The
`case-memory` skill turns adverse history into a corroborating risk signal.
Recall is exact-match and deterministic: it is a pure function of the records
already in the store.

### 3. Outcome feedback loop

Analysts label stored cases as `confirmed_fraud` or `legitimate`. The
`calibrate` command reads those labels and recommends decision thresholds that
separate fraud from legitimate activity. Calibration is advisory only; it never
mutates configuration, so runtime scoring and decisioning stay deterministic and
under human control.

## Determinism guarantees

- Scoring and decisions remain a deterministic function of the case and the
  current store contents.
- Memory contributes a weighted, non-critical signal; it never floors or
  overrides the aggregate score.
- Threshold changes are never applied automatically.

## Usage

```bash
# Investigate with collective memory enabled (persist and recall history)
python -m fraud_investigator.cli investigate data/samples/sample_transactions.json --memory .fraud_memory/memory.db

# Record an analyst-confirmed outcome for a stored case
python -m fraud_investigator.cli feedback <case_id> confirmed_fraud --memory .fraud_memory/memory.db

# Recommend thresholds from labeled feedback (advisory)
python -m fraud_investigator.cli calibrate --memory .fraud_memory/memory.db
```

To enable memory permanently, set `memory.enabled: true` in
`config/config.yaml`. The environment variables `MEMORY_ENABLED` and
`MEMORY_PATH` override the configured values.
