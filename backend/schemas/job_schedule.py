from pydantic import BaseModel
from typing import Literal
from datetime import datetime

class JobScheduleRequest(BaseModel):
    job_type: Literal["scraper", "crawler"]
    search_params_id: int
    interval: Literal["hourly", "daily", "weekly", "3-hourly", "6-hourly"]
    enabled: bool
    next_run: datetime


class JobScheduleUpdateRequest(BaseModel):
    job_type: Literal["scraper", "crawler"] | None = None
    search_params_id: int | None = None
    interval: Literal["hourly", "daily", "weekly", "3-hourly", "6-hourly"] | None = None
    enabled: bool | None = None
    next_run: datetime | None = None
