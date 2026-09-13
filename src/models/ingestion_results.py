from typing import Any, List
from pydantic import BaseModel
from src.models.models import CampaignMetric


class TransformationError(BaseModel):
    line_number: int
    raw_record: Any
    error_type: str
    reason: str


class TransformationResult(BaseModel):
    metrics: List[CampaignMetric] = []
    errors: List[TransformationError] = []

    @property
    def has_errors(self) -> bool:
        return len(self.errors) > 0
