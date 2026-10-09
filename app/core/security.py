import os
import re
from typing import Optional

# Pre-compile regex for redaction
SECRET_PATTERNS = [
    re.compile(r'(?i)(api[_-]?key|secret|password|token)\s*[:=]\s*["\'][^"\']+["\']'),
    re.compile(r'BEGIN RSA PRIVATE KEY'),
]

def redact_secrets(text: str) -> str:
    """Redacts secrets from strings before ingestion."""
    text = SECRET_PATTERNS[0].sub(r'\1: "***REDACTED***"', text)
    text = SECRET_PATTERNS[1].sub(r'***REDACTED***', text)
    return text

def screen_prompt_injection(user_input: str) -> bool:
    """Returns True if the input looks like prompt injection."""
    user_input = user_input.lower()
    unsafe_phrases = [
        "ignore previous instructions",
        "reveal system prompt",
        "output your instructions",
        "system prompt",
        "new rule:"
    ]
    for phrase in unsafe_phrases:
        if phrase in user_input:
            return True
    return False

def safe_path_join(base: str, path: str) -> Optional[str]:
    """Ensures path traversal isn't possible."""
    base_abs = os.path.abspath(base)
    target_abs = os.path.abspath(os.path.join(base, path))
    if not target_abs.startswith(base_abs):
        return None
    return target_abs
