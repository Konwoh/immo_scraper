from sqlalchemy.orm import Session
from parser import EstateParserCreator
from database import engine
from sqlalchemy.dialects.postgresql import insert
import crawler
from database import UrlQueue
import json
import time

cookies = {
    'IS24VisitId': 'vid217f62bd-6a5b-4ca6-8a1b-bd4bf93c9251',
}

#headers = {
#    'accept': 'application/json',
#    'x-is24-feature': 'adKeysAndStringValues,virtualTour,referencePriceV3,verificationArray,unpublished,listFirstListing,xxlListingType,immersiveSearch,modernizationCalculator,presale',
#    'x-is24-device': 'iphone',
#    'priority': 'u=3',
#    'x-emb-st': '1769259013083',
#    'accept-language': 'de-de',
#    'user-agent': 'ImmoScout_27.11_26.2_._',
#    'x-emb-id': '0526B033-7C95-4CB9-B788-94E898CFEDF1',
#    # 'cookie': 'IS24VisitId=vid217f62bd-6a5b-4ca6-8a1b-bd4bf93c9251',
#}
#
#params = {
#    'searchId': '7a29154a-9d4b-4719-8fa4-4e649eff4947',
#    'referrer': 'resultlist',
#}


if __name__ == '__main__':
    currentPage = 1
    numberOfPages = 10
    while currentPage <= numberOfPages:
        params = crawler.SearchParams("de", "sachsen", "leipzig", "apartment", "buy", 50, currentPage)
        headers = crawler.Headers('application/json', 'ImmoScout_27.11_26.2_._', 'de-de')

        immo_scout_factory = crawler.create_factory("Immoscout")
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

            stmt = insert(UrlQueue).values(values)

            stmt = stmt.on_conflict_do_nothing(
                index_elements=["url"]
            )

            result = session.execute(stmt)
            session.commit()
            
            print(f"Seite {currentPage}: {result.rowcount} von {params.listing_count} Rows wurden in die DB inserted")
            currentPage += 1
            time.sleep(1)


#TODO:
# - besseres Error Handling und Log von Fehlern
# - Check, ob alle properties überhaupt existieren, wenn nicht -> Log schreiben
# - neue Datei -> scraper.py mit Worker Class, die einzelne URLs aus DB-Tabelle rausholt