from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from helper import to_float, to_int, Measurement

class Agency:
    def __init__(self, name: Optional[str], rating: Optional[float], rating_count: Optional[int], homepage: Optional[str], address: Optional[str]):
        self.name = name
        self.rating = rating
        self.rating_count = rating_count
        self.homepage = homepage
        self.address = address
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name}, rating={self.rating}, rating_count={self.rating_count}, homepage={self.homepage}, address={self.address})"

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

class RealEstate:
    def __init__(self, title: Optional[str], url: Optional[str], estate_type: Optional[str], price: Optional[Measurement], price_m2: Optional[Measurement], city: Optional[str], address: Optional[str], rooms: Optional[float], living_space: Optional[Measurement], sleeping_rooms: Optional[int], garage_parking_slots: Optional[int], rented: bool|str, provision: Optional[str], rent_income: Optional[Measurement], incidental_purchase_costs: Optional[str], property_acquisition_tax: Optional[str], brokerage_commission: Optional[str], notary_fees: Optional[str], land_registry_entry: Optional[str], total_costs: Optional[float], agency: Agency):
        self.title = title
        self.url = url
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
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(title={self.title}, price={self.price}, url={self.url}, agency={self.agency})"

    def calculate_incidental_purchase_costs(self) -> float:
        if self.incidental_purchase_costs is not None and '%' in self.incidental_purchase_costs:
            incidental_purchase_costs_num = self.incidental_purchase_costs.split(" ")[0]
            incidental_purchase_costs_float = float(incidental_purchase_costs_num)/100
            return incidental_purchase_costs_float
        else:
            raise Exception("No Percent Sign in String")
    
    def calculate_property_acquisition_tax(self) -> float:
        if self.property_acquisition_tax is not None and '%' in self.property_acquisition_tax:
            property_acquisition_tax_num = self.property_acquisition_tax.split(" ")[0]
            property_acquisition_tax_float = float(property_acquisition_tax_num)/100
            return property_acquisition_tax_float
        else:
            raise Exception("No Percent Sign in String")
    
    
    def calculate_brokerage_commission(self) -> float:
        if self.brokerage_commission is not None and '%' in self.brokerage_commission:
            brokerage_commission_num = self.brokerage_commission.split(" ")[0]
            brokerage_commission_float = float(brokerage_commission_num)/100
            return brokerage_commission_float
        else:
            raise Exception("No Percent Sign in String")
    
    def calculate_notary_fees(self) -> float:
        if self.notary_fees is not None and '%' in self.notary_fees:
            notary_fees_num = self.notary_fees.split(" ")[0]
            notary_fees_float = float(notary_fees_num)/100
            return notary_fees_float
        else:
            raise Exception("No Percent Sign in String")
    
    def calculate_land_registry_entry(self) -> float:
        if self.land_registry_entry is not None and '%' in self.land_registry_entry:
            land_registry_entry_num = self.land_registry_entry.split(" ")[0]
            land_registry_entry_float = float(land_registry_entry_num)/100
            return land_registry_entry_float
        else:
            raise Exception("No Percent Sign in String")

class House(RealEstate):
    def __init__(self, title: Optional[str], url: Optional[str], estate_type: Optional[str], price: Optional[Measurement], price_m2: Optional[Measurement], city: Optional[str], address: Optional[str], rooms: Optional[float], living_space: Optional[Measurement], property_space: Optional[Measurement], sleeping_rooms:  Optional[int], garage_parking_slots: Optional[int], rented: bool, provision: Optional[str], rent_income: Optional[Measurement], incidental_purchase_costs: Optional[str], property_acquisition_tax: Optional[str], brokerage_commission: Optional[str], notary_fees: Optional[str], land_registry_entry: Optional[str], total_costs: Optional[float], agency: Agency):
        super().__init__(title, url, estate_type, price, price_m2, city, address, rooms, living_space, sleeping_rooms, garage_parking_slots, rented, provision, rent_income, incidental_purchase_costs, property_acquisition_tax, brokerage_commission, notary_fees, land_registry_entry, total_costs, agency)
        self.property_space = property_space
        
class Apartment(RealEstate):
    def __init__(self, title: Optional[str], url: Optional[str], estate_type: Optional[str], price: Optional[Measurement], price_m2: Optional[Measurement], city: Optional[str], address: Optional[str], rooms: Optional[float], living_space: Optional[Measurement], sleeping_rooms: Optional[int], garage_parking_slots: Optional[int], rented: bool, provision: Optional[str], rent_income: Optional[Measurement], incidental_purchase_costs: Optional[str], property_acquisition_tax: Optional[str], brokerage_commission: Optional[str], notary_fees: Optional[str], land_registry_entry: Optional[str], total_costs: Optional[float], agency: Agency):
        super().__init__(title, url, estate_type, price, price_m2, city, address, rooms, living_space, sleeping_rooms, garage_parking_slots, rented, provision, rent_income, incidental_purchase_costs, property_acquisition_tax, brokerage_commission, notary_fees, land_registry_entry, total_costs, agency)
        
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
            city=params.get("city"),
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
            city=params.get("city"),
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