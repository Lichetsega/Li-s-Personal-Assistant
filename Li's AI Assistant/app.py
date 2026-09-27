import os
import logging
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel

from src.config import config
from src.core.assistant import AssistantCore

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("FastAPIServer")

app = FastAPI(
    title="Gemini AI Voice Assistant",
    description="Interactive Web Interface powered by FastAPI and Gemini AI",
    version="1.0.0"
)

# Initialize Assistant Engine
assistant = AssistantCore()

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
    WebSocket endpoint for real-time bidirectional audio/text communication.
    """
    await websocket.accept()
    logger.info("WebSocket client connected.")
    try:
        while True:
            data = await websocket.receive_text()
            logger.info(f"WS Received: {data}")
            reply = assistant.process_command(data)
            await websocket.send_text(reply)
    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected.")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")

if __name__ == "__main__":
    import uvicorn
    logger.info(f"Starting Gemini Voice Assistant server at http://{config.HOST}:{config.PORT}")
    uvicorn.run("app:app", host=config.HOST, port=config.PORT, reload=config.DEBUG)
