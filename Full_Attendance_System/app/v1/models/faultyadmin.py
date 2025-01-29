from sqlalchemy import Column, String, Boolean, DateTime, Integer, ForeignKey
from app.v1.models.basemodel import BaseModel
from sqlalchemy.orm import relationship
from app.v1.models.department import Department
from app.v1.db.db_conn import Base

class FaultyAdmin(BaseModel, Base):
    __tablename__ = 'FaultyAdmin'
    
    faultyname = Column(String(50), nullable=False)
    faultyemail = Column(String(50), nullable=False)
    password = Column(String(255), nullable=False)
    otp = Column(Integer, nullable=True)
    otp_expiry = Column(DateTime, nullable=True)
    fingerprint = Column(String, nullable=False)
    faultyphone = Column(String(50), nullable=False)
    faultyaddress = Column(String(50), nullable=False)
    departments = relationship(Department, back_populates='faultyadmin')
    
    
    
    