from fastapi import APIRouter, Depends, HTTPException, status
from app.v1.schemas.course_schemas import CourseCreate, CourseUpdate, CourseOut, CourseDelete
from app.v1.services.auth_services.course_services import CourseAuthServices
from sqlalchemy.ext.asyncio import AsyncSession
from app.v1.db.db_conn import get_db
from app.v1.utils.jwt import JWTUtils  # Import updated JWTUtils

router = APIRouter()

def admin_required(user: dict = Depends(JWTUtils.get_current_user)):
    """Ensure only admins can access"""
    if user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this resource",
        )
    return user

@router.post('/create', response_model=CourseOut)
async def create_faculty_admin(
    data: CourseCreate,
    session: AsyncSession = Depends(get_db),
    user: dict = Depends(admin_required)
):
    new_dept = await CourseAuthServices.register_Course(data.dict(), session)
    return new_dept

@router.post("/update", response_model=CourseOut)
async def updateCourse(
    data: CourseUpdate,
    session: AsyncSession = Depends(get_db),
    user: dict = Depends(admin_required)
):
    dept = await CourseAuthServices.update_Course(data.dict(), session)
    return dept

@router.delete("/delete")
async def deleteCourse(
    data: CourseDelete, 
    session: AsyncSession = Depends(get_db),
    user: dict = Depends(admin_required)
):
    return await CourseAuthServices.delete(data.dict(), session)