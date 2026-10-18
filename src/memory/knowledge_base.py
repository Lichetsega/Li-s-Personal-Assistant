import os
import glob
import logging
from typing import List, Dict, Any

logger = logging.getLogger("KnowledgeBase")

DEFAULT_NOTES_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "data", "notes")
)

class KnowledgeBase:
    """
    RAG (Retrieval-Augmented Generation) Engine for local personal documents.
    Indexes text, markdown, and JSON files in src/data/notes/ for semantic query lookup.
    """
    def __init__(self, notes_dir: str = None):
        self.notes_dir = notes_dir or DEFAULT_NOTES_DIR
        os.makedirs(self.notes_dir, exist_ok=True)
        self._ensure_example_note()

    def _ensure_example_note(self):
        """Creates an example template note if directory is empty."""
        example_path = os.path.join(self.notes_dir, "example_notes.md")
        if not os.path.exists(example_path) and not glob.glob(os.path.join(self.notes_dir, "*.*")):
            try:
                with open(example_path, "w", encoding="utf-8") as f:
                    f.write("# Li's Project Notes\n\n- Personal Voice AI Assistant built with Python and Gemini.\n- Key Goals: High performance, multi-tier memory, proactive reminders.\n")
                logger.info(f"Created initial example note at {example_path}")
            except Exception as e:
                logger.warning(f"Could not create example note: {e}")

    def load_documents(self) -> List[Dict[str, str]]:
        """Scans notes directory and returns loaded document chunks with metadata."""
        documents = []
        supported_extensions = ["*.txt", "*.md", "*.json", "*.log"]
        
        filepaths = []
        for ext in supported_extensions:
            filepaths.extend(glob.glob(os.path.join(self.notes_dir, ext)))
            filepaths.extend(glob.glob(os.path.join(self.notes_dir, "**", ext), recursive=True))

        filepaths = list(set(filepaths))

        for path in filepaths:
            try:
                filename = os.path.basename(path)
                with open(path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read().strip()
                
                if content:
                    # Split long documents into chunks of ~500 chars for precise retrieval
                    chunks = [content[i:i+500] for i in range(0, len(content), 400)]
                    for idx, chunk in enumerate(chunks):
                        documents.append({
                            "filename": filename,
                            "chunk_id": idx,
                            "content": chunk
                        })
            except Exception as e:
                logger.error(f"Error loading document {path}: {e}")

        return documents

    def search(self, query: str, top_k: int = 3) -> str:
        """
        Searches personal documents for passages matching keywords in the query.
        Returns formatted context string.
        """
        if not query or not query.strip():
            return ""

        documents = self.load_documents()
        if not documents:
            return ""

        query_keywords = [k.lower() for k in query.split() if len(k) > 2]
        if not query_keywords:
            return ""

        scored_docs = []
        for doc in documents:
            content_lower = doc["content"].lower()
            # Calculate keyword match frequency score
            score = sum(content_lower.count(kw) for kw in query_keywords)
            if score > 0:
                scored_docs.append((score, doc))

        # Sort by relevance score descending
        scored_docs.sort(key=lambda x: x[0], reverse=True)
        top_matches = scored_docs[:top_k]

        if not top_matches:
            return ""

        result = "--- PERSONAL DOCUMENTS & NOTES CONTEXT ---\n"
        for score, doc in top_matches:
            result += f"• [File: {doc['filename']}] {doc['content'].strip()}\n"
        
        return result
