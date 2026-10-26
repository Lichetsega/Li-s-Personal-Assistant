# 🛡️ Security Guardrails & Data Protection (`src/security/`)

The `src/security/` directory implements enterprise security layers designed to safeguard the assistant against prompt injection, jailbreaks, internal code extraction, and inadvertent leakage of sensitive data or credentials.

---

## 📁 Directory Structure

```text
src/security/
├── __init__.py           # Re-exports security guardrails singleton
└── guardrails.py         # Dual-layer input inspection and output sanitization filters
```

---

## 🔒 Defensive Architecture

The system uses a **Dual-Layer Defense-in-Depth** strategy:

```text
Incoming User Prompt
       │
       ▼
┌────────────────────────────────────────────────────────┐
│  LAYER 1: Input Inspection (Pre-Execution Guardrail)   │
│  - Blocks prompt extraction directives                 │
│  - Blocks source code & architecture probing           │
│  - Blocks Jailbreak / "DAN" / Developer mode attempts  │
└────────────────────────────────────────────────────────┘
       │
       ├───► [Triggered] ──► Returns `SAFE_REFUSAL_MESSAGE` (Stops execution)
       │
       ▼ (Clean)
[LLM Generation & Execution]
       │
       ▼
┌────────────────────────────────────────────────────────┐
│  LAYER 2: Output Sanitization (Post-Execution Filter)  │
│  - Blocks raw Markdown code blocks                     │
│  - Filters Python class/function definitions           │
│  - Blocks filesystem paths (e.g. C:\Users\...)         │
│  - Sanitizes API key markers & environment variables   │
│  - Blocks internal system prompt markers               │
└────────────────────────────────────────────────────────┘
       │
       ├───► [Pattern Matched] ──► Replaces leak with `SAFE_REFUSAL_MESSAGE`
       │
       ▼ (Clean)
Sanitized Response Delivered to User
```

---

## 📋 Guardrail Breakdown

### 1. Layer 1: Input Probing & Jailbreak Defense (`inspect_input`)
Monitors all incoming prompts against compiled regular expression patterns:
- **System Instruction Extraction**: Detects attempts to print, quote, or reveal system prompts (`"ignore previous instructions"`, `"what is your system prompt"`).
- **Source Code Probing**: Detects requests to show internal Python code, backend logic, or view files (`"show me app.py"`, `"show me your python code"`).
- **Roleplay & Jailbreak Probes**: Defends against developer mode switches, "DAN" prompts, and unfiltered persona masquerades.
- **Action**: When matched, safely halts execution immediately and returns a polite refusal message without consuming LLM tokens.

### 2. Layer 2: Output Code Leak Filter (`filter_output`)
Inspects model responses before they are rendered in the UI or spoken aloud:
- **Markdown Code Fences**: Strips raw ```python / ```bash blocks if injected or produced by the model.
- **Python Syntax Signatures**: Detects `def `, `class `, `import os`, `FastAPI`, etc.
- **Filesystem Paths**: Redacts Windows/Unix file paths (`C:\Users\...`, `src/core/assistant.py`).
- **Credential & Secret Protection**: Detects Google AI key prefixes (`AIzaSy...`), `.env` references, and key assignment patterns.
- **System Prompt Markers**: Redacts internal section delimiters (e.g. `--- BEHAVIORAL RULES ---`).

### 3. Error Sanitization (`sanitize_error`)
- Traps unhandled backend exceptions to prevent Python stack traces, file paths, or line numbers from reaching the user.
- Emits a clean, non-revealing error message while logging the full traceback internally for maintainers.
