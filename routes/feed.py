from fastapi import APIRouter, Request, UploadFile, Depends
from models.Recipe import Recipe, RecipeLite
from controllers.feedController import FeedController
from typing import Annotated

router = APIRouter(
    prefix="/feed",
    tags= ["Feed"]
)

@router.post("/")
async def add_recipe(request: Request, recipe: Recipe, controller: Annotated[FeedController, Depends()]) -> str:
    return controller.add_recipe(request.state.user_id, recipe)

@router.put("/{recipe_id}")
async def update_recipe(request: Request,recipe_id: str, recipe: Recipe, controller: Annotated[FeedController, Depends()]) -> str:
    return controller.update_recipe(request.state.user_id, recipe_id, recipe)

@router.post('/upload/image')
async def upload_image(file: UploadFile, controller: Annotated[FeedController, Depends()]) -> str:
    return await controller.upload_image(file)

@router.get("/")
async def get_feed(request: Request, controller: Annotated[FeedController, Depends()]) -> list[RecipeLite]:
    user_recipes = controller.get_user_recipes(request.state.household_id)
    suggested_recipes = controller.get_suggested_recipes()
    combined_recipes = controller.remove_duplicates(user_recipes, suggested_recipes)
    sorted_recipes = controller.sort_recipes(request.state.household_id, combined_recipes)
    return sorted_recipes

@router.get('/search/{query}')
async def search_feed(query: str, request: Request, controller: Annotated[FeedController, Depends()]) -> list[RecipeLite]:
    user_recipes = controller.get_user_recipes(request.state.household_id, keyword=query)
    all_recipes = controller.search_all_recipes(query)
    combined_recipes = controller.remove_duplicates(user_recipes, all_recipes)
    sorted_recipes = controller.sort_recipes(request.state.household_id, combined_recipes)
    
    return sorted_recipes