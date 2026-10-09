import json
from app.core.llm import get_llm_client
from app.core.prompts import QUERY_UNDERSTANDING_PROMPT

class QueryUnderstanding:
    def __init__(self):
        self.llm = get_llm_client()

    def understand(self, user_message: str, history: list) -> dict:
        prompt = QUERY_UNDERSTANDING_PROMPT.format(
            user_message=user_message,
            history=json.dumps(history)
        )
        
        response = self.llm.generate(prompt, response_format=dict)
        print(f"DEBUG QU RAW RESPONSE: {response}")
        try:
            # Simple json parsing
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))
            return json.loads(response)
        except:
            # Fallback
            return {
                "language": "en",
                "intent": "how_to",
                "rewrites": [user_message],
                "needs_clarification": False,
                "clarifying_question": None
            }
