from pytest import fixture
from unittest.mock import MagicMock
from models.Recipe import Recipe, MenuItem
from models.Record import Record
from models.User import User
from models.Household import JoinCode, Household
from models.ShoppingItem import ShoppingItem
from datetime import datetime
from google.cloud.firestore_v1.collection import CollectionReference
from google.cloud.firestore_v1.document import DocumentReference
from google.cloud.firestore_v1.base_document import DocumentSnapshot
from google.cloud.firestore_v1.query import Query

@fixture
def mock_user(mock_user_dict):
    mock_user = MagicMock(spec=User)
    mock_user.full_name = 'fake'
    mock_user.google_id = 'data'
    mock_user.recipes = {}
    mock_user.model_dump.return_value = mock_user_dict
    return mock_user

@fixture
def mock_collection(mock_document, mock_query, mock_snapshot):
    mock_collection = MagicMock(spec=CollectionReference)
    mock_collection.document.return_value = mock_document
    mock_collection.where.return_value = mock_query
    mock_collection.add.return_value = ['',mock_snapshot]
    return mock_collection

@fixture
def mock_query(mock_snapshot):
    mock_query = MagicMock(spec=Query)
    mock_query.get.return_value = [mock_snapshot]
    mock_query.where.return_value = mock_query
    return mock_query

@fixture
def mock_document(mock_snapshot):
    mock_doc = MagicMock(spec=DocumentReference)
    mock_doc.get.return_value = mock_snapshot
    return mock_doc

@fixture
def mock_snapshot():
    mock_snapshot = MagicMock(spec=DocumentSnapshot)
    return mock_snapshot

@fixture
def mock_user_dict(mock_recipe_dict):
    return {
    "full_name": "fake",
    "google_id": "data",
    "recipes": {"fake_id":mock_recipe_dict}
    }

@fixture
def mock_recipe(mock_recipe_dict):
    mock_recipe = MagicMock(spec=Recipe)
    mock_recipe.title= "fake recipe"
    mock_recipe.permissions_required = "household"
    mock_recipe.instructions = []
    mock_recipe.img_link = ""
    mock_recipe.author_id = ""
    mock_recipe.servings = ""
    mock_recipe.time_estimate = []
    mock_recipe.src_link = ""
    mock_recipe.src_name = ""
    mock_recipe.ingredients = ""
    mock_recipe.history = []
    mock_recipe.model_dump.return_value = mock_recipe_dict
    return mock_recipe
    

@fixture
def mock_recipe_dict():
    return {
        "title": "fake recipe",
        "permissions_required":"household",
        "instructions": [],
        "img_link": "",
        "author_id": "",
        "servings": "",
        "time_estimate": [],
        "src_link": "",
        "src_name": "",
        "ingredients": [],
        "history": []
    }

@fixture
def mock_record():
    record_mock = MagicMock(spec=Record)
    record_mock.model_dump.return_value = {}
    return record_mock

@fixture
def mock_household_dict(mock_join_code_dict):
    return {
    "id": "fake",
    "users": [""],
    "owner_id": "",
    "join_code": mock_join_code_dict,
    "menu_recipes": [],
    "shopping_list": []
    }

@fixture
def mock_household():
    return MagicMock(spec=Household)

@fixture
def mock_join_code_dict():
    return {
        "code":"1234",
        "expiration_date": datetime(2000,1,1)
    }

@fixture
def mock_join_code():
    return MagicMock(spec=JoinCode)

@fixture
def mock_shopping_item():
    return MagicMock(spec=ShoppingItem)

@fixture
def mock_shopping_item_dict():
    return {
        "name": "fake shopping item",
        "checked": False,
        "time_checked": datetime(2000,1,1),
        "user_id": "",
        "recipe_id": ""
    }

@fixture
def mock_menu_item():
    return MagicMock(spec=MenuItem)

@fixture
def mock_menu_item_dict(mock_recipe_dict):
    return {
        "note": '',
        "date": None,
        "active_items": [],
        # Should have either recipe_id or recipe
        "recipe_id": "1",
        "recipe": mock_recipe_dict
    }