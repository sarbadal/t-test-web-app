"""Decorators for route protection and authorization."""

from functools import wraps
from flask import session, redirect, url_for, jsonify, request

from ..services import UserService
from ..models.base import db


def login_required(f):
    """Decorator to require user login for accessing routes."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if user is logged in
        if not session.get('logged_in') or not session.get('user_id'):
            if request.is_json or request.path.startswith('/api/'):
                return jsonify({'error': 'Authentication required'}), 401
            return redirect(url_for('login.login'))
        
        # Update user activity
        user_id = session.get('user_id')
        if user_id:
            UserService.update_user_activity(user_id)
        
        return f(*args, **kwargs)
    
    return decorated_function


def admin_required(f):
    """Decorator to require admin privileges for accessing routes."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # First check if user is logged in
        if not session.get('logged_in') or not session.get('user_id'):
            if request.is_json or request.path.startswith('/api/'):
                return jsonify({'error': 'Authentication required'}), 401
            return redirect(url_for('login.login'))
        
        # Check if user is admin
        user_id = session.get('user_id')
        user = UserService.get_user_by_id(user_id)
        
        if not user or not user.is_admin:
            if request.is_json or request.path.startswith('/api/'):
                return jsonify({'error': 'Admin access required'}), 403
            return redirect(url_for('home.home'))
        
        # Update user activity
        UserService.update_user_activity(user_id)
        
        return f(*args, **kwargs)
    
    return decorated_function


def api_login_required(f):
    """Decorator specifically for API endpoints that require authentication."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in') or not session.get('user_id'):
            return jsonify({'error': 'Authentication required'}), 401
        
        # Update user activity
        user_id = session.get('user_id')
        if user_id:
            UserService.update_user_activity(user_id)
        
        return f(*args, **kwargs)
    
    return decorated_function


def get_current_user():
    """Helper function to get the current authenticated user."""
    user_id = session.get('user_id')
    if user_id:
        return UserService.get_user_by_id(user_id)
    return None


def require_user_ownership(model_class, id_param='id', user_field='user_id'):
    """
    Decorator to ensure the current user owns the resource being accessed.
    
    Args:
        model_class: The SQLAlchemy model class
        id_param: The parameter name for the resource ID
        user_field: The field name that contains the user ID
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get current user
            user_id = session.get('user_id')
            if not user_id:
                return jsonify({'error': 'Authentication required'}), 401
            
            # Get resource ID from kwargs
            resource_id = kwargs.get(id_param)
            if not resource_id:
                return jsonify({'error': 'Resource ID required'}), 400
            
            # Check if resource exists and belongs to user
            resource = db.session.get(model_class, resource_id)
            if not resource:
                return jsonify({'error': 'Resource not found'}), 404
            
            if getattr(resource, user_field) != user_id:
                return jsonify({'error': 'Access denied'}), 403
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator