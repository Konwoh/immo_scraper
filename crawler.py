from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

@dataclass
class SearchParams:
    city: str
    plz: str
    listing_count: int
    estate_type: Optional[str] = None
    rent_or_buy: Optional[str] = None

# Implementation of concrete Crawler
class BaseCrawler(ABC):
    def __init__(self, city: str, plz: str, listing_count: int):
        self.city = city
        self.plz = plz
        self.listing_count = listing_count

    @abstractmethod
    def build_url(self) -> str:
        ...

class ImmoScoutCrawler(BaseCrawler):
    def __init__(self, city: str, plz: str, listing_count: int, estate_type: Optional[str], rent_or_buy: Optional[str]):
        super().__init__(city, plz, listing_count)
        self.estate_type = estate_type
        self.rent_or_buy = rent_or_buy

    def build_url(self) -> str:
        return ""

class ImmoWeltCrawler(BaseCrawler):
    def build_url(self) -> str:
        return ""

class KleinanzeigenCrawler(BaseCrawler):
    def build_url(self) -> str:
        return ""

# Implementation of Crawler Factories
class CrawlerFactory(ABC):
    
    @abstractmethod
    def create_crawler(self, params: SearchParams) -> BaseCrawler:
        pass

class ImmoScoutCrawlerFactory(CrawlerFactory):
    def create_crawler(self, params: SearchParams) -> BaseCrawler:
        return ImmoScoutCrawler(params.city, params.plz, params.listing_count, params.estate_type, params.rent_or_buy)
    
class ImmoWeltCrawlerFactory(CrawlerFactory):
    def create_crawler(self, params: SearchParams) -> BaseCrawler:
        return ImmoWeltCrawler(params.city, params.plz, params.listing_count)

class KleinanzeigenCrawlerFactory(CrawlerFactory):
    def create_crawler(self, params: SearchParams) -> BaseCrawler:
        return KleinanzeigenCrawler(params.city, params.plz, params.listing_count)
    

# Function to instantiate Crawler Factories depending on input
def create_factory(site: str) -> CrawlerFactory:
    fac = {
        "Immoscout": ImmoScoutCrawlerFactory(),
        "Immowelt": ImmoWeltCrawlerFactory(),
        "Kleinanzeigen": KleinanzeigenCrawlerFactory()
    }
    
    return fac[site]