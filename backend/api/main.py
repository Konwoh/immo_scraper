from fastapi import FastAPI, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from backend.database.models import Job, Status, get_db
from sqlalchemy.orm import Session
from backend.api.routers import users, houses, apartments, search_params, jobs, url_queue, auth, job_schedule
import os
from dotenv import load_dotenv
load_dotenv()

BASE_URL = os.getenv("BASE_URL")
app = FastAPI()

app.include_router(users.router)
app.include_router(houses.router)
app.include_router(apartments.router)
app.include_router(search_params.router)
app.include_router(jobs.router)
app.include_router(url_queue.router)
app.include_router(auth.router)
app.include_router(job_schedule.router)

origins = [
    "http://localhost:5173",
    f"http://{BASE_URL}:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"])