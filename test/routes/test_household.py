from main import app
from auth import get_user, get_test_user_random as mock_auth, get_test_user_fixed as mock_auth_fixed
from pytest import fixture
from firebase import user_test_ref as mock_ref, user_ref, household_ref, household_test_ref
from fastapi.testclient import TestClient


app.dependency_overrides[user_ref] = mock_ref
app.dependency_overrides[household_ref] = household_test_ref
app.dependency_overrides[get_user] = mock_auth

@fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c

def test_get_household_users(client):
    # Act
    response = client.get("/household/users")

    # Assert
    assert response.status_code == 200
    assert len(response.json()) == 1

def test_get_household_code(client):
    app.dependency_overrides[get_user] = mock_auth_fixed
    # Act
    response = client.get("/household/code")
    first_code = response.json()
    response2 = client.get("/household/code")
    second_code = response.json()

    # Assert
    assert response.status_code == 200
    assert len(first_code) == 6

    assert response2.status_code == 200
    assert len(second_code) == 6
    assert first_code == second_code

    # teardown
    app.dependency_overrides[get_user] = mock_auth

def test_join_household(client):
    # Arrange
    # create a random user
    app.dependency_overrides[get_user] = mock_auth
    response = client.get("/household/code")
    code = response.json()

    # switch back to the standard test user
    app.dependency_overrides[get_user] = mock_auth_fixed
    # Act
    response = client.get(f"/household/join/1/{code}")

    # Assert
    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json()[1]['id'] == "1"

def test_kick_user_not_allowed(client):
    # Arrange
    # create a random user
    app.dependency_overrides[get_user] = mock_auth
    response = client.get("/household/code")
    code = response.json()

    # switch back to the standard test user
    app.dependency_overrides[get_user] = mock_auth_fixed
    response = client.get(f"/household/join/1/{code}")

    # Act
    response = client.delete("/household/kick/20")

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": "Only admin can kick other users"}

    # Teardown
    app.dependency_overrides[get_user] = mock_auth