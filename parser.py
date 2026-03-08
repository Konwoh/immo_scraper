from typing import List
from abc import ABC, abstractmethod
from database import RealEstate, EstateFactory, ApartmentEstateFactory, HouseEstateFactory, DefaultAgencyFactory, UrlQueue, UrlStatus
import requests
import logging

scraper_logger = logging.getLogger("scraper")

def read_estate_creator(estate_type: str) -> EstateFactory:
    factories = {
        "Erdgeschosswohnung" : ApartmentEstateFactory(),
        "Etagenwohnung" : ApartmentEstateFactory(),
        "Souterrain " : ApartmentEstateFactory(),
        "Dachgeschoss" : ApartmentEstateFactory(),
        "Maisonette" : ApartmentEstateFactory(),
        "Terrassenwohnung" : ApartmentEstateFactory(),
        "Penthouse" : ApartmentEstateFactory(),
        "Loft" : ApartmentEstateFactory(),
        "Hochparterre": ApartmentEstateFactory(),
        "Sonstige": ApartmentEstateFactory(),
        "Einfamilienhaus (freistehend)" : HouseEstateFactory(),
        "Mehrfamilienhaus" : HouseEstateFactory(),
        "Doppelhaushälfte" : HouseEstateFactory(),
        "Reihenhaus" : HouseEstateFactory(),
        "Bungalow" : HouseEstateFactory(),
        "Villa" : HouseEstateFactory(),
        "Bauernhaus": HouseEstateFactory()
    }
    
    if estate_type in factories:
        return factories[estate_type] 
    else:
        raise KeyError("No estate_type found")

class Parser(ABC):
    @abstractmethod
    def parse(self, response) -> RealEstate:
        pass
    
    @abstractmethod
    def url_parse(self, response) -> List[UrlQueue]:
        pass

class EstateParser(Parser):
    
    def parse(self, response: requests.Response) -> RealEstate:
        try:
            payload = response.json()
        except ValueError as e:
            raise ValueError("Invalid JSON in response") from e
        
        error = payload.get("error")

        if error and "ERROR_RESOURCE_NOT_FOUND" in error:
            raise ValueError("Estate not available anymore")
        elif payload.get("sections") is None:
            raise ValueError("Section Key is not in JSON")

        data = {}
        header = payload.get("header")
        if header is not None:
            object_id = header.get("id")
            if object_id is not None:
                data["url"] = f"https://www.immobilienscout24.de/expose/{object_id}"
            else:
                pass
        else:
            raise ValueError("No header found")
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
                    data["plz_city"] = section.get("addressLine2")
                    if section.get("addressLine1") != "Die vollständige Adresse der Immobilie erhältst du vom Anbieter.":
                        data["address"] = section.get("addressLine1")

                elif section.get("type") == "ATTRIBUTE_LIST" and section.get("title") == "Hauptkriterien":
                    for attribute in section.get("attributes", []):
                        if attribute.get("label") == "Haustyp:" or attribute.get("label") == "Wohnungstyp:":
                            data["estate_type"] = attribute.get("text")
                        elif attribute.get("label") == "Schlafzimmer:":
                            data["sleeping_rooms"] = int(attribute.get("text"))
                        elif attribute.get("label") == "Anzahl Garage/Stellplatz:":
                            data["garage_parking_slots"] = int(attribute.get("text"))

                elif section.get("type") == "ATTRIBUTE_LIST" and section.get("title") == "Kosten":
                    for attribute in section.get("attributes", []):
                        if attribute.get("label") == "Kaufpreis:":
                            data["price"] = attribute.get("text")
                        elif attribute.get("label") == "Preis/m²:":
                            data["price_m2"] = attribute.get("text")
                        elif attribute.get("label") == "Mieteinnahmen pro Monat:":
                            data["rent_income"] = attribute.get("text")

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
                            data["estate_condtion"] = attribute.get("text")
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

                elif section.get("type") == "TEXT_AREA" and section.get("title") == "Ausstattung":
                    data["general_description"] = section.get("text")

                elif section.get("type") == "TEXT_AREA" and section.get("title") == "Lage":
                    data["place_description"] = section.get("text")

                elif section.get("type") == "AGENTS_INFO":
                    homepage = None
                    for reference in section.get("references", []):
                        if reference["label"] == "Homepage des Anbieters":
                            homepage = reference["url"]
                    data["agency"] = {
                        "name": section.get("name"),
                        "rating": section.get("rating", {}).get("value"),
                        "rating_count": section.get("rating", {}).get("numberOfStars"),
                        "address": section.get("address"),
                        "homepage": homepage,
            }
        except Exception as e:
            scraper_logger.error("Fehler bei Attribut Extraction von URL: ", response.url, "Fehler: ", str(e))
            
        factory = read_estate_creator(estate_type=data.get("estate_type", "Sonstige"))
        agency_factory = DefaultAgencyFactory()
        estate = factory.get_estate(data, agency_factory)
        return estate

    def url_parse(self, response: requests.Response) -> List[UrlQueue]:
        try:
            payload = response.json()
        except ValueError as e:
            raise ValueError("Invalid JSON in response") from e
        
        url_queue_list = []
        
        if len(payload["resultListItems"]) > 0:
            for item in payload["resultListItems"]:
                if item["type"] == "EXPOSE_RESULT":
                    id = item["item"]["id"]
                    url_obj = UrlQueue(url=f"https://www.immobilienscout24.de/expose/{id}", status=UrlStatus.open)
                    url_queue_list.append(url_obj)
                elif item["type"] == "DEVELOPER_PROJECT_RESULT":
                    id = item["item"]["id"]
                    url_obj = UrlQueue(url=f"https://www.immobilienscout24.de/expose/{id}", status=UrlStatus.open)
                    url_queue_list.append(url_obj)
                else:
                    continue
        else:
            raise ValueError("List has no objects")
        
        return url_queue_list
            
class ParserFactory(ABC):
    
    @abstractmethod
    def create_parser(self) -> Parser:
        pass

class EstateParserCreator(ParserFactory):
    def create_parser(self) -> Parser:
        return EstateParser()