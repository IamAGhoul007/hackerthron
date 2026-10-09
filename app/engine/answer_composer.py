from app.core.llm import get_llm_client
from app.core.prompts import ANSWER_FROM_JIRA_PROMPT, ANSWER_FROM_CODE_PROMPT, ESCALATION_NOTE_PROMPT

class AnswerComposer:
    def __init__(self):
        self.llm = get_llm_client()

    def compose(self, query: str, context: str, source_type: str) -> str:
        prompt_template = ANSWER_FROM_JIRA_PROMPT if source_type == "jira" else ANSWER_FROM_CODE_PROMPT
        prompt = prompt_template.format(context=context, query=query)
        return self.llm.generate(prompt)

    def compose_escalation(self, query: str, context: str) -> str:
        prompt = ESCALATION_NOTE_PROMPT.format(context=context, query=query)
        return self.llm.generate(prompt)
