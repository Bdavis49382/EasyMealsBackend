from pydantic import BaseModel
from datetime import datetime
from models.Ingredient import Ingredient
from models.Record import Record

class Recipe(BaseModel):
    title: str
    permissions_required: str = "household"
    instructions: list[str]
    img_link: str
    author_id: str | None = None
    servings: str | None = None
    time_estimate: list[str] = [] #total time, prep time, cook time
    src_link: str = ""
    src_name: str | None = None
    ingredients: list[str]
    history: list[Record] = []
    @staticmethod
    def make_recipe_out(r: object, recipe_id: str):
        return Recipe(
            id=recipe_id,
            title=r.title,
            permissions_required =r.permissions_required,
            instructions= r.instructions,
            img_link= r.img_link,
            author_id = r.author_id,
            servings = r.servings,
            time_estimate= r.time_estimate,
            src_link = r.src_link,
            src_name = r.src_name,
            ingredients = r.ingredients,
            history = r.history
        )


class MenuItem(BaseModel):
    note: str = ''
    date: datetime | None = None
    active_items: list[str]
    # Should have either recipe_id or recipe
    recipe_id: str | None = None
    recipe: Recipe | None = None

class MenuItemOut(BaseModel):
    note: str
    date: datetime | None
    active_items: list[str]
    recipe: Recipe


class RecipeOut(BaseModel):
    # when coming out, recipe should have an id
    id: str
    title: str
    permissions_required: str
    instructions: list[str]
    img_link: str
    author_id: str
    servings: str | None
    time_estimate: list[str] #total time, prep time, cook time
    src_link: str
    src_name: str | None
    ingredients: list[str]
    history: list[Record]



# example
# {
#   "title": "cheeseburgers",
#   "permissions_required": "household",
#   "instructions": [
#     "form patties", "cook meat", "add toppings", "enjoy!"
#   ],
#   "img_link": "https://www.sargento.com/assets/Uploads/Recipe/Image/GreatAmericanBurger.jpg",
#   "servings": 4,
#   "time_estimate": [
#     "5","10"
#   ],
#   "ingredients": [
#     {
#       "amount": "1 lb",
#       "name": "ground beef"
#     }
#   ]
# }
