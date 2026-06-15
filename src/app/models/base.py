"""Base model class for all database models."""

from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.ext.declarative import declarative_base

# Create SQLAlchemy instance
db = SQLAlchemy()

# Create base class for all models
BaseModel = declarative_base()

def time_now():
    """Return the current UTC time."""
    return datetime.now(timezone.utc)


class Base(BaseModel):
    """Abstract base model with common fields for all models."""
    
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, default=time_now, nullable=False)
    updated_at = Column(DateTime, default=time_now, onupdate=time_now, nullable=False)

    def to_dict(self):
        """Convert model instance to dictionary."""
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }

    def from_dict(self, data):
        """Update model instance from dictionary."""
        for key, value in data.items():
            setattr(self, key, value)

    def __repr__(self):
        """Return string representation of the model."""
        return f"<{self.__class__.__name__}(id={self.id})>"