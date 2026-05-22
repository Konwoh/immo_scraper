from backend.services.ScheduleService import ScheduleService
from sqlalchemy.orm import Session
from backend.database.models import engine
from datetime import datetime, timezone, timedelta
from backend.shared.loki_handler import get_loki_logger
from backend.database.models import Job, Status, JobSchedule
from typing import List
import time

schedule_loop_logger = get_loki_logger("backend", {"app": "schedule_loop_logger", "env": "dev"})

def worker_loop():
    try:
        scheduler = ScheduleService()
        while True:
            with Session(engine) as session:
                due_jobs: List[JobSchedule] = scheduler.claim_due_schedule(session)
            
                for job_schedule in due_jobs:
                    new_job = Job(
                        job_type=job_schedule.job_type,
                        search_params_id=job_schedule.search_params_id,
                        status=Status.open,
                        schedule_id=job_schedule.id,
                        scheduled_for=job_schedule.next_run,
                    )
                    session.add(new_job)
                    
                    now = datetime.now(timezone.utc)
                    job_schedule.last_run = now
                    
                    if job_schedule.interval == "weekly":
                        job_schedule.next_run = job_schedule.next_run + timedelta(weeks=1)
                    elif job_schedule.interval == "daily":
                        job_schedule.next_run = job_schedule.next_run + timedelta(days=1)
                    elif job_schedule.interval == "hourly":
                        job_schedule.next_run = job_schedule.next_run + timedelta(hours=1)
                    else:
                        raise ValueError(f"No known interval: {job_schedule.interval}")
                    
                session.commit()
                    
            time.sleep(60)
    except Exception as e:
        schedule_loop_logger.exception("Error in schedule loop: %s", e)

if __name__ == '__main__':
    worker_loop()