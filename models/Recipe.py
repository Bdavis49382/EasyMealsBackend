from pydantic import BaseModel
from models.Ingredient import Ingredient
from models.Record import Record

class Recipe(BaseModel):
    title: str
    permissions_required: str | None
    instructions: list[str]
    img_link: str
    author_id: str
    servings: float
    time_estimate: list[str]
    src_link: str
    src_name: str
    ingredients: list[Ingredient]
    history: list[Record]

