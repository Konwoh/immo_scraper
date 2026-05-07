from backend.database.models import create_engine, UrlQueue
from backend.shared.helper import retry
import os
from backend.worker.scraper_worker import Worker

class ScraperService:
    def start_scraper(self, search_params_id: int):
        engine = create_engine(os.environ["DB_CONNECTION_STRING"], echo=False)
        worker_1 = Worker(engine, UrlQueue, search_params_id)
        worker_1.process(amount_rows=100)