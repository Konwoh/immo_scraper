import concurrent.futures
from typing import Type, Optional
from database import UrlQueue, UrlStatus
from sqlalchemy.orm import Session
from sqlalchemy import select, update, create_engine
from helper import Headers
import datetime
import requests
from parser import Parser
import os

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
                # Im Zweifelsfall loggen
                raise
    
    def process(self):
        try:
            headers = self.headers.build_header()
            job = self.get_row()
            if job is not None:
                url = f"https://api.mobile.immobilienscout24.de/expose/{job["url"].split("/")[-1]}"
                response = requests.get(url, headers=headers)
                estate = self.estate_parser.parse(response)
                self.finalize_job(job["id"], True, estate)
                print("Extraction succesful")
        except Exception as exc:
            if job is None:
                print(f"Processing failed: job is None: {str(exc)}")
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
                print(f"Processing failed for job={job["id"]}, url={job["url"]}: {str(exc)}")

from main import EstateParserCreator
engine = create_engine(os.environ["DB_CONNECTION_STRING"], echo=False)
headers = Headers('application/json', 'ImmoScout_27.14.1_26.3_._', 'de-de')
estate_parser = EstateParserCreator()
parser = estate_parser.create_parser()
worker_1 = Worker(engine, UrlQueue, headers, parser)
worker_1.process()