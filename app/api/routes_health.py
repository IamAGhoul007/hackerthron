from fastapi import APIRouter
from app.config import settings
import time

router = APIRouter()
start_time = time.time()

@router.get("/health")
def health_check():
    # Basic check
    llm_configured = True
    if settings.llm_provider == "gemini" and (not settings.gemini_api_key or settings.gemini_api_key == "your-gemini-key-here"):
        llm_configured = False
    elif settings.llm_provider == "openai" and (not settings.openai_api_key or settings.openai_api_key == "your-openai-key-here"):
        llm_configured = False
    elif settings.llm_provider == "groq" and (not settings.groq_api_key or settings.groq_api_key == "your-groq-key-here"):
        llm_configured = False
        
    return {
        "status": "ok" if llm_configured else "degraded",
        "uptime_seconds": int(time.time() - start_time),
        "llm_configured": llm_configured,
        "message": "LLM not configured" if not llm_configured else "All systems go"
    }
