import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, timezone

from src.models.models import CampaignMetric, FieldRule
from src.transformers.campaign_transformer import (
    ConfigurableCampaignTransformer,
    parse_us_date,
    parse_currency,
    parse_micros,
    parse_epoch_ms,
    parse_nested_spend,
    TRANSFORM_FUNCTIONS,
)


# ==========================================
# Standalone Helper Function Tests
# ==========================================

def test_parse_us_date():
    assert parse_us_date("06/07/2026") == "2026-06-07"
    assert parse_us_date(" 12/31/2025 ") == "2025-12-31"


def test_parse_currency():
    assert parse_currency("$200.08") == 200.08
    assert parse_currency("1,250.50") == 1250.50
    assert parse_currency(100.5) == 100.5


@patch("src.transformers.campaign_transformer.rates_service")
def test_parse_micros(mock_rates):
    mock_rates.get_rate.return_value = 1.08

    # Default USD test (no conversion applied)
    assert parse_micros(117410000, "USD") == 117.41
    assert parse_micros(None) == 0.0

    # Foreign currency EUR test (100000000 micros = 100.0 * 1.08 = 108.0)
    assert parse_micros(100000000, "EUR") == 108.0
    mock_rates.get_rate.assert_called_with(date=None, to_currency="EUR")


def test_parse_epoch_ms():
    assert parse_epoch_ms(1782691200000) == "2026-06-29"
    assert parse_epoch_ms("1782691200000") == "2026-06-29"
    assert parse_epoch_ms(None) == ""


@patch("src.transformers.campaign_transformer.rates_service")
def test_parse_nested_spend(mock_rates):
    mock_rates.get_rate.return_value = 1.08

    # 1. Standard USD numeric value
    assert parse_nested_spend(150.0) == 150.0
    assert parse_nested_spend("$150.00") == 150.0
    assert parse_nested_spend(None) == 0.0

    # 2. Nested Dict with EUR inside
    dict_val = {"amount": "100.00", "currency": "EUR"}
    assert parse_nested_spend(dict_val) == 108.0

    # 3. Explicit currency string passed via dependency
    assert parse_nested_spend(100.0, currency="EUR") == 108.0

    # 4. Explicit currency dict passed via dependency
    assert parse_nested_spend(100.0, currency={"currency": "EUR"}) == 108.0


def test_transform_functions_registry():
    assert "parse_us_date" in TRANSFORM_FUNCTIONS
    assert "parse_nested_spend" in TRANSFORM_FUNCTIONS
    assert TRANSFORM_FUNCTIONS["int"] == int


# ==========================================
# ConfigurableCampaignTransformer Class Tests
# ==========================================

class TestConfigurableCampaignTransformer:

    def test_init_with_dict_and_fieldrules(self):
        config = {
            "platform": {"default": "Meta"},
            "campaign": FieldRule(source="campaign_name"),
        }
        transformer = ConfigurableCampaignTransformer(config)
        
        assert isinstance(transformer.config["platform"], FieldRule)
        assert transformer.config["platform"].default == "Meta"
        assert isinstance(transformer.config["campaign"], FieldRule)

    def test_extract_value_dict_and_list(self):
        transformer = ConfigurableCampaignTransformer({})
        row_dict = {"name": "Campaign A"}
        row_list = ["Campaign B", "2026-06-01"]

        assert transformer._extract_value(row_dict, "name") == "Campaign A"
        assert transformer._extract_value(row_dict, "missing") is None
        assert transformer._extract_value(row_list, 0) == "Campaign B"
        assert transformer._extract_value(row_list, 5) is None  # Out of bounds
        assert transformer._extract_value(row_list, None) is None

    def test_transform_dict_input(self):
        config = {
            "platform": {"default": "Meta"},
            "campaign": {"source": "campaign_name"},
            "date": {"source": "date_str", "transform": parse_us_date},
            "spend_usd": {"source": "cost", "transform": parse_currency},
            "impressions": {"source": "imprs", "transform": int},
            "clicks": {"source": "clicks", "transform": int},
        }
        transformer = ConfigurableCampaignTransformer(config)

        raw_record = {
            "campaign_name": "Summer Sale",
            "date_str": "06/07/2026",
            "cost": "$150.50",
            "imprs": "1000",
            "clicks": "50",
        }

        result = transformer.transform(raw_record)

        assert isinstance(result, CampaignMetric)
        assert result.platform == "Meta"
        assert result.campaign == "Summer Sale"
        assert str(result.date) == "2026-06-07"
        assert result.spend_usd == 150.50
        assert result.impressions == 1000
        assert result.clicks == 50

    @patch("src.transformers.campaign_transformer.rates_service")
    def test_transform_list_input_with_dependencies(self, mock_rates):
        mock_rates.get_rate.return_value = 1.08

        # Schema mapping for CSV rows: Campaign, Day, Cost(micros), Currency, Impr, Clicks
        config = {
            "platform": {"default": "Google"},
            "campaign": {"source": 0},
            "date": {"source": 1},
            "spend_usd": {
                "source": 2,
                "dependencies": [3],
                "transform": parse_micros,
            },
            "impressions": {"source": 4, "transform": int},
            "clicks": {"source": 5, "transform": int},
        }
        transformer = ConfigurableCampaignTransformer(config)

        raw_csv_row = ["Search - Brand", "2026-06-07", 100000000, "EUR", 5000, 200]
        result = transformer.transform(raw_csv_row)

        assert isinstance(result, CampaignMetric)
        assert result.platform == "Google"
        assert result.campaign == "Search - Brand"
        assert str(result.date) == "2026-06-07"
        # 100000000 micros = 100 EUR * 1.08 = 108.0 USD
        assert result.spend_usd == 108.0
        assert result.impressions == 5000
        assert result.clicks == 200
