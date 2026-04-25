from fastapi import status, HTTPException, Depends, Path, APIRouter
from database.models import Job, get_db
from sqlalchemy.orm import Session
from core.schemas.pydantic_models import JobRequest

router = APIRouter()

@router.get("/jobs", status_code=status.HTTP_200_OK)
def get_jobs(db: Session = Depends(get_db)):
    jobs = db.query(Job).all()
    if jobs is not None:
        return jobs
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No jobs found")

@router.get("/jobs/{job_id}", status_code=status.HTTP_200_OK)
def get_jobs_by_id(db: Session = Depends(get_db), job_id: int = Path(gt=0)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if job is not None:
        return job
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"job with id: {job_id} not found") 

@router.post("/jobs", status_code=status.HTTP_201_CREATED)
def create_jobs(job_request: JobRequest, db: Session = Depends(get_db)):
    new_job = Job(**job_request.model_dump())
    db.add(new_job)
    db.commit()
    
    return new_job