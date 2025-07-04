from bs4 import BeautifulSoup
from models.Recipe import RecipeLite
from unittest.mock import MagicMock
from functools import lru_cache

import urllib.parse
import urllib.request

import ssl


class AllRecipes():

    @staticmethod
    def _get_soup(url:str) -> BeautifulSoup:
        req = urllib.request.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36')

        handler = urllib.request.HTTPSHandler(context=ssl._create_unverified_context())
        opener = urllib.request.build_opener(handler)
        response = opener.open(req)
        html_content = response.read()

        return BeautifulSoup(html_content, 'html.parser')

    @lru_cache
    @staticmethod
    def get_recipes_from_page(url: str, card_class: str, tag: str="") -> list[RecipeLite]:
        """
        Find all recipes on the page
        """
        try:
            soup = AllRecipes._get_soup(url)
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


    def get(self, url):
        """
        'url' from 'search' method.
            ex. "/recipe/106349/beef-and-spinach-curry/"
        """
        # base_url = "https://allrecipes.com/"
        # url = base_url + uri

        soup = self._get_soup(url)

        return RecipePage(url,soup)

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


class RecipePage(BaseRecipe):
    def __init__(self, url: str, soup: BeautifulSoup):
        super().__init__()
        self.src_link: str = url
        self.soup: BeautifulSoup = soup
        self.name = self.try_find(self._get_name,'name')
        self.ingredients = self.try_find(self._get_ingredients, 'ingredients', [])
        self.steps = self.try_find(self._get_steps, 'steps', [])
        self.rating = self.try_find(self._get_rating,'rating')
        self.prep_time = self.try_find(self._get_prep_time,'prep_time')
        self.cook_time = self.try_find(self._get_cook_time,'cook_time')
        self.total_time = self.try_find(self._get_total_time,'total_time')
        self.nb_servings = self.try_find(self._get_nb_servings,'nb_servings',None)
        self.image = self.try_find(self._get_image,'image')
    
    def try_find(self, function, name: str, default = ''):
        try:
            return function()
        except:
            self.failures.append(name)
            return default

    def _get_times_data(self, text):
        labels = self.soup.find_all("div", {"class":"mm-recipes-details__label"})
        values = self.soup.find_all("div", {"class":"mm-recipes-details__value"})
        res = zip(labels,values)
        data = {}
        for i in res:
            data[i[0].text] = i[1].text
        return data[text]

    def _get_name(self):
        return self.soup.find("h1", {"class": "article-heading"}).get_text().strip(' \t\n\r')

    def _get_ingredients(self):
            return [li.get_text().strip(' \t\n\r') for li in self.soup.find("div", {"id": "mm-recipes-structured-ingredients_1-0"}).find_all("li")]

    def _get_steps(self):
            return [li.get_text().strip(' \t\n\r') for li in self.soup.find("div", {"id": "mm-recipes-steps_1-0"}).find_all("p",{"class": "mntl-sc-block-html"})]
    
    def _get_rating(self):
        return float(self.soup.find("div", {"id": "mm-recipes-review-bar__rating_1-0"}).get_text().strip(' \t\n\r'))

    def _get_prep_time(self):
        return self._get_times_data("Prep Time:")

    def _get_cook_time(self):
        return self._get_times_data("Cook Time:")
    
    def _get_total_time(self):
        return self._get_times_data("Total Time:")
    
    def _get_nb_servings(self):
        return self._get_times_data("Servings:")
    
    def _get_image(self):
        try:
            return self.soup.find("figure", {"class": "mntl-universal-primary-image"}).find("img").get('src')
        except:
            return self.soup.find("div",{"id":"article__photo-ribbon_1-0"}).find_all("img")[0].get('data-src')