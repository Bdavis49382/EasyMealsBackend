from pydantic import BaseModel
from datetime import datetime
from uuid import uuid4

class ShoppingItem(BaseModel):
    name: str
    id: str | None = None
    checked: bool = False
    time_checked: datetime | None = None
    user_id: str | None = None
    recipe_id: str | None = None

class ShoppingItemOut(BaseModel):
    name: str
    id: str
    checked: bool
    time_checked: datetime | None
    user_id: str
    user_initial: str
    recipe_id: str | None
    recipe_title: str | None
