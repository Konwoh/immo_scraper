from pydantic import BaseModel, HttpUrl
from backend.database.models import Status

class UrlQueueRequest(BaseModel):
    search_params_id: int
    url: HttpUrl
    status: Status = Status.open
