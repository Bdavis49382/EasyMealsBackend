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
    response = client.get(f"feed/", headers=header)

    # Assert
    assert response.status_code == 200
    assert len(response.json()) > 0
    
@mark.parametrize('query,valid',[(';lskdlaju',False),('spaghetti',True)])
def test_get_feed(query, valid,client, fake_header):
    # Arrange
    uid, header = fake_header

    # Act
    response = client.get(f"feed/search/{query}", headers=header)

    # Assert
    assert response.status_code == 200
    if valid:
        assert len(response.json()) > 0
    else:
        assert len(response.json()) == 0 