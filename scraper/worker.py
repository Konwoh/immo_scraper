from typing import Type, Optional
from database.models import UrlQueue, UrlStatus
from sqlalchemy.orm import Session
from sqlalchemy import select, update
from core.helper import Headers
from core.parser import EstateParserCreator
import datetime
import requests
from core.loki_handler import get_loki_logger
import time

scraper_logger = get_loki_logger("scraper", {"app": "scraper", "env": "dev"})

class Worker:
    
    def __init__(self, engine, model: Type[UrlQueue]) -> None:
        self.engine = engine
        self.model = model
        
    def get_row(self):
        stmt = (
            select(self.model)
            .where(self.model.status == "open", self.model.claimed_at.is_(None))
            .order_by(self.model.created_at.asc())
            .with_for_update(skip_locked=True)
            .limit(1)
        )
        
        with Session(self.engine) as session:
            job: Optional[UrlQueue] = session.execute(stmt).scalars().first()
            if job is None:
                scraper_logger.info("No open jobs")
                return
            job.claimed_at = datetime.datetime.now()
            job.status = UrlStatus.processing
            if 'immobilienscout24' in job.url:
                result = {"id": job.id, "url": job.url, "site": "immoScout"}
            elif 'kleinanzeigen' in job.url:
                result = {"id": job.id, "url": job.url, "site": "kleinanzeigen"}
            else:
                raise ValueError("Site not available")
            session.commit()

            return result
    
    def finalize_job(self, job_id: int, success: bool, estate_obj=None):
        with Session(self.engine) as session:
            try:
                if estate_obj is not None:
                    session.add(estate_obj)
                    session.flush()

                if success:
                    stmt = (
                        update(self.model)
                        .where(self.model.id == job_id)
                        .values(
                            status=UrlStatus.done,
                        )
                    )
                else:
                    stmt = (
                        update(self.model)
                        .where(self.model.id == job_id)
                        .values(
                            status=UrlStatus.failed,
                        )
                    )

                session.execute(stmt)
                session.commit()
            except Exception:
                session.rollback()
                scraper_logger.error("Finalizing the job failed: Session rollback")
                raise
    
    def process(self, amount_rows: int):
        counter = 0
        estate_parser_creator = EstateParserCreator()
        while counter < amount_rows:
            job = None
            try:
                job = self.get_row()
                if job is None:
                    scraper_logger.info("No open jobs left")
                    break
                
                parser = estate_parser_creator.create_parser(job["site"])
                estate = parser.fetch(job["url"])
                
                self.finalize_job(job["id"], True, estate)
                scraper_logger.info("Extraction successful")
                
                counter += 1
                time.sleep(2)

            except Exception as exc:
                if job is None:
                    scraper_logger.error(f"Processing failed: job is None: {str(exc)}")
                    break
                    
                self.finalize_job(job["id"], False)
                scraper_logger.error(
                    f"Processing failed for job={job['id']}, url={job['url']}: {str(exc)}"
                )
                counter += 1
