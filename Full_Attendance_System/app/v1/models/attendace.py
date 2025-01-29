from sqlalchemy import Column, Integer, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship
from app.v1.models.basemodel import BaseModel
from datetime import datetime
from app.v1.db.db_conn import Base

class Attendance(BaseModel, Base):
    __tablename__ = 'attendances'
    
    ispresent = Column(Boolean, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    student_id = Column(Integer, ForeignKey('students.id'), nullable=False)
    course_id = Column(Integer, ForeignKey('courses.id'), nullable=False)
    department_id = Column(Integer, ForeignKey('departments.id'), nullable=False)
    

    student = relationship("Student", back_populates="attendances")
    course = relationship("Course", back_populates="attendances")
    department = relationship("Department", back_populates="attendances")
