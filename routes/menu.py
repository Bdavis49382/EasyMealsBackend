from fastapi import APIRouter, Request, HTTPException, Depends, Response, status
from models.Household import ActiveItems
from models.Recipe import Recipe, MenuItem, MenuItemLite, RecipeOut, MenuItemOut
from datetime import datetime
from controllers.menuController import MenuController
from controllers.shoppingListController import ShoppingListController
from typing import Annotated

router = APIRouter(
    prefix="/menu",
    tags= ["Menu"]
)

@router.get('/')
async def get_menu(request: Request, controller: Annotated[MenuController, Depends()]) -> list[MenuItemLite]:
    return controller.get_menu(request.state.household_id)

@router.post('/', description="Either a recipe or recipe_id MUST be present in provided menu_item")
async def add_recipe(request: Request, 
        menu_item: MenuItem, 
        controller: Annotated[MenuController, Depends()],
        shopping_list_controller: Annotated[ShoppingListController, Depends()]) -> list[MenuItemLite]:

    controller.add_recipe(request.state.household_id, menu_item, request.state.user_id)

    shopping_list_controller.add_shopping_strings(request.state.household_id, menu_item.active_items, request.state.user_id, menu_item.recipe_id)

    return controller.get_menu(request.state.household_id)

@router.get("/recipes/{recipe_id}")
async def get_recipe(request: Request, recipe_id: str, controller: Annotated[MenuController, Depends()]) -> RecipeOut:
    res = controller.get_recipe(request.state.household_id, recipe_id)
    if res is None:
        raise HTTPException(404, detail= "Recipe was not found or you do not have permission to access it. Is the user who owns this recipe in your household?")
    return res

@router.get("/index/{index}")
async def get_recipe_by_index(request: Request, index: str, controller: Annotated[MenuController, Depends()]) -> MenuItemOut:
    return controller.get_menu_item(request.state.household_id, int(index))

@router.get('/online')
async def get_recipe_online(link:str, controller: Annotated[MenuController, Depends()]) -> Recipe:
    recipe = controller.get_recipe_online(link)
    if recipe == None:
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    return recipe

@router.post('/finish/{recipe_id}')
async def finish_meal(request: Request, recipe_id: str, controller: Annotated[MenuController, Depends()], rating: float | None = None) -> list[MenuItemLite]:
    controller.finish_recipe(request.state.household_id, recipe_id, request.state.user_id, rating)
    return controller.get_menu(request.state.household_id)

@router.patch("/index/{index}")
async def patch_recipe_by_index(request: Request, index: str, updated: MenuItem, controller: Annotated[MenuController, Depends()]) -> MenuItemOut:
    controller.update_menu_item(request.state.household_id, int(index), updated)
    return controller.get_menu_item(request.state.household_id, int(index))