from pytest import fixture, mark
from copy import deepcopy
from unittest.mock import MagicMock
from repositories.householdRepository import HouseholdRepository
from repositories.userRepository import UserRepository
from controllers.feedController import FeedController
from controllers.allRecipes import AllRecipes
from models.Recipe import RecipeLite
from copy import deepcopy
@fixture
def mock_household_repo():
    return MagicMock(spec=HouseholdRepository)

@fixture
def mock_user_repo():
    return MagicMock(spec=UserRepository)

@fixture
def mock_all_recipes():
    return MagicMock(spec=AllRecipes)

@fixture
def feed_controller(mock_household_repo, mock_user_repo, mock_all_recipes):
    return FeedController(mock_household_repo, mock_user_repo, mock_all_recipes)

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
    assert result[0][0].title == mock_recipe.title
    assert result[0][0].img_link == mock_recipe.img_link
    assert result[0][0].id == mock_recipe.id

@mark.parametrize('page,amount_expected',[(-1,15),(0,10),(1,5),(2,0),(200,0)])
def test_get_user_recipes_no_filter_with_paging(page,amount_expected,feed_controller,mock_user_repo, mock_household_repo, mock_recipe):
    # Arrange
    mock_household_repo.get_user_ids.return_value = ["1"]
    mock_recipe.id = "1"
    fake_recipes = {}
    [fake_recipes.setdefault(x,mock_recipe) for x in range(15)]
    mock_user_repo.get_user_recipes.return_value = fake_recipes

    # Act
    result = feed_controller.get_user_recipes("1",page=page)

    # Assert
    assert len(result) == amount_expected

def test_tag_hits(feed_controller, mock_recipe):
    # Arrange
    mock_recipe.tags = ["testTag","testTag2", "testTag3"]

    # Act
    result = feed_controller._tag_hits(mock_recipe, tags=["TESTTAG","TESTTAG2"])

    # Assert
    assert result == 2

def test_keyword_hits(feed_controller, mock_recipe):
    # Arrange
    mock_recipe.title = "tester testing tests"

    # Act
    result = feed_controller._keyword_hits(mock_recipe, keywords="recipe for tests and testing".split(' '))

    # Assert
    assert result == 200

@mark.parametrize('keywords,tags,expected_amount',
    [(['flake'],[],0),
     (['fake'],[],100),
     (['FAKE'],[],100),
     (['Fake'],[],100),
     (['flfake testf l-;'],[],100),
     ([],[],0),
     ([],['flake'],0),
     ([],['fake'],1),
     ([],['FAKE'],1),
     ([],['Fake'],1),
     ([],['flfakef l-;'],0),
     (['fake'],['fake'],101),
     (['fake'],['fake','test'],102),
     (['fake', 'test'],['fake'],201)
     ])
def test_get_user_recipes_filtered(keywords, tags, expected_amount, feed_controller,mock_user_repo, mock_household_repo, mock_recipe):
    # Arrange
    mock_household_repo.get_user_ids.return_value = ["1"]
    mock_recipe.id = "1"
    mock_recipe.title = "fake test"
    mock_recipe.tags = ["fake","test"]
    mock_recipe.rate = None
    mock_user_repo.get_user_recipes.return_value = { '10': mock_recipe }

    # Act
    result = feed_controller.get_user_recipes("1", keywords=keywords, tags=tags)

    # Assert
    assert len(result) == 1
    assert result[0][1] == expected_amount
    assert isinstance(result[0][0],RecipeLite)

@mark.parametrize('keywords,tags,expected_amount',
    [('flake',[],0),
     ('fake',[],100),
     ('FAKE',[],100),
     ('Fake',[],100),
     ('flfake testf l-;',[],0),
     ('',[],0),
     ('fake',['fake'],101),
     ('fake test',['fake'],201)
     ])
def test_search_all_recipes(keywords, tags, expected_amount, feed_controller, mock_all_recipes, mock_recipe):
    # Arrange
    mock_all_recipes.get_recipes_by_tag.return_value = [mock_recipe]
    mock_recipe.id = "1"
    mock_recipe.title = "fake test"
    mock_recipe.tags = ["fake","test"]
    mock_all_recipes.search.return_value = [mock_recipe]

    # Act
    result = feed_controller.search_all_recipes(keywords=keywords, tags=tags)

    # Assert
    if len(tags) != 0 or len(keywords.strip()) != 0:
        assert len(result) >= 1
        assert result[0][1] == expected_amount
    else:
        assert len(result) == 0

