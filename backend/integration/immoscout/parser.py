from typing import List
from backend.database.factory import get_or_create_agency, DefaultAgencyFactory
from backend.database.models import UrlQueue, Status, RealEstate
from backend.parser.base_parser import read_estate_creator, Parser
from sqlalchemy.orm import Session
from backend.database.models import engine
from backend.shared.exceptions import ParsingError
from backend.shared.helper import Headers
import requests
import logging

scraper_logger = logging.getLogger("scraper")

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