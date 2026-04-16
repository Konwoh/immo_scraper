from fastapi import FastAPI
from scraper.base import start_scraper
from crawler.base import start_crawler
from sqlalchemy.dialects.postgresql import insert
from database.models import engine, Jobs, Status
from sqlalchemy.orm import Session

app = FastAPI()

@app.get("/start_scraper")
def start_scraper_endpoint():
    with Session(engine) as session:
        stmt = insert(Jobs).values(job_type="scraper", status=Status.open)
        session.execute(stmt)
        session.commit()
        
        
@app.get("/start_crawler")
def start_crawler_endpoint():
    with Session(engine) as session:
        stmt = insert(Jobs).values(job_type="crawler", status=Status.open)
        session.execute(stmt)
        session.commit()