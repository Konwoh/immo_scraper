from datetime import datetime, timezone
from typing import Type, Optional, List
from backend.database.models import UrlQueue, Status, SearchResults, Apartment, House
from sqlalchemy.orm import Session
from sqlalchemy import select, update
from backend.parser.factory import EstateParserCreator
from backend.parser.base_parser import Parser
from backend.shared.loki_handler import get_loki_logger
import time
from sqlalchemy.exc import IntegrityError
import random

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
            url_queue_obj: Optional[UrlQueue] = session.execute(stmt).scalars().first()
            if url_queue_obj is None:
                scraper_logger.info("No open jobs")
                return
            url_queue_obj.claimed_at = datetime.now(timezone.utc)
            url_queue_obj.status = Status.processing
            if 'immobilienscout24' in url_queue_obj.url:
                result = {"id": url_queue_obj.id, "url": url_queue_obj.url, "site": "immoScout"}
            elif 'kleinanzeigen' in url_queue_obj.url:
                result = {"id": url_queue_obj.id, "url": url_queue_obj.url, "site": "kleinanzeigen"}
            else:
                raise ValueError("Site not available")
            session.commit()

            return result
    
    def finalize_job(self, job_id: int, success: bool, estate_obj = None) -> int|None:
        with Session(self.engine) as session:
            try:
                if estate_obj is not None:
                    persisted = None
                    # Ab hier wird das RealEstate-Objekt "estate_obj" in die jeweilige house oder apartments Tabelle gespeichert.
                    # Zusätzlich wird in der Verknüpfungstabelle search_results ein Eintrag für jedes Estate pro search_param angelegt.
                    # Wenn in unterschiedlichen search_params die gleichen estate kommen, sollen diese über search_results referenziert werden und nicht doppelt
                    # in die house oder apartmens tabellen geschrieben werden.
                try:
                    with session.begin_nested():
                            if estate_obj is None:
                                session.execute(
                                    update(self.model)
                                    .where(self.model.id == job_id)
                                    .values(status=Status.failed)
                                )
                                session.commit()
                                return
                            else:
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
                        raise TypeError(f"Unknown estate type: {type(estate_obj)}")
                    
                estate_id = persisted.id
                        
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
                    
                try:
                    with session.begin_nested():
                        session.add(link)
                        session.flush()
                except IntegrityError:
                    pass
                    
                stmt = (update(self.model).where(self.model.id == job_id).values(status=Status.done if success else Status.failed))
                session.execute(stmt)
                session.commit()
                
                return estate_id
            
            except Exception:
                session.rollback()
                scraper_logger.error("Finalizing the job failed: Session rollback")
                raise
    
    def process(self, amount_rows: int):
        counter = 0
        estate_parser_creator = EstateParserCreator()
        parser_cache: dict[str, Parser] = {}
        found_house_ids: List[int] = []
        found_apartment_ids: List[int] = []
        while counter < amount_rows:
            url_queue_obj = None
            try:
                url_queue_obj = self.get_row()
                if url_queue_obj is None:
                    scraper_logger.info("No open jobs left")
                    break
                site = url_queue_obj["site"]
                self.search_params_id 
                if site not in parser_cache:
                    parser_cache[site] = estate_parser_creator.create_parser(site)

                parser = parser_cache[site]
                
                estate = parser.fetch(url_queue_obj["url"])
                
                if estate is None:
                    raise ValueError("Parser returned None")
                
                estate_id = self.finalize_job(url_queue_obj["id"], True, estate)
                
                if estate_id is not None:
                    if isinstance(estate, House):
                        found_house_ids.append(estate_id)
                    elif isinstance(estate, Apartment):
                        found_apartment_ids.append(estate_id)
                
                counter += 1
                time.sleep(random.uniform(2, 4))

            except Exception as exc:
                if url_queue_obj is None:
                    scraper_logger.error(f"Processing failed: job is None: {str(exc)}")
                    break
                    
                self.finalize_job(url_queue_obj["id"], False)
                scraper_logger.error(
                    f"Processing failed for job={url_queue_obj['id']}, url={url_queue_obj['url']}: {str(exc)}"
                )
                counter += 1
                
        self.check_online_availability(found_house_ids, "House")
        self.check_online_availability(found_apartment_ids, "Apartment")

    def check_online_availability(self, estate_id_list: List[int], estate_type: str):
        with Session(self.engine) as session:
            if estate_type == "House":
                offline_ids = (
                    session.query(House.id)
                    .join(SearchResults, House.id == SearchResults.house_id)
                    .filter(SearchResults.search_params_id == self.search_params_id)
                    .filter(House.id.notin_(estate_id_list))
                    .all()
                )

                offline_ids = [x[0] for x in offline_ids]

                session.query(House).filter(House.id.in_(offline_ids)).update({House.is_online: False}, synchronize_session=False)   
                         
            elif estate_type == "Apartment":
                offline_ids = (
                    session.query(Apartment.id)
                    .join(SearchResults, Apartment.id == SearchResults.apartment_id)
                    .filter(SearchResults.search_params_id == self.search_params_id)
                    .filter(Apartment.id.notin_(estate_id_list))
                    .all()
                )

                offline_ids = [x[0] for x in offline_ids]

                session.query(Apartment).filter(Apartment.id.in_(offline_ids)).update({Apartment.is_online: False}, synchronize_session=False)                   
            session.commit()
