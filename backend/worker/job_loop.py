from backend.services.job_service import JobService
from sqlalchemy.orm import Session
from backend.database.models import engine
import time
from backend.shared.loki_handler import get_loki_logger
from backend.services.scraper_service import ScraperService
from backend.services.crawler_service import CrawlerService

worker_loop_logger = get_loki_logger("backend", {"app": "worker_loop_logger", "env": "dev"})

def worker_loop():
    job_service = JobService(CrawlerService(), ScraperService())
    
    while True:
        job = None

        try:
            with Session(engine) as session:
                job = job_service.claim_next_job(session)

            if job is None:
                time.sleep(2)
                continue


            job_service.process_job(job)

            with Session(engine) as session:
                job_service.mark_job_done(session, job["id"])

            time.sleep(2)
            
        except Exception as exc:
            worker_loop_logger.exception("Error in worker: %s", exc)

            if job is not None:
                try:
                    with Session(engine) as session:
                        job_service.mark_job_failed(session, job["id"])
                except Exception as db_exc:
                    worker_loop_logger.exception("Konnte Job %s nicht auf failed setzen: %s", job["id"], db_exc)

            time.sleep(2)

if __name__ == "__main__":
    worker_loop()