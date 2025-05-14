from pydantic import BaseModel

class Ingredient(BaseModel):
    amount: str
    name: str