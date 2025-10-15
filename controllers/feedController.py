from firebase import bucket
from pathlib import Path
from datetime import datetime, timezone, timedelta
from models.Recipe import Recipe, RecipeLite, RecipeOut
from controllers.allRecipes import AllRecipes
from uuid import uuid4
from fastapi import UploadFile, Depends, HTTPException
from fastapi.responses import RedirectResponse
from typing import Annotated
from repositories.householdRepository import HouseholdRepository
from repositories.userRepository import UserRepository
import random

class FeedController:
    def __init__(self, repo: Annotated[HouseholdRepository, Depends()], user_repo: Annotated[UserRepository, Depends()], all_recipes: Annotated[AllRecipes, Depends()]):
        self.repo = repo
        self.user_repo = user_repo
        self.all_recipes = all_recipes

    def add_recipe(self, user_id: str, recipe: Recipe) -> str:
        # Add a recipe to the user's feed
        recipe.author_id = user_id
        recipe.tags.append("MyRecipes")
        if recipe.src_name is None:
            recipe.src_name = self.user_repo.get_user(user_id).full_name
        recipe_id = self.user_repo.add_recipe(user_id, recipe)
        return recipe_id
    
    def update_recipe(self, household_id: str, recipe_id: str, recipe: Recipe) -> str:
        old_recipe = [recipe for user_id in self.repo.get_user_ids(household_id) for recipe in self.user_repo.get_user_recipes(user_id).values() if recipe.id == recipe_id]
        if len(old_recipe) != 1:
            return ""
        return self.user_repo.update_recipe(old_recipe[0].author_id, recipe_id, recipe)

    async def upload_image(self, user_id:str, file: UploadFile) -> str:
        file_name = user_id + "/" + uuid4().__str__() + Path(file.filename).suffix
        blob = bucket.blob(file_name)
        blob.upload_from_string(await file.read(), content_type=file.content_type)
        return file_name
    
    def _tag_hits(self, recipe: RecipeOut, tags: set[str]):
        return len([x for x in recipe.tags if x.upper() in tags])

    def _keyword_hits(self, recipe: RecipeOut, keywords: list[str]):
        # multiply by 100 so that it will essentially sort by keywords first, then tags within that, so the order will be combined matches, keyword only matches, and then tag only matches.
        return 100 * len([x for x in keywords if x.upper() in recipe.title.upper() or recipe.title.upper() in x.upper()])

    def get_user_recipes(self, household_id: str, keywords: list[str] = [], tags: list[str] = [], page: int = -1) -> list[tuple[RecipeLite, int]]:
        recipes = []
        tags = set([t.upper() for t in tags])
        for user_id in self.repo.get_user_ids(household_id):
            user_recipes = self.user_repo.get_user_recipes(user_id)
            sorted_recipes = self.sort_recipes(household_id,[RecipeLite.make_from_full(x) for x in list(user_recipes.values())])
            if page * 10 < len(sorted_recipes) or page == -1:
                # if page is -1, we just want the whole thing.
                if page == -1:
                    start = 0
                    end = len(sorted_recipes)
                else:
                    start = page * 10
                    end = start + 10 if start + 10 < len(sorted_recipes) else len(sorted_recipes)
                for recipe in sorted_recipes[start:end]:
                    # keeps track of the recipes along with the total number of hits they had.
                    recipes.append((recipe, self._tag_hits(recipe,tags) + self._keyword_hits(recipe, keywords)))
        return recipes
    
    def get_user_tags(self, user_id: str) -> list[str]:
        tags = self.user_repo.get_user_tags(user_id)
        tags.update(["Breakfast","Soups","MainDishes","Desserts"])
        return list(tags)
    
    def search_all_recipes(self, keywords: str, tags: list[str]) -> list[tuple[RecipeLite, int]]:
        out = []
        if len(tags) != 0:
            recipes = self.all_recipes.get_recipes_by_tag(tags)
            for recipe in recipes:
                if len(keywords.strip()) != 0:
                    out.append((recipe, 1 + self._keyword_hits(recipe, keywords.split(' '))))
                else:
                    out.append((recipe,1))
        if len(keywords.strip()) != 0:
            recipes = self.all_recipes.search(keywords)
            for recipe in recipes:
                out.append((recipe, self._keyword_hits(recipe, keywords.split(' '))))
        return out
    
    def get_suggested_recipes(self,page:int=0):
        pages = [self.all_recipes.get_main_dishes(), self.all_recipes.get_soups(), self.all_recipes.get_breakfasts(), self.all_recipes.get_desserts()]
        combined = []
        try:
            combined.extend(pages[page%len(pages)][:20])
            combined.extend(pages[(page + 1)%len(pages)][20:35])
            combined.extend(pages[(page + 2)%len(pages)][35:45])
            combined.extend(pages[(page + 3)%len(pages)][45:50])
        except IndexError:
            print('one of the allrecipes pages did not have 50 items, so it was not added to the feed.')

        return combined
    
    def remove_duplicates(self, user_recipes: list[RecipeLite],other_recipes: list[RecipeLite], household_id: str) -> list[RecipeLite]:
        all_user_recipes = [recipe for user_id in self.repo.get_user_ids(household_id) for recipe in self.user_repo.get_user_recipes(user_id).values()]
        user_titles = set(recipe.title for recipe in all_user_recipes)
        user_recipes.extend([recipe for recipe in other_recipes if recipe.title not in user_titles])
        return user_recipes

    def remove_duplicates_search(self, user_recipes: list[tuple[RecipeLite,int]],other_recipes: list[tuple[RecipeLite,int]], household_id: str) -> list[tuple[RecipeLite,int]]:
        all_user_recipes = [recipe for user_id in self.repo.get_user_ids(household_id) for recipe in self.user_repo.get_user_recipes(user_id).values()]
        user_titles = set(recipe.title for recipe in all_user_recipes)
        user_recipes.extend([recipe for recipe in other_recipes if recipe[0].title not in user_titles])
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
                score -= 500
            if len(recipe.history) > 0:
                most_recent = max(x.timestamp for x in recipe.history)
                waiting_time = 60
                # decide how long to wait before suggesting a recipe again based on how it was rated.
                ratings = [x.rating for x in recipe.history if x.rating != None]
                if len(ratings) > 0:
                    avg_rating = sum(ratings)/len(ratings)
                    if avg_rating == 5:
                        waiting_time = 30
                    if avg_rating >= 4:
                        waiting_time = 45
                    elif avg_rating >= 3:
                        waiting_time = 60
                    else:
                        waiting_time = 90
                    
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
        return [x for x in recipes if x.score > -400]
    
    def sort_search_recipes(self, recipes: list[tuple[RecipeLite,int]]) -> list[RecipeLite]:
        recipes.sort(key = lambda recipe: recipe[1], reverse = True)
        return [x[0] for x in recipes if x[1] != 0]

    def get_image(self, file_path: str) -> RedirectResponse:
        try:
            blob = bucket.blob(file_path)
            if not blob.exists():
                raise HTTPException(status_code=404, detail="Image Not Found")
            
            signed_url = blob.generate_signed_url(expiration=timedelta(hours=1), version="v4")
            return RedirectResponse(url = signed_url)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))