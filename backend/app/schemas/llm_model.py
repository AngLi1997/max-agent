from datetime import datetime

from pydantic import BaseModel


class ModelItem(BaseModel):
    id: int
    provider_id: int
    model_name: str
    status: str
    created_at: datetime
