from fastapi import FastAPI
from app.api.v1.routers.faculty_admin import faculty_router

version = "v1"
app = FastAPI(title="Fingerprint Attendance System", version=version)

app.include_router(faculty_router, prefix="/faculty_admin", tags=["Faculty Admin"])