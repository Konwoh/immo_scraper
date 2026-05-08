from typing import List
from abc import ABC, abstractmethod
from backend.database.factory import EstateFactory, ApartmentEstateFactory, HouseEstateFactory
from backend.database.models import UrlQueue, RealEstate, House, Apartment
import requests
import logging

scraper_logger = logging.getLogger("scraper")

def read_estate_creator(estate_type: str) -> EstateFactory:
    normalized = estate_type.strip().lower()

    apartment_types = {
        "erdgeschosswohnung",
        "etagenwohnung",
        "souterrain",
        "dachgeschoss",
        "dachgeschosswohnung",
        "maisonette",
        "terrassenwohnung",
        "penthouse",
        "loft",
        "hochparterre",
        "sonstige",
        "andere wohnungstypen"
    }

    house_types = {
        "einfamilienhaus (freistehend)",
        "einfamilienhaus freistehend",
        "mehrfamilienhaus",
        "doppelhaushälfte",
        "reihenhaus",
        "bungalow",
        "villa",
        "bauernhaus",
        "andere haustypen",
        "andere",
        "haus_mieten",
        "haus_kaufen"
    }

    if normalized in apartment_types:
        return ApartmentEstateFactory()
    elif normalized in house_types:
        return HouseEstateFactory()
    else:
        raise KeyError("No estate_type found")

class Parser(ABC):
    @abstractmethod
    def fetch(self, normal_url: str) -> House|Apartment:
        pass    
    
    @abstractmethod
    def parse(self, response: requests.Response) -> RealEstate:
        pass
    
    @abstractmethod
    def url_parse(self, response: requests.Response) -> List[UrlQueue]:
        pass