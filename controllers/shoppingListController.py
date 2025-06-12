from firebase import db
from datetime import datetime, timezone, timedelta
from google.cloud.firestore_v1 import ArrayUnion
from models.ShoppingItem import ShoppingItem, ShoppingItemOut
from controllers.userController import UserController
from controllers.menuController import MenuController
from repositories.householdRepository import HouseholdRepository
from repositories.userRepository import UserRepository
from typing import Annotated
from fastapi import Depends

class ShoppingListController:
    def __init__(self, repo: Annotated[HouseholdRepository, Depends()], user_repo: Annotated[UserRepository, Depends()]):
        self.repo = repo
        self.user_repo = user_repo

    def get_shopping_list(self, household_id: str) -> list[ShoppingItemOut]:
        shopping_list = self.repo.get_shopping_list(household_id)
        return self.convert_list(household_id, shopping_list)
    
    def convert_list(self,household_id: str, shopping_list: list[ShoppingItem]) -> list[ShoppingItemOut]:
        user_cache = {}
        recipe_cache = {}
        out_list = []
        for item in shopping_list:
            if item.user_id not in user_cache:
                user = self.user_repo.get_user(item.user_id)
                user_cache[item.user_id] = user
            else:
                user = user_cache[item.user_id]
            user_initial = user.full_name[0]

            if item.recipe_id is not None:
                if item.recipe_id not in recipe_cache:
                    recipe = self.user_repo.find_user_recipe(self.repo.get_user_ids(household_id), item.recipe_id)
                    recipe_cache[item.recipe_id] = recipe
                else:
                    recipe = recipe_cache[item.recipe_id]

                if recipe is not None:
                    recipe_title = recipe.title
                else:
                    recipe_title = recipe.title
            else:
                recipe_title = ""
            out_list.append(ShoppingItemOut(
                name = item.name, 
                checked=item.checked, 
                time_checked=item.time_checked,
                user_id = item.user_id,
                user_initial= user_initial,
                recipe_id= item.recipe_id,
                recipe_title= recipe_title
                ))
        return out_list

    def clean_list(self,household_id: str) -> None:
        menu = self.repo.get_household(household_id).menu_recipes
        menu_ids = [x.recipe_id for x in menu]

        def item_is_valid(item):
            # if an item has been checked for more than 12 hours, remove it from the list
            if 'time_checked' in item and item['time_checked'] is not None:
                if datetime.now(timezone.utc) - item['time_checked'] > timedelta(hours=12):
                    return False
            if 'recipe_id' in item and item['recipe_id'] != None and  item['recipe_id'] not in menu_ids:
                return False
            return True
        
        self.repo.remove_items(household_id, item_is_valid)
        

    def add_item(self, household_id, shopping_item: ShoppingItem) -> None:
        self.repo.add_item(household_id, shopping_item)
    
    def add_items(self, household_id, shopping_items: list[ShoppingItem]) -> None:
        self.repo.add_items(household_id, shopping_items)

    def check_item(self, household_id : str, index: int) -> None:
        self.repo.check_item(household_id, index)

    def edit_item(self, household_id: str, index: int, shopping_item: ShoppingItem) -> None:
        self.repo.update_item(household_id, index, shopping_item)

    def remove_item(self, household_id: str, index: int) -> None:
        self.repo.remove_item(household_id, index)

    def add_shopping_strings(self, household_id,item_strings: list[str], user_id: str, recipe_id: str) -> list[ShoppingItem]:
        return self.add_items(household_id,[ShoppingItem(name=name, user_id=user_id, recipe_id=recipe_id) for name in item_strings])