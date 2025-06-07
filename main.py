from fastapi import FastAPI, Request, HTTPException
from models.Recipe import Recipe
from routes import shopping_list, household, feed, user, menu
from firebase_admin import auth

app = FastAPI()


@app.middleware("http")
async def provide_household_id(request: Request, call_next):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="missing auth token")
    # Remove the Bearer part and verify token with firebase
    user = auth.verify_id_token(auth_header.split(" ")[1])
    if 'uid' in user:
        print(user['uid'])
    request.state.household_id = request.headers.get("household_id") or "3hPKx3PwkPkPPlCVs53q"
    return await call_next(request)

app.include_router(shopping_list.router)
app.include_router(household.router)
app.include_router(feed.router)
app.include_router(user.router)
app.include_router(menu.router)

@app.exception_handler(Exception)
def global_handler(request: Request, exc: Exception):
    raise HTTPException(status_code=500,detail=str(exc))
