from datetime import datetime

from pydantic import BaseModel, ConfigDict


class PropertyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    url: str
    listing_type: str | None = None
    city: str | None = None
    zip_code: str | None = None
    address: str | None = None
    price: str | None = None
    price_m2: str | None = None
    space: str | None = None
    development: str | None = None
    building_permit: str | None = None
    available_from: str | None = None
    recommended_use: str | None = None
    floor_area_ratio: str | None = None
    floor_space_index: str | None = None
    provision: str | None = None
    incidental_purchase_costs: str | None = None
    property_acquisition_tax: str | None = None
    brokerage_commission: str | None = None
    notary_fees: str | None = None
    land_registry_entry: str | None = None
    land_transfer_tax: str | None = None
    general_description: str | None = None
    object_description: str | None = None
    place_description: str | None = None
    other_description: str | None = None
    total_costs: float | None = None
    agency_id: int | None = None
    is_online: bool
    created_at: datetime
    updated_at: datetime
