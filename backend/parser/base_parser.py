from typing import List, Optional
from abc import ABC, abstractmethod
from backend.database.factory import EstateFactory, PropertyFactory, ApartmentEstateFactory, HouseEstateFactory, PropertyEstateFactory
from backend.database.models import UrlQueue, RealEstate, House, Apartment, Property
import requests
import logging

scraper_logger = logging.getLogger("scraper")

def read_estate_creator(estate_type: str, listing_type: Optional[str] = None) -> EstateFactory|PropertyFactory:
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
    
    property_types = {
        "grundstueck_wohnen_kauf",
        "grundstueck_wohnen_mieten"
    }
    
    if normalized in apartment_types:
        return ApartmentEstateFactory()
    elif normalized in house_types:
        return HouseEstateFactory()
    elif normalized in property_types:
        return PropertyEstateFactory()
    elif normalized == "sonstige":
        if listing_type is not None:
            listing_type = listing_type.lower()
            if listing_type == "wohnung_miete" or listing_type == "wohnung_kauf" or listing_type == "wohnung_kaufen" or listing_type == "wohnung_mieten":
                return ApartmentEstateFactory()
            elif listing_type == "haus_miete" or listing_type == "haus_kauf" or listing_type == "haus_kaufen" or listing_type == "haus_mieten":
                return HouseEstateFactory()
        else:
            raise KeyError("Normalized ist 'sonstige' und listing_type ist nicht bekannt")
    else:
        raise KeyError("No estate_type found")

class Parser(ABC):
    @abstractmethod
    def fetch_base(self, normal_url: str) -> requests.Response:
        pass   

    @abstractmethod
    def build_estate(self, normal_url: str) -> House|Apartment|Property:
        pass    
    
    @abstractmethod
    def parse(self, response: requests.Response) -> RealEstate:
        pass
    
    @abstractmethod
    def url_parse(self, response: requests.Response) -> List[UrlQueue]:
        pass
    
    @abstractmethod
    def is_online(self, response: requests.Response) -> bool:
        pass