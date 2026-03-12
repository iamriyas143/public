# dashboard/backend/server.py
import json
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import os
from datetime import datetime
import random

app = FastAPI()

# --- CORS SETTINGS ---
origins = ["http://localhost:5173"]  # Vite dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- LOG FILE PATH ---
LOG_FILE = os.path.join(os.path.dirname(__file__), "../../backend/security_events.jsonl")

# --- CLIENT MANAGEMENT ---
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
        clients.discard(websocket)
        print("WebSocket disconnected")
    except Exception as e:
        clients.discard(websocket)
        print("WebSocket error:", e)

# --- TAIL LOG FILE ---
async def tail_file():
    """Monitor log file and push new lines to all clients."""
    if not os.path.exists(LOG_FILE):
        open(LOG_FILE, "w").close()

    with open(LOG_FILE, "r") as f:
        f.seek(0, os.SEEK_END)  # Start at end of file
        while True:
            line = f.readline()
            if line:
                # Broadcast to all connected clients
                for client in clients.copy():
                    try:
                        await client.send_text(line.strip())
                    except:
                        clients.discard(client)
            else:
                await asyncio.sleep(0.5)  # Wait before checking again

# --- OPTIONAL: FAKE LOG GENERATOR FOR TESTING ---
async def generate_fake_logs():
    """Generate fake log entries every 5 seconds (for testing)."""
    while True:
        fake_log = {
            "event_id": f"EVT-{random.randint(1000,9999)}",
            "timestamp": datetime.utcnow().isoformat(),
            "ip": f"192.168.0.{random.randint(1,255)}",
            "request": {
                "endpoint": f"/api/v{random.randint(1,3)}/data",
                "method": random.choice(["GET","POST"])
            },
            "detection": {
                "severity": random.choice(["Low","Medium","Critical"]),
                "attack_type": random.choice(["SQL Injection","XSS","Brute Force"]),
                "technique": random.choice(["Technique-A","Technique-B"]),
                "risk_score": random.randint(1,10),
                "confidence": round(random.uniform(0.5,1.0),2)
            },
            "response": {
                "action": random.choice(["Blocked","Allowed"])
            }
        }
        with open(LOG_FILE, "a") as f:
            f.write(json.dumps(fake_log) + "\n")
        await asyncio.sleep(5)

# --- START BACKGROUND TASKS ---
@app.on_event("startup")
async def startup_event():
    asyncio.create_task(tail_file())
    # Uncomment next line if you want fake logs for testing
    # asyncio.create_task(generate_fake_logs())
    print("Server started and tailing logs...")
