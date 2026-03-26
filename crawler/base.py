from sqlalchemy.orm import Session
from sqlalchemy import select
from core.parser import EstateParserCreator
from core.helper import Headers, retry
from database.models import engine, UrlQueue, SearchParams
from sqlalchemy.dialects.postgresql import insert
from .crawler import create_factory
from .crawler import crawler_logger
from datetime import datetime
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


def main():
    session = None
    try:
        currentPage = 1

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
            
            continue_flag = True
            while continue_flag:
                result = retry(lambda: process(param, currentPage))
                if result is None:
                    raise RuntimeError(f"process() returned None on page {currentPage}")
                elif result == []:
                    break
                
                values, continue_flag = result
                
                if values:
                    stmt = insert(UrlQueue).values(values).on_conflict_do_nothing(index_elements=["url"])
                    session.execute(stmt)

                currentPage += 1
                time.sleep(2)
                        
            param.last_used = datetime.now()
            session.commit()
                
    except Exception as exc:
        if session is not None:
            session.rollback()
        crawler_logger.error(f"Error: {str(exc)}")

if __name__ == '__main__':
    main()
            


#TODO:
# - Check, ob alle properties überhaupt existieren, wenn nicht -> Log schreiben
