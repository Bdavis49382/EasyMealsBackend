from pytest import fixture, mark
from unittest.mock import MagicMock
from datetime import datetime, timezone, timedelta
from repositories.householdRepository import HouseholdRepository
from controllers.householdController import HouseholdController
from repositories.userRepository import UserRepository

@fixture
def mock_household_repo():
    return MagicMock(spec=HouseholdRepository)

@fixture
def mock_user_repo():
    return MagicMock(spec=UserRepository)

@fixture
def household_controller(mock_household_repo, mock_user_repo):
    return HouseholdController(mock_household_repo, mock_user_repo)

def test_get_household(household_controller,mock_household_repo, mock_household):
    # Arrange
    mock_household_repo.get_household.return_value = mock_household

    # Act
    # incoming household id is assumed to be valid, 
    # because the household id is coming from the database.
    result = household_controller.get_household("1")

    # Assert
    mock_household_repo.get_household.assert_called_once_with("1")
    assert result == mock_household

def test_get_household_users(household_controller, mock_user_repo, mock_user):
    # Arrange
    mock_user_repo.get_users.return_value = [mock_user]


    # Act
    result = household_controller.get_household_users("1")

    # Assert
    assert result[0].id == mock_user.google_id

def test_find_household(household_controller,mock_household_repo):
    # Arrange

    # Act
    # incoming household id is assumed to be valid, 
    # because the household id is coming from the database.
    household_controller.find_household("1")

    # Assert
    mock_household_repo.find_household.assert_called_once_with("1")

def test_get_join_code_none_exists(household_controller,mock_household_repo):
    # Arrange
    mock_household_repo.get_join_code.return_value = None


    # Act
    result = household_controller.get_join_code("1")

    # Assert
    mock_household_repo.get_join_code.assert_called_once_with("1")
    mock_household_repo.update_code.assert_called_once()
    assert result != None
    assert len(result.code) == 6
    assert result.expiration_date != None

def test_get_join_code_expired(household_controller,mock_household_repo, mock_join_code):
    # Arrange
    mock_household_repo.get_join_code.return_value = mock_join_code
    mock_join_code.expiration_date = datetime.now(timezone.utc) - timedelta(minutes=1)


    # Act
    result = household_controller.get_join_code("1")

    # Assert
    mock_household_repo.get_join_code.assert_called_once_with("1")
    mock_household_repo.update_code.assert_called_once()
    assert len(result.code) == 6
    assert result.expiration_date != None
    assert result != mock_join_code

def test_get_join_code_valid_exists(household_controller,mock_household_repo, mock_join_code):
    # Arrange
    mock_household_repo.get_join_code.return_value = mock_join_code
    mock_join_code.expiration_date = datetime.now(timezone.utc) + timedelta(minutes=1)


    # Act
    result = household_controller.get_join_code("1")

    # Assert
    mock_household_repo.get_join_code.assert_called_once_with("1")
    assert result == mock_join_code

def test_join_household_nonexistant(household_controller,mock_household_repo, mock_user_repo):
    # Arrange
    mock_household_repo.get_household_by_code.return_value = None
    mock_user_repo.get_user.return_value = ""

    # Act
    result = household_controller.join_household("1", "code")

    # Assert
    mock_household_repo.get_household_by_code.assert_called_once_with("code")
    assert result == None

def test_join_household_user_nonexistant(household_controller,mock_household_repo, mock_user_repo):
    # Arrange
    mock_household_repo.get_household_by_code.return_value = None
    mock_user_repo.get_user.return_value = None

    # Act
    result = household_controller.join_household("1", "code")

    # Assert
    mock_household_repo.get_household_by_code.assert_called_once_with("code")
    assert result == None

def test_join_household_wrong_code_none(household_controller,mock_household_repo, mock_household, mock_user_repo):
    # Arrange
    mock_household.join_code = None
    mock_household_repo.get_household_by_code.return_value = mock_household
    mock_user_repo.get_user.return_value = ""

    # Act
    result = household_controller.join_household("1", "code")

    # Assert
    mock_household_repo.get_household_by_code.assert_called_once_with("code")
    assert result == None

def test_join_household_wrong_code_value(household_controller,mock_household_repo, mock_household, mock_join_code, mock_user_repo):
    # Arrange
    mock_join_code.code = "notcode"
    mock_household.join_code = mock_join_code
    mock_household_repo.get_household_by_code.return_value = mock_household
    mock_user_repo.get_user.return_value = ""

    # Act
    result = household_controller.join_household("1", "code")

    # Assert
    mock_household_repo.get_household_by_code.assert_called_once_with("code")
    assert result == None

