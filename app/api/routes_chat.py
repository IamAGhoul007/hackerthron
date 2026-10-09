from fastapi import APIRouter, HTTPException, Header, Depends
from typing import Optional
from app.core.schemas import ChatRequest, ChatResponse, FeedbackRequest
from app.engine.cascade import CascadeOrchestrator
from app.core.session import session_store
import uuid
import os
import json
import traceback

router = APIRouter()
orchestrator = CascadeOrchestrator()

from pathlib import Path
import difflib

CACHE_FILE = Path("data/cache/query_cache.jsonl")

def get_from_cache(query: str, threshold: float = 0.85) -> Optional[dict]:
    if not CACHE_FILE.exists():
        return None
    normalized_query = query.lower().strip()
    best_match = None
    best_ratio = 0.0
    with open(CACHE_FILE, "r", encoding="utf-8") as f:
        for line in f:
            try:
                entry = json.loads(line)
                cached_q = entry.get("query", "").lower().strip()
                if cached_q == normalized_query:
                    return entry.get("response")
                ratio = difflib.SequenceMatcher(None, normalized_query, cached_q).ratio()
                if ratio > best_ratio:
                    best_ratio = ratio
                    best_match = entry
            except:
                continue
    if best_ratio >= threshold and best_match:
        return best_match.get("response")
    return None

def save_to_cache(query: str, response: dict):
    CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(CACHE_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps({"query": query, "response": response}) + "\n")

@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    try:
        session_id = request.session_id or str(uuid.uuid4())
        request_id = str(uuid.uuid4())
        history = session_store.get_history(session_id)
        
        cached_resp = get_from_cache(request.message)
        if cached_resp:
            cached_resp["session_id"] = session_id
            cached_resp["request_id"] = request_id
            cached_resp["latency_ms"] = 0  # Indicate it was super fast
            response = ChatResponse(**cached_resp)
            session_store.add_turn(session_id, request.message, response.answer)
            return response
        
        response = orchestrator.process(session_id, request.message, history, request_id)
        
        save_to_cache(request.message, response.dict())
        
        session_store.add_turn(session_id, request.message, response.answer)
        return response
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {e}")

@router.post("/feedback")
def feedback(request: FeedbackRequest):
    log_dir = os.getenv("LOG_DIR", "./data/logs")
    os.makedirs(log_dir, exist_ok=True)
    with open(os.path.join(log_dir, "feedback.jsonl"), "a", encoding="utf-8") as f:
        f.write(json.dumps(request.dict()) + "\n")
    return {"status": "recorded"}
