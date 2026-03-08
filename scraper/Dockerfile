FROM python:3.14-slim-bookworm

WORKDIR /app
COPY scraper/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY scraper/ scraper/
COPY database/ database/
COPY core/ core/

CMD ["python", "-m", "scraper.base"]
