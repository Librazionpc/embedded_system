from sqlalchemy import Column, DateTime, Boolean, UUID, Integer, Table, ForeignKey, String
from uuid import uuid4
from datetime import datetime, timedelta
from app.api.v1.db import db  # Assuming db is your DB utility module
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import class_mapper
from datetime import date
from app.api.v1.db.db_conn import Base

lecturer_course_association = Table(
    'lecturer_course_association',
    Base.metadata,
    Column('lecturer_id', Integer, ForeignKey('lecturers.id')),
    Column('course_id', Integer, ForeignKey('courses.id'))
)
student_course_association = Table(
    "student_course",
    Base.metadata,
    Column("student_id", Integer, ForeignKey("students.id")),
    Column("course_id", Integer, ForeignKey("courses.id"))
)
class BaseModel:
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime, default=None)
    is_deleted = Column(Boolean, default=False)

    @classmethod
    async def new(cls, session: AsyncSession, model) -> object:
        """Add a new record to the database."""
        return await db.new(session, model)

    @classmethod
    async def add_all(cls, session: AsyncSession, models: list) -> list:
        """Add multiple records to the database."""
        return await db.add_all(session, models)

    @classmethod
    async def filter_by(cls, session: AsyncSession, **filters) -> object:
        """Retrieve records using filters."""
        return await db.filter_by(session, cls, **filters)

    @classmethod
    async def update(cls, session: AsyncSession, model, **kwargs) -> object:
        """Update a record with new data."""
        return await db.update(session, model, **kwargs)

    @classmethod
    async def delete(cls, session: AsyncSession, model) -> object:
        """Mark a record as deleted (soft delete)."""
        return await db.delete(session, model)

    @classmethod
    async def set_otp(cls, session: AsyncSession, email: str, otp_code: str, fingerprint: str, expiry_minutes: int = 5) -> object:
        """Set the OTP and its expiration time asynchronously."""
        user = await cls.filter_by(session, email=email)
        if not user:
            return False
        if user:
            user.otp = otp_code
            user.otp_expiry = datetime.utcnow() + timedelta(minutes=expiry_minutes)
            user.fingerprint = fingerprint
            await cls.update(session, user)
            return user

    @classmethod
    async def validate_otp(cls, session: AsyncSession, email: str, otp_code: str) -> bool:
        """Check if OTP is valid asynchronously."""
        user = await cls.filter_by(session, email=email)

        if user and user.otp and user.otp_expiry and datetime.utcnow() < user.otp_expiry:
            return user.otp == otp_code

        return False

    def to_dict(self, seen=None) -> dict:
        """
        Convert the model instance to a dictionary, including relationships,
        while avoiding infinite recursion caused by circular relationships.
        """
        if seen is None:
            seen = set()
        if id(self) in seen:
            return None  # Prevent recursion
        seen.add(id(self))

        result = {}

        # Handle regular fields (columns)
        for key in class_mapper(self.__class__).columns.keys():
            value = getattr(self, key)
            if isinstance(value, (datetime, date)):
                value = value.isoformat()  # Convert datetime or date to ISO format
            result[key] = value

        # Handle relationships
        for key, relationship in class_mapper(self.__class__).relationships.items():
            related_obj = getattr(self, key)
            if related_obj is not None:
                if relationship.uselist:  # List of related objects
                    result[key] = [item.to_dict(seen=seen) for item in related_obj]
                else:  # Single related object
                    result[key] = related_obj.to_dict(seen=seen)

        return result
