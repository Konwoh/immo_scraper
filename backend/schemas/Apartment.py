from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ApartmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    url: str
    estate_type: str | None = None
    listing_type: str | None = None
    price: str | None = None
    price_m2: str | None = None
    rent_cold: str | None = None
    rent_complete: str | None = None
    house_money: str | None = None
    rent_extra_costs: str | None = None
    rent_heating_costs: str | None = None
    rent_deposit: str | None = None
    city: str | None = None
    zip_code: str | None = None
    address: str | None = None
    rooms: float | None = None
    sleeping_rooms: int | None = None
    bathrooms: int | None = None
    floor: str | None = None
    living_space: str | None = None
    garage_parking_slots: int | None = None
    lift: bool | None = None
    barrier_free: bool | None = None
    garden: bool | None = None
    internet_speed_telekom: str | None = None
    fitted_kitchen: bool | None = None
    basement: bool | None = None
    rented: bool | None = None
    available_from: str | None = None
    provision: str | None = None
    rent_income: str | None = None
    incidental_purchase_costs: str | None = None
    property_acquisition_tax: str | None = None
    brokerage_commission: str | None = None
    notary_fees: str | None = None
    land_registry_entry: str | None = None
    building_year: str | None = None
    estate_condition: str | None = None
    interior_quality: str | None = None
    heating_type: str | None = None
    energy_performance_certificate_type: str | None = None
    energy_source: str | None = None
    energy_demand: str | None = None
    energy_efficiency_class: str | None = None
    general_description: str | None = None
    object_description: str | None = None
    place_description: str | None = None
    other_description: str | None = None
    total_costs: float | None = None
    is_online: bool
    agency_id: int | None = None
    created_at: datetime
    updated_at: datetime
