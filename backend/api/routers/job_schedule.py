from fastapi import status, HTTPException, Depends, Path, APIRouter
from backend.database.models import JobSchedule, get_db, SearchParams
from sqlalchemy.orm import Session
from backend.schemas.job_schedule import JobScheduleRequest, JobScheduleUpdateRequest
from backend.api.auth.oauth2 import get_current_user

router = APIRouter(
    prefix="/jobs_schedules",
    tags=["Jobs Schedule"]
)

@router.get("/", status_code=status.HTTP_200_OK)
def get_jobs(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    jobs_schedule = (db.query(JobSchedule).join(SearchParams, JobSchedule.search_params_id == SearchParams.id).filter(SearchParams.user_id == current_user.id).all())

    if jobs_schedule is not None:
        return jobs_schedule
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No jobs schedules found")

@router.get("/{job_schedule_id}", status_code=status.HTTP_200_OK)
def get_jobs_by_id(db: Session = Depends(get_db), job_schedule_id: int = Path(gt=0), current_user = Depends(get_current_user)):
    job = db.query(JobSchedule).filter(JobSchedule.id == job_schedule_id).first()
    if job is not None:
        search_param = db.query(SearchParams).filter(SearchParams.id == job.search_params_id).first()
        if search_param is not None and search_param.user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to retrieve this job schedule")
        return job
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"job schedule with id: {job_schedule_id} not found") 

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_jobs(job_schedule_request: JobScheduleRequest, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    search_param = (db.query(SearchParams).filter(SearchParams.id == job_schedule_request.search_params_id, SearchParams.user_id == current_user.id).first())
    
    if search_param is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to create this job")
        
    new_job = JobSchedule(**job_schedule_request.model_dump())
    db.add(new_job)
    db.commit()
    
    return new_job

@router.patch("/{job_schedule_id}", status_code=status.HTTP_200_OK)
def update_job_schedule(
    job_schedule_request: JobScheduleUpdateRequest,
    job_schedule_id: int = Path(gt=0),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    jobs_schedule = (
        db.query(JobSchedule)
        .join(SearchParams, JobSchedule.search_params_id == SearchParams.id)
        .filter(
            SearchParams.user_id == current_user.id,
            JobSchedule.id == job_schedule_id,
        )
        .first()
    )

    if jobs_schedule is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No jobs schedules found for update",
        )

    update_data = job_schedule_request.model_dump(exclude_unset=True)

    if "search_params_id" in update_data:
        search_param = (
            db.query(SearchParams)
            .filter(
                SearchParams.id == update_data["search_params_id"],
                SearchParams.user_id == current_user.id,
            )
            .first()
        )

        if search_param is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to use this search params entry",
            )

    for key, value in update_data.items():
        setattr(jobs_schedule, key, value)

    db.commit()
    db.refresh(jobs_schedule)

    return jobs_schedule
