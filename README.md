<div align="center">

# 🎙️ Li's AI Virtual Assistant (Personal Intelligence Engine)

<i>An enterprise-grade, modular Python AI assistant powered by <b>Google Gemini</b> and <b>Groq Whisper-large-v3</b>, featuring a <b>Multi-Tier Cognitive Memory Engine</b>, <b>Local Document RAG Reader</b>, <b>Dual-Layer Security Guardrails</b>, <b>Interactive Portfolio & Dark-Mode Resume</b>, <b>Proactive Reminders</b>, and <b>Native Function Calling</b>.</i>

<br>

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-009688?style=for-the-badge&logo=fastapi)
![Google Gemini](https://img.shields.io/badge/Google--Gemini-AI-8E44AD?style=for-the-badge&logo=google)
![Groq Whisper](https://img.shields.io/badge/Groq-Whisper--v3-F55036?style=for-the-badge&logo=openai)
![Pydantic](https://img.shields.io/badge/Pydantic-v2-red?style=for-the-badge&logo=pydantic)
![SQLite](https://img.shields.io/badge/SQLite-3-003B57?style=for-the-badge&logo=sqlite)
![Render](https://img.shields.io/badge/Render-Deployed-46E3B7?style=for-the-badge&logo=render)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

</div>

---

## 🌟 Overview

**Li's AI Assistant** is a multimodal personal intelligence system designed to act as an autonomous digital assistant and an interactive portfolio representative for **Liche Tsegaye**. 

Built with **Python 3.10+**, **FastAPI**, **Google Gemini**, and **Groq's LPU-accelerated Whisper-large-v3**, the assistant integrates cognitive long-term memory, local document retrieval (RAG), and strict enterprise security guardrails.

### 🎯 Key Highlights
- **🎙️ Cloud Speech-to-Text**: High-fidelity 16kHz PCM WAV recording streamed to **Groq Whisper-large-v3** with acoustic confidence filters.
- **🧠 Multi-Tier Cognitive Memory**: Schema-validated user identity, relational SQLite episodic storage, autonomous conversation fact extraction, and local markdown RAG search.
- **🛡️ Enterprise Security Guardrails**: Pre-execution prompt-injection defense and post-generation code/credential leak sanitization.
- **📄 Interactive Portfolio & Dark-Mode Resume**: Embedded interactive developer resume with live GitHub repository querying.
- **👩 Female Voice TTS**: Native browser Web Speech API tuned for female voices (*Microsoft Zira*, *Samantha*) with offline SAPI5 fallback.
- **⚡ Proactive Alerts**: Background timer scheduling with real-time WebSocket alerts and audio announcements.

---

## ✨ Feature Matrix

| Feature | Description | Key Modules |
|---|---|---|
| **High-Fidelity STT** | 16kHz PCM WAV audio capture paired with Groq-hosted Whisper-large-v3 with specialized domain priming. | `src/services/whisper_service.py`, `frontend/script.js` |
| **Cognitive Memory** | Long-term SQLite memory store with automated background extraction of personal facts and habits. | `src/memory/memory_store.py`, `src/memory/memory_extractor.py` |
| **Document RAG** | Scans and retrieves relevant excerpts from local notes (`src/data/notes/`) to augment system context. | `src/memory/knowledge_base.py`, `src/memory/context_builder.py` |
| **Dual-Layer Security** | Blocks prompt injections and jailbreaks; redacts system code, credentials, and internal file paths. | `src/security/guardrails.py`, `tests/test_security.py` |
| **Developer Portfolio** | Responsive glassmorphism dashboard and dedicated interactive dark-mode resume page. | `frontend/index.html`, `frontend/resume.html` |
| **Live GitHub Integration** | Real-time GitHub API tools to inspect public repositories, recent commits, and README files. | `src/services/github_service.py`, `src/ai/tools.py` |
| **Tool Ecosystem** | Gemini function calling for weather (OpenWeatherMap/wttr.in), news (NewsAPI/BBC RSS), and Wikipedia. | `src/ai/tools.py`, `src/services/` |
| **Cloud Deployment** | Production-ready asynchronous server configurations for Render and container environments. | `render.yaml`, `Procfile`, `app.py` |

---

## 📁 Project Architecture & Documentation Index

Every component is modular and documented. Click any folder link below to read its dedicated sub-README:

```text
li-s-personal-assistant/
├── README.md                           # Master Project Documentation (You are here)
├── app.py                              # FastAPI Application Server (REST, WebSockets & Audio Endpoints)
├── main.py                             # Interactive CLI Assistant Entrypoint
├── config.py                           # Re-export configuration wrapper
├── requirements.txt                    # Project dependencies
├── render.yaml                         # Render cloud deployment specification
├── Procfile                            # Process file for cloud hosting
├── .env.example                        # Environment variable configuration template
│
├── frontend/                           # 🎨 User Interface & Audio Client
│   ├── README.md                       # ➔ Frontend documentation
│   ├── index.html                      # Main chat and voice interface
│   ├── resume.html                     # Interactive dark-mode portfolio resume
│   ├── style.css                       # Glassmorphism aesthetic and animations
│   └── script.js                       # 16kHz audio recorder, WebSockets, TTS logic
│
├── src/                                # 🏛️ Core Source Backend
│   ├── README.md                       # ➔ Source backend documentation
│   ├── config.py                       # Configuration & environment variable manager
│   │
│   ├── ai/                             # 🧠 Gemini AI & Tool Calling
│   │   ├── README.md                   # ➔ AI module documentation
│   │   ├── gemini_service.py           # Gemini client, tool dispatch loop & context builder
│   │   └── tools.py                    # Declarative tool schemas (GitHub, weather, news, tasks)
│   │
│   ├── core/                           # ⚙️ Orchestration & Routing
│   │   ├── README.md                   # ➔ Core module documentation
│   │   └── assistant.py                # Central AssistantCore orchestrator
│   │
│   ├── memory/                         # 🧠 Multi-Tier Cognitive Memory Engine
│   │   ├── README.md                   # ➔ Memory engine documentation
│   │   ├── schema.py                   # Pydantic schemas (UserProfile, MemoryItem)
│   │   ├── profile_manager.py          # User profile loader & template fallback
│   │   ├── memory_store.py             # SQLite relational database store
│   │   ├── memory_extractor.py         # Autonomous background fact extractor
│   │   ├── knowledge_base.py           # Local document RAG engine (notes indexer)
│   │   ├── conversation_history.py     # Rolling multi-turn short-term dialogue context
│   │   └── context_builder.py          # Unified prompt context synthesizer
│   │
│   ├── security/                       # 🛡️ Enterprise Security Guardrails
│   │   ├── README.md                   # ➔ Security documentation
│   │   └── guardrails.py               # Input jailbreak defense & output leak filter
│   │
│   ├── services/                       # 🔌 Integrations & Services
│   │   ├── README.md                   # ➔ Services documentation
│   │   ├── whisper_service.py          # Groq Whisper-large-v3 Cloud STT
│   │   ├── github_service.py           # Live GitHub REST API service
│   │   ├── weather.py                  # OpenWeatherMap with wttr.in fallback
│   │   ├── news.py                     # NewsAPI with BBC RSS fallback
│   │   ├── wikipedia_service.py        # Wikipedia query lookup
│   │   ├── scheduler.py                # Background reminder & timer scheduler
│   │   └── task_manager.py             # Personal task manager
│   │
│   ├── voice/                          # 🎙️ Local Voice Audio Engine
│   │   ├── README.md                   # ➔ Voice module documentation
│   │   ├── tts.py                      # Hybrid online/offline female voice TTS
│   │   └── stt.py                      # Local microphone listener (SpeechRecognition)
│   │
│   └── data/                           # 💾 Persistent Stores & RAG Documents
│       ├── README.md                   # ➔ Data documentation
│       ├── user_profile.example.json   # Safe public profile template
│       ├── memory.db                   # SQLite memory database (git-ignored)
│       └── notes/                      # Personal RAG notes (git-ignored)
│           └── example_notes.md        # Public template notes
│
└── tests/                              # 🧪 Automated Test Suite
    ├── README.md                       # ➔ Tests documentation
    └── test_security.py                # Security guardrails & anti-leakage test suite
```

---

## 🚀 Quick Start Guide

### 1. Prerequisites
- **Python 3.10+** installed.
- **Google Gemini API Key** from [Google AI Studio](https://aistudio.google.com/app/apikey).
- *(Recommended)* **Groq API Key** from [Groq Console](https://console.groq.com/keys) for ultra-fast Whisper speech-to-text.

### 2. Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Lichetsega/Li-s-Personal-Assistant.git
   cd Li-s-Personal-Assistant
   ```

2. **Create and activate a virtual environment**:
   - **Windows**:
     ```bash
     python -m venv .venv
     .venv\Scripts\activate
     ```
   - **Linux / macOS**:
     ```bash
     python3 -m venv .venv
     source .venv/bin/activate
     ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**:
   Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

   Fill in your configuration keys in `.env`:
   ```env
   # Core AI
   GEMINI_API_KEY=AIzaSy...YourActualGeminiKey

   # High-Speed Cloud STT (Groq Whisper)
   GROQ_API_KEY=gsk_...YourGroqApiKey

   # GitHub Integration (Optional - increases API rate limit)
   GITHUB_TOKEN=ghp_...YourGitHubToken

   # External Tools (Optional)
   OPENWEATHER_API_KEY=your_openweather_key
   NEWS_API_KEY=your_news_api_key
   ```

---

## 💻 Running the Assistant

### Launch Web Interface (FastAPI + Modern UI)
```bash
python app.py
```
Open your browser and navigate to:
- 💬 **Main Assistant Dashboard**: [http://localhost:8000](http://localhost:8000)
- 📄 **Interactive Developer Resume**: [http://localhost:8000/resume.html](http://localhost:8000/resume.html)

### Launch CLI Voice Mode (Terminal)
```bash
python main.py
```
- Speak into your microphone by typing `voice`.
- Or enter queries directly for instant text responses.

### Run Automated Security Tests
```bash
python -m tests.test_security
```

---

## ☁️ Deployment

The project is pre-configured for one-click deployment on **Render**:
- `render.yaml` defines the web service configuration.
- `Procfile` specifies the ASGI web worker:
  ```text
  web: uvicorn app.py:app --host 0.0.0.0 --port $PORT
  ```

---

## 🔒 Security & Privacy by Design

- **Zero Hardcoded Secrets**: All credentials and sensitive API tokens are dynamically loaded from `.env`.
- **Git Privacy Protection**: `.env`, `src/data/user_profile.json`, `src/data/memory.db`, and `src/data/notes/*` are strictly excluded via `.gitignore`.
- **Active Guardrails**: Every query passes through `src/security/guardrails.py` to prevent unauthorized prompt introspection, backtrace leakage, and path exposure.

---

## 📄 License

This project is licensed under the **MIT License**.
