<div align="center">

# 🎙️ Li's AI Virtual Assistant (Personal Intelligence Engine)

<i>An enterprise-grade, modular Python-based virtual voice assistant powered by <b>Google Gemini AI</b>, featuring a <b>Multi-Tier Cognitive Memory Engine</b>, <b>Local Document RAG Reader</b>, <b>Proactive Background Reminders</b>, <b>Multi-Turn Session History</b>, <b>Mode-Aware Voice/Text Responses</b>, <b>Female Voice TTS Engine</b>, and Native Function Calling.</i>

<br>

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-009688?style=for-the-badge&logo=fastapi)
![Google Gemini](https://img.shields.io/badge/Google--Gemini-AI-8E44AD?style=for-the-badge&logo=google)
![Pydantic](https://img.shields.io/badge/Pydantic-v2-red?style=for-the-badge&logo=pydantic)
![SQLite](https://img.shields.io/badge/SQLite-3-003B57?style=for-the-badge&logo=sqlite)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

</div>

---

## 🌟 Overview

**Li's AI Assistant** is an enterprise-grade personal AI assistant built with **Python 3**, **FastAPI**, **Pydantic**, **SQLite**, and **Google Gemini AI**.

It features an advanced **Multi-Tier Cognitive Engine**:
- **Pydantic User Profile**: Validated identity, communication preferences, and key behavioral guardrails.
- **Relational SQLite Memory Store**: Episodic memory database for long-term user facts, preferences, and goals.
- **Autonomous Fact Extractor**: Asynchronous background LLM pipeline that extracts facts naturally during conversation.
- **Local Document RAG Reader**: Searches and retrieves excerpts from local Markdown, text, and JSON notes in `src/data/notes/`.
- **Proactive Reminder Scheduler**: Background timer engine that broadcasts proactive alerts to voice TTS & WebSockets.
- **Multi-Turn Short-Term History**: Rolling context buffer for natural multi-turn conversations.

---

## ✨ Features

- 🧠 **Multi-Tier Cognitive Memory Architecture**:
  - **Schema-Validated User Profile (`UserProfile`)**: Pydantic-powered user identity, bio, communication style, and custom rules (`src/data/user_profile.json`).
  - **Relational Memory Database (`MemoryStore`)**: SQLite database (`src/data/memory.db`) storing facts, preferences, goals, and habits.
  - **Autonomous Fact Extractor (`MemoryExtractor`)**: Asynchronous background pipeline that extracts new personal facts from natural user conversations.
  - **Local Document RAG Engine (`KnowledgeBase`)**: Indexes and retrieves relevant passages from personal files in `src/data/notes/`.
  - **Proactive Background Scheduler (`ReminderScheduler`)**: Sets background timers and broadcasts proactive alerts via WebSockets and TTS.
  - **Multi-Turn Session History (`ConversationHistory`)**: Rolling context window for natural multi-turn dialogue memory.
  - **Dynamic Context Assembler (`ContextBuilder`)**: Synthesizes persona, profile, SQLite memories, RAG notes, chat history, and live environment into a unified prompt context.
- ⚙️ **Native Gemini Function Calling**: Declarative tool schema integration for weather, news, wikipedia, task management, and reminders.
- 🎙️ **Mode-Aware Response Engine**:
  - **Voice Mode**: Responds aloud with spoken audio when input is given via microphone or voice mode.
  - **Text Mode**: Responds silently in text form when input is typed via keyboard or chat prompt.
- 👩 **Female Voice Text-to-Speech (TTS)**:
  - **Browser Web Speech API**: Configured with female voice preference selection (*Microsoft Zira*, *Google US English Female*, *Samantha*, *Victoria*).
  - **Offline PyTTSx3 Fallback**: Configured to auto-detect and bind to SAPI5 female voice engines (*Microsoft Zira*, *Hazel*).
- 🌤️ **Real-time Weather Updates**: City weather reports powered by OpenWeatherMap with automatic fallback to `wttr.in`.
- 📰 **News Headlines**: Latest top news via NewsAPI with automatic fallback to BBC RSS feeds.
- 📖 **Wikipedia Queries**: Direct summary lookup for people, places, and concepts.
- 📝 **Task & Reminder Management**: Track, list, and clear personal tasks.
- ⚡ **FastAPI Backend**: Asynchronous REST endpoints and real-time WebSockets with proactive alert broadcasting.

---

## 📁 Project Architecture

```text
Li's AI Assistant/
├── .env.example                # Public environment configuration template
├── config.py                   # Re-export configuration wrapper
├── app.py                      # FastAPI Web Server (REST API, WebSockets & Proactive Reminders)
├── main.py                     # Interactive CLI Voice Assistant entrypoint
├── requirements.txt            # Project dependencies
├── .gitignore                  # Git privacy & secret protection configuration
├── src/
│   ├── config.py               # Centralized configuration & environment loader
│   ├── ai/
│   │   ├── gemini_service.py   # Gemini AI client with dynamic context builder & function calling
│   │   └── tools.py            # Gemini Native Tool declarations (weather, news, wikipedia, tasks)
│   ├── memory/
│   │   ├── schema.py           # Pydantic schemas (UserProfile, MemoryItem, MemoryCategory)
│   │   ├── profile_manager.py  # User profile loader & template fallback validator
│   │   ├── memory_store.py     # SQLite relational memory database store
│   │   ├── memory_extractor.py # Autonomous background fact extraction pipeline
│   │   ├── knowledge_base.py   # Local document RAG engine (notes search)
│   │   ├── conversation_history.py # Rolling multi-turn short-term dialogue context
│   │   └── context_builder.py  # Dynamic prompt context synthesizer
│   ├── data/
│   │   ├── user_profile.example.json # Safe public template for GitHub
│   │   ├── user_profile.json   # Local personal profile (git-ignored)
│   │   ├── memory.db           # Local SQLite memory database (git-ignored)
│   │   └── notes/              # Local personal notes & documents RAG folder (git-ignored)
│   │       └── example_notes.md# Public example notes template
│   ├── voice/
│   │   ├── tts.py              # Hybrid Online/Offline Female Voice TTS engine
│   │   └── stt.py              # Speech Recognition microphone listener
│   ├── services/
│   │   ├── weather.py          # Weather API service
│   │   ├── news.py             # News headlines service
│   │   ├── wikipedia_service.py # Wikipedia query lookup service
│   │   ├── jokes.py            # Programming & general jokes generator
│   │   ├── scheduler.py        # Background timer & proactive reminder scheduler
│   │   └── task_manager.py     # Personal task manager
│   └── core/
│       └── assistant.py        # Central Orchestrator & intent router
└── frontend/
    ├── index.html              # Custom Web UI dashboard layout
    ├── style.css               # Glassmorphism dark-mode UI styling
    └── script.js               # Web Speech API & female voice frontend logic
```

---

## 🚀 Quick Start Guide

### 1. Prerequisites
- **Python 3.10+** installed on your system.
- A free **Google Gemini API Key** from [Google AI Studio](https://aistudio.google.com/app/apikey).

### 2. Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/your-username/python-voice-assistant.git
   cd python-voice-assistant
   ```

2. **Create & Activate Virtual Environment**:
   - **Windows (PowerShell/CMD)**:
     ```bash
     python -m venv venv
     .\venv\Scripts\activate
     ```
   - **Linux / macOS**:
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables**:
   Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
   Open `.env` and add your Gemini API Key:
   ```env
   GEMINI_API_KEY=AIzaSy...YourActualKeyHere
   ```

---

## 💻 Usage

### Launch Web Interface (FastAPI)
Run the web application server:
```bash
python app.py
```
Open your browser and navigate to:
👉 **`http://localhost:8000`**

### Launch CLI Voice Mode (Terminal)
Run the command-line assistant:
```bash
python main.py
```
- Type `voice` to speak into your microphone (receives spoken voice audio response).
- Type any query directly into the terminal prompt (receives silent text response).
- Type `exit` to quit.

---

## 🔒 Security & Privacy

This project strictly adheres to enterprise security and privacy standards:
- **Zero Hardcoded Secrets**: All API keys are loaded dynamically from `.env`.
- **Git Privacy Protection**: `.env`, `src/data/user_profile.json`, `src/data/memory.db`, and `src/data/notes/*` are explicitly listed in `.gitignore` so your personal profile, facts, notes, and secrets are **never pushed to GitHub**.
- **Public Template Support**: `user_profile.example.json` and `example_notes.md` are provided as safe public templates for anyone cloning the project.

---

## 📄 License

This project is licensed under the **MIT License**.
