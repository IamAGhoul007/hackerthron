class CurrencyService:
    def convert(self, amount: float, from_currency: str, to_currency: str):
        """
        Multi-currency expenses. Auto-conversion at the day's rate.
        Currency picker is hidden unless cost-center allows it.
        """
        if from_currency == to_currency:
            return amount
        return amount * 1.2 # Dummy conversion
