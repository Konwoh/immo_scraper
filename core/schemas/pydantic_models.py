from pydantic import BaseModel, Field, HttpUrl
from database.models import Status

class JobRequest(BaseModel):
    job_type: str = Field(min_length=1)
    status: Status = Status.open

class UrlQueueRequest(BaseModel):
    url: HttpUrl
    status: Status = Status.open