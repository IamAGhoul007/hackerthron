from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class Source(BaseModel):
    type: str # "jira" or "code"
    id: Optional[str] = None # Ticket ID
    title: Optional[str] = None
    fix_version: Optional[str] = None
    path: Optional[str] = None # File path for code
    lines: Optional[str] = None
    snippet: str
    score: float

class MismatchDetail(BaseModel):
    detected: bool
    explanation: Optional[str] = None

class ChatRequest(BaseModel):
    session_id: Optional[str] = None
    message: str = Field(..., min_length=1, max_length=2000)

class ChatResponse(BaseModel):
    session_id: str
    answer: str
    route: str # "jira | code | jira+code | not_found | clarification | refused"
    confidence: float
    sources: List[Source]
    possible_mismatch: MismatchDetail
    escalation_note: Optional[str] = None
    follow_up_suggestions: List[str] = []
    latency_ms: int = 0
    request_id: str

class FeedbackRequest(BaseModel):
    request_id: str
    helpful: bool
    comment: Optional[str] = None
