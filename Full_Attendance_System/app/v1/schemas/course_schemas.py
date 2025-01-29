from pydantic import BaseModel
from typing import Optional
import uuid


# Schema for creating a new Course
class CourseCreate(BaseModel):
    coursename: str
    cousrecode: str
    departmentid: uuid.UUID


# Schema for updating a Course
class CourseUpdate(BaseModel):
    new_name: Optional[str]  # Correct syntax for Optional[str]
    new_course_code: Optional[str]
    new_dept_id: Optional[str]

class CourseDelete:
    coursecode: str

# Schema for returning a Course's data
class CourseOut(BaseModel):
    id: str
    oursename: str
    created_at: Optional[str]
    updated_at: Optional[str]

    class Config:
        orm_mode = True  # Ensure compatibility with ORM models
