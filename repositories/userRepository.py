from models.User import User, UserLite
from models.Recipe import Recipe, RecipeOut
from models.Record import Record
from firebase import user_ref
from fastapi import Depends
from typing import Annotated
from uuid import uuid4
from google.cloud.firestore_v1.collection import CollectionReference
from google.cloud.firestore_v1 import ArrayUnion, ArrayRemove
from google.cloud.firestore_v1.field_path import FieldPath


class UserRepository:
    def __init__(self, user_ref: Annotated[CollectionReference, Depends(user_ref)]):
        self.user_ref = user_ref

    def create_user(self, user: User) -> None:
        self.user_ref.document(user.google_id).set( user.model_dump())

    def get_user(self, user_id: str) -> User | None:
        user = self.user_ref.document(user_id).get().to_dict()
        try:
            return User.model_validate(user)
        except:
            return None
    
    def get_users(self,white_list: list[str] | None = None) -> list[User]:
        user_list = []
        if white_list != None:
            user_docs = self.user_ref.where(FieldPath.document_id(), "in", white_list)
        else:
            user_docs = self.user_ref.get()
        for user_data in user_docs:
            user_list.append(User.model_validate(user_data.to_dict()))
        return user_list

    def add_recipe(self, user_id: str, recipe: Recipe) -> str:
        recipe_id = uuid4().__str__()
        self.user_ref.document(user_id).update({
            f"recipes.{recipe_id}": recipe.model_dump()
        })
        return recipe_id

    def update_recipe(self, user_id: str, recipe_id: str, recipe: Recipe) -> str:
        self.user_ref.document(user_id).update({
            f"recipes.{recipe_id}": recipe.model_dump()
        })
        return recipe_id
    
    def get_user_recipes(self, user_id: str) -> list[RecipeOut]:
        user_data = self.user_ref.document(user_id).get().to_dict()
        recipes = []
        if user_data is not None and 'recipes' in user_data:
            for id, recipe in user_data['recipes'].items():
                recipe['id'] = id
                recipes.append(RecipeOut.model_validate(recipe))
        return recipes
    
    def search_user_recipes(self, user_id: str, keyword: str) -> list[RecipeOut]:
        return [x for x in self.get_user_recipes(user_id) if keyword.upper() in x.title.upper()]
    
    def add_recipe_record(self, user_id: str, recipe_id: str, record: Record) -> None:
        res = self.user_ref.document(user_id).update({
            f"recipes.{recipe_id}.history" : ArrayUnion([record.model_dump()])
        })

    