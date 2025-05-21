from pydantic import BaseModel
from datetime import datetime


class Record(BaseModel):
    household_id: str
    timestamp: datetime
    rating: float | None = None