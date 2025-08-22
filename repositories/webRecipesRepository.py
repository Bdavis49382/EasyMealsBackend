import urllib.request, urllib.parse, ssl, json
from models.Recipe import Recipe
from bs4 import BeautifulSoup
from pydantic_core import ValidationError
from functools import lru_cache
from fastapi import HTTPException
import re

class WebRecipesRepository:
    def get_soup(self,url:str) -> BeautifulSoup:
        return WebRecipesRepository._get_soup(url)
    
    @lru_cache
    @staticmethod
    def _get_soup(url:str) -> BeautifulSoup:
        try:
            req = urllib.request.Request(url)
            req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36')

            handler = urllib.request.HTTPSHandler(context=ssl._create_unverified_context())
            opener = urllib.request.build_opener(handler)
            response = opener.open(req)
            html_content = response.read()

            return BeautifulSoup(html_content, 'html.parser')
        except:
            raise HTTPException(status_code=404, detail="Invalid provided URL.")
    
    def get_recipe_dict(self, soup):
        info = soup.find("script",attrs={"type":"application/ld+json"})
        if info is None:
            return {}
        data = json.loads(info.contents[0])
        if type(data) == list and len(data) > 0:
            return data[0]
        elif '@graph' in data:
            return [x for x in data['@graph'] if x['@type'] == 'Recipe'][0]
        else:
            return data

    def get(self, url):
        """
        'url' from 'search' method.
            ex. "/recipe/106349/beef-and-spinach-curry/"
        """
        # base_url = "https://allrecipes.com/"
        # url = base_url + uri

        soup = self.get_soup(url)
        return RecipeData(url, self.get_recipe_dict(soup))

class RecipeData:
    def __init__(self, url, recipe_dict):
        self.url = url
        self.recipe_dict = recipe_dict
        self.failures = []
        self.recipe = self.get_recipe()
    
    def get_recipe(self) -> Recipe | None:
        try:
            full_recipe = Recipe(
                title = self.get_value('name'),
                instructions = self.get_instructions(),
                img_link = self.get_value('url',self.get_value('image', expects_dict=True)),
                servings = self.get_servings(),
                time_estimate= self.convert_time(self.get_value('totalTime')),
                src_link= self.url,
                src_name=urllib.parse.urlparse(self.url).hostname,
                ingredients= self.get_ingredients()
            )
            return full_recipe
        except ValidationError as e:
            print(e)
            return None
    
    def get_ingredients(self):
        return self.convert_fractions(self.get_value('recipeIngredient', expects_list=True))
    
    def fractionize(self, decimal_value: str):
        table = {
            "5":"½",
            "25":"¼",
            "75":"¾",
            "125":"⅛",
            "375":"⅜",
            "625":"⅝",
            "875":"⅞",
            "3":"⅓",
            "6":"⅔"

        }
        for key in table.keys():
            if decimal_value.startswith(key):
                return table[key]
        return "." + decimal_value

    def convert_fractions(self, ingredients: list[str]) -> list[str]:
        for i in range(len(ingredients)):
            result = re.findall('\\d{1,2}\\.\\d+', ingredients[i])
            for decimal in result:
                parts = decimal.split(".")
                fraction = f"{parts[0] if parts[0] != '0' else ''} {self.fractionize(parts[1].strip())}".strip()
                ingredients[i] = ingredients[i].replace(decimal,fraction)
            
        return ingredients



    def get_value(self, key: str, recipe: dict| list = None, expects_list: bool = False, expects_dict: bool = False):
        if recipe == None:
            recipe = self.recipe_dict
        
        if type(recipe) == str:
            return recipe
        
        if type(recipe) == list:
            return recipe[0]
        elif key in recipe:
            if type(recipe[key]) == list and expects_list == False:
                return recipe[key][0]
            return recipe[key]
        else:
            self.failures.append(key)
            if expects_list:
                return []
            elif expects_dict:
                return {}
            else:
                return None
    
    def convert_time(self, str: str | None):
        if str == None:
            return []
        try:
            minutes = int(str.replace('P','').replace('T','').replace('M',''))
            return [f'{minutes // 60} hrs {minutes % 60} mins']
        except:
            return []
    
    def get_servings(self):
        servings = self.get_value('recipeYield')
        if servings == None:
            return None
        else:
            return str(servings)
    
    def get_instructions(self):
        raw_instructions = self.get_value('recipeInstructions', expects_list=True)
        instructions = []
        for step in raw_instructions:
            if '@type' in step and step['@type'] == 'HowToStep':
                instructions.append(self.get_value("text", recipe=step))
            elif '@type' in step and step['@type'] == 'HowToSection':
                section = self.get_value('itemListElement',recipe=step)
                instructions.append(self.get_value("text", recipe=section))
        return instructions
