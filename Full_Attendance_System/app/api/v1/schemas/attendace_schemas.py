from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class AttendanceBase(BaseModel):
    student_id: int
    course_id: int
    department_id: int
    ispresent: bool

class AttendanceCreate(AttendanceBase):
    pass
class AttendanceUpdate(BaseModel):
    student_id: Optional[int]
    course_id: Optional[int]
    department_id: Optional[int]
    ispresent: Optional[bool]

    class Config:
        orm_mode = True  # Ensure compatibility with ORM models
class AddStudent:
    coursecode: str
    studentemail: EmailStr
    
class DelStudent:
    coursecode: str
    studentemail: EmailStr
class StartAttendance:
    coursecode : str
    lectureremail: str
    
class AttendanceDelete:
    attendance_id = str

class AttendanceOut(AttendanceBase):
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True