def test_get_suggested_recipes(feed_controller, mock_all_recipes, mock_recipe):
    # Arrange
    mock_all_recipes.get_main_dishes.return_value = [mock_recipe for _ in range(50)]
    mock_all_recipes.get_soups.return_value = [mock_recipe for _ in range(50)]
    mock_all_recipes.get_breakfasts.return_value = [mock_recipe for _ in range(50)]
    mock_all_recipes.get_desserts.return_value = [mock_recipe for _ in range(50)]

    # Act
    result = feed_controller.get_suggested_recipes()

    # Assert
    assert len(result) == 50

def test_get_suggested_recipes_all_recipes_fails(feed_controller, mock_all_recipes, mock_recipe):
    # Arrange
    mock_all_recipes.get_main_dishes.return_value = [mock_recipe for _ in range(50)]
    mock_all_recipes.get_soups.return_value = [mock_recipe for _ in range(50)]
    mock_all_recipes.get_breakfasts.return_value = [mock_recipe for _ in range(50)]
    mock_all_recipes.get_desserts.return_value = [mock_recipe for _ in range(40)]

    # Act
    result = feed_controller.get_suggested_recipes()

    # Assert
    assert len(result) < 50 # the last page failed to provide 50 items so was ignored.

@mark.parametrize('page',[(0),(3),(5),(400)])
def test_get_suggested_recipes_handles_any_page(feed_controller, mock_all_recipes, mock_recipe, page):
    # Arrange
    mock_all_recipes.get_main_dishes.return_value = [mock_recipe for _ in range(50)]
    mock_all_recipes.get_soups.return_value = [mock_recipe for _ in range(50)]
    mock_all_recipes.get_breakfasts.return_value = [mock_recipe for _ in range(50)]
    mock_all_recipes.get_desserts.return_value = [mock_recipe for _ in range(50)]

    # Act
    result = feed_controller.get_suggested_recipes(page=page)

    # Assert
    assert len(result) == 50

def test_get_user_tags(feed_controller,mock_user_repo,):
    # Arrange
    mock_user_repo.get_user_tags.return_value = set(['fakeTag'])

    # Act
    result = feed_controller.get_user_tags("1")

    # Assert
    assert len(result) == 5 # At the moment, the allrecipes tags are added directly in the code here. Likely to change later.
    assert 'fakeTag' in result

def test_remove_duplicates_has_duplicate( feed_controller, mock_recipe, mock_household_repo, mock_user_repo):
    # Arrange
    mock_household_repo.get_user_ids.return_value = ["1"]
    mock_user_repo.get_user_recipes.return_value = {"1":mock_recipe}

    # Act
    result = feed_controller.remove_duplicates([mock_recipe], [mock_recipe],"1")

    # Assert
    assert len(result) == 1

def test_remove_duplicates_unique( feed_controller, mock_recipe, mock_household_repo, mock_user_repo):
    # Arrange
    mock2 = deepcopy(mock_recipe)
    mock2.title = "not the same"
    mock_household_repo.get_user_ids.return_value = ["1"]
    mock_user_repo.get_user_recipes.return_value = {"1":mock_recipe}

    # Act
    result = feed_controller.remove_duplicates([mock_recipe], [mock2],"1")

    # Assert
    assert len(result) == 2

def test_remove_duplicates_search_has_duplicate( feed_controller, mock_recipe, mock_household_repo, mock_user_repo):
    # Arrange
    mock_household_repo.get_user_ids.return_value = ["1"]
    mock_user_repo.get_user_recipes.return_value = {"1":mock_recipe}

    # Act
    result = feed_controller.remove_duplicates_search([(mock_recipe,1)], [(mock_recipe,1)],"1")

    # Assert
    assert len(result) == 1

def test_remove_duplicates_search_unique( feed_controller, mock_recipe, mock_household_repo, mock_user_repo):
    # Arrange
    mock2 = deepcopy(mock_recipe)
    mock2.title = "not the same"
    mock_household_repo.get_user_ids.return_value = ["1"]
    mock_user_repo.get_user_recipes.return_value = {"1":mock_recipe}

    # Act
    result = feed_controller.remove_duplicates_search([(mock_recipe,1)], [(mock2,1)],"1")

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

def test_sort_search_recipes(feed_controller, mock_recipe):
    # Arrange
    mock_recipe.id = ""
    lite = RecipeLite.make_from_full(mock_recipe)
    lite2 = deepcopy(lite)

    # Act
    result = feed_controller.sort_search_recipes([(lite,1),(lite2, 2)])

    # Assert
    assert len(result) == 2
    assert result[0] == lite2
    assert result[1] == lite