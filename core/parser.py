from typing import List
from abc import ABC, abstractmethod
from database.factory import EstateFactory, ApartmentEstateFactory, HouseEstateFactory, get_or_create_agency, DefaultAgencyFactory
from database.models import UrlQueue, Status, RealEstate
from sqlalchemy.orm import Session
from database.models import engine
from core.exceptions import ParsingError, RequestError
from core.helper import Headers
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
        "Andere Wohnungstypen"
    }

    house_types = {
        "einfamilienhaus (freistehend)",
        "mehrfamilienhaus",
        "doppelhaushälfte",
        "reihenhaus",
        "bungalow",
        "villa",
        "bauernhaus",
    }

    if normalized in apartment_types:
        return ApartmentEstateFactory()
    elif normalized in house_types:
        return HouseEstateFactory()
    else:
        raise KeyError("No estate_type found")

class Parser(ABC):
    @abstractmethod
    def fetch(self, normal_url: str) -> RealEstate:
        pass    
    
    @abstractmethod
    def parse(self, response: requests.Response) -> RealEstate:
        pass
    
    @abstractmethod
    def url_parse(self, response: requests.Response) -> List[UrlQueue]:
        pass

class ImmoScoutParser(Parser):
    def fetch(self, normal_url: str) -> RealEstate:
        headers = Headers('application/json', 'ImmoScout_27.14.1_26.3_._', 'de-de')
        headers = headers.build_header()
        expose_id = normal_url.split("/")[-1]
        base_url = f'https://api.mobile.immobilienscout24.de/expose/{expose_id}'
        response = requests.get(base_url, headers=headers)
        estate = self.parse(response)
        return estate
    
    def parse(self, response: requests.Response) -> RealEstate:
        try:
            payload = response.json()
        except ValueError as e:
            raise ValueError("Invalid JSON in response") from e
        
        error = payload.get("error")

        if error and "ERROR_RESOURCE_NOT_FOUND" in error:
            raise ParsingError("Estate not available anymore")
        elif payload.get("sections") is None:
            raise ParsingError("Section Key is not in JSON")

        data = {}
        header = payload.get("header")
        if header is not None:
            object_id = header.get("id")
            if object_id is not None:
                data["url"] = f"https://www.immobilienscout24.de/expose/{object_id}"
            else:
                pass
        else:
            raise ParsingError("No header found")
        try:
            for section in payload.get("sections", []):
                if section.get("type") == "TOP_ATTRIBUTES":
                    for attribute in section.get("attributes", []):
                        if attribute.get("label") == "Zimmer":
                            if "," in attribute.get("text"): 
                                data["rooms"] = float(attribute.get("text").replace(",", "."))
                            else:
                                data["rooms"] = float(attribute.get("text"))
                        elif attribute.get("label") == "Wohnfläche":
                            data["living_space"] = attribute.get("text")
                        elif attribute.get("label") == "Grundstück":
                            data["property_space"] = attribute.get("text")
                elif section.get("type") == "TITLE":
                    data["title"] = section.get("title")
                elif section.get("type") == "MAP":
                    data["city"] = section.get("addressLine2")
                    if section.get("addressLine1") != "Die vollständige Adresse der Immobilie erhältst du vom Anbieter.":
                        data["address"] = section.get("addressLine1")

                elif section.get("type") == "ATTRIBUTE_LIST" and section.get("title") == "Hauptkriterien":
                    for attribute in section.get("attributes", []):
                        if attribute.get("label") == "Haustyp:" or attribute.get("label") == "Wohnungstyp:":
                            data["estate_type"] = attribute.get("text")
                        elif attribute.get("label") == "Schlafzimmer:":
                            data["sleeping_rooms"] = int(attribute.get("text"))
                        elif attribute.get("label") == "Badezimmer:":
                            data["bathrooms"] = int(attribute.get("text"))
                        elif attribute.get("label") == "Etage:":
                            data["floor"] = attribute.get("text")             
                        elif attribute.get("label") == "Garten/-mitbenutzung:":
                            data["garden"] = True
                        elif attribute.get("label") == "Personenaufzug:":
                            data["lift"] = True
                        elif attribute.get("label") == "Einbauküche:":
                            data["fitted_kitchen"] = True
                        elif attribute.get("label") == "Keller:":
                            data["basement"] = True  
                        elif attribute.get("label") == "Anzahl Garage/Stellplatz:":
                            data["garage_parking_slots"] = int(attribute.get("text"))
                        elif attribute.get("label") == "Bezugsfrei ab:":
                            data["available_from"] = attribute.get("text")

                elif section.get("type") == "ATTRIBUTE_LIST" and section.get("title") == "Kosten":
                    for attribute in section.get("attributes", []):
                        if attribute.get("label") == "Kaufpreis:":
                            data["price"] = attribute.get("text")
                        elif attribute.get("label") == "Preis/m²:":
                            data["price_m2"] = attribute.get("text")
                        elif attribute.get("label") == "Mieteinnahmen pro Monat:":
                            data["rent_income"] = attribute.get("text")
                        elif attribute.get("label") == "Kaltmiete (zzgl. Nebenkosten):":
                            data["rent_cold"] = attribute.get("text")
                        elif attribute.get("label") == "Gesamtmiete:":
                            data["rent_complete"] = attribute.get("text")
                        elif attribute.get("label") == "Hausgeld:":
                            data["house_money"] = attribute.get("text")
                        elif attribute.get("label") == "Nebenkosten:":
                            data["rent_extra_costs"] = attribute.get("text")
                        elif attribute.get("label") == "Heizkosten:":
                            data["rent_heating_costs"] = attribute.get("text")
                        elif attribute.get("label") == "Kaution oder Genossenschaftsanteile:":
                            data["rent_deposit"] = attribute.get("text")

                elif section.get("type") == "FINANCE_COSTS":
                    data["incidental_purchase_costs"] = section.get("additionalCosts", {}).get("value")
                    data["total_costs"] = section.get("totalCosts", {}).get("value")
                    data["broker_commision"] = section.get("brokerCommission", {}).get("percentage")
                    data["land_transfer_tax"] = section.get("landTransferTax", {}).get("percentage")
                    data["notary_fees"] = section.get("notaryCosts", {}).get("percentage")
                    data["land_registry_entry"] = section.get("landRegistryEntry", {}).get("percentage")

                elif section.get("type") == "ATTRIBUTE_LIST" and section.get("title") == "Bausubstanz & Energieausweis":
                    for attribute in section.get("attributes", []):
                        if attribute.get("label") == "Baujahr:":
                            data["building_year"] = attribute.get("text")
                        elif attribute.get("label") == "Objektzustand:":
                            data["estate_condition"] = attribute.get("text")
                        elif attribute.get("label") == "Qualität der Ausstattung:":
                            data["interior_quality"] = attribute.get("text")
                        elif attribute.get("label") == "Heizungsart:":
                            data["heating_type"] = attribute.get("text")
                        elif attribute.get("label") == "Energieausweistyp:":
                            data["energy_performance_certificate_type"] = attribute.get("text")
                        elif attribute.get("label") == "Wesentliche Energieträger:":
                            data["energy_source"] = attribute.get("text")
                        elif attribute.get("label") == "Endenergiebedarf:":
                            data["energy_demand"] = attribute.get("text")
                        elif attribute.get("label") == "Energieeffizienzklasse:":
                            data["energy_efficiency_class"] = attribute.get("url")
                        elif attribute.get("label") == "Denkmalschutzobjekt:":
                            data["is_monument_protected"] = True

                elif section.get("type") == "TEXT_AREA" and section.get("title") == "Ausstattung":
                    data["general_description"] = section.get("text")

                elif section.get("type") == "TEXT_AREA" and section.get("title") == "Lage":
                    data["place_description"] = section.get("text")

                elif section.get("type") == "TEXT_AREA" and section.get("title") == "Objektbeschreibung":
                    data["object_description"] = section.get("text")
                    
                elif section.get("type") == "TEXT_AREA" and section.get("title") == "Sonstiges":
                    data["other_description"] = section.get("text")

                elif section.get("type") == "AGENTS_INFO":
                    homepage = None
                    for reference in section.get("references", []):
                        if reference["label"] == "Homepage des Anbieters":
                            homepage = reference["url"]
                    data["agency"] = {
                        "name": section.get("name"),
                        "rating": section.get("rating", {}).get("value"),
                        "address": section.get("address"),
                        "homepage": homepage,}

            immotype = payload.get("adTargetingParameters", {}).get("obj_immotype")
            if immotype:
                data["listing_type"] = immotype
            
            zip_code = payload.get("adTargetingParameters", {}).get("obj_zipCode")
            if zip_code:
                data["zip_code"] = zip_code

            rented = payload.get("adTargetingParameters", {}).get("obj_rented")
            if rented:
                data["rented"] = False if rented == "n" else True 

            barrier_free = payload.get("adTargetingParameters", {}).get("obj_barrierFree")
            if barrier_free:
                data["barrier_free"] = False if barrier_free == "n" else True 
                
            internet_speed_telekom = payload.get("adTargetingParameters", {}).get("obj_telekomInternetSpeed")
            if internet_speed_telekom:
                data["internet_speed_telekom"] = internet_speed_telekom
        
        except Exception as e:
            scraper_logger.error(f"Fehler bei Attribut Extraction von URL {response.url}: {str(e)}")
            raise ParsingError(f"Fehler beim Parsing von URL {response.url}: {str(e)}")
            
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
        
        url_queue_list = []
        
        items = payload.get("resultListItems", [])
        if not items:
            raise ParsingError("List has no objects")
        
        for item in items:
            if item["type"] == "EXPOSE_RESULT":
                id = item["item"]["id"]
                url_obj = UrlQueue(url=f"https://www.immobilienscout24.de/expose/{id}", status=Status.open)
                url_queue_list.append(url_obj)
            elif item["type"] == "DEVELOPER_PROJECT_RESULT":
                id = item["item"]["id"]
                url_obj = UrlQueue(url=f"https://www.immobilienscout24.de/expose/{id}", status=Status.open)
                url_queue_list.append(url_obj)
            else:
                continue
        
        return url_queue_list

