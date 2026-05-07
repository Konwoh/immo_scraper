import requests
import json
from backend.shared.helper import Headers
from backend.shared.exceptions import RequestError
from crawler.base_crawler import BaseCrawler

class KleinanzeigenCrawler(BaseCrawler):
    def __init__(self, country: str, city: str, distance: int, listing_count: int, page: int, headers: Headers, estate_type: str, rent_or_buy: str):
        super().__init__(country, city, listing_count, page, headers)
        self.estate_type = estate_type
        self.rent_or_buy = rent_or_buy
        self.distance = distance

    def param_mapping(self, city: str, estate_type: str, rent_or_buy: str) -> tuple[int, int]:
        city = city.lower()
        estate = estate_type + '_' + rent_or_buy
        mapper_dict = {
            "city" : {
                "leipzig" : 4233,
                "halle": 2409,
                "merseburg": 2300,
                "leuna": 16710,
            }, 
            "category" : {
                "house_buy": 208,
                "house_rent": 205,
                "apartment_buy": 196,
                "apartment_rent": 203,
                "property": 207,
            }
        }
        
        if city in mapper_dict["city"].keys() and estate in mapper_dict["category"].keys():
            city_id = mapper_dict["city"][city]
            estate_id = mapper_dict["category"][estate]
        else:
            raise ValueError("Kleinanzeigen-Crawler: city or estate not in mapper_dict")
        
        return city_id, estate_id
    
    def build_url(self) -> str:
        city_id, estate_id = self.param_mapping(self.city, self.estate_type, self.rent_or_buy)
        return f"https://api.kleinanzeigen.de/api/ads.json?categoryId={estate_id}&distance={self.distance}&page={self.page}&size=30&locationId={city_id}"

    def crawl(self) -> tuple[requests.Response, bool]:
        headers = self.headers.build_header()
        url = self.build_url()
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            response_json = json.loads(response.text)
            continue_flag = True
            if len(response_json["{http://www.ebayclassifiedsgroup.com/schema/ad/v1}ads"]["value"]["ad"]) == 0: #prüfung, ob inserate in liste enthalten sind
                continue_flag = False
            return response, continue_flag
        
        except requests.exceptions.SSLError as e:
            raise RequestError("SSL error during request") from e
        except requests.RequestException as e:
            raise RequestError(f"Request failed for URL: {url}") from e