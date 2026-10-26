# 🎨 Frontend Architecture & Interactive Interface

This directory houses the complete frontend client for **Li's AI Assistant** — a modern, responsive web application delivering real-time multimodal interaction, high-fidelity audio recording, and an interactive developer portfolio.

---

## 📁 Directory Structure

```text
frontend/
├── index.html       # Primary Assistant Dashboard & Chat/Voice Interface
├── resume.html      # Interactive Dark-Mode Developer Resume & Portfolio
├── style.css        # Glassmorphism aesthetic, theme variables, and animations
└── script.js        # Audio recording pipeline, WebSockets, TTS, and UI logic
```

---

## 🌟 Key Features

### 1. 🎙️ 16kHz PCM WAV Audio Capture Engine
- Built directly with browser `AudioContext` and streaming buffers.
- Captures microphone input at **16,000 Hz, single-channel (mono), 16-bit PCM WAV**.
- Streams recorded binary audio to the FastAPI `/api/voice` endpoint for high-speed cloud transcription via **Groq Whisper-large-v3**.
- Features visual microphone pulsation and dynamic audio wave animators during speech.

### 2. 👩 Female Voice Text-to-Speech (TTS)
- Uses the native **Web Speech API** (`window.speechSynthesis`).
- Auto-detects and prioritizes premium natural female voices (*Microsoft Zira*, *Google US English Female*, *Samantha*, *Victoria*).
- Includes pitch and rate calibration tailored for clear conversational output.

### 3. 🌐 Dual Mode-Aware Interaction
- **Voice Mode**: Triggered by the microphone button; assistant speaks aloud and displays spoken text.
- **Text Mode**: Triggered by typing into the prompt box; assistant responds silently with formatted text.
- Mode-toggle button in the header enables or disables auto-speech synthesis on demand.

### 4. 📄 Interactive Portfolio & Dark-Mode Resume (`resume.html`)
- Dedicated showcase displaying Liche Tsegaye's professional experience, education, and technical skills.
- Live interactive project cards with GitHub statistics and direct project repository links.
- Seamlessly linked to the AI assistant for contextual question answering.

### 5. 💎 Glassmorphism Design System (`style.css`)
- Sleek dark theme using deep indigo/violet gradients, frosted glass blur (`backdrop-filter: blur(16px)`), and subtle glowing borders.
- Fully responsive layout optimized for mobile screens, tablets, and desktop displays.
- Visual status indicators for WebSocket connectivity and AI processing states.

---

## ⚙️ How It Connects to Backend

```
[User Browser]
   │
   ├─► Audio Recorder (16kHz PCM WAV) ──────► POST /api/voice ───► Groq Whisper STT
   ├─► Text Query Prompt ──────────────────► POST /api/chat  ───► Gemini Assistant
   └─► Proactive Reminders / Real-time ◄──── WebSocket /ws   ───◄ Background Scheduler
```

---

## 🚀 Running the Frontend

The frontend is served directly by the FastAPI backend:
1. Ensure the backend server is running:
   ```bash
   python app.py
   ```
2. Open your browser at:
   - **Main Assistant**: [http://localhost:8000/](http://localhost:8000/)
   - **Interactive Resume**: [http://localhost:8000/resume.html](http://localhost:8000/resume.html)
