# Career, Technical Skills & Software Engineering

## Professional Summary
- **Current Role**: Software Engineer / AI Developer (5th-Year Graduating Student at Jimma University)
- **Primary Domain**: Artificial Intelligence, Retrieval-Augmented Generation (RAG & Agentic RAG), Python Backend, Full-stack Web Apps
- **Years of Experience**: 3+ years of software development and AI engineering

## Work & Internship Experience
- **Company**: INSA (Information Network Security Administration)
- **Department**: Artificial Intelligence (AI) Department
- **Duration**: 6 Months Internship
- **Key Projects & Responsibilities**: 
  - Researched, designed, and implemented RAG (Retrieval-Augmented Generation) architectures.
  - Developed and scaled Agentic RAG systems for intelligent information retrieval and autonomous workflows.
  - Worked with modern LLM orchestration frameworks, vector databases, and secure AI pipeline design.

## Current Availability & Career Interests
- **Target Roles**: 
  - Remote Software Engineering roles (Python / Full-Stack)
  - AI / Machine Learning Engineering roles or internships
  - Freelance development contracts and AI consulting
  - Full-time graduate software engineering positions upon graduation
- **Work Model**: Remote, Hybrid, or On-site

## Featured GitHub Projects (https://github.com/Lichetsega)

1. **Visit Ethiopia Agentic RAG System** (`Agentic-Retrieval-Augmented-Generation-Agentic-RAG-`):
   - **Overview**: Autonomous, multi-agent RAG system for intelligent exploration of Ethiopian tourism, culture, logistics, and heritage.
   - **Fused Supervisor Planner**: Single low-latency call handling intent classification, conversational pronoun resolution, sentiment analysis, and multi-query expansion.
   - **Domain Expert Sub-Agents**:
     - *Itinerary & Route Planning Expert*: Evaluates overland transit, altitude/terrain realities, and separates logistics from activities.
     - *Culture & Heritage Expert*: Covers UNESCO World Heritage sites (Lalibela, Gondar, Simien Mountains, Harar), festivals (Timkat, Meskel), and cuisine (Injera, coffee ceremonies).
     - *Logistics & Visa Expert*: Handles e-Visa requirements, domestic flight booking logic (Ethiopian Airlines), safety advisories, and currency rules.
   - **Hybrid Retrieval Engine**: Blends dense semantic vector search (ChromaDB) with sparse keyword search (BM25 + Levenshtein distance fuzzy vocabulary expansion for localized phonetic spellings like Wenchi / Wonchi).
   - **Performance & Caching**: Two-tier query caching (exact hash + semantic sequence matching with similarity >= 0.82) returning instant responses with 0 API calls.
   - **Live Tool Augmentation**: Real-time currency exchange API integration converting foreign currencies ($ USD, € EUR) to Ethiopian Birr (ETB).
   - **Resilience & Key Management**: Round-Robin Gemini key rotation with error classification and local Ollama model fallback (`llama3.1:8b-instruct`).
   - **Automated Web Crawler**: Background daemon on East Africa Time (EAT) running headless Selenium to crawl and re-index tourism bureaus with diffing and orphan chunk purging.
   - **Dual Interface**: Production Flask REST API (`/ask`, `/ready`, `/admin`) + Streamlit UI with live agent execution traces.

2. **Li's Personal AI Voice Assistant** (`Li-s-Personal-Assistant`):
   - **Overview**: Intelligent voice assistant and portfolio representative with real-time audio interaction and multi-turn conversation memory.
   - **Core Stack**: FastAPI backend, WebSockets, Google Gemini API with multi-key failover, client-side STT/TTS, and SQLite profile storage.
   - **Confidentiality & Guardrails**: Multi-layered security inspecting incoming prompt injection/jailbreak attempts and sanitizing outgoing code leaks, system instructions, and server filepaths.
   - **Local RAG Fallback**: Keyword-based offline knowledge retrieval engine ensuring smooth visitor responses even during complete quota exhaustion.

3. **Cybersecurity Password Exposure Checker** (`password_checker`):
   - **Overview**: Security tool checking compromised credentials against billions of breached accounts using the Have I Been Pwned Pwned Passwords API.
   - **Privacy Architecture**: Implements SHA-1 hashing and the **k-Anonymity** model, transmitting only the first 5 characters of the password hash to the external API so the plaintext password is never exposed.
   - **Capabilities**: Supports multiple passwords via CLI arguments and reports exact breach frequency.

4. **Hacker News Signal Filter & Scraper** (`hacker_news-scraper`):
   - **Overview**: High-signal Python web scraper extracting top technology discussions without low-engagement noise.
   - **Capabilities**: Multi-page dynamic scraping with BeautifulSoup, filters stories with scores > 99, sorts articles by vote counts, respects ethical scraping limits with rate throttling, and generates a styled visual HTML report.

5. **Document Automation & File Utilities**:
   - `pdf_merger`: CLI automation tool for programmatic PDF document merging.
   - `watermarked-pdf`: Applies custom programmatic watermarks across multi-page document batches.
   - `JPGtoPNG-using-python`: High-performance Python script for batch image conversion and preprocessing.

6. **Interactive JavaScript Games & Audio Suite**:
   - `dice-game`, `guess-my-number`, `world-quiz`: Responsive browser games featuring state machines, score tracking, and DOM manipulation.
   - `drum-kit-`: Virtual interactive drum kit utilizing keyboard event triggers and Web Audio API for zero-latency audio playback.

## Technical Skills & Languages (Dual Specialization)
- **Primary AI & Backend Stack**: Python, FastAPI, PyTorch, LangChain, LlamaIndex, Google Gemini API, OpenAI APIs, Vector DBs (Chroma/FAISS), Pydantic, Uvicorn.
- **Full-Stack Web Development Stack**: MERN Stack (MongoDB, Express, React, Node.js), JavaScript/TypeScript, HTML5/CSS3, RESTful APIs, WebSockets.
- **Databases & Caching**: PostgreSQL, MongoDB, SQLite, Redis.
- **Developer Note for Recruiters**: Li specializes in **both** AI/Backend engineering (Python) and Full-Stack web development (MERN). She is capable of designing intelligent LLM/RAG pipelines and delivering complete, user-facing full-stack applications end-to-end.

## Key Strengths & Soft Skills
- **Strong Communicator**: Clearly articulates technical ideas to both engineers and non-technical stakeholders.
- **High Accountability**: Takes complete ownership of tasks from planning to deployment and maintenance.
- **Problem Solver**: Enjoys tackling hard technical challenges, optimizing architectures, and writing maintainable code.

## Extracurriculars, Hackathons & Certifications
- Active participant in university tech clubs and coding communities at Jimma University.
- Participated in multiple hackathons, collaborating in fast-paced software prototyping.
- Completed notable online technical certifications in AI, machine learning, and software engineering.
