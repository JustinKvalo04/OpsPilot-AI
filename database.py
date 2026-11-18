
import sqlite3
import json
import hashlib
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

DB_NAME = os.getenv(
    "OPSPILOT_DB_PATH",
    str(BASE_DIR / "opspilot.db")
)



# ==========================================
# DATABASE CONNECTION
# ==========================================

def get_connection():
    return sqlite3.connect(DB_NAME)


# ==========================================
# INITIALIZE DATABASE
# ==========================================

def initialize_database():
    connection = get_connection()
    cursor = connection.cursor()

    # Create tickets table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            id TEXT PRIMARY KEY,
            subject TEXT NOT NULL,
            message TEXT NOT NULL,
            status TEXT NOT NULL,
            assigned_department TEXT,
            priority TEXT
        )
    """)

    # Create audit logs table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticket_id TEXT NOT NULL,
            action TEXT NOT NULL,
            details TEXT,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Create AI response cache table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ai_cache (
            cache_key TEXT PRIMARY KEY,
            response TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Create live AI usage tracking table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ai_usage (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """)

    connection.commit()
    connection.close()


# ==========================================
# TICKET MANAGEMENT
# ==========================================

def save_ticket(ticket):
    connection = get_connection()

    connection.execute("""
        INSERT OR REPLACE INTO tickets
        (id, subject, message, status, assigned_department, priority)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        ticket.id,
        ticket.subject,
        ticket.message,
        ticket.status,
        ticket.assigned_department,
        ticket.priority
    ))

    connection.commit()
    connection.close()


def load_tickets():
    connection = get_connection()
    connection.row_factory = sqlite3.Row

    rows = connection.execute(
        "SELECT * FROM tickets"
    ).fetchall()

    connection.close()

    return [dict(row) for row in rows]


# ==========================================
# AUDIT LOGGING
# ==========================================

def log_action(ticket_id: str, action: str, details: str = ""):
    connection = get_connection()

    connection.execute("""
        INSERT INTO audit_logs (ticket_id, action, details)
        VALUES (?, ?, ?)
    """, (ticket_id, action, details))

    connection.commit()
    connection.close()


def get_ticket_history(ticket_id: str):
    connection = get_connection()
    connection.row_factory = sqlite3.Row

    rows = connection.execute("""
        SELECT id, ticket_id, action, details, created_at
        FROM audit_logs
        WHERE ticket_id = ?
        ORDER BY id ASC
    """, (ticket_id,)).fetchall()

    connection.close()

    return [dict(row) for row in rows]


# ==========================================
# AI RESPONSE CACHING
# ==========================================

def generate_cache_key(subject: str, message: str, mode: str):
    # Separate mock and live AI results
    content = f"{mode}:{subject}:{message}"

    return hashlib.sha256(
        content.encode("utf-8")
    ).hexdigest()


def get_cached_analysis(cache_key: str):
    connection = get_connection()

    row = connection.execute("""
        SELECT response
        FROM ai_cache
        WHERE cache_key = ?
    """, (cache_key,)).fetchone()

    connection.close()

    if row is None:
        return None

    return json.loads(row[0])


def save_cached_analysis(cache_key: str, analysis: dict):
    connection = get_connection()

    connection.execute("""
        INSERT OR REPLACE INTO ai_cache (cache_key, response)
        VALUES (?, ?)
    """, (
        cache_key,
        json.dumps(analysis)
    ))

    connection.commit()
    connection.close()


# ==========================================
# LIVE AI USAGE TRACKING
# ==========================================

def get_live_ai_call_count():
    connection = get_connection()

    result = connection.execute(
        "SELECT COUNT(*) FROM ai_usage"
    ).fetchone()

    connection.close()

    return result[0]


def reserve_live_ai_call(max_calls: int):
    """
    Reserve one live AI request before sending it.
    Returns True if allowed, False if the limit is reached.
    """

    connection = get_connection()

    try:
        # Lock the database during the limit check
        connection.execute("BEGIN IMMEDIATE")

        current_count = connection.execute(
            "SELECT COUNT(*) FROM ai_usage"
        ).fetchone()[0]

        if current_count >= max_calls:
            connection.rollback()
            return False

        # Record the request before it happens
        connection.execute(
            "INSERT INTO ai_usage DEFAULT VALUES"
        )

        connection.commit()
        return True

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()

# ==========================================
# RUN DATABASE INITIALIZATION
# ==========================================

if __name__ == "__main__":
    initialize_database()
    print("OpsPilot database initialized successfully!")
