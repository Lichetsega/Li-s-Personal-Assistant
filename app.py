import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from pathlib import Path
from pydantic import BaseModel
from src.config import HOST, PORT, BASE_DIR
from src.core.assistant import AssistantOrchestrator

app = FastAPI(title="Li's AI Assistant API", version="1.0.0")

# Initialize central assistant orchestrator
assistant = AssistantOrchestrator()

# Serve static frontend files
frontend_dir = BASE_DIR / "frontend"
if frontend_dir.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_dir)), name="static")

class QueryRequest(BaseModel):
    query: str
    voice_mode: bool = False

@app.get("/")
async def get_index():
    index_file = frontend_dir / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return HTMLResponse("<h1>Li's AI Virtual Assistant API is running!</h1>")

@app.post("/api/chat")
async def chat_endpoint(req: QueryRequest):
    result = assistant.process_query(req.query, voice_mode=req.voice_mode)
    return result

@app.get("/api/notes")
async def list_notes_endpoint():
    return {"notes": assistant.knowledge_base.list_notes()}

@app.get("/api/memories")
async def list_memories_endpoint():
    return {"memories": [m.model_dump() for m in assistant.memory_store.get_all_memories()]}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            result = assistant.process_query(data, voice_mode=False)
            await websocket.send_json(result)
    except WebSocketDisconnect:
        print("[WebSocket] Client disconnected.")
    except Exception as e:
        print(f"[WebSocket] Error: {e}")

if __name__ == "__main__":
    print(f"🚀 Starting Li's Assistant FastAPI Server at http://{HOST}:{PORT}")
    uvicorn.run("app:app", host=HOST, port=PORT, reload=True)
