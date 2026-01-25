from typing import Any, Dict, Optional, Type
from abc import ABC, abstractmethod
from estate import RealEstate, House, Apartment
from estate import RealEstate
import requests
from estate import EstateFactory, ApartmentEstate, HouseEstate

def read_estate_creator(estate_type: str) -> EstateFactory:
    factories = {
        "Erdgeschosswohnung" : ApartmentEstate(),
        "Etagenwohnung" : ApartmentEstate(),
        "Souterrain " : ApartmentEstate(),
        "Dachgeschoss" : ApartmentEstate(),
        "Maisonette" : ApartmentEstate(),
        "Terrassenwohnung" : ApartmentEstate(),
        "Penthouse" : ApartmentEstate(),
        "Loft" : ApartmentEstate(),
        "Einfamilienhaus (freistehend)" : HouseEstate(),
        "Mehrfamilienhaus" : HouseEstate(),
        "Doppelhaushälfte" : HouseEstate(),
        "Reihenhaus" : HouseEstate(),
        "Bungalow" : HouseEstate(),
        "Villa" : HouseEstate(),
        "Bauernhaus": HouseEstate()
    }
    
    if estate_type in factories:
        return factories[estate_type] 
    else:
        raise KeyError("No estate_type found")

class Parser(ABC):
    @abstractmethod
    def parse(self, response: requests.Response) -> RealEstate:
        pass

class EstateParser(Parser):
    
    def parse(self, response: requests.Response) -> RealEstate:
        try:
            payload = response.json()
        except ValueError as e:
            raise ValueError("Invalid JSON in response") from e
        
        if payload.get("sections") is None:
            raise ValueError("Section Key is not in JSON")

        data = {}

        for section in payload.get("sections", []):
            if section.get("type") == "TOP_ATTRIBUTES":
                for attribute in section.get("attributes", []):
                    if attribute.get("label") == "Zimmer":
                        data["rooms"] = float(attribute.get("text"))
                    elif attribute.get("label") == "Wohnfläche":
                        data["living_space"] = attribute.get("text")
                    elif attribute.get("label") == "Grundstück":
                        data["property_space"] = attribute.get("text")

            elif section.get("type") == "MAP":
                if section.get("addressLine1") == "Die vollständige Adresse der Immobilie erhältst du vom Anbieter.":
                    data["plz_city"] = section.get("addressLine2")

            elif section.get("type") == "ATTRIBUTE_LIST" and section.get("title") == "Hauptkriterien":
                for attribute in section.get("attributes", []):
                    if attribute.get("label") == "Haustyp:":
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
                data["agency"] = {
                    "name": section.get("name"),
                    "rating": float(section.get("rating", {}).get("value")),
                    "rating_count": int(section.get("rating", {}).get("numberOfStars")),
                    "address": section.get("address"),
        }
                
        factory = read_estate_creator(estate_type=data.get("estate_type", ""))
        estate = factory.get_estate(data)
        return estate

class ParserFactory(ABC):
    
    @abstractmethod
    def create_parser(self) -> Parser:
        pass

class EstateParserCreator(ParserFactory):
    def create_parser(self) -> Parser:
        return EstateParser()