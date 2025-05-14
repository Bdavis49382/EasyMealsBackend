from fastapi import APIRouter, Request
from models.Household import ShoppingItem
from controllers.shopping_list import ShoppingListController

router = APIRouter(
    prefix="/shopping-list",
    tags= ["Shopping List"]
)

@router.get("/")
async def get_shopping_list(req: Request):
    # removes any items that have been checked for more than 12 hours before returning the list
    ShoppingListController.clean_list(req.state.household_id)

    return ShoppingListController.get_shopping_list(req.state.household_id)

@router.post("/add")
async def add_item(req: Request, shopping_item: ShoppingItem):
    updated_list = ShoppingListController.add_item(req.state.household_id, shopping_item)
    return {"message": "Item added to shopping list","updated_list": updated_list}

@router.post("/check/{index}")
async def check_item(req: Request, index: int):
    updated_list = ShoppingListController.check_item(req.state.household_id, index)
    return {"message": "Item checked in shopping list", "updated_list": updated_list}

@router.put("/edit/{index}")
async def edit_item(req: Request, index: int, shopping_item: ShoppingItem):
    updated_list = ShoppingListController.edit_item(req.state.household_id, index, shopping_item)
    return {"message": "Item edited in shopping list", "updated_list": updated_list}

@router.delete("/remove/{index}")
async def remove_item(req: Request, index: int):
    updated_list = ShoppingListController.remove_item(req.state.household_id, index)
    return {"message": "Item removed from shopping list", "updated_list": updated_list}