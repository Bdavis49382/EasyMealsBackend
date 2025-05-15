from pydantic import BaseModel
from models.Ingredient import Ingredient
from models.Record import Record

class Recipe(BaseModel):
    title: str
    permissions_required: str = "household"
    instructions: list[str]
    img_link: str
    author_id: str | None = None
    servings: float
    time_estimate: list[str]
    src_link: str = ""
    src_name: str | None = None
    ingredients: list[Ingredient]
    history: list[Record] = []

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
