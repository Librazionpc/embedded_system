from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from app.v1.models.basemodel import BaseModel
from app.v1.models.attendace import Attendance
from app.v1.models.course import Course
class Student(BaseModel):
    
    student_name = Column(String(50), nullable=False)
    student_email = Column(String(50), nullable=False)
    student_phone = Column(String(50), nullable=False)
    course_id = Column(Integer, ForeignKey('courses.id'), nullable=False)
    department_id = Column(Integer, ForeignKey('departments.id'), nullable=False)
    attendances = relationship(Attendance, back_populates="students")
    courses = relationship(Course, back_populates="students")