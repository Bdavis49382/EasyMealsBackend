from fastapi import APIRouter, Request
from models.Household import MenuItem, ActiveItems
from models.Recipe import Recipe
from datetime import datetime
from controllers.menuController import MenuController
from controllers.feedController import FeedController
from controllers.shoppingListController import ShoppingListController

router = APIRouter(
    prefix="/menu",
    tags= ["Menu"]
)

@router.get('/get')
async def get_menu(request: Request):
    return MenuController.get_menu(request.state.household_id)

@router.post('/add')
async def add_recipe(request: Request, menu_item: MenuItem, active_items: ActiveItems, user_id : str):
    res = MenuController.add_recipe(request.state.household_id, menu_item)
    if res is None:
        return {"message":"failed"}
    res = ShoppingListController.add_items(request.state.household_id, ShoppingListController.wrap_items(active_items.items, user_id, menu_item.recipe_id))
    return {"message": "successfully added to menu with items added to shopping list."}

@router.get("/get/recipe")
async def get_recipe(request: Request, recipe_id: str):
    res = MenuController.get_recipe(request.state.household_id, recipe_id)
    return {"recipe_details": res}

@router.get('/get/recipe-online')
async def get_recipe_online(link:str):
    res = MenuController.get_recipe_online(link)
    if res is None:
        return {"message":"failed to retrieve recipe at that link"}
    return res


@router.post('/save')
async def save_recipe(request: Request, user_id: str, active_items: ActiveItems, recipe: Recipe, note: str | None = None, date: datetime | None = None):
    recipe_id = FeedController.add_recipe(user_id, recipe)
    menu_item = MenuItem(note=note,date=date,recipe_id=recipe_id)
    response = MenuController.add_recipe(request.state.household_id, menu_item)
    if response is None:
        return {"message": "failed"}
    ShoppingListController.add_items(request.state.household_id,ShoppingListController.wrap_items(active_items.items, user_id, recipe_id))
    return {"message":"successfully saved and added to menu with items added to shopping list"}

@router.post('/finish')
async def finish_meal(request: Request, recipe_id: str, user_id: str, rating: int | None = None):
    response = MenuController.finish_recipe(request.state.household_id, recipe_id, user_id, rating)
    if response is None:
        return {"message": "failed"}
    return {"message":"sucessfully removed from menu"}