from bs4 import BeautifulSoup

import urllib.parse
import urllib.request

import ssl


class AllRecipes(object):

    @staticmethod
    def get_recipes_from_page(url: str, card_class: str):
        req = urllib.request.Request(url)
        req.add_header('Cookie', 'euConsent=true')

        handler = urllib.request.HTTPSHandler(context=ssl._create_unverified_context())
        opener = urllib.request.build_opener(handler)
        response = opener.open(req)
        html_content = response.read()

        soup = BeautifulSoup(html_content, 'html.parser')

        search_data = []
        articles = soup.findAll("a", {"class": card_class})

        articles = [a for a in articles if "-recipe-" in a["href"] or "/recipe/" in a['href']]

        for article in articles:
            data = {}
            try:
                data["title"] = article.find("span", {"class": "card__title"}).get_text().strip(' \t\n\r')
                data["src_link"] = article['href']
                try:
                    data["rate"] = len(article.find_all("svg", {"class": "icon-star"}))
                    try:
                        if len(article.find_all("svg", {"class": "icon-star-half"})):
                            data["rate"] += 0.5
                    except Exception:
                        pass
                except Exception as e0:
                    data["rate"] = None
                try:
                    data["img_link"] = article.find('img')['data-src']
                except Exception as e1:
                    try:
                        data["img_link"] = article.find('img')['src']
                    except Exception as e1:
                        pass
                    if "img_link" not in data:
                        data["img_link"] = None
            except Exception as e2:
                pass
            if data:
                search_data.append(data)

        return search_data


    @staticmethod
    def search(search_string):
        """
        Search recipes parsing the returned html data.
        """
        base_url = "https://allrecipes.com/search?"
        query_url = urllib.parse.urlencode({"q": search_string})

        url = base_url + query_url

        return AllRecipes.get_recipes_from_page(url,  "mntl-card-list-card--extendable")
    
    @staticmethod
    def get_main_dishes():
        return AllRecipes.get_recipes_from_page('https://www.allrecipes.com/recipes/80/main-dish/','mntl-document-card')

    @staticmethod
    def _get_name(soup):
        return soup.find("h1", {"class": "article-heading"}).get_text().strip(' \t\n\r')

    @staticmethod
    def _get_rating(soup):
        return float(soup.find("div", {"id": "mm-recipes-review-bar__rating_1-0"}).get_text().strip(' \t\n\r'))

    @staticmethod
    def _get_ingredients(soup):
        return [li.get_text().strip(' \t\n\r') for li in soup.find("div", {"id": "mm-recipes-structured-ingredients_1-0"}).find_all("li")]

    @staticmethod
    def _get_steps(soup):
        return [li.get_text().strip(' \t\n\r') for li in soup.find("div", {"id": "mm-recipes-steps_1-0"}).find_all("li")]

    @staticmethod
    def _get_times_data(soup, text):
        labels = soup.find_all("div", {"class":"mm-recipes-details__label"})
        values = soup.find_all("div", {"class":"mm-recipes-details__value"})
        res = zip(labels,values)
        data = {}
        for i in res:
            data[i[0].text] = i[1].text
        return data[text]
    
    @staticmethod
    def _get_image_data(soup):
        return soup.find("div",{"id":"article-content_1-0"}).find("img", {"class": "mntl-image"}).get("data-hi-res-src","")


    @classmethod
    def _get_prep_time(cls, soup):
        return cls._get_times_data(soup, "Prep Time:")

    @classmethod
    def _get_cook_time(cls, soup):
        return cls._get_times_data(soup, "Cook Time:")

    @classmethod
    def _get_total_time(cls, soup):
        return cls._get_times_data(soup, "Total Time:")

    @classmethod
    def _get_nb_servings(cls, soup):
        return cls._get_times_data(soup, "Servings:")
    
    @classmethod
    def _get_image(cls, soup):
        return cls._get_image_data(soup)

    @classmethod
    def get(cls, url):
        """
        'url' from 'search' method.
            ex. "/recipe/106349/beef-and-spinach-curry/"
        """
        # base_url = "https://allrecipes.com/"
        # url = base_url + uri

        req = urllib.request.Request(url)
        req.add_header('Cookie', 'euConsent=true')

        handler = urllib.request.HTTPSHandler(context=ssl._create_unverified_context())
        opener = urllib.request.build_opener(handler)
        response = opener.open(req)
        html_content = response.read()

        soup = BeautifulSoup(html_content, 'html.parser')

        elements = [
            {"name": "name", "default_value": ""},
            {"name": "ingredients", "default_value": []},
            {"name": "steps", "default_value": []},
            {"name": "rating", "default_value": None},
            {"name": "prep_time", "default_value": ""},
            {"name": "cook_time", "default_value": ""},
            {"name": "total_time", "default_value": ""},
            {"name": "nb_servings", "default_value": ""},
            {"name": "image", "default_value": ""},
        ]

        data = {"src_link": url}
        for element in elements:
            try:
                data[element["name"]] = getattr(cls, "_get_" + element["name"])(soup)
            except:
                data[element["name"]] = element["default_value"]

        return data
