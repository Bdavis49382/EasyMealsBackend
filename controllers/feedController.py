from firebase import db
from datetime import datetime, timezone, timedelta
from google.cloud.firestore_v1 import ArrayUnion, ArrayRemove
from models.Recipe import Recipe
from controllers.householdController import HouseholdController
from controllers.allRecipes import AllRecipes
from uuid import uuid4

class FeedController:
    @staticmethod
    def add_recipe(user_id: str, recipe: Recipe):
        # Add a recipe to the user's feed
        recipe_dict = recipe.model_dump()
        recipe_dict['author_id'] = user_id
        if recipe_dict['src_name'] is None:
            recipe_dict['src_name'] = "" # perhaps automatically add user's name
        recipe_id = uuid4().__str__()
        db.collection('users').document(user_id).update({
            f"recipes.{recipe_id}": recipe_dict
        })
        return recipe_id

    @staticmethod
    def get_user_recipes(household_id: str, keyword: str | None = None):
        household = HouseholdController.get_household(household_id)
        recipes = []
        for user_id in [household['owner_id'],*household['users']]:
            user_data = db.collection('users').document(user_id).get().to_dict()
            if user_data is not None and 'recipes' in user_data:
                for id, recipe in user_data['recipes'].items():
                    recipe['id'] = id
                    if keyword is None:
                        recipes.append(recipe)
                    elif keyword.upper() in recipe['title'].upper():
                        recipes.append(recipe)
        return recipes
    
    @staticmethod
    def search_all_recipes(query: str):
        return AllRecipes.search(query)
    
    @staticmethod
    def get_suggested_recipes():
        return AllRecipes.get_main_dishes()
    
    @staticmethod
    def remove_duplicates(user_recipes: list[dict],other_recipes: list[dict]):
        user_titles = set(x['title'] for x in user_recipes)
        user_recipes.extend([x for x in other_recipes if x['title'] not in user_titles])
        return user_recipes

    @staticmethod
    def sort_recipes(household_id : str,recipes: list):
        for recipe in recipes:
            score = 0
            if 'rate' in recipe and recipe['rate'] != None:
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


