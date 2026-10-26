# 💾 Data Stores, Schemas & Knowledge Documents (`src/data/`)

The `src/data/` directory manages all local state, user profiles, relational SQLite databases, and personal notes used by the assistant's cognitive memory and RAG engine.

---

## 📁 Directory Structure

```text
src/data/
├── memory.db                     # Local SQLite database (git-ignored)
├── user_profile.json             # Active user profile (git-ignored)
├── user_profile.example.json     # Public safe template for repository clones
└── notes/                        # Local RAG knowledge base directory
    ├── example_notes.md          # Public safe example notes template
    ├── identity.md               # User identity & background (git-ignored)
    ├── work.md                   # Work history, projects & INSA internship (git-ignored)
    ├── schedule.md               # Daily routines & recurring schedule (git-ignored)
    ├── preferences.md            # Coding & communication preferences (git-ignored)
    ├── health.md                 # Health & fitness context (git-ignored)
    └── goals.md                  # Personal & career aspirations (git-ignored)
```

---

## 🔒 Privacy & Git Safeguards

This directory enforces strict data isolation:
- **Zero Accidental Leaks**: `user_profile.json`, `memory.db`, and all files in `notes/*.md` (except `example_notes.md`) are explicitly excluded in `.gitignore`.
- **Public Template Files**: Safe public templates (`user_profile.example.json` and `notes/example_notes.md`) are committed to Git so anyone who clones the repo can run the assistant immediately without manual configuration.

---

## 🧩 Data Store Components

### 1. `memory.db` (SQLite Relational Store)
- Auto-created upon first run by `MemoryStore`.
- Stores extracted facts, habits, goals, and user preferences with categories, importance scores, and timestamps.
- Indexed for fast retrieval during dynamic context assembly.

### 2. `user_profile.json` (Structured User Identity)
- Adheres to the Pydantic schema in `src/memory/schema.py`.
- Encapsulates:
  - User details (full name, preferred title, location, timezone).
  - Background (education, major, work history).
  - Tone & Communication Rules (conciseness, technical depth, formality).
  - Explicit Behavioral Constraints (confidentiality policies, personal boundaries).

### 3. `notes/` (Document RAG Store)
- Scanned recursively by `KnowledgeBase` at startup and during query processing.
- Supports Markdown (`.md`), plain text (`.txt`), and JSON files.
- Each document is parsed and indexed into semantically relevant chunks for retrieval-augmented generation.
