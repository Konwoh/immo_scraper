from datetime import datetime
from pydantic import BaseModel, ConfigDict
from backend.database.models import Status
from typing import Literal

class JobRequest(BaseModel):
    job_type: Literal["scraper", "crawler"]
    status: Status = Status.open
    search_params_id: int


class JobResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    search_params_id: int
    schedule_id: int | None = None
    job_type: str
    status: Status
    scheduled_for: datetime | None = None
    claimed_at: datetime | None = None
    created_at: datetime
    updated_at: datetime