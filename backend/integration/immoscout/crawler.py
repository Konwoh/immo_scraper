import requests
import json
from backend.shared.helper import Headers
from backend.shared.exceptions import RequestError
from typing import Optional
from crawler.base_crawler import BaseCrawler

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