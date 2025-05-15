from pydantic import BaseModel
from datetime import datetime
from models.Recipe import Recipe

class User(BaseModel):
    full_name: str
    user_name: str
    google_id: str

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
    time_checked: datetime = None
    user_id: str = None
    recipe_id: str = None

class Household(BaseModel):
    users: list[str] = []
    join_code: JoinCode = None
    menu_recipes: list[MenuItem] = []
    shopping_list: list[ShoppingItem] = []