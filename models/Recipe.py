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



class MenuItemLite(BaseModel):
    note: str
    date: datetime | None = None
    recipe_id: str
    img_link: str
    title: str

class RecipeOut(BaseModel):
    # when coming out, recipe should have an id
    id: str | None = None
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

class RecipeLite(BaseModel):
    # Either an id or src_link is required to be able to retrieve the full recipe.
    id: str | None = None
    src_link: str | None = None
    history: list[Record] = []
    title: str
    img_link: str
    rate: float | None = None
    score: float | None = None
    @staticmethod
    def make_from_full(recipe: object):
        return RecipeLite(id=recipe.id, 
                          src_link = recipe.src_link, 
                          title = recipe.title, 
                          img_link= recipe.img_link,
                          history=recipe.history
                          )

class MenuItem(BaseModel):
    note: str = ''
    date: datetime | None = None
    active_items: list[str] = []
    # Should have either recipe_id or recipe
    recipe_id: str | None = None
    recipe: Recipe | None = None
    @staticmethod
    def get_menu_item_lite(menu_item: object, img_link: str, title: str):
        return MenuItemLite(
            note = menu_item.note,
            date = menu_item.date,
            recipe_id= menu_item.recipe_id,
            img_link=img_link,
            title=title
        )

class MenuItemOut(BaseModel):
    note: str = ''
    date: datetime | None = None
    active_items: list[str]
    # Should have either recipe_id or recipe
    recipe_id: str | None = None
    recipe: RecipeOut | None = None


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
