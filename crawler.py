from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Dict
import requests

class Headers:
    def __init__(self, accept, user_agent, accept_language) -> None:
        self.accept = accept
        self.user_agent = user_agent
        self.accept_language = accept_language
    
    def build_header(self) -> Dict[str, str]:
        headers = {}
        headers["accept"] = self.accept
        headers["user-agent"] = self.user_agent
        headers["accept-language"] = self.accept_language
        
        return headers

@dataclass
class SearchParams:
    country: str
    state: str
    city: str
    estate_type: str
    rent_or_buy: str
    listing_count: int
    page: int
    plz: Optional[str] = None

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
    def crawl(self) -> requests.Response:
        ...

class ImmoScoutCrawler(BaseCrawler):
    def __init__(self, country: str, state: str, city:str, plz: Optional[str], listing_count: int, estate_type: str, rent_or_buy: str, page: int, headers: Headers):
        super().__init__(country, city, listing_count, page, headers)
        self.state = state
        self.plz = plz
        self.estate_type = estate_type
        self.rent_or_buy = rent_or_buy

    def build_url(self) -> str:
        return f"https://api.mobile.immobilienscout24.de/search/list?pagenumber={self.page}&realestatetype={self.estate_type + self.rent_or_buy}&searchType=region&geocodes=/{self.country}/{self.state}/{self.city}&pagesize={self.listing_count}"
    
    def crawl(self) -> requests.Response:
        headers = self.headers.build_header()
        url = self.build_url()
        response = requests.post(url, headers=headers)
        return response

class ImmoWeltCrawler(BaseCrawler):
    def build_url(self) -> str:
        return ""
    
    def crawl(self) -> requests.Response:
        return requests.Response()

class KleinanzeigenCrawler(BaseCrawler):
    def build_url(self) -> str:
        return ""

    def crawl(self) -> requests.Response:
        return requests.Response()
    
# Implementation of Crawler Factories
class CrawlerFactory(ABC):
    
    @abstractmethod
    def create_crawler(self, params: SearchParams, header: Headers) -> BaseCrawler:
        pass

class ImmoScoutCrawlerFactory(CrawlerFactory):
    def create_crawler(self, params: SearchParams, header: Headers) -> BaseCrawler:
        return ImmoScoutCrawler(params.country, params.state, params.city, params.plz, params.listing_count, params.estate_type, params.rent_or_buy, params.page, header)
    
class ImmoWeltCrawlerFactory(CrawlerFactory):
    def create_crawler(self, params: SearchParams, header: Headers) -> BaseCrawler:
        return ImmoWeltCrawler(params.country, params.city, params.listing_count, params.page, header)

class KleinanzeigenCrawlerFactory(CrawlerFactory):
    def create_crawler(self, params: SearchParams, header: Headers) -> BaseCrawler:
        return KleinanzeigenCrawler(params.country, params.city, params.listing_count, params.page, header)
    

# Function to instantiate Crawler Factories depending on input
def create_factory(site: str) -> CrawlerFactory:
    fac = {
        "Immoscout": ImmoScoutCrawlerFactory(),
        "Immowelt": ImmoWeltCrawlerFactory(),
        "Kleinanzeigen": KleinanzeigenCrawlerFactory()
    }
    
    return fac[site]