from fastapi import APIRouter, Request, Depends, HTTPException
from controllers.householdController import HouseholdController
from controllers.userController import UserController
from models.User import UserLite
from typing import Annotated

router = APIRouter(
    prefix="/household",
    tags= ["Household"]
)

@router.get("/users")
async def get_household_users(request: Request, controller: Annotated[HouseholdController, Depends()]):
    # Get the household ID from the request
    household_id = request.state.household_id

    if household_id is None:
        return {"message": "No household found"}
    
    return controller.get_household_users(household_id)

@router.get("/code")
async def get_household_code(request: Request, controller: Annotated[HouseholdController, Depends()]):
    code = controller.get_join_code(request.state.household_id)
    return code.code

@router.get("/join/{code}")
async def join_household(request: Request, code: str, controller: Annotated[HouseholdController, Depends()]):
    new_users = controller.join_household(request.state.user_id, code)
    if new_users is None:
        return {"message": "Invalid household ID or code"}
    return new_users

@router.delete("/kick/{user_id}")
async def kick_user(request: Request, user_id: str, controller: Annotated[HouseholdController, Depends()]) -> list[UserLite]:
    if request.state.user_id != controller.get_household(request.state.household_id).owner_id:
        raise HTTPException(status_code=401, detail="Only admin can kick other users")
    new_users = controller.kick_user(request.state.household_id, user_id)
    if new_users is None:
        raise HTTPException(status_code=404, detail="user to kick not found.")
    return new_users