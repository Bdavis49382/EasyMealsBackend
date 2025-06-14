from random import randint
from fastapi import Request, HTTPException, Depends
from typing import Annotated
from firebase_admin import auth
from models.User import User
from controllers.householdController import HouseholdController
from controllers.userController import UserController

def get_test_user_random() -> dict:
    return {'uid':str(randint(1,500)),'name':f'Bob Testerman{randint(1,500)}'}

def get_test_user_fixed() -> dict:
    return {'uid':'1', 'name':'Bob Testerman'}

def get_test_user(request: Request) -> dict:
    auth_header = request.headers.get("Authorization")
    if auth_header is None:
        return {'uid':str(randint(1,500)),'name':f'Bob Testerman{randint(1,500)}'}

    return {'uid':auth_header.split(" ")[1], 'name':'Bob Testerman'}

async def get_user(request: Request) -> dict:
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="missing auth token")

        # Remove the Bearer part and verify token with firebase
        try:
            return auth.verify_id_token(auth_header.split(" ")[1])
        except:
            raise HTTPException(status_code=401, detail="Invalid auth token")

async def provide_household_id(request: Request, user_controller: Annotated[UserController, Depends()], user: Annotated[dict, Depends(get_user)], household_controller: Annotated[HouseholdController, Depends()]):
    if 'uid' in user:
        uid = user['uid']
        request.state.user_id = uid
        user_info = user_controller.get_user(uid)
        if user_info == None:
            res = user_controller.create_user(User(full_name=user['name'],google_id=uid))
            if res == None:
                raise HTTPException(status_code=500, detail="Failed to create new user in database")
        household_id = household_controller.find_household(uid)
        if household_id is None:
            household_id = household_controller.create_household(uid)
        request.state.household_id = household_id
    else:
        raise HTTPException(status_code=401, detail="User information incomplete")