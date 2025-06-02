from firebase import db, bucket
from datetime import datetime, timezone, timedelta
from google.cloud.firestore_v1 import ArrayUnion, ArrayRemove
from models.Recipe import Recipe
from models.Record import Record
from controllers.householdController import HouseholdController
from controllers.allRecipes import AllRecipes
from uuid import uuid4
from fastapi import UploadFile
import random

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
    
    def update_recipe(user_id: str, recipe_id: str, recipe: Recipe):
        db.collection('users').document(user_id).update({
            f"recipes.{recipe_id}": recipe.model_dump()
        })
        return recipe_id

    @staticmethod
    async def upload_image(file: UploadFile):
        blob = bucket.blob(uuid4().__str__())
        blob.upload_from_string(await file.read(), content_type=file.content_type)
        blob.make_public()
        return blob.public_url

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
        if household_id != None:
            menu = HouseholdController.get_household(household_id)['menu_recipes']
            menu_ids = [x['recipe_id'] for x in menu]
        else:
            menu_ids = []
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
                if 'id' in recipe and recipe['id'] in menu_ids:
                    score -= 200
                if 'history' in recipe and len(recipe['history']) != 0:
                    history = [Record(household_id=x['household_id'],timestamp=x['timestamp'],rating=x['rating']) for x in recipe['history']]
                    most_recent = max(x.timestamp for x in history)
                    rating = sum(x.rating for x in history)/len(history)
                    waiting_time = 30
                    # decide how long to wait before suggesting a recipe again based on how it was rated.
                    if rating != None:
                        if rating == 5:
                            waiting_time = 7
                        if rating >= 4:
                            waiting_time = 14
                        elif rating >= 3:
                            waiting_time = 30
                        else:
                            waiting_time = 60
                    if datetime.now(timezone.utc) - most_recent > timedelta(days=waiting_time):
                        score += 3*rating
                    else:
                        score -= 10
                else:
                    score += 10 # recipes that have been added but not tried should go near the top
            score += (random.random() * 10) - 5
            recipe['score'] = score
        recipes.sort(key=lambda x: x['score'], reverse=True)
        return recipes


