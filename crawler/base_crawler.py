from abc import ABC, abstractmethod
import requests
from backend.shared.helper import Headers
from backend.shared.loki_handler import get_loki_logger

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
