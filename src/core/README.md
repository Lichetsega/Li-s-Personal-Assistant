# ⚙️ Core Orchestrator (`src/core/`)

The `src/core/` directory contains the central brain and coordinating logic for **Li's AI Assistant**.

---

## 📁 Directory Structure

```text
src/core/
├── __init__.py           # Package initializer
└── assistant.py          # Central AssistantCore orchestrator & intent router
```

---

## 🧩 Component: `assistant.py` (`AssistantCore`)

`AssistantCore` serves as the primary gateway for all user queries coming from the CLI, WebSockets, or HTTP endpoints. It unifies input sanitization, security guardrails, domain-specific phonetic normalization, asynchronous memory extraction, context synthesis, and LLM execution.

### Responsibilities

1. **Acoustic & Speech Normalization (`_normalize_speech_input`)**:
   - Corrects common acoustic mishearings from speech recognition models (e.g. correcting *"party song"* or *"inside"* to *"INSA"*, *"ragged"* to *"RAG"*, and *"reach's"* to *"Li's"*).

2. **Security Guardrail Enforcement**:
   - **Layer 1 (Pre-execution)**: Passes cleaned user input through `security_guardrails.inspect_input()` to block jailbreaks, system prompt extractions, or code probes before invoking any model.
   - **Layer 2 (Post-execution)**: Sanitizes the generated response via `security_guardrails.filter_output()` to prevent accidental leakage of internal paths, credentials, or source code.

3. **Autonomous Learning Pipeline**:
   - Asynchronously triggers `MemoryExtractor.extract_and_store(clean_text)` in a background worker thread for every valid interaction, extracting facts about user habits and preferences without blocking the conversation flow.

4. **Deterministic Intent Fast-Path**:
   - Rapidly handles time queries, joke generation, explicit task additions, reminder scheduling, and manual memory clearing before falling back to full Gemini LLM processing.

5. **Proactive Reminders Dispatch**:
   - Interfaces with `ReminderScheduler` to register asynchronous callback notifications that broadcast alerts to active WebSocket sessions and voice synthesizers.

---

## 🔄 Request Lifecycle

```text
User Input (Audio / Text)
       │
       ▼
[Speech Normalizer]  (Phonetic domain corrections)
       │
       ▼
[Security Guardrail] (Input Inspection) ────(Violation)───► Safe Refusal Message
       │
   (Authorized)
       │
       ├─► [Background Worker] ──► Autonomous Fact Extractor ──► SQLite Memory
       │
       ▼
[Intent Fast-Path / Gemini Service]
       │
       ▼
[Security Guardrail] (Output Code Leak Filter)
       │
       ▼
Mode-Aware Delivery (Spoken Voice Audio / Silent Formatted Text)
```
