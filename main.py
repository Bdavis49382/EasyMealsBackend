from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Recipe(BaseModel):
    name: str
    reference: str

@app.get('/')
def read_root():
    return {"hello": "world"}

@app.get('/items/{item_id}')
def read_item(item_id: int, q: str | None = None):
    return {"item_id": item_id, "q": q}

@app.put("/items/{item_id}")
def update_item(item_id: int, item : Recipe):
    return {"item_name": item.name, "item_id": item_id}