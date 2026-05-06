FROM python:3.14-slim-bookworm

WORKDIR /app
COPY scraper/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY scraper/ scraper/
COPY backend/ backend/

CMD ["python", "-m", "scraper.base"]
