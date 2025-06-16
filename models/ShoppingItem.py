from pydantic import BaseModel
from datetime import datetime

class ShoppingItem(BaseModel):
    name: str
    checked: bool = False
    time_checked: datetime | None = None
    user_id: str | None = None
    recipe_id: str | None = None

class FullShoppingItem(BaseModel):
    name: str
    checked: bool = False
    time_checked: datetime | None = None
    user_initial: str
    recipe_title: str
    
class ShoppingItemOut(BaseModel):
    name: str
    checked: bool
    time_checked: datetime | None
    user_id: str
    user_initial: str
    recipe_id: str | None
    recipe_title: str | None
