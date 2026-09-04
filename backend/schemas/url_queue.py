from datetime import datetime
from pydantic import BaseModel, ConfigDict, HttpUrl
from backend.database.models import Status

class UrlQueueRequest(BaseModel):
    search_params_id: int
    url: HttpUrl
    status: Status = Status.open


class UrlQueueResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    search_params_id: int
    url: str
    status: Status
    claimed_by: int | None = None
    claimed_at: datetime | None = None
    created_at: datetime
    updated_at: datetime
