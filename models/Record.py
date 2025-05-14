from pydantic import BaseModel
from datetime import datetime

class Rating(BaseModel):
    user_id: str
    value: int

class Record(BaseModel):
    household_id: str
    timestamp: datetime
    rating: Rating