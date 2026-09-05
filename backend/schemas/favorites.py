from datetime import datetime
from pydantic import BaseModel, ConfigDict


class FavoriteResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    house_id: int | None = None
    apartment_id: int | None = None
    property_id: int | None = None
    created_at: datetime
    updated_at: datetime