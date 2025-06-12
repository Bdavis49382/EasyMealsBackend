from fastapi import APIRouter, Request, Depends
from models.ShoppingItem import ShoppingItem, ShoppingItemOut
from controllers.shoppingListController import ShoppingListController
from typing import Annotated

router = APIRouter(
    prefix="/shopping-list",
    tags= ["Shopping List"]
)

@router.get("/")
async def get_shopping_list(req: Request, controller: Annotated[ShoppingListController, Depends()]) -> list[ShoppingItemOut]:
    # removes any items that have been checked for more than 12 hours before returning the list
    controller.clean_list(req.state.household_id)

    return controller.get_shopping_list(req.state.household_id)

@router.post("/")
async def add_item(req: Request, shopping_item: ShoppingItem,controller: Annotated[ShoppingListController, Depends()]) -> list[ShoppingItemOut]:
    controller.add_item(req.state.household_id, shopping_item)
    return controller.get_shopping_list(req.state.household_id)

@router.post("/check/{index}")
async def check_item(req: Request, index: int,controller: Annotated[ShoppingListController, Depends()]) -> list[ShoppingItemOut]:
    controller.check_item(req.state.household_id, index)
    return controller.get_shopping_list(req.state.household_id)

@router.put("/{index}")
async def edit_item(req: Request, index: int, shopping_item: ShoppingItem,controller: Annotated[ShoppingListController, Depends()]) -> list[ShoppingItemOut]:
    controller.edit_item(req.state.household_id, index, shopping_item)
    return controller.get_shopping_list(req.state.household_id)

@router.delete("/{index}")
async def remove_item(req: Request, index: int,controller: Annotated[ShoppingListController, Depends()]) -> list[ShoppingItemOut]:
    controller.remove_item(req.state.household_id, index)
    return controller.get_shopping_list(req.state.household_id)