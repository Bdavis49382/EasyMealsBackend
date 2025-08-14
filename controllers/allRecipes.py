from bs4 import BeautifulSoup
from models.Recipe import RecipeLite, Recipe
from unittest.mock import MagicMock
from fastapi import Depends
from typing_extensions import Annotated
from repositories.webRecipesRepository import WebRecipesRepository

import urllib.parse

class AllRecipes():
    def __init__(self, web_recipes_repo: Annotated[WebRecipesRepository, Depends()]):
        self.web_recipes_repo = web_recipes_repo

    def get_recipes_from_page(self,url: str, card_class: str, tag: str="") -> list[RecipeLite]:
        """
        Find all recipes on the page
        """
        try:
            soup = self.web_recipes_repo.get_soup(url)
        except Exception as e:
            print('Allrecipes error: ',e)
            return []

        articles = soup.find_all("a", {"class": card_class})

        print('getting recipes')
        return [RecipeCard(a).get_recipe_lite(tag=tag) for a in articles if "-recipe-" in a["href"] or "/recipe/" in a['href']]

    def search(self,search_string) -> list[RecipeLite]:
        """
        Search recipes parsing the returned html data.
        """
        base_url = "https://allrecipes.com/search?"
        query_url = urllib.parse.urlencode({"q": search_string})

        url = base_url + query_url

        return AllRecipes.get_recipes_from_page(url,  "mntl-card-list-card--extendable")
    
    def get_main_dishes(self) -> list[RecipeLite]:
        return AllRecipes.get_recipes_from_page('https://www.allrecipes.com/recipes/80/main-dish/','mntl-document-card',"MainDishes")
    
    def get_soups(self) -> list[RecipeLite]:
        return AllRecipes.get_recipes_from_page("https://www.allrecipes.com/recipes/16369/soups-stews-and-chili/soup/", 'mntl-document-card',"Soups")
    
    def get_desserts(self) -> list[RecipeLite]:
        return AllRecipes.get_recipes_from_page("https://www.allrecipes.com/recipes/79/desserts/", 'mntl-document-card',"Desserts")

    def get_breakfasts(self) -> list[RecipeLite]:
        return AllRecipes.get_recipes_from_page("https://www.allrecipes.com/recipes/78/breakfast-and-brunch/", 'mntl-document-card',"Breakfast")
    
    def get_recipes_by_tag(self, tags: list[str]) -> list[RecipeLite]:
        out = []
        for tag in tags:
            match (tag.upper()):
                case 'BREAKFAST':
                    recipes = self.get_breakfasts()
                case 'DESSERTS':
                    recipes = self.get_desserts()
                case 'MAINDISHES':
                    recipes = self.get_main_dishes()
                case 'SOUPS':
                    recipes = self.get_soups()
                case _:
                    recipes = []
            out.extend(recipes)
        return out

class BaseRecipe:
    def __init__(self):
        self.failures = []

    def try_find(self, function, name: str, default = ''):
        try:
            return function()
        except:
            self.failures.append(name)
            return default

class RecipeCard(BaseRecipe):
    def __init__(self, soup: BeautifulSoup):
        super().__init__()
        self.soup: BeautifulSoup = soup
        self.title = self.try_find(self._get_title,'title')
        self.src_link = self.try_find(self._get_src_link,'src_link')
        self.rate = self.try_find(self._get_rate, 'rate', None)
        self.img_link = self.try_find(self.get_img_link,'img_link', None)
    
    def get_recipe_lite(self, tag) -> RecipeLite:
        if tag == '':
            return RecipeLite(src_link=self.src_link,title = self.title, img_link=self.img_link, rate=self.rate)
        else:
            return RecipeLite(src_link=self.src_link,title = self.title, img_link=self.img_link, rate=self.rate, tags=[tag])
        
    def _get_title(self):
        return self.soup.find("span", {"class": "card__title"}).get_text().strip(' \t\n\r')
    def _get_src_link(self):
        return self.soup['href']
    def _get_rate(self):
        stars = len(self.soup.find_all("svg", {"class": "icon-star"}))
        try:
            if len(self.soup.find_all("svg", {"class": "icon-star-half"})):
                stars += 0.5
            return stars
        except:
            return stars
    def get_img_link(self):
        try:
            return self.soup.find('img')['data-src']
        except:
            return self.soup.find('img')['src']