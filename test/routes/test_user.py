from main import app
from auth import get_user, get_test_user_random as mock_auth, get_test_user_fixed as mock_auth_fixed
from pytest import fixture
from firebase import user_test_ref as mock_ref, user_ref
from fastapi.testclient import TestClient


app.dependency_overrides[user_ref] = mock_ref
app.dependency_overrides[get_user] = mock_auth

@fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c

def test_create_user(client, mock_user_dict):
    response = client.post("/user/",json=mock_user_dict)
    assert response.status_code == 200

def test_get_users(client):
    response = client.get("/user")
    assert response.status_code == 200
    assert len(response.json()) > 0

def test_get_user(client):
    response = client.get("/user/1")
    assert response.status_code == 200