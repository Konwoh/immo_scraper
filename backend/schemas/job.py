from pydantic import BaseModel
from backend.database.models import Status
from typing import Literal

class JobRequest(BaseModel):
    job_type: Literal["scraper", "crawler"]
    status: Status = Status.open
    search_params_id: int