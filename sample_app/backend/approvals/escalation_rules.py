class EscalationRules:
    def check_escalation(self, expense_id: str, days_pending: int):
        """
        Escalates if pending for more than 7 days.
        """
        if days_pending > 7:
            return {"status": "escalated"}
        return {"status": "pending"}
