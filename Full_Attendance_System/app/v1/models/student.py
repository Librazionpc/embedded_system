from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.v1.models.basemodel import BaseModel, student_course_association
from app.v1.models.attendace import Attendance
from app.v1.models.course import Course

class Student(BaseModel):
    student_name = Column(String(50), nullable=False)
    student_email = Column(String(50), nullable=False)
    student_phone = Column(String(50), nullable=False)
    
    # Store face recognition data as a string or a file path or hash if storing the image itself is not ideal
    face_rec = Column(String(255), nullable=True)
    
    # Store fingerprint data as a string or a unique identifier/hash for the fingerprint
    fingerprint = Column(String(255), nullable=True)
    
    course_id = Column(Integer, ForeignKey('courses.id'), nullable=False)
    department_id = Column(Integer, ForeignKey('departments.id'), nullable=False)
    
    attendances = relationship(Attendance, back_populates="students")
    courses = relationship("Course", secondary=student_course_association, back_populates="students")

