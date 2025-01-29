from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.v1.models.basemodel import BaseModel
from app.v1.models.faultyadmin import FaultyAdmin
from app.v1.models.lecturer import Lecturer
from app.v1.models.course import Course
from app.v1.db.db_conn import Base
class Department(BaseModel, Base):
    __tablename__ = 'departments'
    
    departmentname = Column(String(50), nullable=False)
    faultyadmin_id = Column(Integer, ForeignKey('faultyadmins.id'), nullable=False)
    lecturers = relationship(Lecturer, back_populates="department")
    courses = relationship(Course, back_populates="department")
    students = relationship("Student", back_populates="department")
    attendances = relationship("Attendance", back_populates="department")