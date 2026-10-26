# 🔌 External Integrations & Service Layer (`src/services/`)

The `src/services/` directory provides modular interfaces to external APIs, background automation engines, cloud audio processors, and productivity tools.

---

## 📁 Directory Structure

```text
src/services/
├── __init__.py               # Package initializer
├── whisper_service.py        # Groq Whisper-large-v3 Cloud STT engine
├── github_service.py         # Live GitHub API queries (repos, commits, READMEs)
├── weather.py                # Real-time weather service (OpenWeatherMap + wttr.in fallback)
├── news.py                   # Global headlines (NewsAPI + BBC RSS fallback)
├── wikipedia_service.py      # Wikipedia encyclopedia summary lookups
├── scheduler.py              # Background timer & proactive reminder scheduler
├── task_manager.py           # In-memory personal task management
├── jokes.py                  # Programming & general humor generator
└── music.py                  # Audio playback handler
```

---

## 🚀 Service Capabilities

### 1. Cloud Speech-to-Text (`whisper_service.py`)
- **Engine**: Groq-hosted `whisper-large-v3` running on ultra-fast LPUs.
- **Contextual Priming (`DOMAIN_PROMPT`)**: Pre-conditions the Whisper decoder with specialized terminology (*"Liche Tsegaye"*, *"INSA"*, *"Agentic RAG"*) to eliminate transcription errors on proper nouns.
- **Acoustic Reliability Filters**:
  - Automatically assesses Whisper's native segment statistics.
  - Drops background noise/silence if `no_speech_prob > 0.65`.
  - Discards hallucinated repetition loops if `compression_ratio > 2.4`.

### 2. Live GitHub Inspection (`github_service.py`)
- Interfaces directly with the GitHub REST API (`https://api.github.com`).
- **`list_user_repos()`**: Dynamically queries public repositories, star counts, descriptions, and primary development languages.
- **`get_latest_commits()`**: Fetches recent commits with commit hashes, authors, messages, and dates.
- **`get_repo_readme_summary()`**: Extracts and decodes base64-encoded `README.md` files from repositories for live AI context.

### 3. Fault-Tolerant Weather (`weather.py`)
- Primary lookup: **OpenWeatherMap API** with rich temperature and weather condition output.
- Automatic Fallback: Queries **`wttr.in`** plain-text format if the primary API key is missing, expired, or rate-limited.

### 4. Resilient News Feeds (`news.py`)
- Primary lookup: **NewsAPI** top headlines across categories.
- Automatic Fallback: Parses official **BBC News RSS Feeds** via `xml.etree.ElementTree` to guarantee news delivery without third-party API dependencies.

### 5. Wikipedia Knowledge (`wikipedia_service.py`)
- Interfaces with the Wikipedia API to retrieve concise 2–3 sentence summaries for historical figures, technological concepts, and geographical locations.

### 6. Proactive Background Scheduler (`scheduler.py`)
- Spawns background `threading.Timer` instances to manage user timers and scheduled tasks.
- Integrates with registered callbacks to broadcast proactive voice announcements and real-time WebSocket alerts to connected browser sessions.

### 7. Task Manager (`task_manager.py`)
- Provides fast, zero-dependency task manipulation: adding items, listing pending tasks, and clearing active task lists.
