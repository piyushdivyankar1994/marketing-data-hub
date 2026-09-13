from enum import Enum
from typing import Any, Dict, List
from datetime import datetime
from pydantic import BaseModel, Field


class CheckScope(str, Enum):
    ROW = "ROW"
    FILE = "FILE"
    DELIVERY = "DELIVERY"


class CheckStatus(str, Enum):
    PASSED = "PASSED"
    WARNING = "WARNING"
    FAILED = "FAILED"


class HealthStatus(str, Enum):
    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    CRITICAL = "CRITICAL"


class QualityCheckResult(BaseModel):
    check_id: str = Field(..., description="Unique code for the check (e.g., ROW_VALIDITY)")
    name: str
    scope: CheckScope
    status: CheckStatus
    message: str
    details: Dict[str, Any] = Field(default_factory=dict)


class SummaryMetrics(BaseModel):
    total_records_processed: int = 0
    valid_records_count: int = 0
    error_records_count: int = 0
    error_rate_percentage: float = 0.0
    duplicate_rows_count: int = 0
    total_spend_usd: float = 0.0


class StructuredQualityReport(BaseModel):
    delivery_id: str
    processed_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    health_status: HealthStatus
    summary: SummaryMetrics
    checks_executed: List[QualityCheckResult] = []
    sample_failures: List[Dict[str, Any]] = []
