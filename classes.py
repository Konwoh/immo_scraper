class Agency:
    def __init__(self, name: str, rating: float, rating_count: int, homepage: str, address: str):
        self.name = name
        self.rating = rating
        self.rating_count = rating_count
        self.homepage = homepage
        self.address = address

class RealEstate:
    def __init__(self, title: str, estate_type: str, price: float, price_m2: float, city: str, address:str, rooms: float, living_space: float, sleeping_rooms: int, garage_parking_slots: int, rented: bool, provision: str, rent_income: float, incidental_purchase_costs: str, property_acquisition_tax: str, brokerage_commission: str, notary_fees: str, land_registry_entry: str, total_costs: float, agency: Agency):
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

class House(RealEstate):
    def __init__(self, title: str, estate_type: str, price: float, price_m2: float, city: str, address:str, rooms: float, living_space: float, sleeping_rooms: int, garage_parking_slots: int, rented: bool, provision: str, rent_income: float, incidental_purchase_costs: str, property_acquisition_tax: str, brokerage_commission: str, notary_fees: str, land_registry_entry: str, total_costs: float, agency: Agency, property_space: float):
        super().__init__(title, estate_type, price, price_m2, city, address, rooms, living_space, sleeping_rooms, garage_parking_slots, rented, provision, rent_income, incidental_purchase_costs, property_acquisition_tax, brokerage_commission, notary_fees, land_registry_entry, total_costs, agency)
        self.property_space = property_space


class Apartment(RealEstate):
    def __init__(self, title: str, estate_type: str, price: float, price_m2: float, city: str, address:str, rooms: float, living_space: float, sleeping_rooms: int, garage_parking_slots: int, rented: bool, provision: str, rent_income: float, incidental_purchase_costs: str, property_acquisition_tax: str, brokerage_commission: str, notary_fees: str, land_registry_entry: str, total_costs: float, agency: Agency):
        super().__init__(title, estate_type, price, price_m2, city, address, rooms, living_space, sleeping_rooms, garage_parking_slots, rented, provision, rent_income, incidental_purchase_costs, property_acquisition_tax, brokerage_commission, notary_fees, land_registry_entry, total_costs, agency)