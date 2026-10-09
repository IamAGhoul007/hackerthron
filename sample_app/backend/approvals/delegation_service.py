from datetime import datetime, timedelta

class DelegationService:
    def delegate_approvals(self, from_user: str, to_user: str, role: str, days: int):
        """
        Delegated approvals.
        Delegate must have role APPROVER.
        Delegation cannot exceed 30 days.
        Error DEL-422 for validation failures.
        """
        if role != "APPROVER":
            raise ValueError("Delegate must be an APPROVER. Error: DEL-422")
            
        if days > 30:
            raise ValueError("Delegation cannot exceed 30 days. Error: DEL-422")
            
        return {"status": "delegated", "expires_in": days}
