from sqlalchemy import Column, DateTime, Boolean, UUID, Integer, Table, ForeignKey
from uuid import uuid4
from datetime import datetime
from app.v1.db import db  # Assuming db is your DB utility module
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import class_mapper
from datetime import date
from app.v1.db.db_conn import Base

lecture_course_association = Table('lecturer_course_association', Base.metadata,
    Column('lecturer_id', Integer, ForeignKey('lecturers.id')),
    Column('course_id', Integer, ForeignKey('courses.id'))
)
class BaseModel:
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime, default=None)
    is_deleted = Column(Boolean, default=False)

    @classmethod
    async def new(cls, session: AsyncSession, model):
        """
        Add a new record to the database using db.new.
        """
        return await db.new(session, model)

    @classmethod
    async def add_all(cls, session: AsyncSession, models):
        """
        Add multiple records to the database using db.add_all.
        """
        return await db.add_all(session, models)

    @classmethod
    async def filter_by(cls, session: AsyncSession, **filters):
        """
        Retrieve records using filters using db.filter_by.
        """
        return await db.filter_by(session, cls, **filters)

    @classmethod
    async def update(cls, session: AsyncSession, model, **kwargs):
        """
        Update a record with new data using db.update.
        """
        return await db.update(session, model, **kwargs)

    @classmethod
    async def delete(cls, session: AsyncSession, model):
        """
        Mark a record as deleted (soft delete) using db.delete.
        """
        return await db.delete(session, model)

    def to_dict(self, seen=None):
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
