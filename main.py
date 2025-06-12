from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import JSONResponse
from models.Household import User
from routes import shopping_list, household, feed, user, menu
from typing_extensions import Annotated
from os import getenv
from auth import provide_household_id, get_user, get_test_user_fixed

    
app = FastAPI(dependencies=[Depends(provide_household_id)])
env = getenv("ENVIRONMENT")
if env != None and 'Dev' in env:
    app.dependency_overrides[get_user] = get_test_user_fixed

app.include_router(shopping_list.router)
app.include_router(household.router)
app.include_router(feed.router)
app.include_router(user.router)
app.include_router(menu.router)

@app.exception_handler(Exception)
def global_handler(request: Request, exc: Exception):
    if isinstance(exc, IndexError):
        return JSONResponse(status_code=400, content={"message":"Index out of bounds. Try again with a different value."})

    print(str(exc))
    raise HTTPException(status_code=500,detail=str(exc))
