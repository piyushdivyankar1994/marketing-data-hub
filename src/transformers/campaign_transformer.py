from abc import ABC, abstractmethod
from typing import Any, Dict, Union
from src.models.models import CampaignMetric, FieldRule
from src.db.repositories import ExchangeRates
from datetime import datetime, timezone

class BaseTransformer(ABC):
    """Abstract base class for chunk-to-CampaignMetric transformers."""

    @abstractmethod
    def transform(self, chunk: Any) -> CampaignMetric:
        """Transforms a single record chunk into a validated CampaignMetric."""
        pass

# Type alias for schema configs
SchemaConfig = Dict[str, Union[FieldRule, dict]]
rates_service = ExchangeRates()

class ConfigurableCampaignTransformer:
    """A generic transformer that maps raw records (dict or list) into a CampaignMetric using a schema config."""

    def __init__(self, config: Dict[str, Dict[str, Any]]):
        """
        :param config: Dictionary defining field extraction rules.
                       Example:
                       {
                           "platform": {"default": "Meta"},
                           "campaign": {"source": "campaign_name"},
                           "date": {"source": "date", "transform": parse_date}
                       }
        """
        self.config = {
            field: rule if isinstance(rule, FieldRule) else FieldRule(**rule)
            for field, rule in config.items()
        }

    def _extract_value(self, raw_row: Union[Dict[str, Any], list, tuple], key: Union[str, int, None]) -> Any:
        if key is None:
            return None
        if isinstance(raw_row, dict):
            return raw_row.get(key)
        elif isinstance(raw_row, list) and isinstance(key, int):
            if 0 <= key < len(raw_row):
                return raw_row[key]
        return None

    def transform(self, chunk: Union[Dict[str, Any], list, tuple]) -> CampaignMetric:
        extracted: Dict[str, Any] = {}

        for target_field, rule in self.config.items():
            val = self._extract_value(chunk, rule.source)

            if val is None and rule.default is not None:
                val = rule.default

            dep_values = []
            if rule.dependencies:
                dep_values = [self._extract_value(chunk, dep) for dep in rule.dependencies]
            # 3. Apply custom field transformation if provided
            if rule.transform is not None and val is not None:
                if dep_values:
                    val = rule.transform(val, *dep_values)
                else:
                    val = rule.transform(val)

            extracted[target_field] = val

        # Pydantic validates types and coerces values automatically
        return CampaignMetric(**extracted)

def parse_us_date(date_str: str) -> str:
    """Parses MM/DD/YYYY into YYYY-MM-DD for Pydantic date parsing."""
    return datetime.strptime(date_str.strip(), "%m/%d/%Y").strftime("%Y-%m-%d")


def parse_currency(val: Any) -> float:
    """Cleans currency strings like '$200.08' or '200.08' into float."""
    if isinstance(val, str):
        val = val.replace("$", "").replace(",", "").strip()
    return float(val)

def parse_micros(val: Any, currency_code: Any="USD") -> float:
    """Converts cost in micros (e.g. 117410000) to standard USD (117.41)."""
    if val is None:
        return 0.0
    
    # 1. Convert micros to standard currency units
    amount = float(val) / 1_000_000.0
    curr = str(currency_code).upper() if currency_code else "USD"

    # 2. Convert to USD via ExchangeRates if needed
    if curr != "USD":
        rate = rates_service.get_rate(date=None, to_currency=curr)
        return round(amount * rate, 2)

    return round(amount, 2)

def parse_epoch_ms(val: Any) -> str:
    """Converts epoch timestamp in milliseconds (e.g. 1782691200000) to YYYY-MM-DD string."""
    if val is None:
        return ""
    # Convert to int/float if passed as a numeric string
    ts_ms = float(val)
    return datetime.fromtimestamp(ts_ms / 1000.0, tz=timezone.utc).strftime("%Y-%m-%d")

def parse_nested_spend(val: Any, currency: Any = None) -> float:
    """Extracts 'amount' from nested dictionary or numeric value and applies currency conversion to USD."""
    if val is None:
        return 0.0

    amount = 0.0
    currency_code = "USD"

    # Extract base amount and infer currency from nested dict if present
    if isinstance(val, dict):
        amount = float(val.get("amount", 0.0))
        currency_code = val.get("currency", "USD")
    elif isinstance(val, str):
        amount = float(val.replace("$", "").replace(",", "").strip())
    else:
        amount = float(val)

    # Override currency if passed explicitly via dependencies
    if currency is not None:
        if isinstance(currency, dict):
            currency_code = currency.get("currency", currency_code)
        elif isinstance(currency, str):
            currency_code = currency

    # Convert to USD using ExchangeRates if non-USD
    curr_upper = currency_code.upper()
    if curr_upper != "USD":
        rate = rates_service.get_rate(date=None, to_currency=curr_upper)
        return round(amount * rate, 2)

    return round(amount, 2)

TRANSFORM_FUNCTIONS = {
    "parse_us_date": parse_us_date,
    "parse_currency": parse_currency,
    "parse_micros": parse_micros,
    "parse_epoch_ms": parse_epoch_ms,
    "parse_nested_spend": parse_nested_spend,
    "float": float,
    "int": int,
}
