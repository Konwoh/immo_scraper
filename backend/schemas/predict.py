from pydantic import BaseModel

class PredictionResponse(BaseModel):
    predicted_price: float

class PredictionPayload(BaseModel):
    estate_type: str | None = None
    rent_cold: float | None = None
    rent_complete: float | None = None
    house_money: float | None = None
    rent_heating_costs: float | None = None
    zip_code: str | None = None
    rooms: float | None = None
    sleeping_rooms: float | None = None
    bathrooms: float | None = None
    floor: float | None = None
    living_space: float | None = None
    garage_parking_slots: float | None = None
    lift: bool | None = None
    barrier_free: bool | None = None
    garden: bool | None = None
    internet_speed_telekom: float | None = None
    fitted_kitchen: bool | None = None
    basement: bool | None = None
    rented: bool | None = None
    provision: str | None = None
    rent_income: float | None = None
    building_year: float | None = None
    estate_condition: str | None = None
    interior_quality: str | None = None
    heating_type: str | None = None
    energy_performance_certificate_type: str | None = None
    energy_source: str | None = None
    energy_demand: float | None = None
    energy_efficiency_class: str | None = None
    is_online: bool | None = None
    property_space: float | None = None
