# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

`immo_scraper` collects German real-estate listings (ImmoScout24 and Kleinanzeigen),
stores them in Postgres, serves them through a FastAPI backend + React frontend, and
trains ML price-prediction models via a ZenML pipeline tracked in MLflow.

## Repo layout

- `backend/api/` – FastAPI app (`backend.api.main:app`), one router per resource, cookie-based JWT auth.
- `backend/worker/` – two long-running polling loops (`job_loop.py`, `schedule_loop.py`) plus `scraper_worker.py`.
- `backend/services/` – `JobService`, `CrawlerService`, `ScraperService`, `ScheduleService` (the orchestration layer between the loops and the integrations).
- `backend/integration/<site>/` – per-site `crawler.py` (build search URLs, fetch result pages) and `parser.py` (turn responses into rows/ORM objects).
- `crawler/` – abstract `BaseCrawler` + `crawler/factory.py`.
- `backend/parser/` – abstract `Parser`, `EstateParserCreator` factory, and `read_estate_creator` (maps scraped type strings → House/Apartment/Property).
- `backend/database/` – SQLAlchemy 2.0 models (`models.py`) and the estate/agency factories (`factory.py`).
- `backend/ml/` – ZenML pipeline (`pipeline_zenml.py`), training (`training/train.py`), preprocessing (`preprocessing/`), MLflow helpers (`utils.py`).
- `alembic/` – migrations; `env.py` pulls `Base` from `backend.database.models`.
- `frontend/` – React 19 + Vite + react-router SPA.
- Each backend service has its own `requirements.txt`; there is no root requirements file.

## Commands

