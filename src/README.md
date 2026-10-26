# 🏛️ Backend Source Architecture (`src/`)

The `src/` directory contains the modular Python backend powering **Li's AI Assistant**. It is engineered with clear separation of concerns across cognitive memory, AI orchestrations, security guardrails, voice pipelines, and external integrations.

---

## 📁 Architecture Overview

```text
src/
├── config.py                 # Centralized environment loader & application settings
├── core/                     # Central assistant orchestrator & intent router
│   └── README.md
├── ai/                       # Google Gemini client & declarative tool execution
│   └── README.md
├── memory/                   # Multi-tier cognitive memory, SQLite & RAG notes engine
│   └── README.md
├── security/                 # Dual-layer input jailbreak inspection & output leak filters
│   └── README.md
├── services/                 # Groq Whisper Cloud STT, GitHub, weather, news & scheduler
│   └── README.md
├── voice/                    # Hybrid online/offline female voice TTS & local STT
│   └── README.md
└── data/                     # Schemas, user profile templates, and local RAG notes
    └── README.md
```

---

## 🧩 Submodule Breakdown

| Module | Description | Detailed Guide |
|---|---|---|
| **[`core/`](file:///c:/Users/liche/Desktop/li's%20Assistance/src/core/README.md)** | The central `AssistantCore` orchestrator: coordinates speech normalization, security guardrails, intent routing, and tool invocation. | [Read core/README.md](file:///c:/Users/liche/Desktop/li's%20Assistance/src/core/README.md) |
| **[`ai/`](file:///c:/Users/liche/Desktop/li's%20Assistance/src/ai/README.md)** | Manages Google Gemini LLM connections, prompt synthesis, and native declarative function calling schemas. | [Read ai/README.md](file:///c:/Users/liche/Desktop/li's%20Assistance/src/ai/README.md) |
| **[`memory/`](file:///c:/Users/liche/Desktop/li's%20Assistance/src/memory/README.md)** | Multi-tier cognitive memory: Pydantic schemas, SQLite long-term store, autonomous fact extractor, local RAG document reader, and context builder. | [Read memory/README.md](file:///c:/Users/liche/Desktop/li's%20Assistance/src/memory/README.md) |
| **[`security/`](file:///c:/Users/liche/Desktop/li's%20Assistance/src/security/README.md)** | Defense-in-depth shield: Layer 1 input injection filter and Layer 2 output code leak sanitizer. | [Read security/README.md](file:///c:/Users/liche/Desktop/li's%20Assistance/src/security/README.md) |
| **[`services/`](file:///c:/Users/liche/Desktop/li's%20Assistance/src/services/README.md)** | Integrations for Groq Whisper-large-v3, GitHub API, Weather, NewsAPI/RSS, Wikipedia, and background task schedulers. | [Read services/README.md](file:///c:/Users/liche/Desktop/li's%20Assistance/src/services/README.md) |
| **[`voice/`](file:///c:/Users/liche/Desktop/li's%20Assistance/src/voice/README.md)** | Audio input/output pipeline: Hybrid female TTS (gTTS + pyttsx3 SAPI5 fallback) and PyAudio microphone listener. | [Read voice/README.md](file:///c:/Users/liche/Desktop/li's%20Assistance/src/voice/README.md) |
| **[`data/`](file:///c:/Users/liche/Desktop/li's%20Assistance/src/data/README.md)** | Local SQLite databases, validated user profiles, and markdown documents for RAG indexing. | [Read data/README.md](file:///c:/Users/liche/Desktop/li's%20Assistance/src/data/README.md) |

---

## ⚙️ Configuration (`config.py`)

Configuration is managed via `pydantic-settings` or `os.getenv` in `src/config.py`, loading values from `.env`:
- `GEMINI_API_KEY`: Google Gemini AI authentication.
- `GROQ_API_KEY`: Ultra-fast Whisper-large-v3 cloud speech-to-text.
- `GITHUB_TOKEN`: (Optional) GitHub REST API rate-limit expansion.
- `OPENWEATHER_API_KEY`: City weather data.
- `NEWS_API_KEY`: Global news headlines.
- `PORT` / `HOST`: Network binding settings for FastAPI.
