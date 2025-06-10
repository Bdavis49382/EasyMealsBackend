from controllers.userController import UserController
from repositories.userRepository import UserRepository
from pytest import fixture, mark
from unittest.mock import MagicMock

@fixture
def mock_user_repo():
    return MagicMock(spec=UserRepository)

@fixture
def user_controller(mock_user_repo):
    return UserController(mock_user_repo)

def test_create_user(user_controller,mock_user_repo, mock_user):
    # Arrange
    mock_user_repo.create_user.return_value = mock_user.google_id
    # Act
    result = user_controller.create_user(mock_user)
    # Assert
    assert result == mock_user.google_id

def test_get_user(user_controller, mock_user_repo, mock_user):
    # Arrange
    mock_user_repo.get_user.return_value = mock_user
    # Act
    result = user_controller.get_user("1")
    # Assert
    assert result.recipes == "0 recipes"
    assert result.id == mock_user.google_id

def test_get_users(user_controller, mock_user_repo, mock_user):
    # Arrange
    mock_user_repo.get_users.return_value = [mock_user]
    # Act
    result = user_controller.get_users(["whitelist"])
    # Assert
    assert result[0].recipes == "0 recipes"
    assert result[0].id == mock_user.google_id
    mock_user_repo.get_users.assert_called_once_with(["whitelist"])