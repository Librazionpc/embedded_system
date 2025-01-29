from pydantic import BaseModel
from typing import Optional


# Schema for creating a new FacultyAdmin
class FacultyAdminCreate(BaseModel):
    faultyname: str
    faultyemail: str
    faultyphone: str
    faultyaddress: str
    department_id: int
    password: str
    fingerprint: str

# Schema for updating a FacultyAdmin
class FacultyAdminUpdate(BaseModel):
    pass

class FaultyAdminLogin(BaseModel):
    faultyemail: str
    password: str
    fingerprint: str
    

class FacultyAdminOut(BaseModel):
    id: str
    created_at: Optional[str]
    updated_at: Optional[str]

    class Config:
        orm_mode = True
