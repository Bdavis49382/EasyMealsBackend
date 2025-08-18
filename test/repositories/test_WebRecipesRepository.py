from repositories.webRecipesRepository import RecipeData, WebRecipesRepository
from pytest import fixture

@fixture(scope="module")
def test_recipe_dict():
    return {
        "image": {
            "@type": "ImageObject",
            "url": "https://fakeurl.com",
            "height": 1125,
            "width": 1500
        },
        "name": "Slow Cooker Lime Cilantro Chicken",
        "aggregateRating": {
            "@type": "AggregateRating",
            "ratingValue": "4.6",
            "ratingCount": "1874"
        },
        "cookTime": "PT240M",
        "prepTime": "PT15M",
        "recipeCategory": [
            "Dinner"
        ],
        "recipeCuisine": [
            "Mexican Inspired",
            "American"
        ],
        "recipeIngredient": [
            "1 (16 ounce) jar salsa",
            "1 (1.25 ounce) package dry taco seasoning mix",
            "1 medium lime, juiced",
            "3 tablespoons chopped fresh cilantro",
            "3 pounds skinless, boneless chicken breast halves"
        ],
        "recipeInstructions": [
            {
            "@type": "HowToStep",
            "image": [
                {
                "@type": "ImageObject",
                "url": "https://www.allrecipes.com/thmb/fzcj2-q3F3p6JiAYEXzV7x0L5mg=/1500x0/filters:no_upscale():max_bytes(150000):strip_icc()/RM-218863-SlowCookerCilantroLimeChicken-ddmfs-step1-3x4-6832-ec8e4a2310f84c94a2e70baa375dffdb.jpg"
                }
            ],
            "text": "Gather all ingredients."
            },
            {
            "@type": "HowToStep",
            "image": [
                {
                "@type": "ImageObject",
                "url": "https://www.allrecipes.com/thmb/t9jGHOnugNX4LXJEwG4WhiWhTNE=/1500x0/filters:no_upscale():max_bytes(150000):strip_icc()/RM-218863-SlowCookerCilantroLimeChicken-ddmfs-step3-3x4-68361-1f68fa504ff8474ea1c58014a7f5b210.jpg"
                }
            ],
            "text": "Stir salsa, taco seasoning, lime juice, and cilantro together in a slow cooker until well combined. Add chicken and spoon salsa mixture over top to coat."
            },
            {
            "@type": "HowToStep",
            "text": "Cover and cook until chicken is no longer pink in the center and the juices run clear, on Low for 6 to 8 hours or High for 4 hours. An instant-read thermometer inserted into the center should read at least 165 degrees F (74 degrees C)."
            },
            {
            "@type": "HowToStep",
            "image": [
                {
                "@type": "ImageObject",
                "url": "https://www.allrecipes.com/thmb/iSlvOzdN9J3NkkwC5myfWRhSPnU=/1500x0/filters:no_upscale():max_bytes(150000):strip_icc()/RM-218863-SlowCookerCilantroLimeChicken-ddmfs-step4-3x4-6969-553dea13bd5842239ae03267f16ccca4.jpg"
                }
            ],
            "text": "Shred chicken in the crock with two forks, then mix with the sauce."
            },
            {
            "@type": "HowToStep",
            "image": [
                {
                "@type": "ImageObject",
                "url": "https://www.allrecipes.com/thmb/R51lWXmSQWzHmL6H7MaRCgQUZ2I=/1500x0/filters:no_upscale():max_bytes(150000):strip_icc()/RM-218863-SlowCookerCilantroLimeChicken-ddmfs-3x4-7030-f166f0f726d24ee3b1d12856f5244b08.jpg"
                }
            ],
            "text": "Enjoy!"
            }
        ],
        "recipeYield": "12",
        "totalTime": "PT255M",
    }


def test_get_empty():
    # Act
    recipe = RecipeData("https://www.fakerecipes.com",{})

    # Assert
    assert recipe.recipe == None

