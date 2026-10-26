# 🎙️ Voice & Audio Pipeline (`src/voice/`)

The `src/voice/` directory houses the local speech input/output engine, audio device bindings, and fallback voice synthesizers for **Li's AI Assistant**.

---

## 📁 Directory Structure

```text
src/voice/
├── __init__.py           # Package initializer
├── stt.py                # Local microphone listener (SpeechRecognition fallback)
└── tts.py                # Hybrid Online/Offline Female Voice TTS Engine
```

---

## 🧩 Audio Modules

### 1. `tts.py` (`HybridTTSEngine`)
- **Primary Voice Persona**: Configured with a dedicated female vocal persona.
- **Dual-Engine Architecture**:
  - **Online Synthesis (`speak_online_gtts`)**: Uses Google Text-to-Speech (`gTTS`) to synthesize high-clarity natural human speech with local audio player playback (`pygame` or `playsound`).
  - **Offline Synthesis (`speak_offline`)**: Automatically initializes a local SAPI5/pyttsx3 voice engine. Dynamically searches installed OS voices to bind to natural female voices (*Microsoft Zira*, *Hazel*, *Samantha*, *Eva*).
- **Speed & Cadence Control**: Configurable voice rate (default 175 words per minute) for a smooth, natural conversational pace.

### 2. `stt.py` (`LocalSTT`)
- **Microphone Interface**: Uses `speech_recognition` and `pyaudio` to capture ambient voice input from local desktop microphones.
- **Ambient Noise Calibration**: Automatically adjusts for background room noise on startup.
- **CLI Voice Mode**: Powers voice interaction in terminal sessions (`python main.py`) when WebSockets or browser interfaces are not in use.

---

## 🔊 Speech Processing Hierarchy

```text
Voice Input:
   1. Primary (Web App): Browser 16kHz PCM WAV ──► Groq Whisper-large-v3 Cloud STT
   2. Secondary (CLI):   PyAudio Microphone    ──► Google SpeechRecognition / Sphinx

Voice Output:
   1. Primary (Web App): Browser Web Speech API (Microsoft Zira / Samantha Female Voice)
   2. Secondary (CLI):   HybridTTSEngine (gTTS Online ──► pyttsx3 SAPI5 Offline Fallback)
```
