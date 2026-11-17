import sqlite3
import json
import time
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "aloha.db")

class AlohaDatabase:
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        self._init_db()

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        """Creates the essential cryptographic tables if they don't exist."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Agents Table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS agents (
                agent_id TEXT PRIMARY KEY,
                class_code TEXT NOT NULL,
                capability_code TEXT NOT NULL,
                public_key TEXT,
                reputation_score INTEGER DEFAULT 0,
                created_at REAL NOT NULL
            );
            """)

            # Signed Messages Table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id TEXT PRIMARY KEY,
                sender_id TEXT NOT NULL,
                recipient_id TEXT NOT NULL,
                subject TEXT NOT NULL,
                body TEXT NOT NULL,
                signature TEXT,
                timestamp REAL NOT NULL,
                priority TEXT DEFAULT 'NORMAL',
                tone TEXT DEFAULT 'FORMAL',
                verified INTEGER DEFAULT 0
            );
            """)

            # Anti-Replay Nonce Ledger
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS nonces (
                nonce TEXT PRIMARY KEY,
                agent_id TEXT NOT NULL,
                timestamp REAL NOT NULL
            );
            """)

            # Search Cache Table (Preserves tokens and offline data)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS search_cache (
                query TEXT PRIMARY KEY,
                markdown_extract TEXT NOT NULL,
                tokens_saved INTEGER,
                cached_at REAL NOT NULL
            );
            """)
            conn.commit()

    def register_agent(self, agent_id: str, cls: str, cap: str, pub_key: str = "") -> bool:
        """Saves a newly minted agent passport permanently."""
        try:
            with self._get_connection() as conn:
                conn.execute(
                    "INSERT OR REPLACE INTO agents (agent_id, class_code, capability_code, public_key, created_at) VALUES (?, ?, ?, ?, ?)",
                    (agent_id, cls, cap, pub_key, time.time())
                )
                conn.commit()
            return True
        except Exception:
            return False

    def record_nonce(self, nonce: str, agent_id: str) -> bool:
        """Class 404 Firewall: Checks and records nonces to prevent replay attacks."""
        try:
            with self._get_connection() as conn:
                conn.execute(
                    "INSERT INTO nonces (nonce, agent_id, timestamp) VALUES (?, ?, ?)",
                    (nonce, agent_id, time.time())
                )
                conn.commit()
            return True
        except sqlite3.IntegrityError:
            # Replay attack detected!
            return False

    def save_message(self, msg: dict) -> bool:
        """Stores a cryptographically signed mail."""
        try:
            with self._get_connection() as conn:
                conn.execute(
                    """INSERT OR REPLACE INTO messages 
                    (id, sender_id, recipient_id, subject, body, signature, timestamp, priority, tone, verified)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        msg.get("id"),
                        msg.get("from"),
                        msg.get("to"),
                        msg.get("subject"),
                        msg.get("body"),
                        msg.get("signature", ""),
                        msg.get("date", time.time()),
                        msg.get("priority", "NORMAL"),
                        msg.get("tone", "FORMAL"),
                        1 if msg.get("status") == "Verified" else 0
                    )
                )
                conn.commit()
            return True
        except Exception:
            return False

    def get_inbox(self, agent_id: str):
        """Retrieves messages for an agent."""
        with self._get_connection() as conn:
            cursor = conn.execute("SELECT * FROM messages WHERE recipient_id = ? ORDER BY timestamp DESC", (agent_id,))
            return [dict(row) for row in cursor.fetchall()]
