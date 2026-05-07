from sqlalchemy import update, select
from sqlalchemy.sql import func
from backend.services.scraper_service import ScraperService
from backend.services.crawler_service import CrawlerService
from backend.database.models import Job, Status

class JobService:
    def __init__(self, crawler_service: CrawlerService, scraper_service: ScraperService):
        self.crawler_service = crawler_service
        self.scraper_service = scraper_service
    
    
    def claim_next_job(self, session):
        subquery = (select(Job.id).where(Job.status == Status.open).order_by(Job.created_at.asc()).limit(1).with_for_update(skip_locked=True).scalar_subquery())
        stmt = (update(Job).where(Job.id == subquery).values(status=Status.processing, claimed_at=func.now()).returning(Job.id, Job.job_type, Job.search_params_id))
        result = session.execute(stmt)
        row = result.fetchone()
        session.commit()

        if row is None:
            return None
        return {
            "id": row.id,
            "job_type": row.job_type,
            "search_params_id": row.search_params_id
        }

    def mark_job_done(self, session, job_id: int): 
        stmt = update(Job).where(Job.id == job_id).values(status=Status.done)
        
        session.execute(stmt, {"job_id": job_id})
        session.commit()

    def mark_job_failed(self, session, job_id: int): 
        stmt = update(Job).where(Job.id == job_id).values(status=Status.failed)
        
        session.execute(stmt)
        session.commit()

    def process_job(self, job: dict):
        if job["job_type"] == "crawler":
            self.crawler_service.start_crawler(job["search_params_id"])
        elif job["job_type"] == "scraper":
            self.scraper_service.start_scraper(job["search_params_id"])
        else:
            raise ValueError(f"Unbekannter job_type: {job['job_type']}")