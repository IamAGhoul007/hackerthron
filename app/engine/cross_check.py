import json
from app.core.llm import get_llm_client
from app.core.prompts import CROSS_CHECK_PROMPT

class CrossCheck:
    def __init__(self):
        self.llm = get_llm_client()

    def compare(self, jira_results: list, code_results: list) -> dict:
        if not jira_results or not code_results:
            return {"consistent": True, "difference": None, "user_facing_guidance": None, "confidence": 1.0}
            
        jira_context = "\n".join([r['document'] for r in jira_results[:3]])
        code_context = "\n".join([r['document'] for r in code_results[:3]])
        
        prompt = CROSS_CHECK_PROMPT.format(jira_context=jira_context, code_context=code_context)
        response = self.llm.generate(prompt, response_format=dict)
        
        try:
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))
            return json.loads(response)
        except:
            return {"consistent": True, "difference": None, "user_facing_guidance": None, "confidence": 1.0}
