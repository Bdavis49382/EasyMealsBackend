from models.User import User
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

    def create_user(self, user: User) -> str:
        self.user_ref.document(user.google_id).set( user.model_dump())
        return user.google_id

    def get_user(self, user_id: str) -> User | None:
        user = self.user_ref.document(user_id).get().to_dict()
        try:
            return User.model_validate(user)
        except:
            return None

    
    def get_users(self,white_list: list[str] | None = None) -> list[User]:
        user_list = {}
        if white_list != None:
            user_docs = self.user_ref.where(FieldPath.document_id(), "in", white_list).get()
        else:
            user_docs = self.user_ref.get()
        for user_data in user_docs:
            user_list[user_data.id] = User.model_validate(user_data.to_dict())
        if white_list != None:
            # if there is a white list, we want to return the values in the same order they were in the list.
            return [user_list[x] for x in white_list]
        else:
            return list(user_list.values())

    def add_recipe(self, user_id: str, recipe: Recipe) -> str:
        recipe_id = uuid4().__str__()
        self.user_ref.document(user_id).update({
            f"recipes.{recipe_id}": recipe.model_dump()
        })
        return recipe_id
    
    def find_user_recipe(self, user_ids: list[str], recipe_id: str) -> RecipeOut | None:
        users = self.get_users(user_ids)
        user = [x for x in users if recipe_id in x.recipes.keys()]
        if len(user) == 1:
            return Recipe.make_recipe_out(user[0].recipes[recipe_id], recipe_id)
        else:
            return None


    def update_recipe(self, user_id: str, recipe_id: str, recipe: Recipe) -> str:
        self.user_ref.document(user_id).update({
            f"recipes.{recipe_id}": recipe.model_dump()
        })
        return recipe_id
    
    def get_user_recipes(self, user_id: str) -> dict[str,RecipeOut]:
        user_data = self.user_ref.document(user_id).get().to_dict()
        recipes = {}
        if user_data is not None and 'recipes' in user_data:
            for id, recipe in user_data['recipes'].items():
                recipe['id'] = id
                recipes[id] = RecipeOut.model_validate(recipe)
        return recipes

    def get_user_tags(self, user_id: str) -> set[str]:
        user = self.get_user(user_id)
        # flatten tags lists
        return set([tag for r in user.recipes.values() for tag in r.tags])
    
    def search_user_recipes(self, user_id: str, keyword: str) -> list[RecipeOut]:
        return [x for x in self.get_user_recipes(user_id).values() if keyword.upper() in x.title.upper()]
    
    def add_recipe_record(self, user_id: str, recipe_id: str, record: Record) -> None:
        res = self.user_ref.document(user_id).update({
            f"recipes.{recipe_id}.history" : ArrayUnion([record.model_dump()])
        })

    