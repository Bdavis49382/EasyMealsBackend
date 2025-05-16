from firebase import db
from datetime import datetime, timezone, timedelta
from google.cloud.firestore_v1 import ArrayUnion, ArrayRemove
from models.Recipe import Recipe
from controllers.householdController import HouseholdController

class MenuController:
    @staticmethod
    def add_recipe(user_id: str, recipe: Recipe):
        # Add a recipe to the user's menu
        pass

    @staticmethod
    def get_menu(household_id: str):
        pass
    
    @staticmethod
    def finish_recipe(household_id: str, recipe_id: str):
        pass