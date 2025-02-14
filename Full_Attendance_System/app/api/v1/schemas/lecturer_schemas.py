from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

# Base Schema for Lecturer
class LecturerBase(BaseModel):
    lecturername: str
    lectureremail: EmailStr
    lecturerphone: str
    department_id: int

# Schema for creating a new Lecturer
class LecturerCreate(LecturerBase):
    fingerprint: str
    password: str

# Schema for updating Lecturer information
class LecturerUpdate(BaseModel):
    lecturername: Optional[str]
    lectureremail: Optional[EmailStr]
    lecturerphone: Optional[str]
    department_id: Optional[int]

# Schema for updating a Lecturer password
class LecturerResetPassword(BaseModel):
    lectureremail: EmailStr
    password: str
    newPassword: str
    fingerprint: str

# Schema for OTP request
class LecturerGetOTP(BaseModel):
    lectureremail: EmailStr
    fingerprint: str

# Schema for Lecturer login
class LecturerLogin(BaseModel):
    lectureremail: EmailStr
    password: str
    fingerprint: str

class LecturerDelete(BaseModel):
    lectureremail: EmailStr

class LecturerAddStudent:
    coursecode: str
    studentemail: EmailStr
    
class LecturerDelStudent:
    coursecode: str
    studentemail: EmailStr

# Schema for returning Lecturer data
class LecturerOut(LecturerBase):
    id: int
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True