def test_get_live_all_recipes():
    # Act
    result = WebRecipesRepository().get("https://www.allrecipes.com/recipe/218863/slow-cooker-cilantro-lime-chicken/")

    # Assert
    assert result != None
    assert len(result.failures) == 0
    assert result.recipe.title ==  "Slow Cooker Lime Cilantro Chicken"

def test_get_live_lilluna():
    # Act
    result = WebRecipesRepository().get("https://lilluna.com/dr-pepper-ribs/")

    # Assert
    assert result != None
    assert len(result.failures) == 0
    assert result.recipe.title == 'Dr. Pepper Ribs Recipe'

def test_get_live_other():
    # Act
    result = WebRecipesRepository().get("https://www.laurafuentes.com/fluffy-pancakes-recipe/")

    # Assert
    assert result != None
    assert len(result.failures) == 0
    assert result.recipe.title == 'Best Fluffy Pancake Recipe'
    assert len(result.recipe.instructions) > 0

def test_get_live_no_data():
    # Act
    result = WebRecipesRepository().get("https://www.shemakesandbakes.com/home/perfect-pancakes")

    # Assert
    assert result != None
    assert len(result.failures) == 7
    assert result.recipe == None

def test_get_full(test_recipe_dict):
    # Act
    recipe_data = RecipeData("https://www.fakerecipe.com/recipe1",test_recipe_dict)
    recipe = recipe_data.recipe

    # Assert
    assert recipe != None
    assert recipe.title == test_recipe_dict['name']
    assert recipe.img_link == test_recipe_dict['image']['url']
    assert len(recipe.ingredients) == len(test_recipe_dict['recipeIngredient'])
    assert recipe.ingredients[0] == test_recipe_dict['recipeIngredient'][0]
    assert len(recipe.instructions) == len(test_recipe_dict['recipeInstructions'])
    assert recipe.instructions[0] == test_recipe_dict['recipeInstructions'][0]['text']
    assert recipe.src_link == "https://www.fakerecipe.com/recipe1"
    assert recipe.src_name == "www.fakerecipe.com"
    assert recipe.time_estimate[0] == "4 hrs 15 mins"
    assert recipe.servings == test_recipe_dict['recipeYield']

def test_get_handles_non_essential_not_there(test_recipe_dict):
    # Arrange
    del test_recipe_dict['recipeYield']

    # Act
    recipe_data = RecipeData("https://www.fakerecipe.com/recipe1",test_recipe_dict)
    recipe = recipe_data.recipe

    # Assert
    assert recipe != None
    assert len(recipe_data.failures) == 1
    assert recipe_data.failures[0] == 'recipeYield'
    assert recipe.servings == None

    assert recipe.title == test_recipe_dict['name']
    assert recipe.img_link == test_recipe_dict['image']['url']
    assert len(recipe.ingredients) == len(test_recipe_dict['recipeIngredient'])
    assert recipe.ingredients[0] == test_recipe_dict['recipeIngredient'][0]
    assert len(recipe.instructions) == len(test_recipe_dict['recipeInstructions'])
    assert recipe.instructions[0] == test_recipe_dict['recipeInstructions'][0]['text']
    assert recipe.src_link == "https://www.fakerecipe.com/recipe1"
    assert recipe.src_name == "www.fakerecipe.com"
    assert recipe.time_estimate[0] == "4 hrs 15 mins"

    # Tear Down
    test_recipe_dict['recipeYield'] = '15'

def test_get_handles_essential_not_there(test_recipe_dict):
    # Arrange
    del test_recipe_dict['name']

    # Act
    recipe_data = RecipeData("https://www.fakerecipe.com/recipe1",test_recipe_dict)
    recipe = recipe_data.recipe

    # Assert
    assert recipe == None
    assert len(recipe_data.failures) == 1
    assert recipe_data.failures[0] == 'name'

    # Tear Down
    test_recipe_dict['name'] = 'fake recipe'