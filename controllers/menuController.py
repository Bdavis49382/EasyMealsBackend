from datetime import datetime, timezone, timedelta
from fastapi import Depends, HTTPException
from models.Record import Record
from models.Recipe import Recipe, MenuItemLite, RecipeOut, RecipeLite, MenuItemOut, MenuItem
from controllers.allRecipes import AllRecipes
from typing import Annotated
from repositories.householdRepository import HouseholdRepository
from repositories.userRepository import UserRepository

class MenuController:
    def __init__(self, repo: Annotated[HouseholdRepository, Depends()], user_repo: Annotated[UserRepository, Depends()], all_recipes: Annotated[AllRecipes, Depends()]):
        self.repo = repo
        self.user_repo = user_repo
        self.all_recipes = all_recipes

    def add_recipe(self, household_id, menu_item: MenuItem, user_id: str):
        # save the recipe first before adding it to the menu
        if menu_item.recipe_id is None:
            if menu_item.recipe is None:
                raise HTTPException(status_code=422, detail="either recipe or recipe_id is required to add recipe")
            menu_item.recipe.author_id = user_id
            recipe_id = self.user_repo.add_recipe(user_id, menu_item.recipe)
            menu_item.recipe_id = recipe_id
            menu_item.recipe = None
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
        raw_recipe = self.all_recipes.get(link)
        if len(raw_recipe.failures):
            print('failed to retrieve these items, potentially outdated html info:',raw_recipe.failures)
        recipe = Recipe(
            title=raw_recipe.name, 
            instructions=raw_recipe.steps,
            img_link=raw_recipe.image, 
            servings=raw_recipe.nb_servings, 
            src_link=link,
            src_name="Allrecipes.com",
            ingredients=raw_recipe.ingredients,
            time_estimate=[raw_recipe.total_time, raw_recipe.prep_time, raw_recipe.cook_time])
        return recipe
    
    def finish_recipe(self, household_id: str, recipe_id: str, user_id : str, rating: int | None = None) -> None:
        # remove from menu
        self.repo.remove_menu_item(household_id, recipe_id)

        #add a record for this interaction
        record = Record(household_id=household_id,timestamp=datetime.now(timezone.utc), rating = rating)
        self.user_repo.add_recipe_record(user_id, recipe_id, record)

    def update_menu_item(self, household_id: str, index: int, updated: MenuItem) -> None:
        self.repo.update_menu_item(household_id, index, updated)