def test_join_household_code_expired(household_controller,mock_household_repo, mock_household, mock_join_code, mock_user_repo):
    # Arrange
    mock_join_code.code = "code"
    mock_join_code.expiration_date = datetime.now(timezone.utc) - timedelta(minutes=1)
    mock_household.join_code = mock_join_code
    mock_household_repo.get_household_by_code.return_value = mock_household
    mock_user_repo.get_user.return_value = ""

    # Act
    result = household_controller.join_household("1", "code")

    # Assert
    mock_household_repo.get_household_by_code.assert_called_once_with("code")
    assert result == None

def test_join_household_no_old_household(household_controller,mock_household_repo, mock_household, mock_join_code, mock_user, mock_user_repo):
    # Arrange
    mock_join_code.code = "code"
    mock_join_code.expiration_date = datetime.now(timezone.utc) + timedelta(minutes=1)
    mock_household.join_code = mock_join_code
    mock_household.id = "1"
    mock_household_repo.get_household_by_code.return_value = mock_household
    mock_household_repo.find_household.return_value = None
    mock_user_repo.get_users.return_value = [mock_user]
    mock_user_repo.get_user.return_value = ""

    # Act
    result = household_controller.join_household("1", "code")

    # Assert
    mock_household_repo.get_household_by_code.assert_called_once_with("code")
    mock_household_repo.find_household.assert_called_once_with("1")
    mock_household_repo.add_user.assert_called_once_with(mock_household.id, "1")
    assert len(result) == 1
    assert result[0].id == mock_user.google_id

def test_join_household_leave_old_household(household_controller,mock_household_repo, mock_household, mock_join_code, mock_user, mock_user_repo):
    # Arrange
    mock_join_code.code = "code"
    mock_join_code.expiration_date = datetime.now(timezone.utc) + timedelta(minutes=1)
    mock_household.join_code = mock_join_code
    mock_household.id = "1"
    mock_household_repo.get_household_by_code.return_value = mock_household
    mock_household_repo.get_user_ids.return_value = ["1"]
    mock_household_repo.find_household.return_value = "2"
    mock_user_repo.get_users.return_value = [mock_user]
    mock_user_repo.get_user.return_value = ""

    # Act
    result = household_controller.join_household("1", "code")

    # Assert
    mock_household_repo.delete_household.assert_called_once()
    mock_household_repo.get_household_by_code.assert_called_once_with("code")
    mock_household_repo.find_household.assert_called_once_with("1")
    mock_household_repo.add_user.assert_called_once_with(mock_household.id, "1")
    assert len(result) == 1
    assert result[0].id == mock_user.google_id

def test_join_household_same_household(household_controller,mock_household_repo, mock_household, mock_join_code, mock_user, mock_user_repo):
    # Arrange
    mock_join_code.code = "code"
    mock_join_code.expiration_date = datetime.now(timezone.utc) + timedelta(minutes=1)
    mock_household.join_code = mock_join_code
    mock_household.id = "1"
    mock_household_repo.get_household_by_code.return_value = mock_household
    mock_household_repo.find_household.return_value = "1"
    mock_user_repo.get_users.return_value = [mock_user]
    mock_user_repo.get_user.return_value = ""

    # Act
    result = household_controller.join_household("1", "code")

    # Assert
    mock_household_repo.get_household_by_code.assert_called_once_with("code")
    mock_household_repo.find_household.assert_called_once_with("1")
    mock_household_repo.kick_user.assert_not_called()
    mock_household_repo.delete_household.assert_not_called()
    mock_household_repo.add_user.assert_not_called()
    assert len(result) == 1
    assert result[0].id == mock_user.google_id

def test_kick_user_owner(household_controller,mock_household_repo):
    # Arrange
    mock_household_repo.get_user_ids.return_value = ["1","2"]

    # Act
    result = household_controller.kick_user("1","1")

    # Assert
    mock_household_repo.get_user_ids.assert_called_once_with("1")
    mock_household_repo.delete_household.assert_called_once()
    assert result == None

def test_kick_user(household_controller,mock_household_repo, mock_user_repo, mock_user):
    # Arrange
    mock_household_repo.get_user_ids.return_value = ["2","1"]
    mock_user_repo.get_users.return_value = [mock_user]

    # Act
    result = household_controller.kick_user("1","1")

    # Assert
    mock_household_repo.delete_household.assert_not_called()
    mock_household_repo.kick_user.assert_called_once_with("1","1")
    assert len(result) == 1

def test_kick_user_wrong_id(household_controller,mock_household_repo):
    # Arrange
    mock_household_repo.get_user_ids.return_value = ["2"]

    # Act
    result = household_controller.kick_user("1","1")

    # Assert
    mock_household_repo.get_user_ids.assert_called_once_with("1")
    mock_household_repo.delete_household.assert_not_called()
    assert result == None

def test_create_household(household_controller,mock_household_repo):
    # Arrange
    mock_household_repo.create_household.return_value = "household"

    # Act
    result = household_controller.create_household("1")

    # Assert
    mock_household_repo.create_household.assert_called_once_with("1")
    assert result == 'household'
