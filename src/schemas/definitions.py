from src.transformers.campaign_transformer import parse_us_date, parse_micros

meta_config = {
    "platform": {"default": "Meta"},
    "campaign": {"source": 0},
    "date_": {"source": 1, "transform": parse_us_date},
    "spend_usd": {"source": 2, "transform": float},
    "impressions": {"source": 3, "transform": int},
    "clicks": {"source": 4, "transform": int},
}

from datetime import datetime, timezone

def parse_epoch_ms_to_date(ts_ms: int) -> str:
    """Converts epoch milliseconds (e.g. 1780272000000) to YYYY-MM-DD format."""
    return datetime.fromtimestamp(ts_ms / 1000.0, tz=timezone.utc).strftime("%Y-%m-%d")

def convert_eur_to_usd(amount_str: str, eur_to_usd_rate: float = 1.08) -> float:
    """Converts amount string to float and applies currency conversion if needed."""
    amount = float(amount_str)
    return round(amount * eur_to_usd_rate, 2)

# Schema Config for nested JSON payload
abm_json_config = {
    "platform": {
        "default": "LinkedIn"  # Static fallback platform name
    },
    "campaign": {
        "source": "campaign"
    },
    "date": {
        "source": "date_ts",
        "transform": parse_epoch_ms_to_date
    },
    "spend_usd": {
        # Using lambda/function to extract nested 'amount' key from spend dictionary
        "source": "spend",
        "transform": lambda spend_dict: convert_eur_to_usd(spend_dict.get("amount", 0.0))
    },
    "impressions": {
        "source": "impressions",
        "transform": int
    },
    "clicks": {
        "source": "clicks",
        "transform": int
    }
}

google_ads_csv_config = {
    "platform": {
        "default": "Google"
    },
    "campaign": {
        "source": "Campaign"  # or index 0 if reading raw lists
    },
    "date": {
        "source": "Day"        # or index 1; YYYY-MM-DD is auto-parsed by Pydantic
    },
    "spend_usd": {
        "source": "Cost (micros)",  # or index 2
        "transform": parse_micros
    },
    "impressions": {
        "source": "Impr.",    # or index 4
        "transform": int
    },
    "clicks": {
        "source": "Clicks",    # or index 5
        "transform": int
    }
}
