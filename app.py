from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from .llm_engine import engine

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- CHANGED: Name must match the frontend key ---
class ChatRequest(BaseModel):
    prompt: str  # Changed from 'message' to 'prompt'

@app.post("/ask")
async def chat(request: ChatRequest):
    try:
        # Pass request.prompt to the engine
        bot_response = engine.generate_response(request.prompt)
        return {"response": bot_response}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
