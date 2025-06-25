from pytest import fixture, mark, raises
from unittest.mock import MagicMock
from repositories.householdRepository import HouseholdRepository
from repositories.userRepository import UserRepository
from controllers.menuController import MenuController

@fixture
def mock_household_repo():
    return MagicMock(spec=HouseholdRepository)

@fixture
def mock_user_repo():
    return MagicMock(spec=UserRepository)

@fixture
def menu_controller(mock_household_repo, mock_user_repo):
    return MenuController(mock_household_repo, mock_user_repo)

def test_add_recipe(menu_controller,mock_household_repo, mock_menu_item, mock_recipe):
    # Arrange

    # Act
    menu_controller.add_recipe("1", mock_menu_item, "1")

    # Assert
    mock_household_repo.add_recipe_to_menu.assert_called_once()

def test_get_menu(menu_controller,mock_household_repo, mock_menu_item, mock_recipe, mock_user_repo):
    # Arrange
    mock_menu_item.recipe_id = "10"

    mock_household_repo.get_menu_items.return_value = [mock_menu_item]
    mock_household_repo.get_user_ids.return_value = ["1"]
    mock_recipe.id = "10"
    mock_user_repo.get_user_recipes.return_value = {"10" : mock_recipe}

    # Act
    result = menu_controller.get_menu("1")

    # Assert
    assert result[0].recipe_id == "10"
    assert result[0].img_link == mock_recipe.img_link
    assert result[0].title == mock_recipe.title

def test_get_menu_recipes_not_found(menu_controller,mock_household_repo, mock_menu_item, mock_recipe, mock_user_repo):
    # Arrange
    mock_menu_item.recipe_id = "11"

    mock_household_repo.get_menu_items.return_value = [mock_menu_item]
    mock_household_repo.get_user_ids.return_value = ["1"]
    mock_recipe.id = "10"
    mock_user_repo.get_user_recipes.return_value = {"10" : mock_recipe}

    # Act
    result = menu_controller.get_menu("1")

    # Assert
    assert len(result) == 0

def test_get_menu_item(menu_controller,mock_household_repo, mock_menu_item, mock_recipe, mock_user_repo, mock_menu_item_dict, mock_recipe_dict):
    # Arrange
    mock_menu_item.recipe_id = "10"
    mock_menu_item.model_dump.return_value = mock_menu_item_dict
    mock_menu_item_dict['recipe_id'] = '10'

    mock_household_repo.get_menu_items.return_value = [mock_menu_item]
    mock_household_repo.get_user_ids.return_value = ["1"]
    mock_recipe.id = "10"
    mock_user_repo.get_user_recipes.return_value = {"10" : mock_recipe}

    # Act
    result = menu_controller.get_menu_item("1",0)

    # Assert
    assert result.recipe_id == "10"
    assert result.recipe.img_link == mock_recipe.img_link
    assert result.recipe.title == mock_recipe.title
    assert result.note == mock_menu_item.note
    assert result.date == mock_menu_item.date

def test_get_menu_item_invalid_index(menu_controller,mock_household_repo):
    # Arrange
    mock_household_repo.get_menu_items.return_value = []

    # Act
    with raises(IndexError) as exception:
        result = menu_controller.get_menu_item("1",0)

    # Assert
    assert exception.errisinstance(IndexError)

def test_get_household_recipes(menu_controller,mock_household_repo, mock_recipe, mock_user_repo):
    # Arrange
    mock_recipe.id = "10"
    mock_user_repo.get_user_recipes.return_value = {"10": mock_recipe}
    mock_household_repo.get_user_ids.return_value = ["1"]

    # Act
    result = menu_controller._get_household_recipes("1")

    # Assert
    assert len(result) == 1
    assert '10' in result
    assert result['10'].title == mock_recipe.title

@mark.parametrize('recipe_id,correct',[('10',True),('5',False),('0', False)])
def test_get_recipe(recipe_id, correct, menu_controller,mock_household_repo, mock_recipe, mock_user_repo):
    # Arrange
    mock_recipe.id = "10"
    mock_household_repo.get_user_ids.return_value = ["1"]
    mock_user_repo.get_user_recipes.return_value = {"10": mock_recipe}

    # Act
    result = menu_controller.get_recipe("1",recipe_id)

    # Assert
    if correct:
        assert result != None
        assert result.title == mock_recipe.title
    else:
        assert result == None

def test_finish_recipe(menu_controller,mock_household_repo, mock_recipe, mock_user_repo):
    # Arrange

    # Act
    result = menu_controller.finish_recipe("1","10","1",5)

    # Assert
    mock_household_repo.remove_menu_item.assert_called_once()
    mock_user_repo.add_recipe_record.assert_called_once()

def test_finish_recipe_no_rating(menu_controller,mock_household_repo, mock_user_repo):
    # Arrange

    # Act
    menu_controller.finish_recipe("1","10","1")

    # Assert
    mock_household_repo.remove_menu_item.assert_called_once()
    mock_user_repo.add_recipe_record.assert_called_once()

def test_update_menu_item(menu_controller, mock_household_repo, mock_menu_item):
    #Act
    menu_controller.update_menu_item("1", 0, mock_menu_item)

    #Assert
    mock_household_repo.update_menu_item.assert_called_once()