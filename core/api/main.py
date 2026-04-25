from fastapi import FastAPI, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from database.models import Job, Status, get_db
from sqlalchemy.orm import Session
from core.api.routers import users, houses, apartments, search_params, jobs, url_queue
app = FastAPI()

app.include_router(users.router)
app.include_router(houses.router)
app.include_router(apartments.router)
app.include_router(search_params.router)
app.include_router(jobs.router)
app.include_router(url_queue.router)

origins = [
    "http://localhost:7000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["GET"],
    allow_headers=["*"])

@app.get("/start_scraper", status_code=status.HTTP_200_OK)
def start_scraper_endpoint(db: Session = Depends(get_db)):
    job = Job(job_type="scraper", status=Status.open)
    db.add(job)
    db.commit()
    # ToDO: Success Meldung in response gegebn mit response_model von pydantic
        
        
@app.get("/start_crawler", status_code=status.HTTP_200_OK)
def start_crawler_endpoint(db: Session = Depends(get_db)):
    job = Job(job_type="crawler", status=Status.open)
    db.add(job)
    db.commit()
    # ToDO: Success Meldung in response gegebn mit response_model von pydantic