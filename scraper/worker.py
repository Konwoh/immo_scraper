from datetime import datetime, timezone
from typing import Type, Optional
from database.models import UrlQueue, Status, SearchResults, Apartment, House
from sqlalchemy.orm import Session
from sqlalchemy import select, update
from core.parser import EstateParserCreator
from core.loki_handler import get_loki_logger
import time
from sqlalchemy.exc import IntegrityError

scraper_logger = get_loki_logger("scraper", {"app": "scraper", "env": "dev"})

class Worker:
    
    def __init__(self, engine, model: Type[UrlQueue], search_params_id: int) -> None:
        self.engine = engine
        self.model = model
        self.search_params_id = search_params_id
        
    def get_row(self):
        stmt = (
            select(self.model)
            .filter(UrlQueue.search_params_id == self.search_params_id)
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
            job.claimed_at = datetime.now(timezone.utc)
            job.status = Status.processing
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
                    persisted = None
                # Ab hier wird das RealEstate-Objekt "estate_obj" in die jeweilige house oder apartments Tabelle gespeichert. 
                # Zusätzlich wird in der Verknüpfungstabelle search_results ein Eintrag für jedes Estate pro search_param angelegt
                # wenn in unterschiedlichen search_params die gleichen estate kommen, sollen diese über search_results referenziert werden und nicht doppelt
                # in die house oder apartmens tabellen geschrieben werden
                try:
                    with session.begin_nested():
                            session.add(estate_obj)
                            session.flush()
                            persisted = estate_obj
                except IntegrityError: # Fehler, wenn estate_obj schon in house oder apartments tabelle existiert
                    if isinstance(estate_obj, House):
                        persisted = session.execute(
                            select(House).where(
                                House.url == estate_obj.url,
                                House.title == estate_obj.title,
                            ) # Referenz des original eintrag bekommen um das dann in search_results tabelle referenzieren zu können
                        ).scalar_one()
                    elif isinstance(estate_obj, Apartment):
                        persisted = session.execute(
                            select(Apartment).where(
                                Apartment.url == estate_obj.url,
                                Apartment.title == estate_obj.title,
                            )
                        ).scalar_one()
                    else:
                        raise TypeError(f"Unknown estate type: {type(persisted)}")                
                        
                if isinstance(persisted, House):
                    link = SearchResults(
                        search_params_id=self.search_params_id,
                        house_id=persisted.id,
                        apartment_id=None
                    )
                elif isinstance(persisted, Apartment):
                    link = SearchResults(
                        search_params_id=self.search_params_id,
                        house_id=None,
                        apartment_id=persisted.id
                    )
                else:
                    raise TypeError("Unknown estate type")
                    
                session.add(link)
                try:
                    session.flush()
                except IntegrityError:
                    session.rollback()
                    
                stmt = (update(self.model).where(self.model.id == job_id).values(status=Status.done if success else Status.failed))
                session.execute(stmt)
                session.commit()
                
            except Exception:
                session.rollback()
                scraper_logger.error("Finalizing the job failed: Session rollback")
                raise
    
    def process(self, amount_rows: int):
        counter = 0
        estate_parser_creator = EstateParserCreator()
        parser_cache = {}
        while counter < amount_rows:
            job = None
            try:
                job = self.get_row()
                if job is None:
                    scraper_logger.info("No open jobs left")
                    break
                site = job["site"]
                
                if site not in parser_cache:
                    parser_cache[site] = estate_parser_creator.create_parser(site)

                parser = parser_cache[site]
                
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
