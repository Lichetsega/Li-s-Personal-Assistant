# 🧠 AI Core & Native Function Calling (`src/ai/`)

This directory implements the LLM intelligence engine for **Li's AI Assistant**, managing Google Gemini model interactions, system instruction conditioning, and declarative function calling (tools).

---

## 📁 Directory Structure

```text
src/ai/
├── __init__.py           # Package initializer
├── gemini_service.py     # Gemini AI client & dynamic multi-turn conversation manager
└── tools.py              # Native tool definitions & declarative execution registry
```

---

## 🧩 Component Architecture

### 1. `gemini_service.py` (`GeminiService`)
- **LLM Client Wrapper**: Integrates with the official `google-generativeai` SDK.
- **Model Support**: Configured to run on `gemini-1.5-flash` (or `gemini-2.0-flash` / `gemini-1.5-pro` depending on environment configuration).
- **Dynamic Context Injection**: Merges the unified system prompt (persona, validated user profile, episodic SQLite memories, local RAG document chunks, and live date/time) directly into the model's system instructions.
- **Tool Orchestration Loop**:
  - Automatically declares tools to the Gemini model.
  - Intercepts `function_call` parts returned by the model.
  - Dispatches calls to matching Python functions in `TOOL_FUNCTIONS`.
  - Feeds function results back to the model to produce a final, coherent natural language response.

### 2. `tools.py` (`GeminiTools`)
Defines the declarative schemas and execution wrappers for native function calling:
- **`get_weather(city)`**: Retrieves real-time temperature, condition, and humidity via OpenWeatherMap with `wttr.in` fallback.
- **`get_news(category)`**: Fetches top global headlines via NewsAPI with BBC RSS feed fallback.
- **`add_task(task_text)`**, **`get_tasks()`**, **`clear_tasks()`**: Manages Li's active personal tasks.
- **`list_github_repos()`**: Fetches live public repositories from Liche's GitHub account with star counts and primary languages.
- **`get_github_commits(repo_name)`**: Fetches the latest commits with messages, authors, and timestamps.
- **`get_github_readme(repo_name)`**: Reads and extracts an overview of any public repository's README.

---

## 🔄 Function Calling Flow

```text
[User Prompt + Context]
          │
          ▼
   [Gemini Service] ────(Evaluates intent)────► Model detects tool requirement
          │
          ├───────────── FunctionCall: get_github_commits("Li-s-Personal-Assistant")
          │
          ▼
     [tools.py] ────────► Invokes `github_service.get_latest_commits()`
          │
          ▼
  [Tool Response] ──────► Sent back to Gemini as FunctionResponse
          │
          ▼
[Final Response] ──────► Returned to AssistantCore for safety filtering
```
