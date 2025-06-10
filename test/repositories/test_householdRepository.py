from pytest import mark, fixture
from repositories.householdRepository import HouseholdRepository
from models.Household import Household

@fixture
def repo(mock_collection):
    return HouseholdRepository(mock_collection)

def test_find_household(repo, mock_snapshot):
    # Arrange
    mock_snapshot.id = "1234"

    # Act
    result: str = repo.find_household("1")

    # Assert
    assert result == "1234"

def test_create_household(mock_collection, repo, mock_snapshot):
    # Arrange
    mock_snapshot.id = "1234"

    # Act
    result: str = repo.create_household("1")

    # Assert
    assert result == "1234"
    mock_collection.add.assert_called_once()

def test_add_user(repo, mock_document):
    # Arrange

    # Act
    repo.add_user("1","1")

    # Assert
    mock_document.update.assert_called_once()

def test_kick_user(repo, mock_document):
    # Arrange

    # Act
    repo.kick_user("1","1")

    # Assert
    mock_document.update.assert_called_once()

def test_get_household_by_code(repo, mock_snapshot, mock_household_dict):
    # Arrange
    mock_snapshot.to_dict.return_value = mock_household_dict
    mock_snapshot.id = "fake"

    # Act
    household: Household = repo.get_household_by_code("1")

    # Assert
    mock_snapshot.to_dict.assert_called_once()
    assert household.model_dump() == mock_household_dict
    assert household.id == "fake"

def test_get_household_by_code_no_result(repo, mock_query):
    # Arrange
    mock_query.get.return_value = []

    # Act
    household: Household | None = repo.get_household_by_code("1")

    # Assert
    assert household == None

def test_update_code(repo, mock_document):
    # Arrange

    # Act
    repo.update_code("1","1")

    # Assert
    mock_document.update.assert_called_once()
    assert "1" in mock_document.update.call_args[0][0]['join_code']

def test_add_items(repo, mock_document, mock_snapshot, mock_household_dict, mock_shopping_item):
    # Arrange
    mock_snapshot.to_dict.return_value = mock_household_dict
    mock_shopping_item.model_dump.return_value = "fake shopping item"

    # Act
    repo.add_items("1",[mock_shopping_item])

    # Assert
    mock_document.update.assert_called_once()
    assert "fake shopping item" == mock_document.update.call_args[0][0]['shopping_list'][0]

def test_add_item(repo, mock_document, mock_shopping_item):
    # Arrange

    # Act
    repo.add_item("1",mock_shopping_item)

    # Assert
    mock_document.update.assert_called_once()

def test_get_household(repo, mock_snapshot, mock_household_dict):
    # Arrange
    mock_snapshot.to_dict.return_value = mock_household_dict

    # Act
    household: Household | None = repo.get_household("1")

    # Assert
    assert household.id == mock_household_dict['id']

def test_get_shopping_list(repo, mock_snapshot, mock_household_dict, mock_shopping_item_dict):
    # Arrange
    mock_household_dict['shopping_list'] = [mock_shopping_item_dict]
    mock_snapshot.to_dict.return_value = mock_household_dict

    # Act
    shopping_list: list = repo.get_shopping_list("1")

    # Assert
    assert shopping_list[0].model_dump() == mock_shopping_item_dict

def test_check_item(repo, mock_snapshot, mock_document, mock_household_dict, mock_shopping_item_dict):
    # Arrange
    mock_shopping_item_dict['checked'] = False
    mock_household_dict['shopping_list'] = [mock_shopping_item_dict]
    mock_snapshot.to_dict.return_value = mock_household_dict

    # Act
    repo.check_item("1", 0)

    # Assert
    mock_document.update.assert_called_once()
    assert mock_document.update.call_args[0][0]['shopping_list'][0]['checked'] == True

def test_update_item(repo, mock_snapshot, mock_shopping_item, mock_document, mock_household_dict, mock_shopping_item_dict):
    # Arrange
    mock_household_dict['shopping_list'] = [mock_shopping_item_dict]
    mock_snapshot.to_dict.return_value = mock_household_dict
    mock_shopping_item.model_dump.return_value = "fake"

    # Act
    repo.update_item("1", 0, mock_shopping_item)

    # Assert
    mock_document.update.assert_called_once()
    mock_shopping_item.model_dump.assert_called_once()
    assert mock_document.update.call_args[0][0]['shopping_list'][0] == "fake"

def test_remove_item(repo, mock_snapshot, mock_shopping_item, mock_document, mock_household_dict, mock_shopping_item_dict):
    # Arrange
    mock_household_dict['shopping_list'] = [mock_shopping_item_dict]
    mock_snapshot.to_dict.return_value = mock_household_dict

    # Act
    repo.remove_item("1", 0)

    # Assert
    mock_document.update.assert_called_once()
    assert mock_document.update.call_args[0][0]['shopping_list'] == []

def test_get_menu_items(repo, mock_snapshot, mock_household_dict, mock_menu_item_dict):
    # Arrange
    mock_household_dict['menu_recipes'] = [mock_menu_item_dict]
    mock_snapshot.to_dict.return_value = mock_household_dict

    # Act
    menu_items: list = repo.get_menu_items("1")

    # Assert
    assert menu_items[0].model_dump() == mock_menu_item_dict

def test_get_menu_item_by_index(repo, mock_snapshot, mock_household_dict, mock_menu_item_dict):
    # Arrange
    mock_household_dict['menu_recipes'] = [mock_menu_item_dict]
    mock_snapshot.to_dict.return_value = mock_household_dict

    # Act
    menu_item = repo.get_menu_item_by_index("1",0)

    # Assert
    assert menu_item.model_dump() == mock_menu_item_dict

def test_add_recipe_to_menu(repo, mock_document, mock_menu_item):
    # Arrange

    # Act
    repo.add_recipe_to_menu("1", mock_menu_item)

    # Assert
    mock_menu_item.model_dump.assert_called_once()
    mock_document.update.assert_called_once()

def test_get_user_ids(repo, mock_snapshot, mock_household_dict, mock_menu_item_dict):
    # Arrange
    mock_household_dict['owner_id'] = "1"
    mock_household_dict['users'] = ["2","3"]
    mock_snapshot.to_dict.return_value = mock_household_dict

    # Act
    ids : list[str] = repo.get_user_ids("1")

    # Assert
    assert ids[0] == "1"
    assert ids[1] == "2"
    assert ids[2] == "3"

@mark.parametrize('input_value,expected_size',[('1',0),('notRightId',1)])
def test_remove_menu_item(repo, mock_document, mock_household_dict, mock_snapshot, mock_menu_item_dict, input_value, expected_size):
    # Arrange
    mock_household_dict['menu_recipes'] = [mock_menu_item_dict]
    mock_snapshot.to_dict.return_value = mock_household_dict

    # Act
    repo.remove_menu_item("1", input_value)

    # Assert
    mock_document.update.assert_called_once()
    assert len(mock_document.update.call_args[0][0]['menu_recipes']) == expected_size