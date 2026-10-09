import time
import os
from typing import Dict, List

class SessionManager:
    def __init__(self):
        self.sessions: Dict[str, Dict] = {}
        self.ttl = int(os.getenv("SESSION_TTL_MINUTES", "60")) * 60
        self.max_turns = int(os.getenv("MAX_HISTORY_TURNS", "6"))

    def get_history(self, session_id: str) -> List[Dict]:
        self._cleanup()
        if session_id in self.sessions:
            self.sessions[session_id]['last_accessed'] = time.time()
            return self.sessions[session_id]['history']
        return []

    def add_turn(self, session_id: str, user_msg: str, assistant_msg: str):
        if session_id not in self.sessions:
            self.sessions[session_id] = {'history': [], 'last_accessed': time.time()}
        
        self.sessions[session_id]['history'].append({'user': user_msg, 'assistant': assistant_msg})
        if len(self.sessions[session_id]['history']) > self.max_turns:
            self.sessions[session_id]['history'].pop(0)
            
        self.sessions[session_id]['last_accessed'] = time.time()

    def _cleanup(self):
        now = time.time()
        to_delete = [sid for sid, data in self.sessions.items() if now - data['last_accessed'] > self.ttl]
        for sid in to_delete:
            del self.sessions[sid]

session_store = SessionManager()
