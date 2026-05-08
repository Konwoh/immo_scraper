from typing import List
from backend.database.factory import get_or_create_agency, DefaultAgencyFactory
from backend.database.models import UrlQueue, Status, House, Apartment
from backend.parser.base_parser import read_estate_creator, Parser
from sqlalchemy.orm import Session
from backend.database.models import engine
from backend.shared.exceptions import ParsingError, RequestError
from backend.shared.helper import Headers
import requests
import logging

scraper_logger = logging.getLogger("scraper")

class KleinanzeigenParser(Parser):
    def fetch(self, normal_url: str) -> House|Apartment:
        headers = Headers('*/*', 'Kleinanzeigen/2026.12.0 (com.ebaykleinanzeigen.ebc; build:26.072.16409187; iOS 26.3.1) Alamofire/5.11.1', 'de-DE;q=1.0', 'Basic aXBob25lOmc0Wmk5cTEw')
        headers = headers.build_header()
        last_string_segment = normal_url.split("/")[-1]
        expose_id = last_string_segment.split("-")[0]
        base_url = f'https://api.kleinanzeigen.de/api/ads/{expose_id}.json'
        response = requests.get(base_url, headers=headers)
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            if response.status_code == 404:
                raise RequestError(f"Inserat {base_url} nicht mehr verfügbar")
            raise RequestError(f"Kleinanzeigen API Fehler: {e}")
        estate = self.parse(response)
        return estate
    
    def parse(self, response: requests.Response) -> House|Apartment:
        try:
            payload = response.json()
            payload = payload.get("{http://www.ebayclassifiedsgroup.com/schema/ad/v1}ad", {}).get("value")
        except ValueError as e:
            raise ValueError("Invalid JSON in response") from e
        try:
            data = {}
            data["id"]                  = payload.get("id")
            data["title"]               = payload.get("title", {}).get("value")
            data["url"]                 = f'https://www.kleinanzeigen.de/s-anzeige/{data["title"]}/{data["id"]}'
            data["listing_type"]        = payload.get("category", {}).get("localized-name", {}).get("value")
            if payload.get("category", {}).get("localized-name", {}).get("value") == "Eigentumswohnungen":
                data["total_costs"]     = payload.get("price", {}).get("amount", {}).get("value")
            data["general_description"] = payload.get("description", {}).get("value")
            data["zip_code"]            = payload.get("ad-address", {}).get("zip-code", {}).get("value")
            data["address"]             = payload.get("ad-address", {}).get("street", {}).get("value")
            data["city"]                = payload.get("ad-address", {}).get("state", {}).get("value")
            data["status"]              = payload.get("ad-status", {}).get("value")
            data["agency"]              = {"name": payload.get("company", {}).get("name")}
            
            for section in payload.get("attributes", {}).get("attribute", []):
                if section["localized-label"] == "Wohnfläche":
                    data["living_space"] = section.get("value", [])[0].get("value")
                    data["living_space_unit"] = section.get("unit")
                
                elif section["localized-label"] == "Warmmiete":
                    data["rent_complete"] = section.get("value", [])[0].get("value")
                
                elif section["localized-label"] == "Nebenkosten":
                    data["rent_extra_costs"] = section.get("value", [])[0].get("value")
                
                elif section["localized-label"] == "Zimmer":
                    data["rooms"] = float(section.get("value", [])[0].get("value"))
                
                elif section["localized-label"] == "Schlafzimmer":
                    data["sleeping_rooms"] = int(section.get("value", [])[0].get("value"))
                
                elif section["localized-label"] == "Badezimmer":
                    value = section.get("value", [])[0].get("value")
                    data["bathrooms"] = int(float(str(value).replace(",", ".")))
                
                elif section["localized-label"] == "Etage":
                    data["floor"] = section.get("value", [])[0].get("value")
                
                elif section["localized-label"] == "Wohnungstyp" or section["localized-label"] == "Haustyp":
                    data["estate_type"] = section.get("value", [])[0].get("localized-label")          
                    
                elif section["localized-label"] == "Baujahr":
                    data["building_year"] = section.get("value", [])[0].get("value")

                elif section["localized-label"] == "Keller":
                    data["basement"] = True if section.get("value", [])[0].get("value") == "true" else False
                
                elif section["localized-label"] == "Balkon":
                    data["balcony"] = True if section.get("value", [])[0].get("value") == "true" else False
                
                elif section["localized-label"] == "Garten/-mitnutzung":
                    data["garden"] = True if section.get("value", [])[0].get("value") == "true" else False
                
                elif section["localized-label"] == "Hausgeld":
                    data["house_money"] = section.get("value", [])[0].get("value")
                
                elif section["localized-label"] == "Aktuell vermietet":
                    data["rented"] = True if section.get("value", [])[0].get("value") == "true" else False
                
                elif section["localized-label"] == "Verfügbar ab":
                    data["available_from"] = section.get("value", [])[0].get("value")
            
            if not data.get("estate_type"):
                category = payload.get("category", {}).get("id-name", {}).get("value")

                if category == "Haus_mieten":
                    data["estate_type"] = "Andere Haustypen"
                elif category == "Haus_kaufen":
                    data["estate_type"] = "Andere Haustypen"
                elif category == "Wohnung_mieten":
                    data["estate_type"] = "Andere Wohnungstypen"
                elif category == "Wohnung_kaufen":
                    data["estate_type"] = "Andere Wohnungstypen"
                                       
        except Exception as e:
            scraper_logger.error(f"Fehler beim Parsing von URL {response.url}: {str(e)}")
            raise ParsingError(f"KleinanzeigenParser: Fehler beim Parsen: {e}")
        
        factory = read_estate_creator(estate_type=data.get("estate_type", "Sonstige"))
        with Session(engine) as session:
            agency_factory = DefaultAgencyFactory()
            agency = get_or_create_agency(session, data, agency_factory)
            estate = factory.get_estate(data, agency)
        return estate
    
    def url_parse(self, response: requests.Response) -> List[UrlQueue]:
        try:
            payload = response.json()
        except ValueError as e:
            raise ValueError("Invalid JSON in response") from e 

        url_list = payload["{http://www.ebayclassifiedsgroup.com/schema/ad/v1}ads"]["value"]["ad"]
        
        url_queue_list = []
        
        if len(url_list) > 0:
            for ad in url_list:
                if "id" in ad.keys():
                    for link_obj in ad["link"]:
                        if link_obj["rel"] == "self-public-website":
                            url = link_obj["href"]
                    url_obj = UrlQueue(url=url, status=Status.open)
                    url_queue_list.append(url_obj)
        
        return url_queue_list