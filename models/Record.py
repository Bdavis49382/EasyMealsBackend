from pydantic import BaseModel
from datetime import datetime


class Record(BaseModel):
    household_id: str
    timestamp: datetime
    rating: int | None = None