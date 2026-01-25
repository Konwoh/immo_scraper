from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Any, Optional

class Agency:
    def __init__(self, name: str, rating: Optional[float], rating_count: int, homepage: str, address: str):
        self.name = name
        self.rating = rating
        self.rating_count = rating_count
        self.homepage = homepage
        self.address = address

class RealEstate:
    def __init__(self, title: str, estate_type: str, price: Optional[float], price_m2: Optional[float], city: str, address:str, rooms: Optional[float], living_space: Optional[float], sleeping_rooms: int, garage_parking_slots: int, rented: bool|str, provision: str, rent_income: Optional[float], incidental_purchase_costs: str, property_acquisition_tax: str, brokerage_commission: str, notary_fees: str, land_registry_entry: str, total_costs: Optional[float], agency: Agency):
        self.title = title
        self.type = estate_type
        self.price = price
        self.price_m2 = price_m2
        self.city = city
        self.address = address
        self.rooms = rooms
        self.sleeping_rooms = sleeping_rooms
        self.living_space = living_space
        self.garage_parking_slots = garage_parking_slots
        self.rented = rented
        self.provision = provision
        self.rent_income = rent_income
        self.incidental_purchase_costs = incidental_purchase_costs
        self.property_acquisition_tax = property_acquisition_tax
        self.brokerage_commission = brokerage_commission
        self.notary_fees = notary_fees
        self.land_registry_entry = land_registry_entry
        self.total_costs = total_costs
        self.agency = agency

    def calculate_incidental_purchase_costs(self) -> float:
        if '%' in self.incidental_purchase_costs:
            incidental_purchase_costs_num = self.incidental_purchase_costs.split(" ")[0]
            incidental_purchase_costs_float = float(incidental_purchase_costs_num)/100
            return incidental_purchase_costs_float
        else:
            raise Exception("No Percent Sign in String")
    
    def calculate_property_acquisition_tax(self) -> float:
        if '%' in self.property_acquisition_tax:
            property_acquisition_tax_num = self.property_acquisition_tax.split(" ")[0]
            property_acquisition_tax_float = float(property_acquisition_tax_num)/100
            return property_acquisition_tax_float
        else:
            raise Exception("No Percent Sign in String")
    
    
    def calculate_brokerage_commission(self) -> float:
        if '%' in self.brokerage_commission:
            brokerage_commission_num = self.brokerage_commission.split(" ")[0]
            brokerage_commission_float = float(brokerage_commission_num)/100
            return brokerage_commission_float
        else:
            raise Exception("No Percent Sign in String")
    
    def calculate_notary_fees(self) -> float:
        if '%' in self.notary_fees:
            notary_fees_num = self.notary_fees.split(" ")[0]
            notary_fees_float = float(notary_fees_num)/100
            return notary_fees_float
        else:
            raise Exception("No Percent Sign in String")
    
    def calculate_land_registry_entry(self) -> float:
        if '%' in self.land_registry_entry:
            land_registry_entry_num = self.land_registry_entry.split(" ")[0]
            land_registry_entry_float = float(land_registry_entry_num)/100
            return land_registry_entry_float
        else:
            raise Exception("No Percent Sign in String")
    
def to_float(v, default=""):
    if v is None:
        return None
    if isinstance(v, str) and v.strip() == "":
        return None
    try:
        return float(v)
    except (TypeError, ValueError):
        return None

def to_int(v, default=""):
    if v is None:
        return None
    if isinstance(v, str) and v.strip() == "":
        return None
    try:
        return int(v)
    except (TypeError, ValueError):
        return None 
        

class House(RealEstate):
    def __init__(self, title: str, estate_type: str, price: Optional[float], price_m2: Optional[float], city: str, address: str, rooms: Optional[float], living_space: Optional[float], property_space: Optional[float], sleeping_rooms: int, garage_parking_slots: int, rented: bool, provision: str, rent_income: Optional[float], incidental_purchase_costs: str, property_acquisition_tax: str, brokerage_commission: str, notary_fees: str, land_registry_entry: str, total_costs: Optional[float], agency: Agency):
        super().__init__(title, estate_type, price, price_m2, city, address, rooms, living_space, sleeping_rooms, garage_parking_slots, rented, provision, rent_income, incidental_purchase_costs, property_acquisition_tax, brokerage_commission, notary_fees, land_registry_entry, total_costs, agency)
        self.property_space = property_space
        
