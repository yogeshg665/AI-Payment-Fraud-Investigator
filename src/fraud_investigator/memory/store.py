"""SQLite-backed collective memory for investigations and analyst feedback.

The store provides three capabilities:

* persistence of completed investigations (collective memory),
* deterministic recall of prior cases for an account or card (retrieval), and
* an outcome feedback loop used for offline threshold calibration.

It depends only on the Python standard library so the engine stays portable and
fully deterministic.
"""

from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from fraud_investigator.memory.models import (
    CaseMemoryRecord,
    FeedbackLabel,
    RecallSummary,
)
from fraud_investigator.models.case import InvestigationCase
from fraud_investigator.models.decision import Decision, DecisionOutcome
from fraud_investigator.models.transaction import Transaction
from fraud_investigator.utils.logging import get_logger

logger = get_logger(__name__)

_SCHEMA = """
CREATE TABLE IF NOT EXISTS case_memory (
    case_id        TEXT PRIMARY KEY,
    account_id     TEXT NOT NULL,
    card_token     TEXT NOT NULL,
    merchant_id    TEXT NOT NULL,
    amount         REAL NOT NULL,
    currency       TEXT NOT NULL,
    occurred_at    TEXT NOT NULL,
    risk_score     REAL NOT NULL,
    outcome        TEXT NOT NULL,
    signal_names   TEXT NOT NULL,
    narrative      TEXT NOT NULL,
    label          TEXT NOT NULL,
    label_note     TEXT,
    recorded_at    TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_case_memory_account ON case_memory(account_id);
CREATE INDEX IF NOT EXISTS idx_case_memory_card ON case_memory(card_token);
"""


