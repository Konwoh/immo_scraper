from fastapi import FastAPI, HTTPException, Request
from fastapi.exception_handlers import http_exception_handler
from fastapi.middleware.cors import CORSMiddleware
from backend.api.routers import users, houses, apartments, search_params, jobs, url_queue, auth, job_schedule, property, predict
from backend.shared.loki_handler import get_loki_logger
import os
from dotenv import load_dotenv
load_dotenv()

BASE_URL = os.getenv("BASE_URL")
api_logger = get_loki_logger("api_logger", {"app": "api", "env": os.getenv("ENV", "dev")})
app = FastAPI()


@app.exception_handler(HTTPException)
async def log_http_exception(request: Request, exc: HTTPException):
    api_logger.error(
        "HTTPException method=%s path=%s status_code=%s detail=%s",
        request.method,
        request.url.path,
        exc.status_code,
        exc.detail,
    )
    return await http_exception_handler(request, exc)

app.include_router(users.router)
app.include_router(houses.router)
app.include_router(apartments.router)
app.include_router(search_params.router)
app.include_router(jobs.router)
app.include_router(url_queue.router)
app.include_router(auth.router)
app.include_router(job_schedule.router)
app.include_router(property.router)
app.include_router(predict.router)


origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    f"http://{BASE_URL}:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["*"])
