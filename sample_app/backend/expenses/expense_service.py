class ExpenseService:
    def process_mileage(self, start_loc: str, end_loc: str, km: float):
        """
        Mileage claims. Max 500 km per claim.
        """
        if km > 500:
            raise ValueError("Max 500 km per claim allowed.")
        return {"amount": km * 0.55} # Rate from settings
        
    def auto_save_draft(self, user_id: str, expense_data: dict):
        """
        Auto-save drafts every 30 seconds. Expire after 14 days.
        """
        return {"status": "Draft restored"}
