"""Database utility functions."""

import logging
from flask import current_app
from sqlalchemy import text

from ..models.base import Base, db


logger = logging.getLogger(__name__)


def init_database(app=None):
    """Initialize database with the Flask app."""
    if app is None:
        app = current_app
    
    db.init_app(app)
    logger.info("Database initialized successfully")


def create_tables():
    """Create all database tables."""
    try:
        Base.metadata.create_all(bind=db.engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {str(e)}")
        raise


def drop_tables():
    """Drop all database tables."""
    try:
        Base.metadata.drop_all(bind=db.engine)
        logger.info("Database tables dropped successfully")
    except Exception as e:
        logger.error(f"Error dropping database tables: {str(e)}")
        raise


def recreate_tables():
    """Drop and recreate all database tables."""
    drop_tables()
    create_tables()


def check_database_connection():
    """Check if database connection is working."""
    try:
        # Execute a simple query to test connection
        db.session.execute(text('SELECT 1'))
        db.session.commit()
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {str(e)}")
        return False


def get_database_info():
    """Get information about the database."""
    try:
        # Get database URL (without credentials)
        db_url = current_app.config.get('SQLALCHEMY_DATABASE_URI', 'Unknown')
        if '://' in db_url:
            db_type = db_url.split('://')[0]
        else:
            db_type = 'Unknown'
        
        return {
            'database_type': db_type,
            'connection_active': check_database_connection(),
            'echo_enabled': current_app.config.get('SQLALCHEMY_ECHO', False),
        }
    except Exception as e:
        logger.error(f"Error getting database info: {str(e)}")
        return {'error': str(e)}


def backup_database(backup_path: str):
    """Create a backup of the database (SQLite only)."""
    db_url = current_app.config.get('SQLALCHEMY_DATABASE_URI', '')
    
    if not db_url.startswith('sqlite:'):
        raise ValueError("Database backup is only supported for SQLite databases")
    
    import shutil
    import os
    
    # Extract database file path
    db_file = db_url.replace('sqlite:///', '').replace('sqlite://', '')
    
    if not os.path.exists(db_file):
        raise FileNotFoundError(f"Database file not found: {db_file}")
    
    try:
        shutil.copy2(db_file, backup_path)
        logger.info(f"Database backed up to: {backup_path}")
    except Exception as e:
        logger.error(f"Error backing up database: {str(e)}")
        raise


def restore_database(backup_path: str):
    """Restore database from backup (SQLite only)."""
    db_url = current_app.config.get('SQLALCHEMY_DATABASE_URI', '')
    
    if not db_url.startswith('sqlite:'):
        raise ValueError("Database restore is only supported for SQLite databases")
    
    import shutil
    import os
    
    if not os.path.exists(backup_path):
        raise FileNotFoundError(f"Backup file not found: {backup_path}")
    
    # Extract database file path
    db_file = db_url.replace('sqlite:///', '').replace('sqlite://', '')
    
    try:
        shutil.copy2(backup_path, db_file)
        logger.info(f"Database restored from: {backup_path}")
    except Exception as e:
        logger.error(f"Error restoring database: {str(e)}")
        raise


def seed_database():
    """Seed database with initial data."""
    from ..models import User
    from ..services import UserService
    
    try:
        # Check if admin user already exists
        admin_user = db.session.query(User).filter_by(username='admin').first()
        
        if not admin_user:
            # Create default admin user
            admin_user = UserService.create_user(
                username='admin',
                password='admin123',  # Change this in production!
                email='admin@example.com',
                first_name='Admin',
                last_name='User',
                is_admin=True
            )
            logger.info("Default admin user created")
        else:
            logger.info("Admin user already exists")
        
        db.session.commit()
        logger.info("Database seeded successfully")
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error seeding database: {str(e)}")
        raise