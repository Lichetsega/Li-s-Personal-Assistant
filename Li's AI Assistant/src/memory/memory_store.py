import os
import sqlite3
import time
import logging
from typing import List, Optional

from src.memory.schema import MemoryItem, MemoryCategory

logger = logging.getLogger("MemoryStore")

DEFAULT_DB_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "data", "memory.db")
)

class MemoryStore:
    """
    SQLite-backed Relational Memory Database for storing episodic facts,
    preferences, goals, and user relationships.
    """
    def __init__(self, db_path: str = None):
        self.db_path = db_path or DEFAULT_DB_PATH
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        """Initializes the database schema if not present."""
        try:
            with self._get_connection() as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS memories (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        category TEXT NOT NULL DEFAULT 'FACT',
                        fact_text TEXT NOT NULL UNIQUE,
                        confidence_score REAL DEFAULT 1.0,
                        created_at REAL NOT NULL,
                        updated_at REAL NOT NULL
                    );
                """)
                conn.execute("CREATE INDEX IF NOT EXISTS idx_category ON memories(category);")
                conn.commit()
            logger.info(f"Initialized SQLite Memory Database at {self.db_path}")
        except Exception as e:
            logger.error(f"Failed to initialize Memory Database: {e}")

    def add_memory(
        self,
        fact_text: str,
        category: MemoryCategory = MemoryCategory.FACT,
        confidence: float = 1.0
    ) -> Optional[MemoryItem]:
        """Inserts a new fact or updates an existing memory."""
        if not fact_text or not fact_text.strip():
            return None

        clean_text = fact_text.strip()
        now = time.time()
        cat_str = category.value if isinstance(category, MemoryCategory) else str(category)

        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO memories (category, fact_text, confidence_score, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?)
                    ON CONFLICT(fact_text) DO UPDATE SET
                        confidence_score = excluded.confidence_score,
                        updated_at = excluded.updated_at;
                """, (cat_str, clean_text, confidence, now, now))
                conn.commit()
                mem_id = cursor.lastrowid

            logger.info(f"Added/Updated memory: [{cat_str}] {clean_text}")
            return MemoryItem(
                id=mem_id,
                category=MemoryCategory(cat_str),
                fact_text=clean_text,
                confidence_score=confidence,
                created_at=now,
                updated_at=now
            )
        except Exception as e:
            logger.error(f"Error adding memory: {e}")
            return None

    def get_all_memories(self, category: Optional[MemoryCategory] = None) -> List[MemoryItem]:
        """Retrieves memories, optionally filtered by category."""
        memories = []
        try:
            with self._get_connection() as conn:
                if category:
                    cat_str = category.value if isinstance(category, MemoryCategory) else str(category)
                    rows = conn.execute("SELECT * FROM memories WHERE category = ? ORDER BY created_at DESC;", (cat_str,))
                else:
                    rows = conn.execute("SELECT * FROM memories ORDER BY created_at DESC;")

                for r in rows.fetchall():
                    memories.append(MemoryItem(
                        id=r["id"],
                        category=MemoryCategory(r["category"]),
                        fact_text=r["fact_text"],
                        confidence_score=r["confidence_score"],
                        created_at=r["created_at"],
                        updated_at=r["updated_at"]
                    ))
        except Exception as e:
            logger.error(f"Error retrieving memories: {e}")
        return memories

    def search_memories(self, query: str, limit: int = 5) -> List[MemoryItem]:
        """Searches memories relevant to a query keyword."""
        if not query or not query.strip():
            return self.get_all_memories()[:limit]

        memories = []
        keywords = [k.strip() for k in query.lower().split() if len(k) > 2]
        if not keywords:
            return self.get_all_memories()[:limit]

        try:
            with self._get_connection() as conn:
                where_clauses = " OR ".join(["LOWER(fact_text) LIKE ?" for _ in keywords])
                params = [f"%{k}%" for k in keywords]
                sql = f"SELECT * FROM memories WHERE {where_clauses} ORDER BY confidence_score DESC, updated_at DESC LIMIT ?;"
                params.append(limit)

                rows = conn.execute(sql, params).fetchall()
                for r in rows:
                    memories.append(MemoryItem(
                        id=r["id"],
                        category=MemoryCategory(r["category"]),
                        fact_text=r["fact_text"],
                        confidence_score=r["confidence_score"],
                        created_at=r["created_at"],
                        updated_at=r["updated_at"]
                    ))
        except Exception as e:
            logger.error(f"Error searching memories: {e}")
        return memories

    def delete_memory(self, memory_id: int) -> bool:
        """Deletes a specific memory item by ID."""
        try:
            with self._get_connection() as conn:
                conn.execute("DELETE FROM memories WHERE id = ?;", (memory_id,))
                conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error deleting memory ID {memory_id}: {e}")
            return False
