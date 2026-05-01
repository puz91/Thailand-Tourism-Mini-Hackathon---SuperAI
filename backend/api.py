"""
Bangkok Transit RAG — FastAPI Backend
POST /api/chat  →  Agent Loop + Gemini
"""

import os, sys
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env'))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import os, sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai_core import BangkokRAGAgent, get_all_stations, get_all_categories

app = FastAPI(title="Bangkok Transit RAG API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        os.environ.get("FRONTEND_URL", ""),
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

_agent: Optional[BangkokRAGAgent] = None

def get_agent() -> BangkokRAGAgent:
    global _agent
    if _agent is None:
        _agent = BangkokRAGAgent()
    return _agent


class Message(BaseModel):
    role: str   # "user" | "assistant"
    content: str

class ChatRequest(BaseModel):
    message: str
    history: list[Message] = []

class ChatResponse(BaseModel):
    response: str
    places_found: list[dict] = []
    tools_used: list[dict] = []


@app.get("/")
def root():
    return {"status": "ok", "message": "Bangkok Transit RAG API 🚇"}

@app.get("/api/stations")
def list_stations():
    return {"stations": get_all_stations()}

@app.get("/api/categories")
def list_categories():
    return {"categories": get_all_categories()}

@app.post("/api/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    """
    Main endpoint — Agent Loop + Gemini
    Body: { "message": "อยากไปคาเฟ่แถวสยาม", "history": [...] }
    """
    if not req.message.strip():
        raise HTTPException(status_code=400, detail="message ต้องไม่ว่าง")
    try:
        agent = get_agent()
        history = [{"role": m.role, "content": m.content} for m in req.history]
        result = agent.chat(req.message, history=history)
        return ChatResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"เกิดข้อผิดพลาด: {str(e)}")

@app.get("/api/health")
def health():
    from ai_core.rag_engine import _FAISS_AVAILABLE
    return {
        "status": "healthy",
        "gemini_api_key_configured": bool(os.environ.get("GEMINI_API_KEY")),
        "faiss_available": _FAISS_AVAILABLE,
        "places_loaded": len(get_all_stations()),  # proxy สำหรับจำนวนสถานี
        "categories": get_all_categories(),
    }