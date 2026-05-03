from sqlalchemy.orm import Session
from sqlalchemy import select, update
from core.parser import EstateParserCreator
from core.helper import Headers, retry
from database.models import engine, UrlQueue, SearchParams
from sqlalchemy.dialects.postgresql import insert
from .crawler import create_factory
from .crawler import crawler_logger
from datetime import datetime, timezone
import time


def process(param: SearchParams, currentPage: int):

    param.page = currentPage
    
    if param.site == "immoScout":
        headers = Headers('application/json', 'ImmoScout_27.11_26.2_._', 'de-de')
        crawler_factory = create_factory("Immoscout")
    elif param.site == "kleinanzeigen":
        headers = Headers('*/*', 'Kleinanzeigen/2026.12.0 (com.ebaykleinanzeigen.ebc; build:26.072.16409187; iOS 26.3.1) Alamofire/5.11.1', 'de-DE;q=1.0', 'Basic aXBob25lOmc0Wmk5cTEw')
        crawler_factory = create_factory("Kleinanzeigen")
    else:
        raise ValueError(f"Unsupported site: {param.site}")
    
    crawler = crawler_factory.create_crawler(param, headers)
    response, continue_flag = crawler.crawl()

    estate_parser = EstateParserCreator()
    parser = estate_parser.create_parser(param.site)
    if parser is not None:
        url_queue_list = parser.url_parse(response=response)
        if len(url_queue_list) > 0: 
            values = [
                        {
                            "search_params_id": param.id,
                            "url": obj.url,
                            "status": obj.status,
                        }
                        for obj in url_queue_list
                    ]
            return values, continue_flag
        else:
            return url_queue_list
    else:
        raise ValueError("Parser is None")


def start_crawler(search_params_id: int):
    session = None
    try:
        currentPage = 1

        with Session(engine) as session:
            
            param = session.execute(
                select(SearchParams)
                .filter(SearchParams.id == search_params_id)
                .order_by(SearchParams.last_used.asc().nullsfirst())
                .limit(1)
                .with_for_update(skip_locked=True)
            ).scalar_one_or_none()
             
            if param is None:
                session.rollback()
                raise RuntimeError(f"No search params available for id={search_params_id}")
            
            param_id = param.id
            
        continue_flag = True
        while continue_flag:
            result = retry(lambda: process(param, currentPage))
            if result is None:
                raise RuntimeError(f"process() returned None on page {currentPage}")
            elif result == []:
                break
            
            values, continue_flag = result
            
            if values:
                with Session(engine) as session:
                    stmt = insert(UrlQueue).values(values)
                    session.execute(stmt)
                    session.commit()
                
            currentPage += 1
            time.sleep(2)
            
        with Session(engine) as session:
            stmt = (
                update(SearchParams)
                .where(SearchParams.id == param_id)
                .values(last_used=datetime.now(timezone.utc))
            )
            session.execute(stmt)
            session.commit()
                
    except Exception:
        crawler_logger.exception("Error while processing crawler job")
        raise

if __name__ == '__main__':
    start_crawler()
