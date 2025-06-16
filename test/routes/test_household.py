from main import app
from auth import get_user, get_test_user
from pytest import fixture
from firebase import user_test_ref as mock_ref, user_ref, household_ref, household_test_ref
from fastapi.testclient import TestClient


app.dependency_overrides[user_ref] = mock_ref
app.dependency_overrides[household_ref] = household_test_ref
app.dependency_overrides[get_user] = get_test_user

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

def test_get_household_code(client, fake_header):
    # Arrange
    uid, header = fake_header

    # Act
    response = client.get("/household/code", headers=header)
    first_code = response.json()
    response2 = client.get("/household/code", headers=header)
    second_code = response.json()

    # Assert
    assert response.status_code == 200
    assert len(first_code) == 6

    assert response2.status_code == 200
    assert len(second_code) == 6
    assert first_code == second_code


def test_join_household(client, fake_header):
    # Arrange
    uid, header = fake_header
    response = client.get("/household/code", headers = header)
    code = response.json()

    # Act
    response = client.get(f"/household/join/{code}", headers = {"Authorization": "Bearer 1"})

    # Assert
    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json()[1]['id'] == "1"

def test_kick_user_not_allowed(client, fake_header):
    # Arrange
    response = client.get("/household/code", headers ={"Authorization": "Bearer 101"})
    code = response.json()

    uid, header = fake_header
    response = client.get(f"/household/join/{code}", headers= header)

    # Act
    response = client.delete("/household/kick/101", headers= header)

    # Assert
    assert response.status_code == 401

def test_kick_user(client, fake_header):
    # Arrange
    uid, header = fake_header
    response = client.get("/household/code", headers = header)
    code = response.json()

    response = client.get(f"/household/join/{code}", headers={"Authorization": "Bearer 1"} )

    # Act
    response = client.delete("/household/kick/1", headers= header)

    # Assert
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]['id'] == uid