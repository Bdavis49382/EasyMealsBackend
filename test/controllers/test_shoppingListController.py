from pytest import fixture
from unittest.mock import MagicMock
from repositories.userRepository import UserRepository
from repositories.householdRepository import HouseholdRepository
from controllers.shoppingListController import ShoppingListController

@fixture
def mock_user_repo():
    return MagicMock(spec=UserRepository)

@fixture
def mock_household_repo():
    return MagicMock(spec=HouseholdRepository)

@fixture
def shopping_list_controller(mock_household_repo, mock_user_repo):
    return ShoppingListController(mock_household_repo, mock_user_repo)


def test_get_shopping_list(shopping_list_controller, mock_household_repo, mock_shopping_item, mock_user_repo, mock_user, mock_recipe):
    # Arrange
    mock_household_repo.get_shopping_list.return_value = [mock_shopping_item]
    mock_user.full_name = "Bob Joe"
    mock_user_repo.get_user.return_value = mock_user
    mock_recipe.title = "Fake Soup"
    mock_user_repo.find_user_recipe.return_value = mock_recipe
    # Act
    result = shopping_list_controller.get_shopping_list("1")
    # Assert
    assert result[0].user_id == mock_shopping_item.user_id
    assert result[0].recipe_id == mock_shopping_item.recipe_id
    assert result[0].name == mock_shopping_item.name
    assert result[0].user_initial == "B"
    assert result[0].recipe_title == "Fake Soup"

def test_clean_list(shopping_list_controller, mock_household_repo, mock_household, mock_menu_item):
    # Arrange
    mock_menu_item.recipe_id = "101"
    mock_household.menu_recipes = [mock_menu_item]
    mock_household_repo.get_household.return_value = mock_household


    # Act
    shopping_list_controller.clean_list("1")

    # Assert
    mock_household_repo.remove_items.assert_called_once()



def test_add_item(shopping_list_controller, mock_household_repo, mock_user_repo, mock_shopping_item):
    # Arrange

    # Act
    shopping_list_controller.add_item("1", "1",mock_shopping_item)

    # Assert
    mock_household_repo.add_item.assert_called_once()
    mock_user_repo.add_user_suggestion.assert_called_once()

def test_get_suggestions(shopping_list_controller, mock_user_repo):
    # Arrange
    mock_user_repo.get_user_suggestions.return_value = ["1","2"]

    # Act
    result = shopping_list_controller.get_suggestions("1")

    # Assert
    mock_user_repo.get_user_suggestions.assert_called_once()
    assert type(result) == list
    assert len(result) == 2

def test_add_items(shopping_list_controller, mock_household_repo, mock_shopping_item):
    # Arrange

    # Act
    shopping_list_controller.add_items("1", [mock_shopping_item])

    # Assert
    mock_household_repo.add_items.assert_called_once()

def test_add_shopping_strings(shopping_list_controller, mock_household_repo, mock_shopping_item):
    # Arrange

    # Act
    shopping_list_controller.add_shopping_strings("1", ["Fake Item"], "0", "0")

    # Assert
    mock_household_repo.add_items.assert_called_once()

def test_check_item(shopping_list_controller, mock_household_repo):
    # Arrange

    # Act
    shopping_list_controller.check_item("1", 0)

    # Assert
    mock_household_repo.check_item.assert_called_once()

def test_edit_item(shopping_list_controller, mock_household_repo, mock_shopping_item):
    # Arrange

    # Act
    shopping_list_controller.edit_item("1", 0, mock_shopping_item)

    # Assert
    mock_household_repo.update_item.assert_called_once()

def test_remove_item(shopping_list_controller, mock_household_repo):
    # Arrange

    # Act
    shopping_list_controller.remove_item("1", 0)

    # Assert
    mock_household_repo.remove_item.assert_called_once()