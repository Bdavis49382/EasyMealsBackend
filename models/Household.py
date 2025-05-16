from pydantic import BaseModel
from datetime import datetime
from models.Recipe import Recipe

class User(BaseModel):
    full_name: str
    user_name: str
    google_id: str
    recipes: list[Recipe] = []

class JoinCode(BaseModel):
    code: str
    expiration_date: datetime

class MenuItem(Recipe):
    note: str
    date: datetime

class ShoppingItem(BaseModel):
    amount: str
    name: str
    checked: bool = False
    time_checked: datetime | None = None
    user_id: str | None = None
    recipe_id: str | None = None

class Household(BaseModel):
    users: list[str] = []
    join_code: JoinCode | None = None
    menu_recipes: list[MenuItem] = []
    shopping_list: list[ShoppingItem] = []