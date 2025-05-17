from firebase import db
from datetime import datetime, timezone, timedelta
from google.cloud.firestore_v1 import ArrayUnion, ArrayRemove
from models.Household import MenuItem
from models.Record import Record
from models.Recipe import Recipe
from controllers.householdController import HouseholdController
from controllers.feedController import FeedController
from controllers.userController import UserController
from controllers.allRecipes import AllRecipes
from uuid import uuid4

class MenuController:
    @staticmethod
    def add_recipe(household_id, menu_item: MenuItem):
        return db.collection('households').document(household_id).update({
            "menu_recipes": ArrayUnion([menu_item.model_dump()])
        })


    @staticmethod
    def get_menu(household_id: str) -> list:
        return HouseholdController.get_household(household_id)['menu_recipes']
    
    @staticmethod
    def get_recipe(household_id: str, recipe_id: str):
        household = HouseholdController.get_household(household_id)
        for user_id in household['users']:
            user = UserController.get_user(user_id)
                
            if user is not None and recipe_id in user['recipes']:
                return user['recipes'][recipe_id]
    
    @staticmethod
    def get_recipe_online(link: str):
        raw_recipe = AllRecipes.get(link)
        recipe = Recipe(title=raw_recipe['name'], instructions=raw_recipe["steps"],img_link=raw_recipe['image'], servings=raw_recipe['nb_servings'], time_estimate= [raw_recipe['total_time']], src_link=link,src_name="Allrecipes.com", ingredients=raw_recipe['ingredients'])
        return recipe
    
    @staticmethod
    def finish_recipe(household_id: str, recipe_id: str, user_id : str, rating: int | None = None):
        menu = MenuController.get_menu(household_id)

        # remove from menu
        menu = [x for x in menu if x['recipe_id'] != recipe_id]
        db.collection('households').document(household_id).update({
            "menu_recipes" : menu
        })

        #add a record for this interaction
        record = Record(household_id=household_id,timestamp=datetime.now(timezone.utc), rating = rating)

        return db.collection('users').document(user_id).update({
            f"recipes.{recipe_id}.history" : ArrayUnion([record.model_dump()])
        })
