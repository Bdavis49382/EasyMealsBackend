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
    if shopping_item.user_id == None:
        shopping_item.user_id = req.state.user_id
    controller.add_item(req.state.household_id, shopping_item)
    return controller.get_shopping_list(req.state.household_id)

@router.post("/check/{id}")
async def check_item(req: Request, id: str,controller: Annotated[ShoppingListController, Depends()]) -> list[ShoppingItemOut]:
    controller.check_item(req.state.household_id, id)
    return controller.get_shopping_list(req.state.household_id)

@router.put("/{id}")
async def edit_item(req: Request, id: str, shopping_item: ShoppingItem,controller: Annotated[ShoppingListController, Depends()]) -> list[ShoppingItemOut]:
    controller.edit_item(req.state.household_id, id, shopping_item)
    return controller.get_shopping_list(req.state.household_id)

@router.delete("/{index}")
async def remove_item(req: Request, index: int,controller: Annotated[ShoppingListController, Depends()]) -> list[ShoppingItemOut]:
    controller.remove_item(req.state.household_id, index)
    return controller.get_shopping_list(req.state.household_id)

@router.patch("/move")
async def move_item(req: Request, from_index: str, to_index:str,controller: Annotated[ShoppingListController, Depends()]) -> list[ShoppingItemOut]:
    controller.move_item(req.state.household_id, int(from_index), int(to_index))
    return controller.get_shopping_list(req.state.household_id)