from firebase import bucket
from datetime import datetime, timezone, timedelta
from models.Recipe import Recipe, RecipeLite
from controllers.allRecipes import AllRecipes
from uuid import uuid4
from fastapi import UploadFile, Depends, HTTPException
from typing import Annotated
from repositories.householdRepository import HouseholdRepository
from repositories.userRepository import UserRepository
import random

class FeedController:
    def __init__(self, repo: Annotated[HouseholdRepository, Depends()], user_repo: Annotated[UserRepository, Depends()]):
        self.repo = repo
        self.user_repo = user_repo

    def add_recipe(self, user_id: str, recipe: Recipe) -> str:
        # Add a recipe to the user's feed
        recipe.author_id = user_id
        recipe.tags.append("MyRecipes")
        if recipe.src_name is None:
            recipe.src_name = self.user_repo.get_user(user_id).full_name
        recipe_id = self.user_repo.add_recipe(user_id, recipe)
        return recipe_id
    
    def update_recipe(self, user_id: str, recipe_id: str, recipe: Recipe) -> str:
        return self.user_repo.update_recipe(user_id, recipe_id, recipe)

    async def upload_image(self, file: UploadFile) -> str:
        blob = bucket.blob(uuid4().__str__())
        blob.upload_from_string(await file.read(), content_type=file.content_type)
        blob.make_public()
        return blob.public_url

    def get_user_recipes(self, household_id: str, keyword: str | None = None) -> list[RecipeLite]:
        recipes = []
        for user_id in self.repo.get_user_ids(household_id):
            user_recipes = self.user_repo.get_user_recipes(user_id)
            for recipe in user_recipes.values():
                if keyword is None:
                    recipes.append(RecipeLite.make_from_full(recipe))
                elif keyword.upper() in recipe.title.upper():
                    recipes.append(RecipeLite.make_from_full(recipe))
        return recipes
    
    def search_all_recipes(self, query: str):
        return AllRecipes.search(query)
    
    def get_suggested_recipes(self):
        return AllRecipes.get_main_dishes()
    
    def remove_duplicates(self, user_recipes: list[RecipeLite],other_recipes: list[RecipeLite]) -> list[RecipeLite]:
        user_titles = set(recipe.title for recipe in user_recipes)
        user_recipes.extend([recipe for recipe in other_recipes if recipe.title not in user_titles])
        return user_recipes
    
    def score_recipe(self, recipe: RecipeLite, menu_ids: list[str], visited_titles: set[str]) -> int:
        score = 0
        if recipe.title in visited_titles:
            score = -400
        if recipe.rate != None:
            if recipe.rate == 5:
                score += 10
            elif recipe.rate > 4:
                score += 5
            elif recipe.rate > 3:
                score += 1
            else:
                score -= 5
        else:
            if recipe.id != None and recipe.id in menu_ids:
                score -= 200
            if len(recipe.history) > 0:
                most_recent = max(x.timestamp for x in recipe.history)
                waiting_time = 30
                # decide how long to wait before suggesting a recipe again based on how it was rated.
                ratings = [x.rating for x in recipe.history if x.rating != None]
                if len(ratings) > 0:
                    avg_rating = sum(ratings)/len(ratings)
                    if avg_rating == 5:
                        waiting_time = 7
                    if avg_rating >= 4:
                        waiting_time = 14
                    elif avg_rating >= 3:
                        waiting_time = 30
                    else:
                        waiting_time = 60
                    
                    if datetime.now(timezone.utc) - most_recent > timedelta(days=waiting_time):
                        score += 3 * avg_rating
                if datetime.now(timezone.utc) - most_recent > timedelta(days=waiting_time):
                    score += 10
            else:
                score += 10 # recipes that have been added but not tried should go near the top
        score += (random.random() * 10) - 5
        recipe.score = score
        visited_titles.add(recipe.title)
        return score

    def sort_recipes(self, household_id : str,recipes: list[RecipeLite]):
        visited_titles = set()
        if household_id != None:
            menu = self.repo.get_menu_items(household_id)
            menu_ids = [x.recipe_id for x in menu]
        else:
            menu_ids = []

        recipes.sort(key=lambda recipe: self.score_recipe(recipe, menu_ids, visited_titles), reverse=True)
        return [x for x in recipes if x.score > -100]
