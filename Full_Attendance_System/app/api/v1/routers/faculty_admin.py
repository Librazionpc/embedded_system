from fastapi import APIRouter, Depends, HTTPException
from app.api.v1.schemas.faulty_admin import (
    FacultyAdminCreate, FacultyAdminOut, 
    FacultyAdminLogin, FacultyResetPassword, 
    FacultyGetOTP
)
from app.api.v1.services.auth_services.faculty_admin_auth_service import FacultyAdminAuthService
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.v1.db.db_conn import get_db

faculty_router = APIRouter()

@faculty_router.post("/create", response_model=FacultyAdminOut)
async def create_faculty_admin(data: FacultyAdminCreate, session: AsyncSession = Depends(get_db)):
    # Pass the data as a dictionary to the service
    new_admin = await FacultyAdminAuthService.register_admin(data.dict(), session)

    return {"message": "Server Returns", "data": new_admin}

@faculty_router.post("/login", response_model=FacultyAdminOut)
async def login_faculty_admin(data: FacultyAdminLogin, session: AsyncSession = Depends(get_db)):
    admin = await FacultyAdminAuthService.authenticate_admin(data.dict(), session)
   
    return {"message": "Server Returns", "data": admin}

@faculty_router.post("/validate_email", response_model=FacultyAdminOut)
async def login_faculty_admin(data: FacultyGetOTP, session: AsyncSession = Depends(get_db)):
    await FacultyAdminAuthService.validate_email(data.dict(), session)

@faculty_router.post("/reset_password", response_model=FacultyAdminOut)
async def reset_password(data:FacultyResetPassword, session: AsyncSession = Depends(get_db)):
    admin = await FacultyAdminAuthService.reset_password(data.dict(), session)
    return {"message": "Server Returns", "data": admin}