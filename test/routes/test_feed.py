from main import app
from auth import get_user, get_test_user
from unittest.mock import MagicMock
from controllers.allRecipes import AllRecipes
from models.Recipe import RecipeLite
from pytest import fixture, mark
from firebase import user_test_ref as mock_ref, user_ref, household_ref, household_test_ref
from fastapi.testclient import TestClient

def mock_all_recipes():
    mock = MagicMock(spec=AllRecipes)
    recipe = RecipeLite(title="spaghetti",img_link="")
    mock.search.return_value = [recipe]
    mock.get_main_dishes.return_value = [recipe for _ in range(50)]
    mock.get_soups.return_value = [recipe for _ in range(50)]
    mock.get_desserts.return_value = [recipe for _ in range(50)]
    mock.get_breakfasts.return_value = [recipe for _ in range(50)]
    return mock

app.dependency_overrides[user_ref] = mock_ref
app.dependency_overrides[household_ref] = household_test_ref
app.dependency_overrides[get_user] = get_test_user
app.dependency_overrides[AllRecipes] = mock_all_recipes

@fixture(scope="module")
def client():
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c

def test_add_recipe(client, fake_header, mock_recipe_dict):
    # Arrange
    uid, header = fake_header

    # Act
    response = client.post(f"feed/", headers=header, json=mock_recipe_dict)

    # Assert
    assert response.status_code == 200
    assert len(response.json()) == 36

def test_update_recipe(client, fake_header, mock_recipe_dict):
    # Arrange
    uid, header = fake_header

    # Act
    response = client.post(f"feed/", headers=header, json=mock_recipe_dict)
    assert response.status_code == 200
    recipe_id = response.json()
    assert len(recipe_id) == 36

    mock_recipe_dict['title'] = 'changed title'
    response2 = client.put(f"feed/{recipe_id}", headers=header, json=mock_recipe_dict)

    assert recipe_id == response2.json()

    response3 = client.get(f"menu/recipes/{recipe_id}", headers=header)

    # Assert
    assert response3.status_code == 200
    assert response3.json()['title'] == 'changed title'

def test_get_feed(client, fake_header, mock_recipe_dict):
    # Arrange
    uid, header = fake_header

    # Act
    response = client.post(f"feed/", headers=header, json=mock_recipe_dict)
    response = client.get(f"feed/", headers=header)
    
    # Assert
    assert response.status_code == 200
    assert len(response.json()) == 51
    
def test_search(client, fake_header):
    # Arrange
    uid, header = fake_header

    # Act
    response = client.get(f"feed/search?query=spaghetti", headers=header)

    # Assert
    assert response.status_code == 200
    assert len(response.json()) == 1

def test_get_user_tags(client, fake_header, mock_recipe_dict):
    # Arrange
    uid, header = fake_header
    mock_recipe_dict['tags'] = ['fakeTag']

    # Act
    response = client.post(f"feed/", headers=header, json=mock_recipe_dict)
    response = client.get(f"feed/tags", headers=header)

    # Assert
    assert response.status_code == 200
    assert len(response.json()) == 6 # includes all the tags that come from allrecipes.
    assert 'fakeTag' in response.json()
    assert 'MyRecipes' in response.json()
