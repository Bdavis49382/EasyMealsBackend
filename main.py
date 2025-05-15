from fastapi import FastAPI, Request
from models.Recipe import Recipe
from routes import shopping_list, household

app = FastAPI()


@app.middleware("http")
async def provide_household_id(request: Request, call_next):
    request.state.household_id = request.headers.get("household_id") or "3hPKx3PwkPkPPlCVs53q"
    return await call_next(request)

app.include_router(shopping_list.router)
app.include_router(household.router)

# @app.get('/')
# def read_root():
#     return {"hello": "world"}

# @app.get('/items/{item_id}')
# def read_item(item_id: int, q: str | None = None):
#     return {"item_id": item_id, "q": q}

# @app.put("/items/{item_id}")
# def update_item(item_id: int, item : Recipe):
#     return {"item_name": item.title, "item_id": item_id}