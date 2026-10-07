import os
import logging
import asyncio
from typing import List
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel

from src.config import config
from src.core.assistant import AssistantCore

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("FastAPIServer")

app = FastAPI(
    title="Li's AI Voice Assistant",
    description="Interactive Web Interface powered by FastAPI and Gemini AI",
    version="2.0.0"
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
    """
    user_msg = request.message
    logger.info(f"API Chat request received: '{user_msg}'")
    bot_reply = assistant.process_command(user_msg)
    return ChatResponse(response=bot_reply)

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
            logger.info(f"WS Received: {data}")
            reply = assistant.process_command(data)
            await websocket.send_text(reply)
    except WebSocketDisconnect:
        if websocket in active_websockets:
            active_websockets.remove(websocket)
        logger.info("WebSocket client disconnected.")
    except Exception as e:
        if websocket in active_websockets:
            active_websockets.remove(websocket)
        logger.error(f"WebSocket error: {e}")

if __name__ == "__main__":
    import uvicorn
    logger.info(f"Starting Gemini Voice Assistant server at http://{config.HOST}:{config.PORT}")
    uvicorn.run("app:app", host=config.HOST, port=config.PORT, reload=config.DEBUG)
