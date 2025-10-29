from pydantic import BaseModel
from models.Recipe import Recipe

class UserLite(BaseModel):
    full_name: str
    id: str
    recipes: str

class User(BaseModel):
    full_name: str
    google_id: str
    recipes: dict[str,Recipe] = {}
    suggestions: set[str] = set()

    @staticmethod
    def make_user_lite( user: object) -> UserLite:
        return UserLite(
            full_name=user.full_name, 
            id=user.google_id,
            recipes= f"{len(user.recipes)} recipes")
