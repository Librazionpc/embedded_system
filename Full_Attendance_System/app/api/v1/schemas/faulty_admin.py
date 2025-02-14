from pydantic import BaseModel, EmailStr
from typing import Optional


# Schema for creating a new FacultyAdmin
class FacultyAdminBase(BaseModel):
    facultyname: str
    facultyemail: EmailStr
    facultyphone: str
    facultyaddress: str

    class Config:
        orm_mode = True

class FacultyAdminCreate(FacultyAdminBase):

    password: str
    fingerprint: str

# Schema for updating a FacultyAdmin
class FacultyResetPassword(BaseModel):
    facultyemail: EmailStr
    password: str
    newPassword: str
    fingerprint: str

class FacultyGetOTP(BaseModel):
    facultyemail : EmailStr
    fingerprint: str
class FacultyAdminLogin(BaseModel):
    facultyemail: EmailStr
    password: str
    fingerprint: str
    
class FacultyAdminOut(FacultyAdminBase):
    id: str
    created_at: Optional[str]
    updated_at: Optional[str]

    class Config:
        orm_mode = True
