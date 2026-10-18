import os
import re
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

    def answer_query_locally(self, query: str, profile_manager=None) -> str:
        """
        Local RAG Fallback Engine:
        Directly answers visitor inquiries using local markdown notes and profile data
        when Gemini AI API quota is exhausted (429) or offline.
        """
        if not query or not query.strip():
            return "How can I help you learn more about Li?"

        clean_q = query.strip().lower()
        profile = profile_manager.get_profile() if profile_manager else None
        identity = profile.identity if profile else None

        # 1. Contact / Social Links Fast Path
        contact_triggers = ["contact", "email", "telegram", "github", "reach", "hire", "phone", "message", "social"]
        if any(w in clean_q for w in contact_triggers):
            email = getattr(identity, "email", "lichetsega@gmail.com") or "lichetsega@gmail.com"
            telegram = getattr(identity, "telegram", "https://t.me/Lichetsega") or "https://t.me/Lichetsega"
            github = getattr(identity, "github", "https://github.com/Lichetsega") or "https://github.com/Lichetsega"
            return (
                f"You can reach Li directly via her primary contact channels:\n"
                f"• Email: {email}\n"
                f"• Telegram: {telegram}\n"
                f"• GitHub: {github}\n\n"
                f"Feel free to get in touch for collaborations, inquiries, or discussions!"
            )

        # 2. Location / Origin Fast Path
        if any(w in clean_q for w in ["where is", "location", "based", "living", "live", "hometown", "country"]):
            loc = getattr(identity, "location", "Jimma / Woliso, Ethiopia") or "Jimma / Woliso, Ethiopia"
            return f"Li is currently based in {loc}."

        # 3. Document Notes Search (Extract relevant snippets)
        documents = self.load_documents()
        stop_words = {
            "what", "when", "where", "which", "who", "whom", "this", "that", "these", "those",
            "have", "has", "had", "would", "should", "could", "the", "and", "but", "with",
            "about", "into", "through", "during", "before", "after", "tell", "show", "give",
            "does", "she", "her", "fiche", "liche", "projects"
        }

        query_words = [re.sub(r"[^\w]", "", w.lower()) for w in query.split()]
        significant_keywords = [w for w in query_words if len(w) > 2 and w not in stop_words]

        matched_snippets = []
        if significant_keywords:
            for doc in documents:
                content = doc.get("content", "")
                lines = [line.strip() for line in re.split(r"[\n•\-\*]+", content) if len(line.strip()) > 15]
                for line in lines:
                    line_lower = line.lower()
                    score = sum(1 for kw in significant_keywords if kw in line_lower)
                    if score > 0:
                        matched_snippets.append((score, line))

        if matched_snippets:
            matched_snippets.sort(key=lambda x: x[0], reverse=True)
            seen = set()
            top_lines = []
            for score, line in matched_snippets:
                cleaned_line = line.strip(" -*•#")
                if cleaned_line not in seen:
                    seen.add(cleaned_line)
                    top_lines.append(f"• {cleaned_line}")
                if len(top_lines) >= 3:
                    break

            if top_lines:
                return "Here is what I found in Li's portfolio records:\n" + "\n".join(top_lines)

        # 4. Fallback if no relevant notes found
        return (
            "I don't have specific details on that in Li's portfolio records yet. "
            "You can reach out to Li directly via Telegram (https://t.me/Lichetsega) or Email (lichetsega@gmail.com)!"
        )
