from fastapi import APIRouter, Request, HTTPException
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

@router.post('/add/{user_id}', description="Either a recipe or recipe_id MUST be present in provided menu_item")
async def add_recipe(request: Request, menu_item: MenuItem, user_id : str):
    if menu_item.recipe_id is None:
        if menu_item.recipe is None:
            raise HTTPException(status_code=422, detail="either recipe or recipe_id is required to add recipe")
        recipe_id = FeedController.add_recipe(user_id, menu_item.recipe)
        menu_item.recipe_id = recipe_id
        menu_item.recipe = None
    res = MenuController.add_recipe(request.state.household_id, menu_item)
    if res is None:
        return {"message":"failed"}
    res = ShoppingListController.add_items(request.state.household_id, ShoppingListController.wrap_items(menu_item.active_items, user_id, menu_item.recipe_id))
    return {"message": "successfully added to menu with items added to shopping list.","recipe_id":menu_item.recipe_id}

@router.get("/get/recipe")
async def get_recipe(request: Request, recipe_id: str):
    res = MenuController.get_recipe(request.state.household_id, recipe_id)
    return res

@router.get("/get/recipe/{index}")
async def get_recipe_by_index(request: Request, index: str):
    res = MenuController.get_menu_item(request.state.household_id, int(index))
    if res is None:
        return {"message": "failed to retrieve by that index"}
    return res

@router.get('/get/recipe-online')
async def get_recipe_online(link:str):
    res = MenuController.get_recipe_online(link)
    if res is None:
        return {"message":"failed to retrieve recipe at that link"}
    return res


@router.post('/finish')
async def finish_meal(request: Request, recipe_id: str, user_id: str, rating: float | None = None):
    response = MenuController.finish_recipe(request.state.household_id, recipe_id, user_id, rating)
    if response is None:
        return {"message": "failed"}
    return {"message":"sucessfully removed from menu"}