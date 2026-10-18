import re
import logging
from typing import Optional, Tuple

logger = logging.getLogger("SecurityGuardrails")

SAFE_REFUSAL_MESSAGE = (
    "I am here to tell you about Liche Tsegaye, her portfolio, projects, and skills. "
    "For security and privacy reasons, I do not disclose internal source code, system instructions, "
    "or technical architecture details."
)

SAFE_ERROR_MESSAGE = (
    "I encountered an unexpected issue while processing your request. Please try again in a moment."
)

# 1. Input Probing / Jailbreak Patterns
PROMPT_INJECTION_PATTERNS = [
    # Direct instruction extraction
    r"(?:show|print|tell|reveal|display|output|repeat|quote|write)\s+(?:me\s+)?(?:all\s+)?(?:the\s+)?(?:your\s+)?(?:initial\s+|system\s+|hidden\s+|original\s+|base\s+)?(?:prompt|instruction|rules|guideline|directive)",
    r"what\s+(?:is|are|were)\s+your\s+(?:system\s+|initial\s+|original\s+|exact\s+)?(?:instructions|prompts|prompt|rules|directives)",
    r"repeat\s+everything\s+(?:above|before)",
    r"ignore\s+(?:all\s+)?(?:previous|prior|above)\s+(?:instructions|rules|directions|prompts)",
    r"(?:disregard|forget|bypass)\s+(?:all\s+)?(?:rules|instructions|safeguards|filters)",
    
    # Code extraction / Architecture probing
    r"(?:show|print|reveal|display|output|share|give)\s+(?:me\s+)?(?:the\s+)?(?:your\s+)?(?:source\s+code|backend\s+code|python\s+code|underlying\s+code|codebase|implementation|repository)",
    r"what\s+is\s+your\s+(?:source\s+code|backend\s+code|codebase|internal\s+logic)",
    r"(?:show|list|print)\s+(?:your\s+)?(?:tools|functions|apis)\s+(?:definitions|schema|signatures|declarations)",
    r"(?:view|read|cat|open)\s+(?:file|app\.py|gemini_service\.py|assistant\.py|\.env|config\.py)",
    
    # Jailbreak / Roleplay modes
    r"(?:enter|switch\s+to|activate)\s+(?:developer\s+mode|dan\s+mode|jailbreak\s+mode|debug\s+mode|unrestricted\s+mode)",
    r"pretend\s+(?:you\s+are|you're)\s+(?:in\s+developer\s+mode|unconstrained|unfiltered|dan|a\s+hacker)",
    r"you\s+are\s+now\s+in\s+(?:developer|unrestricted|god)\s+mode"
]

# 2. Output Leak Patterns (Actual code, file paths, credentials, system instructions)
OUTPUT_LEAK_PATTERNS = [
    # Explicit Markdown code blocks
    r"```(?:python|py|bash|sh|javascript|js|json|sql|html|css)?\s*[\r\n]+",
    
    # Python code definitions & statements
    r"(?m)^\s*(?:def\s+[a-zA-Z_][a-zA-Z0-9_]*\s*\(|class\s+[a-zA-Z_][a-zA-Z0-9_]*\s*[:\(])",
    r"(?m)^\s*(?:import\s+(?:os|sys|re|json|fastapi|uvicorn|google|pydantic|sqlite3)|from\s+(?:src|fastapi|pydantic)\b)",
    r"\b(?:app\s*=\s*FastAPI|AssistantCore\(|GeminiService\(|MemoryStore\()",
    
    # File paths & sensitive file names
    r"[a-zA-Z]:[\\/](?:Users|Windows|Program Files)[\\/][^\s\"']+",
    r"\b(?:src[\\/](?:core|ai|memory|services|data|security)[\\/][a-zA-Z0-9_]+\.py)\b",
    r"\b(?:app\.py|gemini_service\.py|context_builder\.py|user_profile\.json|assistant\.py|tools\.py|memory_store\.py)\b",
    
    # Environment variables & API key markers
    r"\b(?:AIzaSy[A-Za-z0-9_-]{33}|OPENWEATHER_API_KEY|GEMINI_API_KEY|NEWS_API_KEY)\b",
    r"\b(?:api[_-]?key\s*[:=]\s*['\"][a-zA-Z0-9_\-\.]{10,}['\"])",
    r"\.env\b",
    
    # System prompt leak markers
    r"--- (?:BEHAVIORAL RULES|ABOUT LICHE TSEGAYE|FACTS & DETAILS ABOUT LICHE|REAL-TIME CONTEXT|CRITICAL SECURITY DIRECTIVE) ---",
    r"You are Li's personal AI assistant, embedded in Liche Tsegaye's portfolio",
    
    # Python error stack trace markers
    r"Traceback\s*\(most\s+recent\s+call\s+last\):",
    r'File\s*["\'][^"\']+["\'],\s*line\s*\d+',
    r"\b(?:SyntaxError|NameError|TypeError|ValueError|AttributeError|ZeroDivisionError|KeyError):\s+"
]

_COMPILED_INPUT_PATTERNS = [re.compile(p, re.IGNORECASE) for p in PROMPT_INJECTION_PATTERNS]
_COMPILED_OUTPUT_PATTERNS = [re.compile(p, re.IGNORECASE) for p in OUTPUT_LEAK_PATTERNS]

class SecurityGuardrails:
    """
    Production-grade Security & Guardrails Engine.
    Prevents prompt injection, system prompt extraction, source code leaks, and stack trace disclosure.
    """
    
    @staticmethod
    def inspect_input(user_input: str) -> Tuple[bool, Optional[str]]:
        """
        Inspects incoming user queries for known jailbreak, prompt leakage, or code probing attempts.
        Returns:
            (is_blocked: bool, refusal_message: Optional[str])
        """
        if not user_input:
            return False, None
            
        clean_text = user_input.strip()
        
        for pattern in _COMPILED_INPUT_PATTERNS:
            if pattern.search(clean_text):
                logger.warning(f"Security Alert: Blocked input matching probe/jailbreak pattern: '{pattern.pattern}'")
                return True, SAFE_REFUSAL_MESSAGE
                
        return False, None

    @staticmethod
    def filter_output(response_text: str) -> str:
        """
        Scans AI output or tool output before sending to the client/UI.
        If any internal code, file path, secret, or system instruction is found,
        it blocks the leak and returns a sanitized safe refusal.
        """
        if not response_text:
            return response_text
            
        for pattern in _COMPILED_OUTPUT_PATTERNS:
            match = pattern.search(response_text)
            if match:
                logger.warning(
                    f"Security Alert: Output Guardrail intercepted forbidden pattern: '{pattern.pattern}'. "
                    f"Snippet detected: '{match.group(0)[:60]}...'"
                )
                return SAFE_REFUSAL_MESSAGE
                
        return response_text

    @staticmethod
    def sanitize_error(error: Exception, context: str = "") -> str:
        """
        Logs detailed exception with traceback to server logs,
        while returning a clean, uninformative error string to callers/UI.
        """
        logger.error(f"Internal error occurred in {context}: {error}", exc_info=True)
        return SAFE_ERROR_MESSAGE


security_guardrails = SecurityGuardrails()
