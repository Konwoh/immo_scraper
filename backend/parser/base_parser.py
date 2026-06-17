from typing import List, Optional
from abc import ABC, abstractmethod
from backend.database.factory import EstateFactory, PropertyFactory, ApartmentEstateFactory, HouseEstateFactory, PropertyEstateFactory
from backend.database.models import UrlQueue, RealEstate, House, Apartment, Property
import requests

def read_estate_creator(estate_type: str, listing_type: Optional[str] = None) -> EstateFactory | PropertyFactory:
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
        "andere wohnungstypen",
    }

    house_types = {
        "einfamilienhaus (freistehend)",
        "einfamilienhaus freistehend",
        "mehrfamilienhaus",
        "doppelhaushälfte",
        "reihenhaus",
        "reihenmittelhaus",
        "reiheneckhaus",
        "bungalow",
        "villa",
        "bauernhaus",
        "andere haustypen",
        "wohnimmobilie (sonstige)",
        "andere",
        "haus_mieten",
        "haus_kaufen",
    }

    property_types = {
        "grundstueck_wohnen_kauf",
        "grundstueck_wohnen_mieten",
    }

    listing_type_factories = {
        "wohnung_miete": ApartmentEstateFactory,
        "wohnung_kauf": ApartmentEstateFactory,
        "wohnung_kaufen": ApartmentEstateFactory,
        "wohnung_mieten": ApartmentEstateFactory,
        "haus_miete": HouseEstateFactory,
        "haus_kauf": HouseEstateFactory,
        "haus_kaufen": HouseEstateFactory,
        "haus_mieten": HouseEstateFactory,
    }

    if normalized in apartment_types:
        return ApartmentEstateFactory()

    if normalized in house_types:
        return HouseEstateFactory()

    if normalized in property_types:
        return PropertyEstateFactory()

    if normalized != "sonstige":
        raise KeyError(f"No estate_type found. Normalized: {normalized}")

    if listing_type is None:
        raise KeyError("Normalized ist 'sonstige' und listing_type ist None")

    factory = listing_type_factories.get(listing_type.strip().lower())

    if factory is None:
        raise KeyError("listing_type ist nicht bekannt")

    return factory()

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