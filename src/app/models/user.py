"""User model for authentication and user management."""

from datetime import datetime, timezone
from sqlalchemy import Column, String, Boolean, DateTime, Text
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash

from .base import Base, db


class User(Base):
    """User model for authentication and session management."""
    
    __tablename__ = 'users'
    
    # User identification
    username = Column(String(80), unique=True, nullable=False, index=True)
    email = Column(String(120), unique=True, nullable=True, index=True)
    
    # Password management
    password_hash = Column(String(255), nullable=False)
    
    # User status
    is_active = Column(Boolean, default=True, nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)
    
    # Profile information
    first_name = Column(String(50), nullable=True)
    last_name = Column(String(50), nullable=True)
    organization = Column(String(100), nullable=True)
    bio = Column(Text, nullable=True)
    
    # Session management
    last_login = Column(DateTime, nullable=True)
    last_activity = Column(DateTime, nullable=True)
    
    # Relationships
    analyses = relationship("TTestAnalysis", back_populates="user", lazy="dynamic")
    datasets = relationship("DataSet", back_populates="user", lazy="dynamic")
    
    def __init__(self, username, password, email=None, **kwargs):
        """Initialize user with hashed password."""
        self.username = username
        self.set_password(password)
        self.email = email
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def set_password(self, password):
        """Hash and set the user's password."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if provided password matches the stored hash."""
        return check_password_hash(self.password_hash, password)
    
    def update_last_activity(self):
        """Update the user's last activity timestamp."""
        self.last_activity = datetime.now(timezone.utc)
        db.session.commit()
    
    def update_last_login(self):
        """Update the user's last login timestamp."""
        self.last_login = datetime.now(timezone.utc)
        db.session.commit()
    
    @property
    def full_name(self):
        """Return the user's full name."""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        elif self.last_name:
            return self.last_name
        else:
            return self.username
    
    def to_dict(self, include_sensitive=False):
        """Convert user to dictionary, optionally including sensitive data."""
        user_dict = {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': self.full_name,
            'organization': self.organization,
            'bio': self.bio,
            'is_active': self.is_active,
            'is_admin': self.is_admin,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'last_activity': self.last_activity.isoformat() if self.last_activity else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
        }
        
        if include_sensitive:
            user_dict['password_hash'] = self.password_hash
        
        return user_dict
    
    def __repr__(self):
        """Return string representation of the user."""
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"