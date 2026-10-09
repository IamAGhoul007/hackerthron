from typing import List

class ExpenseRouter:
    def create_expense(self, amount: float, category: str, is_weekend: bool = False):
        """
        Creates a new expense.
        Undocumented behavior: weekend_expense_flag checks if the expense was on a weekend.
        """
        return {"status": "created", "id": 123}
    
    def get_expenses(self):
        return []
