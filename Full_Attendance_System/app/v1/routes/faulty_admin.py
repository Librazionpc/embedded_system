from fastapi import APIRouter, Depends
from app.v1.schemas.faulty_admin import FacultyAdminCreate, FacultyAdminOut, FaultyAdminLogin, FacultyResetPassword, FaultyGetOTP
from app.v1.services.auth_services.faulty_admin_auth_service import FaultyAdminAuthService
from sqlalchemy.ext.asyncio import AsyncSession
from app.v1.db.db_conn import get_db

router = APIRouter()

@router.post("/create", response_model=FacultyAdminOut)
async def create_faculty_admin(data: FacultyAdminCreate, session: AsyncSession = Depends(get_db)):
    # Pass the data as a dictionary to the service
    new_admin = await FaultyAdminAuthService.register_admin(data.dict(), session)
    return new_admin

@router.post("/login", response_model=FacultyAdminOut)
async def login_faculty_admin(data: FaultyAdminLogin, session: AsyncSession = Depends(get_db)):
    admin = await FaultyAdminAuthService.authenticate_admin(data.dict(), session)
    return admin

@router.post("/validate_email", response_model=FacultyAdminOut)
async def login_faculty_admin(data: FaultyGetOTP, session: AsyncSession = Depends(get_db)):
    await FaultyAdminAuthService.validate_email(data.dict(), session)

@router.post("/reset_password", response_model=FacultyAdminOut)
async def reset_password(data:FacultyResetPassword, session: AsyncSession = Depends(get_db)):
    admin = await FaultyAdminAuthService.reset_password(data.dict(), session)
    return admin