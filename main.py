from fastapi import FastAPI, Request, HTTPException, Depends
from models.Household import User
from routes import shopping_list, household, feed, user, menu
from firebase_admin import auth
from typing_extensions import Annotated
from controllers.householdController import HouseholdController
from controllers.userController import UserController

async def provide_household_id(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="missing auth token")

    # Remove the Bearer part and verify token with firebase
    try:
        user = auth.verify_id_token(auth_header.split(" ")[1])
    except:
        raise HTTPException(status_code=401, detail="Invalid auth token")

    print(user)
    if 'uid' in user:
        user_info = UserController.get_user(user['uid'])
        if user_info == None:
            res = UserController.create_user(User(full_name=user['displayName'],google_id=user['uid']))
            if res == None:
                raise HTTPException(status_code=500, detail="Failed to create new user in database")
        household_id = HouseholdController.find_household(user['uid'])
        if household_id is None:
            household_id = HouseholdController.create_household(user['uid'])
        request.state.household_id = household_id
    else:
        raise HTTPException(status_code=401, detail="User information incomplete")

app = FastAPI(dependencies=[Depends(provide_household_id)])


app.include_router(shopping_list.router)
app.include_router(household.router)
app.include_router(feed.router)
app.include_router(user.router)
app.include_router(menu.router)

@app.exception_handler(Exception)
def global_handler(request: Request, exc: Exception):
    raise HTTPException(status_code=500,detail=str(exc))
