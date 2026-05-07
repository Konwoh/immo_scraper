from abc import ABC, abstractmethod
from backend.shared.helper import Headers
from backend.database.models import SearchParams
from backend.integration.immoscout.crawler import ImmoScoutCrawler
from backend.integration.kleinanzeigen.crawler import KleinanzeigenCrawler
from backend.integration.immowelt.crawler import ImmoWeltCrawler
from crawler.base_crawler import BaseCrawler

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