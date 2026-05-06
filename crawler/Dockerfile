FROM python:3.14-slim-bookworm

WORKDIR /app
COPY scraper/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY crawler/ crawler/
COPY backend/ backend/

CMD ["python", "-m", "crawler.base"]