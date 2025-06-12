from main import app
from auth import get_user, get_test_user_customized
from pytest import fixture, mark
from firebase import user_test_ref as mock_ref, user_ref, household_ref, household_test_ref
from fastapi.testclient import TestClient
from uuid import uuid4


app.dependency_overrides[user_ref] = mock_ref
app.dependency_overrides[household_ref] = household_test_ref
app.dependency_overrides[get_user] = get_test_user_customized

@fixture(scope="module")
def client():
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c

def test_get_shopping_list_empty(client):
    # Arrange

    # Act
    response = client.get("shopping-list/", headers={"Authorization":"Bearer 1"})

    print(response)
    # Assert
    assert response.status_code == 200
    assert len(response.json()) == 0

def test_get_shopping_list(client, fake_header):
    # Arrange
    app.dependency_overrides[get_user] = get_test_user_customized
    uid, header = fake_header
    response = client.post("shopping-list/",json={"name":"fake item", "user_id": uid}, headers=header)

    # Act
    response2 = client.get("shopping-list/", headers=header)

    # Assert
    assert response.status_code == 200
    list1 = response.json()
    list2 = response2.json()
    assert len(list1) == len(list2)
    assert list1[0]['user_id'] == list2[0]['user_id']
    assert list1[0]['name'] == list2[0]['name']

def test_add_item(client, fake_header):
    # Arrange
    uid, header = fake_header

    # Act
    response = client.post("shopping-list/",json={"name":"fake item", "user_id": uid}, headers=header)

    # Assert
    assert response.status_code == 200
    response_list = response.json()
    assert len(response_list) == 1
    assert response_list[0]['name'] == "fake item"
    assert response_list[0]['user_id'] == uid

@mark.parametrize('index_value,safe',[(0, True), (1, False)])
def test_check_item(client, index_value, safe, fake_header):
    # Arrange
    uid, header = fake_header

    # Act
    response1 = client.post("shopping-list/",json={"name":"fake item", "user_id": uid}, headers=header)
    response2 = client.post(f"shopping-list/check/{index_value}",json={"name":"fake item", "user_id": uid}, headers=header)

    # Assert
    assert response1.status_code == 200
    response_list1 = response1.json()
    assert len(response_list1) == 1
    assert response_list1[0]['name'] == "fake item"
    assert response_list1[0]['user_id'] == uid
    assert response_list1[0]['checked'] == False

    if safe:
        assert response2.status_code == 200
        response_list2 = response2.json()
        assert len(response_list2) == 1
        assert response_list2[0]['name'] == "fake item"
        assert response_list2[0]['user_id'] == uid
        assert response_list2[0]['checked'] == True
    else:
        assert response2.status_code == 400


@mark.parametrize('index_value,safe',[(0, True), (1, False)])
def test_edit_item(client, index_value, safe, fake_header):
    # Arrange
    uid, header = fake_header

    # Act
    response1 = client.post("shopping-list/",json={"name":"fake item", "user_id": uid}, headers=header)
    response2 = client.put(f"shopping-list/{index_value}",json={"name":"changed item", "user_id": uid}, headers=header)

    # Assert
    if safe:
        assert response1.status_code == 200
        response_list1 = response1.json()
        assert len(response_list1) == 1
        assert response_list1[0]['name'] == "fake item"
        assert response_list1[0]['user_id'] == uid
        assert response_list1[0]['checked'] == False

        assert response2.status_code == 200
        response_list2 = response2.json()
        assert len(response_list2) == 1
        assert response_list2[0]['name'] == "changed item"
        assert response_list2[0]['user_id'] == uid
        assert response_list2[0]['checked'] == False
    else:
        assert response2.status_code == 400

@mark.parametrize('index_value,safe',[(0, True), (1, False)])
def test_delete_item(client, index_value, safe, fake_header):
    # Arrange
    uid, header = fake_header

    # Act
    response1 = client.post("shopping-list/",json={"name":"fake item", "user_id": uid}, headers=header)
    response2 = client.delete(f"shopping-list/{index_value}", headers=header)

    # Assert
    if safe:
        assert response1.status_code == 200
        response_list1 = response1.json()
        assert len(response_list1) == 1
        assert response_list1[0]['name'] == "fake item"
        assert response_list1[0]['user_id'] == uid
        assert response_list1[0]['checked'] == False

        assert response2.status_code == 200
        response_list2 = response2.json()
        assert len(response_list2) == 0
    else:
        assert response2.status_code == 400