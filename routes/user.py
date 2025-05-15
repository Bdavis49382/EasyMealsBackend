from fastapi import APIRouter, Request
from models.Household import User
from controllers.userController import UserController

router = APIRouter(
    prefix="/user",
    tags= ["User"]
)
@router.post("/create")
async def create_user(user: User):
    # Create a new user
    user_id = UserController.create_user(user)
    return {"message": "User created successfully", "user_id": user_id}

@router.get("/get/{user_id}")
async def get_user(user_id: str):
    # Get user data
    user_data = UserController.get_user(user_id)
    if user_data is None:
        return {"message": "User not found"}
    return {"user": user_data}

@router.get("/get")
async def get_users():
    # Get user data
    user_data = UserController.get_users()
    if user_data is None:
        return {"message": "Users not found"}
    return {"users": user_data}