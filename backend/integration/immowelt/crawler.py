import requests
from crawler.base_crawler import BaseCrawler

class ImmoWeltCrawler(BaseCrawler):
    def build_url(self) -> str:
        return ""
    
    def crawl(self) -> tuple[requests.Response, bool]:
        return requests.Response(), True