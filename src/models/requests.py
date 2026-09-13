from pydantic import BaseModel
from typing import Dict, Any, Optional

class IngestionRequest(BaseModel):
    delivery_id: str
    filepath: str
    file_format: str
    config: Optional[Dict[str, Any]] = None
