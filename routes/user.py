from fastapi import APIRouter, Request, Depends
from models.Household import User
from controllers.userController import UserController
from typing import Annotated

router = APIRouter(
    prefix="/user",
    tags= ["User"]
)
@router.post("/")
async def create_user(user: User, controller: Annotated[UserController, Depends()]):
    # Create a new user
    user_id = controller.create_user(user)
    return {"message": "User created successfully", "user_id": user_id}

@router.get("/{user_id}")
async def get_user(user_id: str, controller: Annotated[UserController, Depends()]):
    # Get user data
    user_data = controller.get_user(user_id)
    if user_data is None:
        return {"message": "User not found"}
    return user_data

@router.get("/")
async def get_users(controller: Annotated[UserController, Depends()]):
    # Get user data
    user_data = controller.get_users()
    return user_data