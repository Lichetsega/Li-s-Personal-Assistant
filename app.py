import os
import logging
import asyncio
from typing import List
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from pydantic import BaseModel

from src.config import config
from src.core.assistant import AssistantCore
from src.services.whisper_service import groq_whisper_service

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("FastAPIServer")

app = FastAPI(
    title="Li's AI Voice Assistant",
    description="Interactive Web Interface powered by FastAPI and Gemini AI",
    version="2.0.0"
)

# Global exception handlers to prevent any stack trace or path disclosure
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global unhandled exception on {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred. Please try again."}
    )

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail if exc.status_code < 500 else "An internal server error occurred."}
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.warning(f"Request validation error on {request.url.path}: {exc}")
    return JSONResponse(
        status_code=422,
        content={"detail": "Invalid request payload format."}
    )

# Initialize Assistant Engine
assistant = AssistantCore()

# Active WebSocket connections pool
active_websockets: List[WebSocket] = []

def notify_websockets_reminder(alert_msg: str):
    """Callback triggered when a proactive background reminder fires."""
    logger.info(f"Broadcasting proactive reminder alert: {alert_msg}")
    for ws in active_websockets:
        try:
            # Use asyncio to schedule send_text across active connections
            loop = asyncio.get_event_loop()
            if loop.is_running():
                asyncio.run_coroutine_threadsafe(ws.send_text(f"[PROACTIVE_REMINDER] {alert_msg}"), loop)
        except Exception as e:
            logger.error(f"Error sending proactive alert to WebSocket: {e}")

# Register reminder callback
assistant.register_reminder_callback(notify_websockets_reminder)

# Mount static frontend assets
frontend_dir = os.path.join(os.path.dirname(__file__), "frontend")
if os.path.exists(frontend_dir):
    app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str

@app.get("/", response_class=HTMLResponse)
async def serve_index():
    index_path = os.path.join(frontend_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return HTMLResponse(content="<h1>Gemini Voice Assistant Server Running</h1>")

@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    REST endpoint for processing user chat message and returning AI response.
    Guaranteed not to leak exceptions, file paths, or stack traces.
    """
    try:
        user_msg = request.message
        logger.info("API Chat request received.")
        bot_reply = assistant.process_command(user_msg)
        return ChatResponse(response=bot_reply)
    except Exception as e:
        logger.error(f"Error in chat_endpoint: {e}", exc_info=True)
        return ChatResponse(response="I encountered an unexpected issue while processing your request. Please try again.")

class TranscribeResponse(BaseModel):
    success: bool
    text: str
    engine: str

@app.get("/api/transcribe/status")
async def transcribe_status():
    """Returns whether Groq cloud Whisper STT is available or if browser fallback should be used."""
    return {"whisper_available": groq_whisper_service.is_available()}

@app.post("/api/transcribe", response_model=TranscribeResponse)
async def transcribe_audio_endpoint(file: UploadFile = File(...)):
    """
    Transcribes audio payload using Groq Whisper-large-v3 with domain vocabulary priming.
    """
    if not groq_whisper_service.is_available():
        return TranscribeResponse(success=False, text="", engine="fallback")

    try:
        audio_bytes = await file.read()
        if not audio_bytes or len(audio_bytes) < 100:
            return TranscribeResponse(success=False, text="", engine="groq_whisper")

        filename = file.filename or "recording.webm"
        text = groq_whisper_service.transcribe(audio_bytes, filename=filename)
        if text:
            return TranscribeResponse(success=True, text=text, engine="groq_whisper")
        return TranscribeResponse(success=False, text="", engine="groq_whisper")
    except Exception as e:
        logger.error(f"Error in transcribe endpoint: {e}", exc_info=True)
        return TranscribeResponse(success=False, text="", engine="error")

@app.websocket("/ws/chat")
async def websocket_chat_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time bidirectional audio/text communication & proactive alerts.
    """
    await websocket.accept()
    active_websockets.append(websocket)
    logger.info("WebSocket client connected.")
    try:
        while True:
            data = await websocket.receive_text()
            logger.info("WS message received.")
            try:
                reply = assistant.process_command(data)
                await websocket.send_text(reply)
            except Exception as e:
                logger.error(f"Error in WebSocket process_command: {e}", exc_info=True)
                await websocket.send_text("I encountered an unexpected issue while processing your request. Please try again.")
    except WebSocketDisconnect:
        if websocket in active_websockets:
            active_websockets.remove(websocket)
        logger.info("WebSocket client disconnected.")
    except Exception as e:
        if websocket in active_websockets:
            active_websockets.remove(websocket)
        logger.error(f"WebSocket connection error: {e}")

if __name__ == "__main__":
    import uvicorn
    logger.info(f"Starting Gemini Voice Assistant server at http://{config.HOST}:{config.PORT}")
    uvicorn.run("app:app", host=config.HOST, port=config.PORT, reload=config.DEBUG)
