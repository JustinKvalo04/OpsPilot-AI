

import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

DB_PATH = Path(
    os.getenv(
        "OPSPILOT_DB_PATH",
        str(BASE_DIR / "opspilot.db")
    )
)


VALID_STATUSES = {
    "draft",
    "pending_review",
    "approved",
    "rejected",
    "sent",
}


def get_connection():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def now():
    return datetime.now(timezone.utc).isoformat()


def initialize_response_database():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS customer_responses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticket_id TEXT NOT NULL UNIQUE,
                subject TEXT NOT NULL,
                body TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'draft',
                reviewer TEXT,
                review_reason TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                sent_at TEXT
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS response_audit (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticket_id TEXT NOT NULL,
                action TEXT NOT NULL,
                actor TEXT NOT NULL,
                details TEXT,
                created_at TEXT NOT NULL
            )
        """)


def log_response_action(conn, ticket_id, action, actor, details=""):
    conn.execute(
        """
        INSERT INTO response_audit
        (ticket_id, action, actor, details, created_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (ticket_id, action, actor, details, now()),
    )


def get_response(ticket_id):
    with get_connection() as conn:
        row = conn.execute(
            """
            SELECT * FROM customer_responses
            WHERE ticket_id = ?
            """,
            (ticket_id,),
        ).fetchone()

    return dict(row) if row else None


def save_response(ticket_id, subject, body, actor="operator"):
    timestamp = now()

    with get_connection() as conn:
        existing = conn.execute(
            """
            SELECT id, status FROM customer_responses
            WHERE ticket_id = ?
            """,
            (ticket_id,),
        ).fetchone()


        if existing and existing["status"] in (
            "pending_review",
            "approved",
            "sent",
        ):
            raise ValueError(
                f"Cannot edit a response with status "
                f"'{existing['status']}'."
            )


        if existing:
            conn.execute(
                """
                UPDATE customer_responses
                SET subject = ?, body = ?, status = 'draft',
                    reviewer = NULL, review_reason = NULL,
                    updated_at = ?
                WHERE ticket_id = ?
                """,
                (subject, body, timestamp, ticket_id),
            )
        else:
            conn.execute(
                """
                INSERT INTO customer_responses
                (ticket_id, subject, body, status,
                 created_at, updated_at)
                VALUES (?, ?, ?, 'draft', ?, ?)
                """,
                (ticket_id, subject, body, timestamp, timestamp),
            )

        log_response_action(
            conn, ticket_id, "draft_saved", actor,
            "Draft saved; previous review status cleared.",
        )

    return get_response(ticket_id)


def transition_response(
    ticket_id,
    action,
    actor,
    reason="",
):
    transitions = {
        "submit": ("draft", "pending_review"),
        "approve": ("pending_review", "approved"),
        "reject": ("pending_review", "rejected"),
        "reopen": ("rejected", "draft"),
        "simulate_send": ("approved", "sent"),
    }

    if action not in transitions:
        raise ValueError("Unknown response action.")

    expected, next_status = transitions[action]

    with get_connection() as conn:
        row = conn.execute(
            """
            SELECT * FROM customer_responses
            WHERE ticket_id = ?
            """,
            (ticket_id,),
        ).fetchone()

        if row is None:
            raise ValueError("Save a response first.")

        if row["status"] != expected:
            raise ValueError(
                f"Action '{action}' requires status '{expected}'. "
                f"Current status: '{row['status']}'."
            )

        if action == "reject" and not reason.strip():
            raise ValueError("A rejection reason is required.")

        reviewer = actor if action in ("approve", "reject") else row["reviewer"]
        review_reason = reason if action in ("approve", "reject") else row["review_reason"]
        sent_at = now() if action == "simulate_send" else row["sent_at"]

        conn.execute(
            """
            UPDATE customer_responses
            SET status = ?, reviewer = ?, review_reason = ?,
                updated_at = ?, sent_at = ?
            WHERE ticket_id = ? AND status = ?
            """,
            (
                next_status,
                reviewer,
                review_reason,
                now(),
                sent_at,
                ticket_id,
                expected,
            ),
        )

        log_response_action(
            conn,
            ticket_id,
            action,
            actor,
            reason or f"Status changed to {next_status}",
        )

    return get_response(ticket_id)


def get_response_history(ticket_id):
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT * FROM response_audit
            WHERE ticket_id = ?
            ORDER BY id DESC
            """,
            (ticket_id,),
        ).fetchall()

    return [dict(row) for row in rows]
