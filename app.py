import os
import logging
import asyncio
from typing import List, Optional
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, UploadFile, File, Query, Response
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from pydantic import BaseModel

from src.config import config
from src.core.assistant import AssistantCore
from src.services.whisper_service import groq_whisper_service
from src.services.tts_service import cloud_tts_service
from src.security.rate_limiter import rate_limiter

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("FastAPIServer")

app = FastAPI(
    title="Li's AI Portfolio Assistant",
    description="Interactive Web Interface powered by FastAPI, Groq Whisper, and Gemini AI",
    version="2.1.0"
)

def get_client_ip(request: Request) -> str:
    """Extracts client IP address supporting reverse proxies and Cloudflare/Render headers."""
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    real_ip = request.headers.get("x-real-ip")
    if real_ip:
        return real_ip.strip()
    return request.client.host if request.client else "127.0.0.1"

# Global exception handlers to prevent any stack trace or path disclosure
@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request: Request, exc: StarletteHTTPException):
    if exc.status_code == 404:
        return JSONResponse(status_code=404, content={"detail": "Resource not found."})
    if exc.status_code == 429:
        return JSONResponse(status_code=429, content={"detail": "Too many requests. Please slow down."})
    return JSONResponse(status_code=exc.status_code, content={"detail": "A server error occurred."})

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(status_code=422, content={"detail": "Invalid input provided."})

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled server exception: {exc}", exc_info=True)
    return JSONResponse(status_code=500, content={"detail": "An unexpected error occurred. Please try again."})

# Initialize Assistant Core
assistant = AssistantCore()

# Active WebSocket connections for real-time interaction
active_websockets: List[WebSocket] = []

# Mount static frontend assets
frontend_dir = os.path.join(os.path.dirname(__file__), "frontend")
if os.path.exists(frontend_dir):
    app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = "default_session"

class ChatResponse(BaseModel):
    response: str
    session_id: Optional[str] = None

@app.get("/", response_class=HTMLResponse)
async def serve_index():
    index_path = os.path.join(frontend_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return HTMLResponse(content="<h1>Li's AI Portfolio Assistant Server Running</h1>")

@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(request_obj: Request, body: ChatRequest):
    """
    REST endpoint for processing user chat messages.
    Features IP rate limiting and visitor-level conversation history isolation.
    """
    client_ip = get_client_ip(request_obj)
    allowed, retry_after = rate_limiter.is_allowed(client_ip, endpoint="chat", limit=30, window_seconds=60)
    if not allowed:
        logger.warning(f"Rate limit exceeded for IP: {client_ip} on /api/chat")
        return ChatResponse(
            response=f"You're sending queries a bit too quickly! Please pause for {retry_after} seconds before asking another question.",
            session_id=body.session_id
        )

    try:
        user_msg = body.message
        session_id = (body.session_id or "default_session").strip()
        logger.info(f"API Chat request from session: {session_id[:8]}...")
        bot_reply = await asyncio.to_thread(assistant.process_command, user_msg, session_id)
        return ChatResponse(response=bot_reply, session_id=session_id)
    except Exception as e:
        logger.error(f"Error in chat_endpoint: {e}", exc_info=True)
        return ChatResponse(
            response="I encountered an unexpected issue while processing your request. Please try again in a moment.",
            session_id=body.session_id
        )

class TranscribeResponse(BaseModel):
    success: bool
    text: str
    engine: str

@app.get("/api/transcribe/status")
async def transcribe_status():
    """Returns whether Groq cloud Whisper STT is available or if browser fallback should be used."""
    return {"whisper_available": groq_whisper_service.is_available()}

@app.post("/api/transcribe", response_model=TranscribeResponse)
async def transcribe_audio_endpoint(request: Request, file: UploadFile = File(...)):
    """
    Transcribes audio payload using Groq Whisper-large-v3 with domain vocabulary priming.
    Protected by IP rate limiting to prevent cloud quota abuse.
    """
    client_ip = get_client_ip(request)
    allowed, _ = rate_limiter.is_allowed(client_ip, endpoint="transcribe", limit=18, window_seconds=60)
    if not allowed:
        return TranscribeResponse(success=False, text="", engine="rate_limited")

    if not groq_whisper_service.is_available():
        return TranscribeResponse(success=False, text="", engine="fallback")

    try:
        audio_bytes = await file.read()
        if not audio_bytes or len(audio_bytes) < 100:
            return TranscribeResponse(success=False, text="", engine="groq_whisper")

        filename = file.filename or "recording.webm"
        text = await asyncio.to_thread(groq_whisper_service.transcribe, audio_bytes, filename=filename)
        if text:
            return TranscribeResponse(success=True, text=text, engine="groq_whisper")
        return TranscribeResponse(success=False, text="", engine="groq_whisper")
    except Exception as e:
        logger.error(f"Error in transcribe endpoint: {e}", exc_info=True)
        return TranscribeResponse(success=False, text="", engine="error")

@app.get("/api/tts")
async def stream_tts_audio(request: Request, text: str = Query(..., max_length=500)):
    """
    Streams server-synthesized MP3 audio for mobile visitors (iOS Safari & Android Chrome)
    where native browser SpeechSynthesis is blocked or sound quality is poor.
    """
    client_ip = get_client_ip(request)
    allowed, _ = rate_limiter.is_allowed(client_ip, endpoint="tts", limit=35, window_seconds=60)
    if not allowed:
        return Response(status_code=429, content=b"Rate limit exceeded.")

    if not text or not text.strip():
        return Response(status_code=400, content=b"Empty text parameter.")

    audio_bytes = await asyncio.to_thread(cloud_tts_service.synthesize_audio, text.strip())
    if not audio_bytes:
        return Response(status_code=500, content=b"TTS synthesis failed.")

    return Response(
        content=audio_bytes,
        media_type="audio/mpeg",
        headers={"Cache-Control": "public, max-age=3600"}
    )

@app.websocket("/ws/chat")
async def websocket_chat_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time bidirectional communication.
    Supports session isolation per connection.
    """
    await websocket.accept()
    active_websockets.append(websocket)
    session_id = f"ws_{id(websocket)}"
    logger.info(f"WebSocket client connected with session {session_id}.")
    try:
        while True:
            data = await websocket.receive_text()
            response_text = await asyncio.to_thread(assistant.process_command, data, session_id)
            await websocket.send_text(response_text)
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected: {session_id}")
    except Exception as e:
        logger.error(f"WebSocket error for {session_id}: {e}", exc_info=True)
    finally:
        if websocket in active_websockets:
            active_websockets.remove(websocket)

if __name__ == "__main__":
    import uvicorn
    port = config.PORT or 8000
    host = config.HOST or "0.0.0.0"
    uvicorn.run("app:app", host=host, port=port, reload=True)
