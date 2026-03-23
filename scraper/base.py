from core.parser import EstateParserCreator
from database.models import create_engine, UrlQueue
from core.helper import Headers, retry
import os
from scraper.worker import Worker

def main():
    engine = create_engine(os.environ["DB_CONNECTION_STRING"], echo=False)
    headers = Headers('application/json', 'ImmoScout_27.14.1_26.3_._', 'de-de')
    estate_parser = EstateParserCreator()
    parser = estate_parser.create_parser()
    worker_1 = Worker(engine, UrlQueue, headers, parser)
    worker_1.process(amount_rows=100)

if __name__ == '__main__':
    retry(main)