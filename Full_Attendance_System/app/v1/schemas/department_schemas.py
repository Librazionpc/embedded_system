from pydantic import BaseModel
from typing import Optional
import uuid


# Schema for creating a new Department
class DepartmentCreate(BaseModel):
    departmentname: str
    faultyid: uuid.UUID


# Schema for updating a Department
class DepartmentUpdate(BaseModel):
    departmentname: str
    new_name: Optional[str]  # Correct syntax for Optional[str]
    faultyid: Optional[uuid.UUID]  # Correct type for Optional[uuid.UUID]


# Schema for returning a Department's data
class DepartmentOut(BaseModel):
    id: str
    created_at: Optional[str]
    updated_at: Optional[str]

    class Config:
        orm_mode = True  # Ensure compatibility with ORM models
