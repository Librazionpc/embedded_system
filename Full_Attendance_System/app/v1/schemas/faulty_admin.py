from pydantic import BaseModel
from typing import Optional


# Schema for creating a new FacultyAdmin
class FacultyAdminBase(BaseModel):
    faultyname: str
    faultyemail: str
    faultyphone: str
    faultyaddress: str

    class Config:
        orm_mode = True

class FacultyAdminCreate(FacultyAdminBase):

    department_id: int
    password: str
    fingerprint: str

# Schema for updating a FacultyAdmin
class FacultyResetPassword(BaseModel):
    faultyemail: str
    password: str
    newPassword: str
    fingerprint: str

class FaultyGetOTP(BaseModel):
    faultyemail : str
    fingerprint: str
class FaultyAdminLogin(BaseModel):
    faultyemail: str
    password: str
    fingerprint: str
    
class FacultyAdminOut(FacultyAdminBase):
    id: str
    created_at: Optional[str]
    updated_at: Optional[str]

    class Config:
        orm_mode = True
