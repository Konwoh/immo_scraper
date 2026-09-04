from datetime import datetime
from pydantic import BaseModel, ConfigDict
from typing import Optional, Literal

class SearchParamRequest(BaseModel):
    site: str
    country: str
    state: str
    city: str
    distance: Optional[int] = None
    zip_code: Optional[str] = None
    estate_type: Literal["apartment", "house", "property"]
    rent_or_buy: Literal["buy", "rent"]
    page: int
    listing_count: int


class SearchParamsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    site: str
    country: str
    state: str
    city: str
    distance: Optional[int] = None
    zip_code: Optional[str] = None
    estate_type: str
    rent_or_buy: str
    page: int
    listing_count: int
    last_used: Optional[datetime] = None