FROM python:3.14-slim-bookworm

WORKDIR /app
COPY backend/worker/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ backend/
COPY crawler/ crawler/

CMD ["python", "-m", "backend.worker.job_loop"]