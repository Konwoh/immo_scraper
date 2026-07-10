FROM python:3.14-slim-bookworm

WORKDIR /app

COPY backend/ml/requirements.txt requirements.txt

RUN apt-get update \
    && apt-get install -y --no-install-recommends libgomp1 \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir -r requirements.txt

COPY backend /app/backend

CMD ["python", "-m", "backend.ml.pipeline_zenml"]
