from datetime import date as datetype
from pydantic import BaseModel, Field, NonNegativeInt, PositiveFloat
from typing import Optional, Union, Any, Callable, List

class CampaignMetric(BaseModel):
    platform: str = Field(..., min_length=1, description="Marketing platform (e.g., Google, Meta)")
    campaign: str = Field(..., min_length=1, description="Campaign name or ID")
    date: datetype = Field(..., description="Date of the campaign record (YYYY-MM-DD)")
    spend_usd: PositiveFloat = Field(..., ge=0.0, description="Spend in USD")
    impressions: NonNegativeInt = Field(..., description="Number of impressions")
    clicks: NonNegativeInt = Field(..., description="Number of clicks")


class FieldRule(BaseModel):
    source: Optional[Union[str, int]] = None
    default: Optional[Any] = None
    transform: Optional[Callable[[Any], Any]] = None
    dependencies: Optional[List[Union[str, int]]] = None
