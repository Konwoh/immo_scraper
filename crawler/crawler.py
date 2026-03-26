from abc import ABC, abstractmethod
from typing import Optional
import requests
import json
from core.helper import Headers
from core.loki_handler import get_loki_logger
from database.models import SearchParams
from core.exceptions import RequestError

crawler_logger = get_loki_logger("crawler", {"app": "crawler", "env": "dev"})

# Implementation of concrete Crawler
class BaseCrawler(ABC):
    def __init__(self, country:str, city: str, listing_count: int, page: int, headers: Headers):
        self.country = country
        self.city = city
        self.listing_count = listing_count
        self.page = page
        self.headers = headers

    @abstractmethod
    def build_url(self) -> str:
        ...
    
    @abstractmethod
    def crawl(self) -> tuple[requests.Response, bool]:
        ...

class ImmoScoutCrawler(BaseCrawler):
    def __init__(self, country: str, state: str, city:str, zip_code: Optional[str], listing_count: int, estate_type: str, rent_or_buy: str, page: int, headers: Headers):
        super().__init__(country, city, listing_count, page, headers)
        self.state = state
        self.zip_code = zip_code
        self.estate_type = estate_type
        self.rent_or_buy = rent_or_buy

    def build_url(self) -> str:
        return f"https://api.mobile.immobilienscout24.de/search/list?pagenumber={self.page}&realestatetype={self.estate_type + self.rent_or_buy}&searchType=region&geocodes=/{self.country}/{self.state}/{self.city}&pagesize={self.listing_count}"
    
    def crawl(self) -> tuple[requests.Response, int]:
        headers = self.headers.build_header()
        url = self.build_url()
        try:
            response = requests.post(url, headers=headers)
            response.raise_for_status()
            response_json = json.loads(response.text)
            numberOfPages = response_json["numberOfPages"]
            continue_flag = True
            if self.page == numberOfPages:
                continue_flag = False
            return response, continue_flag
        
        except requests.exceptions.SSLError as e:
            raise RequestError("SSL error during request") from e
        except requests.RequestException as e:
            raise RequestError(f"Request failed for URL: {url}") from e

class ImmoWeltCrawler(BaseCrawler):
    def build_url(self) -> str:
        return ""
    
    def crawl(self) -> tuple[requests.Response, bool]:
        return requests.Response(), True

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
    
# Implementation of Crawler Factories
class CrawlerFactory(ABC):

    @abstractmethod
    def create_crawler(self, params: SearchParams, headers: Headers) -> BaseCrawler:
        pass

class ImmoScoutCrawlerFactory(CrawlerFactory):
    def create_crawler(self, params: SearchParams, headers: Headers) -> BaseCrawler:
        return ImmoScoutCrawler(params.country, params.state, params.city, params.zip_code, params.listing_count, params.estate_type, params.rent_or_buy, params.page, headers)
    
class ImmoWeltCrawlerFactory(CrawlerFactory):
    def create_crawler(self, params: SearchParams, headers: Headers) -> BaseCrawler:
        return ImmoWeltCrawler(params.country, params.city, params.listing_count, params.page, headers)

class KleinanzeigenCrawlerFactory(CrawlerFactory):
    def create_crawler(self, params: SearchParams, headers: Headers) -> BaseCrawler:
        return KleinanzeigenCrawler(params.country, params.city, params.distance, params.listing_count, params.page, headers, params.estate_type, params.rent_or_buy)
    

# Function to instantiate Crawler Factories depending on input
def create_factory(site: str) -> CrawlerFactory:
    fac = {
        "Immoscout": ImmoScoutCrawlerFactory(),
        "Immowelt": ImmoWeltCrawlerFactory(),
        "Kleinanzeigen": KleinanzeigenCrawlerFactory()
    }
    
    return fac[site]
