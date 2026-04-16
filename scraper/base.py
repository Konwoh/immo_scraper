from database.models import create_engine, UrlQueue
from core.helper import retry
import os
from scraper.worker import Worker

def start_scraper():
    engine = create_engine(os.environ["DB_CONNECTION_STRING"], echo=False)
    worker_1 = Worker(engine, UrlQueue)
    worker_1.process(amount_rows=100)

if __name__ == '__main__':
    retry(start_scraper)