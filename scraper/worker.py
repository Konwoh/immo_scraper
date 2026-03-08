from typing import Type, Optional
from database.models import UrlQueue, UrlStatus
from sqlalchemy.orm import Session
from sqlalchemy import select, update
from core.helper import Headers
from core.parser import Parser
import datetime
import requests
import logging
import time

logging.basicConfig(
    filename="logging/scraper.log",
    level=logging.ERROR,
    format="{asctime} - {levelname} - {message}",
    style="{",
    datefmt="%Y-%m-%d %H:%M:%S")

scraper_logger = logging.getLogger("scraper")

class Worker:
    
    def __init__(self, engine, model: Type[UrlQueue], headers: Headers, estate_parser: Parser) -> None:
        self.engine = engine
        self.model = model
        self.headers = headers
        self.estate_parser = estate_parser
        
    def get_row(self):
        stmt = (
            select(self.model)
            .where(self.model.status == "open", self.model.claimed_at.is_(None))
            .order_by(self.model.created_at.desc())
            .with_for_update(skip_locked=True)
            .limit(1)
        )
        
        with Session(self.engine) as session:
            job: Optional[UrlQueue] = session.execute(stmt).scalars().first()
            if job is None:
                print("No open jobs")
                return
            job.claimed_at = datetime.datetime.now()
            job.status = UrlStatus.processing
            result = {"id": job.id, "url": job.url}
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
        while counter < amount_rows:
            try:
                headers = self.headers.build_header()
                job = self.get_row()
                if job is not None:
                    url = f"https://api.mobile.immobilienscout24.de/expose/{job["url"].split("/")[-1]}"
                    #url="https://api.mobile.immobilienscout24.de/expose/164276395"
                    response = requests.get(url, headers=headers)
                    estate = self.estate_parser.parse(response)
                    self.finalize_job(job["id"], True, estate)
                    time.sleep(2)
                    counter += 1
                    scraper_logger.info("Extraction succesful")

            except Exception as exc:
                if job is None:
                    scraper_logger.error(f"Processing failed: job is None: {str(exc)}")
                    counter += 1
                else:
                    with Session(self.engine) as session:
                        stmt = (
                                update(self.model)
                                .where(self.model.id == job["id"])
                                .values(
                                    status=UrlStatus.failed,
                                )
                            )
                        session.execute(stmt)
                        session.commit()
                    scraper_logger.error(f"Processing failed for job={job["id"]}, url={job["url"]}: {str(exc)}")
                    counter += 1