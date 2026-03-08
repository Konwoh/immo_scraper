from sqlalchemy.orm import Session
from core.parser import EstateParserCreator
from core.helper import Headers
from database.models import engine, UrlQueue
from sqlalchemy.dialects.postgresql import insert
from .crawler import SearchParams, create_factory
import json
import time
import logging

cookies = {
    'IS24VisitId': 'vid217f62bd-6a5b-4ca6-8a1b-bd4bf93c9251',
}


if __name__ == '__main__':
    currentPage = 1
    numberOfPages = 10
    while currentPage <= numberOfPages:
        try:
            params = SearchParams("de", "sachsen", "leipzig", "apartment", "buy", 50, currentPage)
            headers = Headers('application/json', 'ImmoScout_27.11_26.2_._', 'de-de')

            immo_scout_factory = create_factory("Immoscout")
            immo_scout_crawler = immo_scout_factory.create_crawler(params, headers)
            response = immo_scout_crawler.crawl()
            response_json = json.loads(response.text)
            numberOfPages = response_json["numberOfPages"]


            estate_parser = EstateParserCreator()
            parser = estate_parser.create_parser()
            url_queue_list = parser.url_parse(response=response)
            with Session(engine) as session:
                values = [
                            {
                                "url": obj.url,
                                "status": obj.status,
                            }
                            for obj in url_queue_list
                        ]

                stmt = insert(UrlQueue).values(values).on_conflict_do_nothing(index_elements=["url"])

                result = session.execute(stmt)
                session.commit()
                
                print(f"Seite {currentPage}: {result.rowcount} von {params.listing_count} Rows wurden in die DB inserted")
                currentPage += 1
                time.sleep(1)
        except Exception as exc:
            logging.error(f"Crawling failed: {str(exc)}")
            


#TODO:
# - besseres Error Handling und Log von Fehlern
# - Check, ob alle properties überhaupt existieren, wenn nicht -> Log schreiben