class KleinanzeigenParser(Parser):
    def fetch(self, normal_url: str) -> RealEstate:
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
    
    def parse(self, response: requests.Response) -> RealEstate:
        try:
            payload = response.json()
            payload = payload.get("{http://www.ebayclassifiedsgroup.com/schema/ad/v1}ad", {}).get("value")
        except ValueError as e:
            raise ValueError("Invalid JSON in response") from e
        try:
            data = {}
            data["id"] = payload.get("id")
            data["title"] = payload.get("title", {}).get("value")
            data["url"] = f'https://www.kleinanzeigen.de/s-anzeige/{data["title"]}/{data["id"]}'
            data["listing_type"] = payload.get("category", {}).get("localized-name", {}).get("value")
            if payload.get("category", {}).get("localized-name", {}).get("value") == "Eigentumswohnungen":
                data["total_costs"] = payload.get("price", {}).get("amount", {}).get("value")
            data["description"] = payload.get("description", {}).get("value")
            data["zip_code"] = payload.get("ad-address", {}).get("zip-code", {}).get("value")
            data["address"] = payload.get("ad-address", {}).get("street", {}).get("value")
            data["city"] = payload.get("ad-address", {}).get("state", {}).get("value")
            data["status"] = payload.get("ad-status", {}).get("value")
            data["agency"] = {"name": payload.get("company", {}).get("name")}
            
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
                    data["bathrooms"] = int(section.get("value", [])[0].get("value"))
                
                elif section["localized-label"] == "Etage":
                    data["floor"] = section.get("value", [])[0].get("value")
                
                elif section["localized-label"] == "Wohnungstyp":
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
    
class ParserFactory(ABC):
    
    @abstractmethod
    def create_parser(self, site: str) -> Parser:
        pass

class EstateParserCreator(ParserFactory):
    def __init__(self):
        self._parsers = {
            "immoScout": ImmoScoutParser(),
            "kleinanzeigen": KleinanzeigenParser(),
        }

    def create_parser(self, site: str) -> Parser:
        if site in self._parsers:
            return self._parsers[site]
        raise ValueError("Site not available")
