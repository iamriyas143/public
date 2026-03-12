# dashboard/backend/server.py
import json
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI()

# Allow your frontend origin
origins = ["http://localhost:5173"]  # Vite dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Path to security logs
LOG_FILE = os.path.join(os.path.dirname(__file__), "../../backend/security_events.jsonl")

# Manage connected websocket clients
clients = set()

@app.websocket("/ws/logs")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    clients.add(websocket)
    try:
        # On connection, send all existing logs
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, "r") as f:
                for line in f:
                    await websocket.send_text(line.strip())
        while True:
            # Keep connection alive
            await asyncio.sleep(10)
    except WebSocketDisconnect:
        clients.remove(websocket)

async def tail_file():
    """Monitor log file and push new lines to clients"""
    if not os.path.exists(LOG_FILE):
        open(LOG_FILE, "w").close()

    with open(LOG_FILE, "r") as f:
        f.seek(0, os.SEEK_END)  # Start at end of file
        while True:
            line = f.readline()
            if line:
                for client in clients.copy():
                    try:
                        await client.send_text(line.strip())
                    except:
                        clients.remove(client)
            else:
                await asyncio.sleep(0.5)  # Check every 0.5 sec

# Start background task
@app.on_event("startup")
async def startup_event():
    asyncio.create_task(tail_file())
