from backend.database.models import JobSchedule
from sqlalchemy import select
from datetime import datetime, timezone
from sqlalchemy.orm import Session

class ScheduleService():
    def __init__(self):
        pass
    
    def claim_due_schedule(self, session: Session):
        now = datetime.now(timezone.utc)
        stmt = select(JobSchedule).filter(JobSchedule.enabled == True, JobSchedule.next_run <= now).with_for_update(skip_locked=True)
        due_jobs = session.execute(stmt)
        due_jobs = [x[0] for x in due_jobs]
        
        return due_jobs