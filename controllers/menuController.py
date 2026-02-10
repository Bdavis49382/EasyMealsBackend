from datetime import datetime, timezone, timedelta
from fastapi import Depends, HTTPException
from models.Record import Record
from models.Recipe import Recipe, MenuItemLite, RecipeOut, RecipeLite, MenuItemOut, MenuItem
from controllers.allRecipes import AllRecipes
from repositories.webRecipesRepository import RecipeData
from typing import Annotated
from repositories.householdRepository import HouseholdRepository
from repositories.userRepository import UserRepository
from repositories.webRecipesRepository import WebRecipesRepository

class MenuController:
    def __init__(self, 
                 repo: Annotated[HouseholdRepository, Depends()], 
                 user_repo: Annotated[UserRepository, Depends()], 
                 web_recipes_repo: Annotated[WebRecipesRepository, Depends()]):
        self.repo = repo
        self.user_repo = user_repo
        self.web_recipes_repo = web_recipes_repo

    def add_recipe(self, household_id, menu_item: MenuItem, user_id: str):
        # save the recipe first before adding it to the menu
        if menu_item.recipe_id is None:
            if menu_item.recipe is None:
                raise HTTPException(status_code=422, detail="either recipe or recipe_id is required to add recipe")
            menu_item.recipe.author_id = user_id
            recipe_id = self.user_repo.add_recipe(user_id, menu_item.recipe)
            menu_item.recipe_id = recipe_id
            menu_item.recipe = None
        menu_items = self.repo.get_menu_items(household_id)
        item = [x for x in menu_items if x.recipe_id == menu_item.recipe_id]
        if len(item) > 0:
            raise HTTPException(status_code=409, detail="That recipe is already added to the menu.")
        self.repo.add_recipe_to_menu(household_id, menu_item)
    
    def get_menu(self, household_id: str) -> list[MenuItemLite]:
        menu = self.repo.get_menu_items(household_id)
        out_list = []
        recipes = self._get_household_recipes(household_id)

        for menu_item in menu:
            if menu_item.recipe_id in recipes:
                recipe = recipes[menu_item.recipe_id]
                out_list.append(MenuItem.get_menu_item_lite(menu_item, recipe.img_link, recipe.title))

        return out_list
    
    def get_menu_item(self, household_id: str, index: int) -> MenuItemOut:
        menu_item = self.repo.get_menu_items(household_id)[index]
        menu_item = MenuItemOut.model_validate(menu_item.model_dump())
        recipe = self.get_recipe(household_id, menu_item.recipe_id)
        menu_item.recipe = recipe
        return menu_item
    
    def get_menu_item_by_recipe_id(self, household_id: str, recipe_id: str) -> MenuItemOut | None:
        menu_items = self.repo.get_menu_items(household_id)
        item = [x for x in menu_items if x.recipe_id == recipe_id]
        if len(item) != 1:
            return None
        menu_item =  MenuItemOut.model_validate(item[0].model_dump())
        recipe = self.get_recipe(household_id, menu_item.recipe_id)
        menu_item.recipe = recipe
        return menu_item


    def _get_household_recipes(self, household_id: str) -> dict[str,RecipeLite]:
        recipes = {}
        for user_id in self.repo.get_user_ids(household_id):
            recipes.update(self.user_repo.get_user_recipes(user_id))

        for recipe_id in recipes.keys():
            recipes[recipe_id] = RecipeLite.make_from_full(recipes[recipe_id])
        return recipes
        
    def get_recipe(self, household_id: str, recipe_id: str) -> RecipeOut | None:
        for user_id in self.repo.get_user_ids(household_id):
            recipes = self.user_repo.get_user_recipes(user_id)
            if recipe_id in recipes:
                return recipes[recipe_id]
        return None
    
    def get_recipe_online(self, link: str) -> Recipe:
        recipe_data: RecipeData = self.web_recipes_repo.get(link)
        if len(recipe_data.failures):
            print('failed to retrieve these items:',recipe_data.failures)
        return recipe_data.recipe
    
    def finish_recipe(self, household_id: str, recipe_id: str,rating: int | None = None) -> None:
        # remove from menu
        self.repo.remove_menu_item(household_id, recipe_id)

        #add a record for this interaction
        record = Record(household_id=household_id,timestamp=datetime.now(timezone.utc), rating = rating)
        recipe = self.get_recipe(household_id, recipe_id)
        if recipe == None:
            raise HTTPException(status_code=404,detail="Issue occurred with finding recipe to add rating to.")
        self.user_repo.add_recipe_record(recipe.author_id, recipe_id, record)

    def remove_menu_item(self, household_id: str, recipe_id: str) -> None:
        # remove from menu
        self.repo.remove_menu_item(household_id, recipe_id)

    def update_menu_item(self, household_id: str, index: int, updated: MenuItem) -> None:
        self.repo.update_menu_item(household_id, index, updated)

    def update_menu_item_by_recipe_id(self, household_id: str, recipe_id: str, updated: MenuItem) -> None:
        self.repo.update_menu_item_by_recipe_id(household_id, recipe_id, updated)