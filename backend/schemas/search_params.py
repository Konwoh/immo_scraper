from pydantic import BaseModel
from typing import Optional, Literal

class SearchParamRequest(BaseModel):
    site: str
    country: str
    state: str
    city: str
    distance: Optional[int] = None
    zip_code: Optional[str] = None
    estate_type: Literal["apartment", "house"]
    rent_or_buy: Literal["buy", "rent"]
    page: int
    listing_count: int