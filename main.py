from fastapi import FastAPI, Request
from models.Recipe import Recipe
from routes import shopping_list

app = FastAPI()

app.include_router(shopping_list.router)

@app.middleware("http")
async def provide_household_id(request: Request, call_next):
    request.state.household_id = request.headers.get("household_id") or "twJkkoWv6zb5Nw4JPnmz"
    return await call_next(request)

# @app.get('/')
# def read_root():
#     return {"hello": "world"}

# @app.get('/items/{item_id}')
# def read_item(item_id: int, q: str | None = None):
#     return {"item_id": item_id, "q": q}

# @app.put("/items/{item_id}")
# def update_item(item_id: int, item : Recipe):
#     return {"item_name": item.title, "item_id": item_id}