class MemoryStore:
    """Persistent, deterministic store of investigation history."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        if self.path.parent and str(self.path.parent) not in ("", "."):
            self.path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(str(self.path))
        self._conn.row_factory = sqlite3.Row
        self._conn.executescript(_SCHEMA)
        self._conn.commit()

    # -- persistence -------------------------------------------------------

    def record_investigation(self, case: InvestigationCase, decision: Decision) -> CaseMemoryRecord:
        """Persist a completed investigation as a memory record."""
        record = CaseMemoryRecord(
            case_id=case.case_id,
            account_id=case.transaction.account_id,
            card_token=case.transaction.card_token,
            merchant_id=case.transaction.merchant_id,
            amount=case.transaction.amount,
            currency=case.transaction.currency,
            occurred_at=case.transaction.timestamp,
            risk_score=case.risk_score,
            outcome=decision.outcome.value,
            signal_names=[signal.name for signal in case.triggered_signals()],
            narrative=decision.narrative,
        )
        self._upsert(record)
        return record

    def _upsert(self, record: CaseMemoryRecord) -> None:
        self._conn.execute(
            """
            INSERT INTO case_memory (
                case_id, account_id, card_token, merchant_id, amount, currency,
                occurred_at, risk_score, outcome, signal_names, narrative,
                label, label_note, recorded_at
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            ON CONFLICT(case_id) DO UPDATE SET
                account_id=excluded.account_id,
                card_token=excluded.card_token,
                merchant_id=excluded.merchant_id,
                amount=excluded.amount,
                currency=excluded.currency,
                occurred_at=excluded.occurred_at,
                risk_score=excluded.risk_score,
                outcome=excluded.outcome,
                signal_names=excluded.signal_names,
                narrative=excluded.narrative,
                recorded_at=excluded.recorded_at
            """,
            (
                record.case_id,
                record.account_id,
                record.card_token,
                record.merchant_id,
                record.amount,
                record.currency,
                record.occurred_at.isoformat(),
                record.risk_score,
                record.outcome,
                "|".join(record.signal_names),
                record.narrative,
                record.label.value,
                record.label_note,
                record.recorded_at.isoformat(),
            ),
        )
        self._conn.commit()

    # -- retrieval ---------------------------------------------------------

    def recall_similar(self, transaction: Transaction) -> RecallSummary:
        """Summarize prior cases that share the account or card of a transaction.

        Recall is exact-match on the pseudonymous account identifier and the
        tokenized card reference, excluding the transaction's own case. The
        result is deterministic given the current store contents.
        """
        rows = self._conn.execute(
            """
            SELECT * FROM case_memory
            WHERE (account_id = ? OR card_token = ?)
              AND case_id != ?
            ORDER BY occurred_at DESC, case_id ASC
            """,
            (transaction.account_id, transaction.card_token, _case_marker(transaction)),
        ).fetchall()

        summary = RecallSummary()
        if not rows:
            return summary

        matched: set[str] = set()
        for row in rows:
            if row["account_id"] == transaction.account_id:
                matched.add("account_id")
            if row["card_token"] == transaction.card_token:
                matched.add("card_token")
            summary.total_prior_cases += 1
            label = row["label"]
            outcome = row["outcome"]
            if label == FeedbackLabel.CONFIRMED_FRAUD.value:
                summary.confirmed_fraud_count += 1
            elif label == FeedbackLabel.LEGITIMATE.value:
                summary.legitimate_count += 1
            if outcome == DecisionOutcome.DECLINE.value:
                summary.prior_decline_count += 1
            elif outcome == DecisionOutcome.ESCALATE.value:
                summary.prior_escalation_count += 1

        summary.matched_on = sorted(matched)
        most_recent = rows[0]
        summary.most_recent_outcome = most_recent["outcome"]
        summary.most_recent_at = _parse_dt(most_recent["occurred_at"])
        return summary

    def all_records(self) -> list[CaseMemoryRecord]:
        """Return every stored record, ordered by recording time."""
        rows = self._conn.execute(
            "SELECT * FROM case_memory ORDER BY recorded_at ASC, case_id ASC"
        ).fetchall()
        return [_row_to_record(row) for row in rows]

    # -- feedback loop -----------------------------------------------------

    def record_feedback(
        self,
        case_id: str,
        label: FeedbackLabel,
        note: str | None = None,
    ) -> bool:
        """Attach an analyst-confirmed label to a recorded case.

        Returns ``True`` when a matching case was updated, ``False`` otherwise.
        """
        cursor = self._conn.execute(
            "UPDATE case_memory SET label = ?, label_note = ? WHERE case_id = ?",
            (label.value, note, case_id),
        )
        self._conn.commit()
        updated = cursor.rowcount > 0
        if not updated:
            logger.warning("No memory record found for case_id=%s", case_id)
        return updated

    def stats(self) -> dict[str, int]:
        """Return simple counts describing the store contents."""
        total = self._conn.execute("SELECT COUNT(*) AS n FROM case_memory").fetchone()["n"]
        fraud = self._conn.execute(
            "SELECT COUNT(*) AS n FROM case_memory WHERE label = ?",
            (FeedbackLabel.CONFIRMED_FRAUD.value,),
        ).fetchone()["n"]
        legit = self._conn.execute(
            "SELECT COUNT(*) AS n FROM case_memory WHERE label = ?",
            (FeedbackLabel.LEGITIMATE.value,),
        ).fetchone()["n"]
        return {
            "total_cases": int(total),
            "confirmed_fraud": int(fraud),
            "legitimate": int(legit),
        }

    def close(self) -> None:
        """Close the underlying database connection."""
        self._conn.close()

    def __enter__(self) -> "MemoryStore":
        return self

    def __exit__(self, *_exc: object) -> None:
        self.close()


def _case_marker(transaction: Transaction) -> str:
    """Stable placeholder so a transaction never recalls its own future case."""
    return f"__pending__{transaction.transaction_id}"


def _parse_dt(value: str) -> datetime:
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed


def _row_to_record(row: sqlite3.Row) -> CaseMemoryRecord:
    signal_names = [name for name in (row["signal_names"] or "").split("|") if name]
    return CaseMemoryRecord(
        case_id=row["case_id"],
        account_id=row["account_id"],
        card_token=row["card_token"],
        merchant_id=row["merchant_id"],
        amount=row["amount"],
        currency=row["currency"],
        occurred_at=_parse_dt(row["occurred_at"]),
        risk_score=row["risk_score"],
        outcome=row["outcome"],
        signal_names=signal_names,
        narrative=row["narrative"] or "",
        label=FeedbackLabel(row["label"]),
        label_note=row["label_note"],
        recorded_at=_parse_dt(row["recorded_at"]),
    )
