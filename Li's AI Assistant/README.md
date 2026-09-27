<div align="center">

# 🎙️ Gemini AI Voice Assistant

<i>A modern, modular Python-based virtual voice assistant powered by <b>Google Gemini AI</b>, featuring an interactive Web UI, Speech Recognition, Hybrid Text-to-Speech (Online gTTS + Offline fallback), Weather updates, News headlines, Wikipedia summaries, Music playback, and Task management.</i>

<br>

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-009688?style=for-the-badge&logo=fastapi)
![Google Gemini](https://img.shields.io/badge/Google--Gemini-AI-8E44AD?style=for-the-badge&logo=google)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

</div>

---

## 🌟 Overview

The **Gemini AI Voice Assistant** is an extendable virtual assistant built with **Python 3**, **FastAPI**, and the official **Google GenAI SDK**. It combines real-time voice processing (Speech-to-Text & Text-to-Speech) with intelligent AI response generation and external API service integrations.

The application features a **Dual Interface System**:
- **Interactive Web Interface**: A responsive glassmorphism web dashboard with an animated AI voice orb visualizer, WebSocket communication, and built-in speech controls.
- **Terminal CLI Mode**: A lightweight interactive command-line interface for direct terminal voice and text interaction.

---

## ✨ Features

- 🤖 **Gemini AI Conversational Intelligence**: Powered by Google Gemini AI with customized system prompts optimized for concise, natural vocal responses.
- 🔊 **Hybrid Text-to-Speech (TTS) Engine**:
  - **Primary (Online)**: High-quality `gTTS` / Web Speech Synthesis.
  - **Fallback (Offline)**: Automatic, silent transition to `pyttsx3` (SAPI5) if connection drops.
- 🎙️ **Voice Recognition (STT)**: Microphone voice listening via `SpeechRecognition` and Web Speech API.
- 🌤️ **Real-time Weather Updates**: City weather reports powered by OpenWeatherMap with automatic fallback to `wttr.in`.
- 📰 **News Headlines**: Latest top news via NewsAPI with automatic fallback to BBC RSS feeds.
- 🎵 **Music Playback**: Direct search and playback on YouTube.
- 📖 **Wikipedia Queries**: Direct summary lookup for people, places, and concepts.
- 📝 **Task & Reminder Management**: Track, list, and clear personal tasks.
- ⚡ **FastAPI Backend**: Asynchronous REST endpoints and real-time WebSockets.

---

## 📁 Project Architecture

```text
Li's AI Assistant/
├── .env.example                # Public environment configuration template
├── config.py                   # Re-export configuration wrapper
├── app.py                      # FastAPI Web Server (REST API & WebSockets)
├── main.py                     # Interactive CLI Voice Assistant entrypoint
├── requirements.txt            # Project dependencies
├── .gitignore                  # Git privacy & secret protection configuration
├── src/
│   ├── config.py               # Centralized configuration & environment loader
│   ├── ai/
│   │   └── gemini_service.py   # Gemini AI API wrapper & model fallback candidate router
│   ├── voice/
│   │   ├── tts.py              # Hybrid Online/Offline Text-to-Speech engine
│   │   └── stt.py              # Speech Recognition microphone listener
│   ├── services/
│   │   ├── weather.py          # Weather API service
│   │   ├── news.py             # News headlines service
│   │   ├── wikipedia_service.py # Wikipedia query lookup service
│   │   ├── music.py            # YouTube music playback service
│   │   ├── jokes.py            # Programming & general jokes generator
│   │   └── task_manager.py     # Personal task & reminder manager
│   └── core/
│       └── assistant.py        # Central Orchestrator & intent router
└── frontend/
    ├── index.html              # Custom Web UI dashboard layout
    ├── style.css               # Glassmorphism dark-mode UI styling
    └── script.js               # Web Speech API & WebSocket frontend logic
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
- Type `voice` to speak into your microphone.
- Type any query directly into the terminal prompt.
- Type `exit` to quit.

---

## 🔒 Security & Privacy

This project strictly adheres to environment security best practices:
- **Zero Hardcoded Secrets**: All API keys are loaded dynamically from environment variables.
- **Git Protection**: `.env` is listed in `.gitignore` to prevent secret credentials from ever being committed to GitHub.

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome! Feel free to check out the issues page.

---

## 📄 License

This project is licensed under the **MIT License**.
