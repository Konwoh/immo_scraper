from fastapi import FastAPI, status, HTTPException, Depends, Path
from fastapi.middleware.cors import CORSMiddleware
from database.models import Job, Status, Apartment, House, SearchParams, UrlQueue, Agency, get_db
from sqlalchemy.orm import Session
from core.schemas.pydantic_models import JobRequest, UrlQueueRequest

app = FastAPI()

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
        
        
@app.get("/start_crawler", status_code=status.HTTP_200_OK)
def start_crawler_endpoint(db: Session = Depends(get_db)):
    job = Job(job_type="crawler", status=Status.open)
    db.add(job)
    db.commit()
        

@app.get("/apartments", status_code=status.HTTP_200_OK)
def get_apartmens(db: Session = Depends(get_db)):
    apartments = db.query(Apartment).all()
    if apartments is not None:
        return apartments
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No apartments found") 

@app.get("/apartments/{apartment_id}", status_code=status.HTTP_200_OK)
def get_apartment_by_id(db: Session = Depends(get_db), apartment_id: int = Path(gt=0)):
    apartment = db.query(Apartment).filter(Apartment.id == apartment_id).first()
    if apartment is not None:
        return apartment
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"apartment with id {apartment_id} not found") 

@app.get("houses", status_code=status.HTTP_200_OK)
def get_houses(db: Session = Depends(get_db)):
    houses = db.query(House).all()
    if houses is not None:
        return houses
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No houses found")

@app.get("house/{id}", status_code=status.HTTP_200_OK)
def get_houses_by_id(db: Session = Depends(get_db), house_id: int = Path(gt=0)):
    house = db.query(House).filter(House.id == house_id).first()
    if house is not None:
        return house
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"house with id: {house_id} not found")

@app.get("search_params", status_code=status.HTTP_200_OK)
def get_search_params(db: Session = Depends(get_db)):
    search_params = db.query(SearchParams).all()
    if search_params is not None:
        return search_params
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No search params found")

@app.get("search_params/{id}", status_code=status.HTTP_200_OK)
def get_search_params_by_id(db: Session = Depends(get_db), search_params_id: int = Path(gt=0)):
    search_param = db.query(SearchParams).filter(SearchParams.id == search_params_id).first()
    if search_param is not None:
        return search_param
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"search param with id: {search_params_id} not found")

@app.get("/jobs", status_code=status.HTTP_200_OK)
def get_jobs(db: Session = Depends(get_db)):
    jobs = db.query(Job).all()
    if jobs is not None:
        return jobs
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No jobs found")

@app.get("/jobs/{job_id}", status_code=status.HTTP_200_OK)
def get_jobs_by_id(db: Session = Depends(get_db), job_id: int = Path(gt=0)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if job is not None:
        return job
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"job with id: {job_id} not found") 

@app.post("/jobs", status_code=status.HTTP_201_CREATED)
def create_jobs(job_request: JobRequest, db: Session = Depends(get_db)):
    new_job = Job(**job_request.model_dump())
    db.add(new_job)
    db.commit()

@app.get("/url_queue", status_code=status.HTTP_200_OK)
def get_url_queue(db: Session = Depends(get_db)):
    url_queue = db.query(UrlQueue).all()
    if url_queue is not None:
        return url_queue
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No url queue found")

@app.get("/url_queue/{url_queue_id}", status_code=status.HTTP_200_OK)
def get_url_queue_by_id(db: Session = Depends(get_db), url_queue_id: int = Path(gt=0)):
    url_queue_obj = db.query(UrlQueue).filter(UrlQueue.id == url_queue_id).first()
    if url_queue_obj is not None:
        return url_queue_obj
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"url queue object with id: {url_queue_id} not found")

@app.post("/url_queue", status_code=status.HTTP_201_CREATED)
def create_url_queue(url_queue_request: UrlQueueRequest, db: Session = Depends(get_db)):
    new_url_queue_obj = Job(**url_queue_request.model_dump())
    db.add(new_url_queue_obj)
    db.commit()