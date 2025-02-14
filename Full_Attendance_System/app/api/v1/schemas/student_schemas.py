from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

# Base Schema for Student (excluding fingerprint)
class StudentBase(BaseModel):
    studentname: str
    studentemail: EmailStr
    studentphone: str
    department_id: int

# Schema for creating a new Student
class StudentCreate(StudentBase):
    password: str
    fingerprint: str

# Schema for updating a Student password
class StudentResetPassword(BaseModel):
    studentemail: EmailStr
    password: str
    newPassword: str
    fingerprint: str

# Schema for OTP request
class StudentGetOTP(BaseModel):
    studentemail: EmailStr
    fingerprint: str

# Schema for Student login
class StudentLogin(BaseModel):
    studentemail: EmailStr
    password: str
    fingerprint: str

class StudentUpdate(StudentBase):
    pass

class StudentDelete:
    studentemail: EmailStr

# Schema for returning Student data
class StudentOut(StudentBase):
    id: int
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True
