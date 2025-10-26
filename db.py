"""
db.py
-----
Handles all database operations for key storage and retrieval.
Uses SQLite with Write-Ahead Logging (WAL) for concurrent access.
"""

import sqlite3
from typing import Optional, Tuple, List

# Database file name (must match assignment spec)
DB_FILE = "totally_not_my_privateKeys.db"

# Schema: single table for RSA keys
SCHEMA = """
CREATE TABLE IF NOT EXISTS keys(
    kid INTEGER PRIMARY KEY AUTOINCREMENT,
    key BLOB NOT NULL,
    exp INTEGER NOT NULL
);
"""

def get_conn() -> sqlite3.Connection:
    """Opens a database connection and ensures schema exists."""
    conn = sqlite3.connect(DB_FILE)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute(SCHEMA)
    return conn

def insert_key(pem: bytes, exp_ts: int) -> int:
    """Inserts a new private key (PEM + expiration timestamp)."""
    with get_conn() as conn:
        cur = conn.execute("INSERT INTO keys(key, exp) VALUES(?, ?)", (pem, exp_ts))
        return cur.lastrowid

def fetch_one_key(expired: bool) -> Optional[Tuple[int, bytes, int]]:
    """
    Fetches one key (expired or valid).
    - expired=True → returns the most recent expired key
    - expired=False → returns the soonest-expiring valid key
    """
    sql = (
        "SELECT kid, key, exp FROM keys WHERE exp < strftime('%s','now') "
        "ORDER BY exp DESC LIMIT 1"
        if expired else
        "SELECT kid, key, exp FROM keys WHERE exp >= strftime('%s','now') "
        "ORDER BY exp ASC LIMIT 1"
    )
    with get_conn() as conn:
        row = conn.execute(sql).fetchone()
        return row if row else None

def fetch_valid_keys() -> List[Tuple[int, bytes, int]]:
    """Returns all valid (non-expired) keys for the JWKS endpoint."""
    with get_conn() as conn:
        return conn.execute(
            "SELECT kid, key, exp FROM keys WHERE exp >= strftime('%s','now') ORDER BY kid ASC"
        ).fetchall()