Run all Python commands **from the repo root** (imports are absolute `backend.*` / `crawler.*`).
A git-ignored `.env` at the repo root is required (`DB_CONNECTION_STRING`, `SECRET_KEY`,
`ALGORITHM`, `REFRESH_SECRET_KEY`, and for ML: `MLFLOW_TRACKING_URI`,
`MLFLOW_S3_ENDPOINT_URL`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`).

```bash
# Backend API (dev)
pip install -r backend/api/requirements.txt
uvicorn backend.api.main:app --reload --host 0.0.0.0 --port 8000

# Workers (each is a separate process; needs backend/worker/requirements.txt)
python -m backend.worker.job_loop        # claims + runs crawler/scraper jobs
python -m backend.worker.schedule_loop   # materialises due JobSchedule rows into jobs

# Database
alembic upgrade head
alembic revision --autogenerate -m "message"
python -m backend.database.models        # create_all + seed sample SearchParams (dev bootstrap)

# ML pipeline (needs backend/ml/requirements.txt + a running ZenML server & MLflow)
zenml login <zenml-server-url> && zenml stack set immo_mlflow_stack
python -m backend.ml.pipeline_zenml

# Frontend
cd frontend
npm install
npm run dev        # Vite dev server on :5173
npm run build      # tsc -b && vite build
npm run lint       # eslint .

# Full stack
docker compose up                 # api, workers, frontend, loki, grafana, mlflow, minio, zenml, mysql
docker compose --profile ml up ml_pipeline
```

There is **no backend test suite** and no backend linter/type-checker configured.

## Architecture

### Two-phase scraping pipeline

A `search_params` row (site + location + estate_type + rent/buy) is the unit of work.
Jobs reference a `search_params_id` and a `job_type`:

1. **crawler job** → `CrawlerService.start_crawler` walks result pages via the site
   crawler, the site parser turns each page into detail-page URLs, and those are
   inserted into `url_queue` (status `open`).
2. **scraper job** → `ScraperService.start_scraper` runs `worker.scraper_worker.Worker`,
   which claims `url_queue` rows (`FOR UPDATE SKIP LOCKED`), fetches each detail page,
   builds a `House` / `Apartment` / `Property` ORM object via the site parser +
   `read_estate_creator`, persists it, and records a row in `search_results` linking
   the estate to the `search_params`. After the run it flips `is_online = False` on
   estates for that search that were not seen this time.

Estates are deduplicated across searches by a natural-key `UniqueConstraint`
(`title, price, city, living_space` for houses/apartments; `title, price, city, space`
for properties). `search_results` is the many-to-many link and has a check constraint
enforcing exactly one of `house_id` / `apartment_id` / `property_id`.

### Worker loops

Both loops in `backend/worker/` are `while True` + `time.sleep` pollers (no broker).
`job_loop` claims the oldest `open` job (`Job.status`), calls
`JobService.process_job` (dispatches to crawler or scraper service), then marks it
`done`/`failed`. `schedule_loop` scans `job_schedule` every 60s and inserts a new
`Job` for each schedule whose `next_run` has passed, advancing `next_run` by the
schedule's `interval` (`INTERVAL_DELTAS`).

### Factories (how a site/type is resolved)

- `crawler/factory.py::create_factory("Immoscout"|"Kleinanzeigen"|"Immowelt")` → crawler.
- `backend/parser/factory.py::EstateParserCreator` keyed by `"immoScout"|"kleinanzeigen"`.
- `backend/parser/base_parser.py::read_estate_creator` maps a scraped `estate_type`
  (and sometimes `listing_type`) string to `HouseEstateFactory` /
  `ApartmentEstateFactory` / `PropertyEstateFactory` in `backend/database/factory.py`.
- At scrape time the parser is chosen by URL substring (`immobilienscout24` /
  `kleinanzeigen`), not by the stored site value.

### ML flow

`pipeline_zenml.py` steps: load houses+apartments from DB → `DataCleaner` (separate
buy/rent cleaners with explicit column lists) → `DataTraining.train` runs
`RandomizedSearchCV` over a **randomly chosen** model per run (`get_random_model`:
LinearRegression / RandomForest / AdaBoost / XGB) → log + register to the MLflow
model registry under the model-type name → promote to alias `@champion` only if test
R² beats the current champion. `backend/api/routers/predict.py` loads
`models:/RandomForest@champion`, `models:/AdaBoost@champion`, `models:/XGB@champion`
and returns each prediction plus their mean.

### Auth

Cookie-based JWT (`backend/api/auth/oauth2.py`). `/login` sets httponly
`access_token` (15 min) + `refresh_token` (7 days) cookies; refresh tokens are also
stored in the `refresh_tokens` table and rotated on `/token/refresh`. Protected
routes depend on `get_current_user`. Frontend never sees the tokens; `apiFetch`
in `frontend/src/api/client.ts` retries once via `/token/refresh` on a 401.

### Frontend

Generic CRUD engine in `frontend/src/components/crud/` (`CrudPage`/`CrudTable`/`CrudForm`)
driven by per-entity config + API modules in `frontend/src/entities/<name>/`. Routing
in `src/App.tsx` (tables vs. tiles views, plus `/predict`). `@` path alias → `src/`.
UI text and many code comments/log messages are in German.

### Observability

`backend/shared/loki_handler.py` ships JSON logs to Loki (`LOKI_URL`, default
`http://localhost:3100`) on a background thread; view in Grafana. Loggers are
configured at `ERROR` level.

## Gotchas

- DB must be **Postgres** (uses `SKIP LOCKED` and `ON CONFLICT`).
- Site name casing differs by layer: crawler factory uses `"Immoscout"` /
  `"Kleinanzeigen"`; parser factory and `search_params.site` use `"immoScout"` /
  `"kleinanzeigen"`.
- ImmoWelt has a crawler class but no parser and is not dispatched by
  `CrawlerService` — treat it as unfinished.
- `retry()` / availability code and the ORM natural keys assume listing fields are
  stored as **strings** (`Mapped[str]`); numeric parsing happens later in the ML
  cleaners and the predict route. **Exceptions:** `price`, `living_space`,
  `rent_extra_costs` (houses/apartments) and `price`, `space` (property) are
  `double precision` (`Mapped[float | None]`) — the site parsers cast them to
  `float` inline, and migration `f3a1c9d24b7e` converted the existing text data.
