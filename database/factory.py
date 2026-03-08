from typing import Dict, Any
from abc import ABC, abstractmethod
from .models import Agency, House, RealEstate, Apartment
from core.helper import to_float, to_int

class AgencyFactory(ABC):
    @abstractmethod
    def get_agency(self, params: Dict[str, Any]) -> Agency:
        pass

class DefaultAgencyFactory(AgencyFactory):
    def get_agency(self, params: Dict[str, Any]) -> Agency:
        return Agency(
            name=params.get("name"),
            rating=to_float(params.get("rating")),
            rating_count=to_int(params.get("rating_count")),
            homepage=params.get("homepage"),
            address=params.get("address"),
        )

class EstateFactory(ABC):
    @abstractmethod
    def get_estate(self, params: Dict[str, Any], agency: AgencyFactory) -> RealEstate:
        pass

class HouseEstateFactory(EstateFactory):
    def get_estate(self, params: Dict[str, Any], agency: AgencyFactory) -> House:
        return House(
            title=params.get("title"),
            url=params.get("url"),
            estate_type=params.get("estate_type"),
            price=params.get("price"),
            price_m2=params.get("price_m2"),
            city=params.get("plz_city"),
            address=params.get("address"),
            rooms=to_float(params.get("rooms")),
            living_space=params.get("living_space"),
            sleeping_rooms=to_int(params.get("sleeping_rooms")),
            garage_parking_slots=to_int(params.get("garage_parking_slots")),
            rented=bool(params.get("rented")),
            provision=params.get("provision"),
            rent_income=params.get("rent_income"),
            incidental_purchase_costs=params.get("incidental_purchase_costs"),
            property_acquisition_tax=params.get("property_acquisition_tax"),
            brokerage_commission=params.get("brokerage_commission"),
            notary_fees=params.get("notary_fees"),
            land_registry_entry=params.get("land_registry_entry"),
            total_costs=to_float(params.get("total_costs")),
            agency=agency.get_agency(params.get("agency", {})),
            property_space=params.get("property_space")
        )
    
class ApartmentEstateFactory(EstateFactory):
    def get_estate(self, params: Dict[str, Any], agency: AgencyFactory) -> Apartment:
        return Apartment(
            title=params.get("title"),
            url=params.get("url"),
            estate_type=params.get("estate_type"),
            price=params.get("price"),
            price_m2=params.get("price_m2"),
            city=params.get("plz_city"),
            address=params.get("address"),
            rooms=to_float(params.get("rooms")),
            living_space=params.get("living_space"),
            sleeping_rooms=to_int(params.get("sleeping_rooms")),
            garage_parking_slots=to_int(params.get("garage_parking_slots")),
            rented=bool(params.get("rented")),
            provision=params.get("provision"),
            rent_income=params.get("rent_income"),
            incidental_purchase_costs=params.get("incidental_purchase_costs"),
            property_acquisition_tax=params.get("property_acquisition_tax"),
            brokerage_commission=params.get("brokerage_commission"),
            notary_fees=params.get("notary_fees"),
            land_registry_entry=params.get("land_registry_entry"),
            total_costs=to_float(params.get("total_costs")),
            agency=agency.get_agency(params.get("agency", {})),
        )