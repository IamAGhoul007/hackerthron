import os
from typing import List, Dict

def compute_confidence(results: List[Dict]) -> float:
    if not results:
        return 0.0
        
    # Simple normalization: max score from RRF
    # Real implementations might use a calibrated model or cross-encoder
    max_score = results[0]["score"]
    
    # Heuristic: RRF scores are usually small. We map [0, ~0.1] to [0, 1]
    confidence = min(max_score * 10, 1.0)
    return float(confidence)

def check_confidence(confidence: float, source: str) -> bool:
    if source == "jira":
        threshold = float(os.getenv("JIRA_CONFIDENCE_THRESHOLD", "0.55"))
    else:
        threshold = float(os.getenv("CODE_CONFIDENCE_THRESHOLD", "0.50"))
    return confidence >= threshold
