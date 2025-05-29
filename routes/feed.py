from fastapi import APIRouter, Request, UploadFile
from models.Recipe import Recipe
from controllers.feedController import FeedController

router = APIRouter(
    prefix="/feed",
    tags= ["Feed"]
)

@router.post("/add/{user_id}")
async def add_recipe(user_id: str, recipe: Recipe):
    FeedController.add_recipe(user_id, recipe)
    return {"message": "Recipe added to feed successfully"}

@router.post('/upload/image')
async def upload_image(file: UploadFile):
    url = await FeedController.upload_image(file)
    return url

@router.get("/get")
async def get_feed(request: Request):
    user_recipes = FeedController.get_user_recipes(request.state.household_id)
    all_recipes = FeedController.get_suggested_recipes()
    sorted_recipes = FeedController.sort_recipes(request.state.household_id, [*user_recipes, *all_recipes])
    return sorted_recipes

@router.get('/search/{query}')
async def search_feed(query: str, request: Request):
    user_recipes = FeedController.get_user_recipes(request.state.household_id, keyword=query)
    all_recipes = FeedController.search_all_recipes(query)
    combined_recipes = FeedController.remove_duplicates(user_recipes, all_recipes)
    sorted_recipes = FeedController.sort_recipes(request.state.household_id, combined_recipes)
    
    return sorted_recipes