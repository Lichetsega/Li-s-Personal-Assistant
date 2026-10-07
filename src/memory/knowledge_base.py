import os
import json
from pathlib import Path
from typing import List
from src.config import NOTES_DIR
from src.memory.schema import KnowledgeExcerpt

class KnowledgeBase:
    def __init__(self, notes_dir: Path = NOTES_DIR):
        self.notes_dir = notes_dir
        self.notes_dir.mkdir(parents=True, exist_ok=True)

    def search_notes(self, query: str, top_k: int = 3) -> List[KnowledgeExcerpt]:
        results: List[KnowledgeExcerpt] = []
        if not self.notes_dir.exists():
            return results

        query_terms = [t.lower() for t in query.split() if len(t) > 2]
        
        for file_path in self.notes_dir.glob("*"):
            if file_path.suffix.lower() in [".md", ".txt", ".json", ".markdown"]:
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        text = f.read()

                    # Simple keyword frequency relevance score
                    text_lower = text.lower()
                    score = 0.0
                    for term in query_terms:
                        score += text_lower.count(term) * 1.5

                    # If query is short or score > 0, include excerpt
                    if score > 0 or not query_terms:
                        # Extract most relevant paragraph or top chunk
                        lines = [line.strip() for line in text.splitlines() if line.strip()]
                        excerpt_text = "\n".join(lines[:15])  # Top excerpt preview
                        
                        results.append(
                            KnowledgeExcerpt(
                                file_name=file_path.name,
                                file_path=str(file_path),
                                content=excerpt_text,
                                relevance_score=score if query_terms else 1.0
                            )
                        )
                except Exception as e:
                    print(f"[KnowledgeBase] Warning: Failed to read note {file_path}: {e}")

        # Sort by relevance score descending
        results.sort(key=lambda x: x.relevance_score, reverse=True)
        return results[:top_k]

    def list_notes(self) -> List[str]:
        if not self.notes_dir.exists():
            return []
        return [f.name for f in self.notes_dir.glob("*") if f.is_file()]

    def read_note(self, filename: str) -> str:
        target_path = self.notes_dir / filename
        if target_path.exists() and target_path.is_file():
            with open(target_path, "r", encoding="utf-8") as f:
                return f.read()
        return f"Note '{filename}' not found."
