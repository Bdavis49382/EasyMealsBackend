
from firebase import db
from datetime import datetime, timezone, timedelta
from google.cloud.firestore_v1 import ArrayUnion, ArrayRemove
from models.Recipe import Recipe
from controllers.householdController import HouseholdController
import string, random

class FeedController:
    def add_recipe(user_id: str, recipe: Recipe):
        # Add a recipe to the user's feed
        recipe_dict = recipe.model_dump()
        recipe_dict['author_id'] = user_id
        if recipe_dict['src_name'] is None:
            recipe_dict['src_name'] = "" # perhaps automatically add user's name
        db.collection('users').document(user_id).update({
            "recipes": ArrayUnion([recipe_dict])
        })
        return recipe_dict
    
    def get_user_recipes(household_id: str):
        users = HouseholdController.get_household(household_id)['users']
        recipes = []
        for user_id in users:
            user_data = db.collection('users').document(user_id).get().to_dict()
            if user_data is not None and 'recipes' in user_data:
                for recipe in user_data['recipes']:
                    recipes.append(recipe)
        return recipes

