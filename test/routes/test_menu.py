from main import app
from auth import get_user, get_test_user
from pytest import fixture, mark
from firebase import user_test_ref as mock_ref, user_ref, household_ref, household_test_ref
from fastapi.testclient import TestClient


app.dependency_overrides[user_ref] = mock_ref
app.dependency_overrides[household_ref] = household_test_ref
app.dependency_overrides[get_user] = get_test_user

@fixture(scope="module")
def client():
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c

def test_add_recipe(client, fake_header, mock_menu_item_dict):
    # Arrange
    uid, header = fake_header
    mock_menu_item_dict["recipe_id"] = None

    # Act
    response = client.post(f"menu/", headers=header, json=mock_menu_item_dict)

    # Assert
    assert response.status_code == 200
    assert len(response.json()) == 1

def test_get_menu(client, fake_header, mock_menu_item_dict, mock_recipe_dict):
    # Arrange
    uid, header = fake_header
    mock_menu_item_dict["recipe_id"] = None

    # Act
    response1 = client.post(f"menu/", headers=header, json=mock_menu_item_dict)
    response2 = client.get(f"menu/", headers=header)

    # Assert
    assert response1.status_code == 200
    assert len(response1.json()) == 1

    assert response2.status_code == 200
    assert len(response2.json()) == 1
    menu_item = response2.json()[0]
    assert menu_item['note'] == mock_menu_item_dict['note']
    assert menu_item['date'] == mock_menu_item_dict['date']
    # Check that it saved and used data from the mock_recipe
    assert menu_item['recipe_id'] is not None
    assert menu_item['img_link'] == mock_recipe_dict['img_link']
    assert menu_item['title'] == mock_recipe_dict['title']

def test_get_recipe(client, fake_header, mock_menu_item_dict, mock_recipe_dict):
    # Arrange
    uid, header = fake_header
    mock_menu_item_dict["recipe_id"] = None

    response1 = client.post(f"menu/", headers=header, json=mock_menu_item_dict)
    assert response1.status_code == 200
    assert len(response1.json()) == 1
    menu_item = response1.json()[0]
    assert 'recipe_id' in menu_item
    assert menu_item['recipe_id'] is not None

    # Act
    response2 = client.get(f"menu/recipes/{menu_item['recipe_id']}", headers=header)

    # Assert
    assert response2.status_code == 200
    assert menu_item['img_link'] == response2.json()['img_link']
    assert menu_item['title'] == response2.json()['title']

def test_get_recipe_nonexistant(client, fake_header, mock_menu_item_dict, mock_recipe_dict):
    # Arrange
    uid, header = fake_header

    # Act
    response = client.get(f"menu/recipes/1", headers=header)

    # Assert
    assert response.status_code == 404

def test_get_recipe_by_index(client, fake_header, mock_menu_item_dict, mock_recipe_dict):
    # Arrange
    uid, header = fake_header
    mock_menu_item_dict["recipe_id"] = None

    # Act
    response1 = client.post(f"menu/", headers=header, json=mock_menu_item_dict)
    response2 = client.get(f"menu/index/0", headers=header)

    # Assert
    assert response1.status_code == 200
    assert len(response1.json()) == 1

    assert response2.status_code == 200
    menu_item = response2.json()
    assert menu_item['note'] == mock_menu_item_dict['note']
    assert menu_item['date'] == mock_menu_item_dict['date']
    # Check that it saved and used data from the mock_recipe
    assert menu_item['recipe_id'] is not None
    assert menu_item['recipe']['img_link'] == mock_recipe_dict['img_link']
    assert menu_item['recipe']['title'] == mock_recipe_dict['title']

def test_finish_meal(client, fake_header, mock_menu_item_dict, mock_recipe_dict):
    # Arrange
    uid, header = fake_header
    mock_menu_item_dict["recipe_id"] = None

    response1 = client.post(f"menu/", headers=header, json=mock_menu_item_dict)
    assert response1.status_code == 200
    assert len(response1.json()) == 1
    menu_item = response1.json()[0]
    assert 'recipe_id' in menu_item
    assert menu_item['recipe_id'] is not None

    # Act
    response2 = client.post(f"menu/finish/{menu_item['recipe_id']}", headers=header)

    # Assert
    assert response2.status_code == 200
    assert len(response2.json()) == 0
    