from firebase import db
from datetime import datetime, timezone, timedelta
from google.cloud.firestore_v1 import ArrayUnion, ArrayRemove
from models.Recipe import Recipe
from controllers.householdController import HouseholdController
from controllers.allRecipes import AllRecipes
import string, random

class FeedController:
    @staticmethod
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

    @staticmethod
    def get_user_recipes(household_id: str, keyword: str | None = None):
        users = HouseholdController.get_household(household_id)['users']
        recipes = []
        for user_id in users:
            user_data = db.collection('users').document(user_id).get().to_dict()
            if user_data is not None and 'recipes' in user_data:
                for recipe in user_data['recipes']:
                    if keyword is None:
                        recipes.append(recipe)
                    elif keyword in recipe['title']:
                        recipes.append(recipe)

        return recipes
    
    @staticmethod
    def search_all_recipes(query: str):
        return AllRecipes.search(query)
    
    @staticmethod
    def get_suggested_recipes():
        return AllRecipes.get_main_dishes()
    
    @staticmethod
    def sort_recipes(household_id : str,recipes: list):
        for recipe in recipes:
            score = 0
            if 'rate' in recipe:
                if recipe['rate'] == 5:
                    score += 10
                elif recipe['rate'] > 4:
                    score += 5
                elif recipe['rate'] > 3:
                    score += 1
                else:
                    score -= 5
            else:
                score = 50
            recipe['score'] = score
        recipes.sort(key=lambda x: x['score'], reverse=True)
        return recipes


