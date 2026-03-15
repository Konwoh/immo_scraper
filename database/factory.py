from typing import Dict, Any
from abc import ABC, abstractmethod
from .models import Agency, House, RealEstate, Apartment
from core.helper import to_float, to_int
from sqlalchemy import select

class AgencyFactory(ABC):
    @abstractmethod
    def get_agency(self, params: Dict[str, Any]) -> Agency:
        pass

class DefaultAgencyFactory(AgencyFactory):
    def get_agency(self, params: Dict[str, Any]) -> Agency:
        return Agency(
            name=params.get("name"),
            rating=to_float(params.get("rating")),
            homepage=params.get("homepage"),
            address=params.get("address"),
        )

class EstateFactory(ABC):
    def _base_params(self, params: Dict[str, Any], agency: Agency | None) -> Dict[str, Any]:
        return {
            "title": params.get("title"),
            "url": params.get("url"),
            "estate_type": params.get("estate_type"),
            "listing_type": params.get("listing_type"),
            "price": params.get("price"),
            "price_m2": params.get("price_m2"),
            "rent_cold": params.get("rent_cold"),
            "rent_complete": params.get("rent_complete"),
            "rent_extra_costs": params.get("rent_extra_costs"),
            "rent_heating_costs": params.get("rent_heating_costs"),
            "rent_deposit": params.get("rent_deposit"),
            "city": params.get("plz_city"),
            "address": params.get("address"),
            "rooms": to_float(params.get("rooms")),
            "living_space": params.get("living_space"),
            "sleeping_rooms": to_int(params.get("sleeping_rooms")),
            "garage_parking_slots": to_int(params.get("garage_parking_slots")),
            "rented": bool(params.get("rented")),
            "provision": params.get("provision"),
            "rent_income": params.get("rent_income"),
            "incidental_purchase_costs": params.get("incidental_purchase_costs"),
            "property_acquisition_tax": params.get("property_acquisition_tax"),
            "brokerage_commission": params.get("brokerage_commission"),
            "notary_fees": params.get("notary_fees"),
            "land_registry_entry": params.get("land_registry_entry"),
            "building_year": params.get("building_year"),
            "estate_condition": params.get("estate_condition"),
            "interior_quality": params.get("interior_quality"),
            "heating_type": params.get("heating_type"),
            "energy_performance_certificate_type": params.get("energy_performance_certificate_type"),
            "energy_source": params.get("energy_source"),
            "energy_demand": params.get("energy_demand"),
            "energy_efficiency_class": params.get("energy_efficiency_class"),
            "general_description": params.get("general_description"),
            "place_description": params.get("place_description"),
            "other_description": params.get("other_description"),
            "total_costs": to_float(params.get("total_costs")),
            "agency": agency,
        }
    
    @abstractmethod
    def get_estate(self, params: Dict[str, Any], agency: Agency | None) -> RealEstate:
        pass

class HouseEstateFactory(EstateFactory):
    def get_estate(self, params: Dict[str, Any], agency: Agency | None) -> House:
        data = self._base_params(params, agency)
        data["property_space"] = params.get("property_space")
        return House(**data)
    
class ApartmentEstateFactory(EstateFactory):
    def get_estate(self, params: Dict[str, Any], agency: Agency | None) -> Apartment:
        data = self._base_params(params, agency)
        return Apartment(**data)

def get_or_create_agency(session, params: Dict, agency_factory: DefaultAgencyFactory) -> Agency:
    agency_data = params.get("agency", {})

    existing_agency = session.execute(
        select(Agency).where(
            Agency.name == agency_data.get("name"),
            Agency.homepage == agency_data.get("homepage"),
        )
    ).scalar_one_or_none()

    if existing_agency is not None:
        return existing_agency

    new_agency = agency_factory.get_agency(agency_data)
    return new_agency