from pydantic import BaseModel
from datetime import datetime
from models.Recipe import Recipe, MenuItem

class User(BaseModel):
    full_name: str
    google_id: str
    recipes: dict[str,Recipe] = {}

class JoinCode(BaseModel):
    code: str
    expiration_date: datetime

class ShoppingItem(BaseModel):
    name: str
    checked: bool = False
    time_checked: datetime | None = None
    user_id: str | None = None
    recipe_id: str | None = None

class ActiveItems(BaseModel):
    items: list[str] = []

class Household(BaseModel):
    id: str | None = None
    users: list[str] = []
    owner_id: str
    join_code: JoinCode | None = None
    menu_recipes: list[MenuItem] = []
    shopping_list: list[ShoppingItem] = []