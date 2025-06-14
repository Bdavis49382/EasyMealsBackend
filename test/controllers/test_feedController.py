from pytest import fixture, mark
from unittest.mock import MagicMock
from repositories.householdRepository import HouseholdRepository
from repositories.userRepository import UserRepository
from controllers.feedController import FeedController
from models.Recipe import RecipeLite
from copy import deepcopy
@fixture
def mock_household_repo():
    return MagicMock(spec=HouseholdRepository)

@fixture
def mock_user_repo():
    return MagicMock(spec=UserRepository)

@fixture
def feed_controller(mock_household_repo, mock_user_repo):
    return FeedController(mock_household_repo, mock_user_repo)

def test_add_recipe_provides_src_name(feed_controller,mock_user_repo, mock_user, mock_recipe):
    # Arrange
    mock_recipe.src_name = None
    mock_user.full_name = "Fake Test"
    mock_user_repo.get_user.return_value = mock_user

    # Act
    result = feed_controller.add_recipe("1", mock_recipe)

    # Assert
    mock_user_repo.add_recipe.assert_called_once()
    assert mock_user_repo.add_recipe.call_args[0][1].src_name == "Fake Test"

def test_add_recipe_has_src_name(feed_controller,mock_user_repo, mock_user, mock_recipe):
    # Arrange
    mock_recipe.src_name = "This Guy's Mom"
    mock_user.full_name = "Fake Test"
    mock_user_repo.get_user.return_value = mock_user

    # Act
    result = feed_controller.add_recipe("1", mock_recipe)

    # Assert
    mock_user_repo.add_recipe.assert_called_once()
    assert mock_user_repo.add_recipe.call_args[0][1].src_name == "This Guy's Mom"

def test_update_recipe(feed_controller,mock_user_repo, mock_user, mock_recipe):
    # Arrange

    # Act
    result = feed_controller.update_recipe("1","1", mock_recipe)

    # Assert
    mock_user_repo.update_recipe.assert_called_once_with("1","1", mock_recipe)

def test_get_user_recipes_empty(feed_controller,mock_user_repo, mock_household_repo, mock_recipe):
    # Arrange
    mock_household_repo.get_user_ids.return_value = []

    # Act
    result = feed_controller.get_user_recipes("1")

    # Assert
    assert result == []
    mock_household_repo.get_user_ids.assert_called_once()

def test_get_user_recipes_no_filter(feed_controller,mock_user_repo, mock_household_repo, mock_recipe):
    # Arrange
    mock_household_repo.get_user_ids.return_value = ["1"]
    mock_recipe.id = "1"
    mock_user_repo.get_user_recipes.return_value = {'10':mock_recipe}

    # Act
    result = feed_controller.get_user_recipes("1")

    # Assert
    assert len(result) == 1
    assert result[0].title == mock_recipe.title
    assert result[0].img_link == mock_recipe.img_link
    assert result[0].id == mock_recipe.id

@mark.parametrize('title,expected_amount',[('flake',0),('fake',1),('FAKE',1),('Fake',1),('flfakef l-;',1)])
def test_get_user_recipes_filtered(title, expected_amount, feed_controller,mock_user_repo, mock_household_repo, mock_recipe):
    # Arrange
    mock_household_repo.get_user_ids.return_value = ["1"]
    mock_recipe.id = "1"
    mock_recipe.title = title
    mock_user_repo.get_user_recipes.return_value = { '10': mock_recipe }

    # Act
    result = feed_controller.get_user_recipes("1", keyword="fake")

    # Assert
    assert len(result) == expected_amount

def test_remove_duplicates_has_duplicate( feed_controller, mock_recipe):
    # Arrange

    # Act
    result = feed_controller.remove_duplicates([mock_recipe], [mock_recipe])

    # Assert
    assert len(result) == 1

def test_remove_duplicates_unique( feed_controller, mock_recipe):
    # Arrange
    mock2 = deepcopy(mock_recipe)
    mock2.title = "not the same"

    # Act
    result = feed_controller.remove_duplicates([mock_recipe], [mock2])

    # Assert
    assert len(result) == 2

def test_score_recipe():
    # Will need a whole suite of tests at some point.
    assert True

def test_sort_recipes(feed_controller, mock_recipe):
    # Arrange
    mock_recipe.id = ""
    lite = RecipeLite.make_from_full(mock_recipe)

    # Act
    result = feed_controller.sort_recipes(None, [lite])

    # Assert
    assert len(result) == 1