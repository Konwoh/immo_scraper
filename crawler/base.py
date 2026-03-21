from sqlalchemy.orm import Session
from sqlalchemy import select
from core.parser import EstateParserCreator
from core.helper import Headers
from database.models import engine, UrlQueue, SearchParams
from sqlalchemy.dialects.postgresql import insert
from .crawler import create_factory
from .crawler import crawler_logger
from datetime import datetime
import json
import time

cookies = {
    'IS24VisitId': 'vid217f62bd-6a5b-4ca6-8a1b-bd4bf93c9251',
}


def main():
    try:
        currentPage = 1
        numberOfPages = 10
        with Session(engine) as session:
            
            param = session.execute(
                select(SearchParams)
                .order_by(SearchParams.last_used.asc().nullsfirst())
                .limit(1)
                .with_for_update(skip_locked=True)
            ).scalar_one_or_none()
            
            if param is None:
                session.rollback()
                crawler_logger.error("No search params available")
                return   
            
            completed = True
            
            while currentPage <= numberOfPages:
                try:
                    headers = Headers('application/json', 'ImmoScout_27.11_26.2_._', 'de-de')

                    param.page = currentPage
                    immo_scout_factory = create_factory("Immoscout")
                    immo_scout_crawler = immo_scout_factory.create_crawler(param, headers)
                    response = immo_scout_crawler.crawl()
                    response_json = json.loads(response.text)
                    numberOfPages = response_json["numberOfPages"]

                    estate_parser = EstateParserCreator()
                    parser = estate_parser.create_parser()
                    url_queue_list = parser.url_parse(response=response)
                    values = [
                                {
                                    "url": obj.url,
                                    "status": obj.status,
                                }
                                for obj in url_queue_list
                            ]
                    
                    if values:
                        stmt = insert(UrlQueue).values(values).on_conflict_do_nothing(index_elements=["url"])
                        session.execute(stmt)
                                
                    currentPage += 1
                    time.sleep(2)
                        
                except Exception as exc:
                    completed = False
                    session.rollback()
                    crawler_logger.error(f"Crawling failed: {str(exc)}")
                    break
            
            if completed:
                param.last_used = datetime.now()
                session.commit()
                
    except Exception as exc:
        session.rollback()
        crawler_logger.error(f"Error: {str(exc)}")

if __name__ == '__main__':
    main()
            


#TODO:
# - Check, ob alle properties überhaupt existieren, wenn nicht -> Log schreiben
