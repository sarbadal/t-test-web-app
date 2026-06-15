"""User service for handling user management and authentication."""

from typing import Optional, Dict, Any
from flask import current_app
from datetime import datetime, timezone

from ..models import User, db


class UserService:
    """Service class for managing users."""
    
    @staticmethod
    def create_user(username: str, password: str, email: str = None, **kwargs) -> User:
        """Create a new user."""
        try:
            # Check if username already exists
            if db.session.query(User).filter_by(username=username).first():
                raise ValueError(f"Username '{username}' already exists")
            
            # Check if email already exists (if provided)
            if email and db.session.query(User).filter_by(email=email).first():
                raise ValueError(f"Email '{email}' already exists")
            
            # Create user instance
            user = User(username=username, password=password, email=email, **kwargs)
            
            # Save to database
            db.session.add(user)
            db.session.commit()
            
            current_app.logger.info(f"User created successfully: {user.username}")
            return user
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error creating user: {str(e)}")
            raise
    
    @staticmethod
    def authenticate_user(username: str, password: str) -> Optional[User]:
        """Authenticate user with username and password."""
        user = db.session.query(User).filter_by(username=username).first()
        
        if user and user.check_password(password) and user.is_active:
            # Update last login timestamp
            user.update_last_login()
            current_app.logger.info(f"User authenticated: {username}")
            return user
        
        current_app.logger.warning(f"Authentication failed for: {username}")
        return None
    
    @staticmethod
    def get_user_by_id(user_id: int) -> Optional[User]:
        """Get user by ID."""
        return db.session.get(User, user_id)
    
    @staticmethod
    def get_user_by_username(username: str) -> Optional[User]:
        """Get user by username."""
        return db.session.query(User).filter_by(username=username).first()
    
    @staticmethod
    def get_user_by_email(email: str) -> Optional[User]:
        """Get user by email."""
        return db.session.query(User).filter_by(email=email).first()
    
    @staticmethod
    def update_user_profile(user_id: int, **kwargs) -> Optional[User]:
        """Update user profile information."""
        user = db.session.get(User, user_id)
        if not user:
            return None
        
        # Update allowed fields
        allowed_fields = [
            'email', 'first_name', 'last_name', 'organization', 'bio'
        ]
        
        for field, value in kwargs.items():
            if field in allowed_fields and hasattr(user, field):
                setattr(user, field, value)
        
        try:
            db.session.commit()
            current_app.logger.info(f"User profile updated: {user.username}")
            return user
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error updating user profile: {str(e)}")
            raise
    
    @staticmethod
    def update_user_password(user_id: int, new_password: str) -> bool:
        """Update user password."""
        user = db.session.get(User, user_id)
        if not user:
            return False
        
        try:
            user.set_password(new_password)
            db.session.commit()
            current_app.logger.info(f"Password updated for user: {user.username}")
            return True
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error updating password: {str(e)}")
            return False
    
    @staticmethod
    def deactivate_user(user_id: int) -> bool:
        """Deactivate a user account."""
        user = db.session.get(User, user_id)
        if not user:
            return False
        
        try:
            user.is_active = False
            db.session.commit()
            current_app.logger.info(f"User deactivated: {user.username}")
            return True
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error deactivating user: {str(e)}")
            return False
    
    @staticmethod
    def activate_user(user_id: int) -> bool:
        """Activate a user account."""
        user = db.session.get(User, user_id)
        if not user:
            return False
        
        try:
            user.is_active = True
            db.session.commit()
            current_app.logger.info(f"User activated: {user.username}")
            return True
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error activating user: {str(e)}")
            return False
    
    @staticmethod
    def update_user_activity(user_id: int) -> None:
        """Update user's last activity timestamp."""
        user = db.session.get(User, user_id)
        if user:
            user.update_last_activity()
    
    @staticmethod
    def get_user_dashboard_data(user_id: int) -> Dict[str, Any]:
        """Get comprehensive dashboard data for a user."""
        user = db.session.get(User, user_id)
        if not user:
            return {}
        
        # Get user's datasets and analyses counts
        datasets_count = user.datasets.count()
        analyses_count = user.analyses.count()
        
        # Get recent activity
        recent_datasets = user.datasets.order_by(
            'created_at DESC'
        ).limit(5).all()
        
        recent_analyses = user.analyses.order_by(
            'created_at DESC'
        ).limit(5).all()
        
        return {
            'user_info': user.to_dict(),
            'stats': {
                'total_datasets': datasets_count,
                'total_analyses': analyses_count,
            },
            'recent_datasets': [d.to_dict() for d in recent_datasets],
            'recent_analyses': [a.to_dict() for a in recent_analyses],
        }