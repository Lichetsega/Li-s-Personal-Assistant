# 🧠 Multi-Tier Cognitive Memory Engine (`src/memory/`)

The `src/memory/` directory implements an enterprise-grade cognitive memory architecture for **Li's AI Assistant**, combining structured profile validation, episodic relational memory, autonomous conversational fact extraction, local document retrieval (RAG), and dynamic context synthesis.

---

## 📁 Directory Structure

```text
src/memory/
├── __init__.py               # Re-exports core memory modules
├── schema.py                 # Pydantic data models & categories
├── profile_manager.py        # Validated UserProfile loader & template fallbacks
├── memory_store.py           # Relational SQLite database store
├── memory_extractor.py       # Autonomous background fact extractor
├── knowledge_base.py         # Local Markdown/text Document RAG engine
├── conversation_history.py   # Rolling multi-turn session history
└── context_builder.py        # Unified prompt context synthesizer
```

---

## 🧩 Architectural Tiers

### 1. Schema Validation Layer (`schema.py`)
- Defines strict Pydantic models for user identity, communication preferences, and cognitive memory records.
- **`UserProfile`**: Validates user persona, name, background, tone, speech preferences, and safety guidelines.
- **`MemoryItem`**: Encapsulates episodic memory entries with category, content, importance score, and ISO timestamps.
- **`MemoryCategory`**: Enumerates storage domains (`FACT`, `PREFERENCE`, `HABIT`, `GOAL`, `SYSTEM`).

### 2. User Profile Manager (`profile_manager.py`)
- Loads personal user profile data from `src/data/user_profile.json`.
- Safely falls back to `src/data/user_profile.example.json` if local personal data is missing or git-ignored.
- Enforces runtime schema adherence so invalid data never crashes the assistant.

### 3. Episodic SQLite Store (`memory_store.py`)
- Manages persistent SQLite database storage at `src/data/memory.db`.
- Supports indexing, category-based querying, search keyword filtering, and atomic insertions.
- Includes automated timestamping and importance sorting to prioritize high-value facts.

### 4. Autonomous Background Fact Extractor (`memory_extractor.py`)
- Non-blocking background LLM task that analyzes user dialogue in real time.
- Identifies personal details, preferences, habits, and goals mentioned in conversation.
- Automatically stores newly discovered facts into `MemoryStore` without interrupting the conversation.

### 5. Local Document RAG Engine (`knowledge_base.py`)
- Indexes local documentation files inside `src/data/notes/` (`.md`, `.txt`, `.json`).
- Automatically scans personal notes (e.g. `work.md`, `identity.md`, `schedule.md`).
- Executes keyword & semantic relevance ranking to retrieve and inject relevant contextual passages into prompt context.

### 6. Rolling Multi-Turn History (`conversation_history.py`)
- Maintains a short-term rolling FIFO context window of user-assistant interaction turns.
- Preserves natural conversational continuity without exceeding LLM context window limits.

### 7. Unified Context Builder (`context_builder.py`)
- Assembles all cognitive tiers into a single cohesive system instruction payload for the Gemini AI model:
  1. Base Persona & Behavioral Directives
  2. Validated User Profile (Name, Bio, Style)
  3. Relevant Episodic Memories from SQLite
  4. Local Document RAG Excerpts
  5. Live Environmental State (Local Date, Time, System State)
  6. Recent Multi-Turn Dialogue History

---

## 🔄 Cognitive Data Pipeline

```text
User Query
    │
    ├─► [ConversationHistory] ───► Injects recent short-term turns
    ├─► [MemoryStore (SQLite)] ──► Retrieves categorized long-term facts
    ├─► [KnowledgeBase (RAG)] ───► Scans local notes/ for relevant passages
    ├─► [ProfileManager] ────────► Supplies identity & communication rules
    │
    ▼
[ContextBuilder] ───────────────► Compiles unified prompt payload
    │
    ▼
[Gemini AI Engine]
    │
    └─► (Asynchronously) ────────► [MemoryExtractor] ──► Discovers new facts ──► SQLite
```
