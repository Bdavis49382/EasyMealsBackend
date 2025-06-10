from pytest import mark, fixture
from models.User import User
from models.Recipe import RecipeOut
from repositories.userRepository import UserRepository

@fixture
def user_repo(mock_collection):
    return UserRepository(mock_collection)

def test_create_user(user_repo, mock_document, mock_user, mock_user_dict):
    # Arrange

    # Act
    result: str = user_repo.create_user(mock_user)

    # Assert
    mock_document.set.assert_called_once()
    mock_user.model_dump.assert_called_once()
    mock_document.set.assert_called_with(mock_user_dict)
    assert result == mock_user.google_id

def test_get_user(user_repo, mock_snapshot, mock_user_dict):
    # Arrange
    mock_snapshot.to_dict.return_value = mock_user_dict

    # Act
    result: User = user_repo.get_user("1")

    # Assert
    mock_snapshot.to_dict.assert_called_once()
    assert result == User.model_validate(mock_user_dict)
    
def test_get_user_wrong_id(user_repo, mock_snapshot):
    # Arrange
    mock_snapshot.to_dict.return_value = ""
    

    # Act
    result: User = user_repo.get_user("1")

    # Assert
    mock_snapshot.to_dict.assert_called_once()
    assert result == None

def test_get_users_no_whitelist(mock_collection, user_repo, mock_snapshot, mock_user_dict):
    # Arrange
    mock_collection.where.return_value = []
    mock_collection.get.return_value = [mock_snapshot]
    mock_snapshot.to_dict.return_value = mock_user_dict
    

    # Act
    result: list[User] = user_repo.get_users()

    # Assert
    mock_collection.assert_not_called()
    assert result[0] == User.model_validate(mock_user_dict)
    assert len(result) == 1

def test_get_users_with_whitelist(mock_collection, user_repo, mock_snapshot, mock_user_dict):
    # Arrange
    mock_collection.where.return_value = [mock_snapshot]
    mock_collection.get.return_value = []
    mock_snapshot.to_dict.return_value = mock_user_dict
    
    # Act
    result: list[User] = user_repo.get_users(["fake"])

    # Assert
    mock_collection.assert_not_called()
    assert result[0] == User.model_validate(mock_user_dict)
    assert len(result) == 1

def test_add_recipe(user_repo, mock_document, mock_recipe):
    # Arrange
    
    # Act
    user_repo.add_recipe("1", mock_recipe)

    # Assert
    mock_document.update.assert_called_once()
    mock_recipe.model_dump.assert_called_once()

def test_update_recipe(user_repo, mock_document, mock_recipe):
    # Arrange
    
    # Act
    user_repo.update_recipe("1","1", mock_recipe)

    # Assert
    mock_document.update.assert_called_once()
    mock_recipe.model_dump.assert_called_once()

def test_get_user_recipes_empty(user_repo, mock_snapshot, mock_user_dict):
    # Arrange
    mock_snapshot.to_dict.return_value = mock_user_dict
    mock_user_dict['recipes'] = {}
    

    # Act
    result: list[RecipeOut] = user_repo.get_user_recipes("1")

    # Assert
    mock_snapshot.to_dict.assert_called_once()
    assert len(result) == 0

def test_get_user_recipes(user_repo, mock_snapshot, mock_user_dict, mock_recipe_dict):
    # Arrange
    mock_snapshot.to_dict.return_value = mock_user_dict
    

    # Act
    result: list[RecipeOut] = user_repo.get_user_recipes("1")

    # Assert
    mock_snapshot.to_dict.assert_called_once()
    assert len(result) == 1
    # the result should be the same recipe we entered in the "database"
    assert result[0].model_dump() == mock_recipe_dict
    assert result[0].id == "fake_id"

@mark.parametrize("test_input, expected", [( "fake", 1 ), ( "FAKE", 1), ("f",1), ("Flake", 0)])
def test_search_user_recipes(user_repo, mock_snapshot, mock_user_dict, mock_recipe_dict, test_input, expected):
    # Arrange
    mock_snapshot.to_dict.return_value = mock_user_dict
    

    # Act
    result: list[RecipeOut] = user_repo.search_user_recipes("1",test_input)

    # Assert
    mock_snapshot.to_dict.assert_called()
    assert len(result) == expected

def test_add_record(user_repo, mock_document, mock_record):
    # Arrange
    
    # Act
    user_repo.add_recipe_record("1","1", mock_record)

    # Assert
    mock_document.update.assert_called_once()
    mock_record.model_dump.assert_called_once()