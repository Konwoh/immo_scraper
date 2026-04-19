from sqlalchemy import update, select
from sqlalchemy.sql import func
from scraper.base import start_scraper
from crawler.base import start_crawler
from sqlalchemy.orm import Session
from database.models import engine, Job, Status
import time
from core.loki_handler import get_loki_logger
worker_loop_logger = get_loki_logger("core", {"app": "worker_loop_logger", "env": "dev"})

def claim_next_job(session):
    subquery = (select(Job.id).where(Job.status == Status.open).order_by(Job.created_at.asc()).limit(1).with_for_update(skip_locked=True).scalar_subquery())
    stmt = (update(Job).where(Job.id == subquery).values(status=Status.processing, claimed_at=func.now()).returning(Job.id, Job.job_type))
    result = session.execute(stmt)
    row = result.fetchone()
    session.commit()

    if row is None:
        return None
    return {
        "id": row.id,
        "job_type": row.job_type,
    }

def mark_job_done(session, job_id: int): 
    stmt = update(Job).where(Job.id == job_id).values(status=Status.done)
    
    session.execute(stmt, {"job_id": job_id})
    session.commit()

def mark_job_failed(session, job_id: int): 
    stmt = update(Job).where(Job.id == job_id).values(status=Status.failed)
    
    session.execute(stmt)
    session.commit()

def process_job(job: dict):
    if job["job_type"] == "crawler":
        start_crawler()
    elif job["job_type"] == "scraper":
        start_scraper()
    else:
        raise ValueError(f"Unbekannter job_type: {job['job_type']}")

def worker_loop():
    while True:
        job = None

        try:
            with Session(engine) as session:
                job = claim_next_job(session)

            if job is None:
                time.sleep(2)
                continue


            process_job(job)

            with Session(engine) as session:
                mark_job_done(session, job["id"])

            time.sleep(2)
            
        except Exception as exc:
            worker_loop_logger.exception("Error in worker: %s", exc)

            if job is not None:
                try:
                    with Session(engine) as session:
                        mark_job_failed(session, job["id"])
                except Exception as db_exc:
                    worker_loop_logger.exception("Konnte Job %s nicht auf failed setzen: %s", job["id"], db_exc)

            time.sleep(2)

if __name__ == "__main__":
    worker_loop()