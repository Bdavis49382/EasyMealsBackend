from fastapi import APIRouter, Request
from models.Household import MenuItem
from models.Recipe import Recipe
from datetime import datetime
from controllers.menuController import MenuController
from controllers.feedController import FeedController

router = APIRouter(
    prefix="/menu",
    tags= ["Menu"]
)

@router.get('/get')
async def get_menu(request: Request):
    return MenuController.get_menu(request.state.household_id)

@router.post('/add')
async def add_recipe(request: Request, menu_item: MenuItem):
    res = MenuController.add_recipe(request.state.household_id, menu_item)
    if res is None:
        return {"message":"failed"}
    return {"message": "successfully added to menu"}

@router.get("/get/recipe")
async def get_recipe(request: Request, recipe_id: str):
    res = MenuController.get_recipe(request.state.household_id, recipe_id)
    return {"recipe_details": res}


@router.post('/save')
async def save_recipe(request: Request, user_id: str, recipe: Recipe, note: str | None = None, date: datetime | None = None):
    recipe_id = FeedController.add_recipe(user_id, recipe)
    menu_item = MenuItem(note=note,date=date,recipe_id=recipe_id)
    response = MenuController.add_recipe(request.state.household_id, menu_item)
    if response is None:
        return {"message": "failed"}
    return {"message":"successfully saved and added to menu"}

@router.post('/finish')
async def finish_meal(request: Request, recipe_id: str, user_id: str, rating: int | None = None):
    response = MenuController.finish_recipe(request.state.household_id, recipe_id, user_id, rating)
    if response is None:
        return {"message": "failed"}
    return {"message":"sucessfully removed from menu"}