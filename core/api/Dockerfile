FROM python:3.14-slim-bookworm

WORKDIR /app
COPY core/api/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY core/ core/
COPY database/ database/

CMD ["uvicorn", "core.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
