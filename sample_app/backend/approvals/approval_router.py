class ApprovalRouter:
    def get_pending_approvals(self, user_id: str):
        return []
        
    def approve_expense(self, expense_id: str, user_id: str):
        return {"status": "approved"}