class Apartment(RealEstate):
    def __init__(self, title: str, estate_type: str, price: Optional[float], price_m2: Optional[float], city: str, address: str, rooms: Optional[float], living_space: Optional[float], sleeping_rooms: int, garage_parking_slots: int, rented: bool, provision: str, rent_income: Optional[float], incidental_purchase_costs: str, property_acquisition_tax: str, brokerage_commission: str, notary_fees: str, land_registry_entry: str, total_costs: Optional[float], agency: Agency):
        super().__init__(title, estate_type, price, price_m2, city, address, rooms, living_space, sleeping_rooms, garage_parking_slots, rented, provision, rent_income, incidental_purchase_costs, property_acquisition_tax, brokerage_commission, notary_fees, land_registry_entry, total_costs, agency)
        
class EstateFactory(ABC):
    @abstractmethod
    def get_estate(self, params: Dict[str, Any]) -> RealEstate:
        pass

class HouseEstate(EstateFactory):
    def get_estate(self, params: Dict[str, Any]) -> House:
        return House(
                    title=params.get("title", ""),
                    estate_type=params.get("estate_type", ""),
                    price=to_float(params.get("price", "")),
                    price_m2=to_float(params.get("price_m2", "")),
                    city=params.get("city", ""),
                    address=params.get("address") or "",
                    rooms=float(params.get("rooms", "")),
                    living_space=float(params.get("living_space", "")),
                    sleeping_rooms=int(params.get("sleeping_rooms", "")),
                    garage_parking_slots=int(params.get("garage_parking_slots", "")),
                    rented=bool(params.get("rented")),
                    provision=params.get("provision", ""),
                    rent_income=float(params.get("rent_income", "")),
                    incidental_purchase_costs=params.get("incidental_purchase_costs", ""),
                    property_acquisition_tax=params.get("property_acquisition_tax", ""),
                    brokerage_commission=params.get("brokerage_commission", ""),
                    notary_fees=params.get("notary_fees", ""),
                    land_registry_entry=params.get("land_registry_entry", ""),
                    total_costs=float(params.get("total_costs", "")),
                    agency=(
                        Agency(
                            name=params.get("agency", {}).get("name", ""),
                            rating=float(params.get("agency", {}).get("rating")) ,
                            rating_count=int(params.get("agency", {}).get("rating_count")),
                            homepage=params.get("agency", {}).get("homepage", ""),
                            address=params.get("agency", {}).get("address", "")
                        )
                    ),
                    property_space=float(params.get("property_space", ""))
                )
    
class ApartmentEstate(EstateFactory):
    def get_estate(self, params: Dict[str, Any]) -> Apartment:
        return Apartment(
            title=params.get("title", ""),
            estate_type=params.get("estate_type", ""),
            price=to_float(params.get("price")),
            price_m2=to_float(params.get("price_m2", "")),
            city=params.get("city", ""),
            address=params.get("address") or "",
            rooms=to_float(params.get("rooms", "")),
            living_space=to_float(params.get("living_space", "")),
            sleeping_rooms=int(params.get("sleeping_rooms", "")),
            garage_parking_slots=int(params.get("garage_parking_slots", "")),
            rented=bool(params.get("rented")),
            provision=params.get("provision", ""),
            rent_income=to_float(params.get("rent_income", "")),
            incidental_purchase_costs=params.get("incidental_purchase_costs", ""),
            property_acquisition_tax=params.get("property_acquisition_tax", ""),
            brokerage_commission=params.get("brokerage_commission", ""),
            notary_fees=params.get("notary_fees", ""),
            land_registry_entry=params.get("land_registry_entry", ""),
            total_costs=to_float(params.get("total_costs", "")),
            agency=Agency(
                name=params.get("agency", {}).get("name", ""),
                rating=to_float(params.get("agency", {}).get("rating")),
                rating_count=int(params.get("agency", {}).get("rating_count")),
                homepage=params.get("agency", {}).get("homepage", ""),
                address=params.get("agency", {}).get("address", ""),
            ),
        )