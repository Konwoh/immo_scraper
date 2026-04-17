FROM python:3.14-slim-bookworm

WORKDIR /app
COPY core/worker/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY core/ core/
COPY crawler/ crawler/
COPY scraper/ scraper/
COPY database/ database/

CMD ["python", "-m", "core.worker.main"]