from pydantic import BaseModel
from typing import Literal
from datetime import datetime

class JobScheduleRequest(BaseModel):
    job_type: Literal["scraper", "crawler"]
    search_params_id: int
    interval: Literal["hourly", "daily", "weekly"]
    enabled: bool
    next_run: datetime