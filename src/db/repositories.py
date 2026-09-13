import json
from pathlib import Path

# Resolve default path relative to this file: src/db/repositories.py -> root/data/exchange_rate.json
DEFAULT_RATES_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "exchange_rates.json"
class ExchangeRates:
    def __init__(self, filepath=DEFAULT_RATES_PATH):
        with open(filepath) as f:
            self.data = json.load(f)
        self.rates = self.data["rates"]

    def get_rate(self, date, to_currency):
        if to_currency == 'EUR':
            return float(self.rates.get('EUR', 1.08))
        return 1.0
