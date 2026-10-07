import sqlite3
from pathlib import Path
from typing import List, Optional
from src.config import MEMORY_DB_PATH
from src.memory.schema import MemoryItem, MemoryCategory

class MemoryStore:
    def __init__(self, db_path: Path = MEMORY_DB_PATH):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS memories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
            """)
            conn.commit()

    def add_memory(self, content: str, category: MemoryCategory = MemoryCategory.FACT) -> int:
        category_str = category.value if isinstance(category, MemoryCategory) else str(category)
        item = MemoryItem(category=category, content=content)
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO memories (category, content, created_at) VALUES (?, ?, ?)",
                (category_str, item.content, item.created_at)
            )
            conn.commit()
            return cursor.lastrowid

    def get_all_memories(self, category: Optional[MemoryCategory] = None) -> List[MemoryItem]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            if category:
                category_str = category.value if isinstance(category, MemoryCategory) else str(category)
                cursor.execute("SELECT id, category, content, created_at FROM memories WHERE category = ? ORDER BY id DESC", (category_str,))
            else:
                cursor.execute("SELECT id, category, content, created_at FROM memories ORDER BY id DESC")
            
            rows = cursor.fetchall()
            return [
                MemoryItem(
                    id=row[0],
                    category=MemoryCategory(row[1]) if row[1] in MemoryCategory._value2member_map_ else MemoryCategory.GENERAL,
                    content=row[2],
                    created_at=row[3]
                )
                for row in rows
            ]

    def search_memories(self, query: str) -> List[MemoryItem]:
        query_terms = [q.strip().lower() for q in query.split() if len(q.strip()) > 2]
        if not query_terms:
            return self.get_all_memories()[:10]
            
        all_items = self.get_all_memories()
        results = []
        for item in all_items:
            content_lower = item.content.lower()
            if any(term in content_lower for term in query_terms):
                results.append(item)
        return results

    def delete_memory(self, memory_id: int) -> bool:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM memories WHERE id = ?", (memory_id,))
            conn.commit()
            return cursor.rowcount > 0
