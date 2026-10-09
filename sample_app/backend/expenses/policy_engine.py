class PolicyEngine:
    def check_limits(self, category: str, amount: float, city_tier: int, has_justification: bool):
        """
        Policy limit warnings. 
        Soft warning at 80% of category limit.
        Hard block at 100% unless Justification is added.
        Meal limit differs by city tier.
        Error EXP-1042 for limit exceeded without justification.
        """
        limit = 100.0 if city_tier == 1 else 50.0
        
        if amount > limit:
            if not has_justification:
                raise ValueError("Limit exceeded. Error: EXP-1042")
            return {"status": "approved_with_justification"}
        elif amount >= limit * 0.8:
            return {"status": "warning", "message": "Approaching limit"}
            
        return {"status": "ok"}
