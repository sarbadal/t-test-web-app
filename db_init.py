#!/usr/bin/env python3
"""
Database initialization and migration script for T-Test Analysis Application.

This script provides utilities for:
- Initializing the database
- Creating/dropping tables
- Seeding with initial data
- Backing up and restoring data

Usage:
    python db_init.py init          # Initialize database and create tables
    python db_init.py seed          # Seed database with initial data
    python db_init.py reset         # Drop and recreate all tables
    python db_init.py backup <path> # Backup database (SQLite only)
    python db_init.py restore <path> # Restore database (SQLite only)
    python db_init.py info          # Show database information
"""

import os
import sys
import click
import logging
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.app.run import create_app
from src.app.utils.database import (
    create_tables, drop_tables, recreate_tables, 
    backup_database, restore_database, 
    get_database_info, seed_database, 
    check_database_connection
)
from src.app.models.base import db

# Configure logging
logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Keep CLI output clean unless there's a warning/error.
logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
logging.getLogger('sqlalchemy.pool').setLevel(logging.WARNING)
logging.getLogger('app').setLevel(logging.WARNING)


def _cli_app():
    """Create app configured for quiet CLI output."""
    return create_app(sqlalchemy_echo=False)


@click.group()
def cli():
    """T-Test Analysis Database Management CLI"""
    pass


@cli.command()
def init():
    """Initialize the database and create all tables."""
    click.echo("Initializing database...")
    
    app = _cli_app()
    with app.app_context():
        try:
            create_tables()
            click.echo("✓ Database tables created successfully!")
        except Exception as e:
            click.echo(f"✗ Error creating tables: {str(e)}", err=True)
            sys.exit(1)


@cli.command()
def seed():
    """Seed the database with initial data."""
    click.echo("Seeding database with initial data...")
    
    app = _cli_app()
    with app.app_context():
        try:
            seed_database()
            click.echo("✓ Database seeded successfully!")
            click.echo("Default admin user: admin / admin123")
            click.echo("⚠️  Please change the admin password in production!")
        except Exception as e:
            click.echo(f"✗ Error seeding database: {str(e)}", err=True)
            sys.exit(1)


@cli.command()
@click.confirmation_option(prompt='This will delete ALL data. Are you sure?')
def reset():
    """Drop all tables and recreate them."""
    click.echo("Resetting database...")
    
    app = _cli_app()
    with app.app_context():
        try:
            recreate_tables()
            click.echo("✓ Database reset successfully!")
        except Exception as e:
            click.echo(f"✗ Error resetting database: {str(e)}", err=True)
            sys.exit(1)


@cli.command()
@click.argument('backup_path')
def backup(backup_path):
    """Backup the database to a file (SQLite only)."""
    click.echo(f"Backing up database to {backup_path}...")
    
    app = _cli_app()
    with app.app_context():
        try:
            # Add timestamp to backup path if it's a directory
            if os.path.isdir(backup_path):
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_path = os.path.join(backup_path, f"ttest_backup_{timestamp}.db")
            
            backup_database(backup_path)
            click.echo(f"✓ Database backed up to: {backup_path}")
        except Exception as e:
            click.echo(f"✗ Error backing up database: {str(e)}", err=True)
            sys.exit(1)


@cli.command()
@click.argument('backup_path')
@click.confirmation_option(prompt='This will replace the current database. Are you sure?')
def restore(backup_path):
    """Restore the database from a backup file (SQLite only)."""
    click.echo(f"Restoring database from {backup_path}...")
    
    app = _cli_app()
    with app.app_context():
        try:
            restore_database(backup_path)
            click.echo("✓ Database restored successfully!")
        except Exception as e:
            click.echo(f"✗ Error restoring database: {str(e)}", err=True)
            sys.exit(1)


@cli.command()
def info():
    """Show database information."""
    app = _cli_app()
    with app.app_context():
        try:
            db_info = get_database_info()
            
            click.echo("Database Information:")
            click.echo(f"  Type: {db_info.get('database_type', 'Unknown')}")
            click.echo(f"  Connection: {'✓ Active' if db_info.get('connection_active') else '✗ Failed'}")
            click.echo(f"  Echo: {'Enabled' if db_info.get('echo_enabled') else 'Disabled'}")
            
            # Show table information
            if db_info.get('connection_active'):
                from src.app.models import User, DataSet, TTestAnalysis
                
                user_count = db.session.query(User).count()
                dataset_count = db.session.query(DataSet).count()
                analysis_count = db.session.query(TTestAnalysis).count()
                
                click.echo("\nTable Statistics:")
                click.echo(f"  Users: {user_count}")
                click.echo(f"  Datasets: {dataset_count}")
                click.echo(f"  Analyses: {analysis_count}")
            
        except Exception as e:
            click.echo(f"✗ Error getting database info: {str(e)}", err=True)
            sys.exit(1)


@cli.command()
def test_connection():
    """Test database connection."""
    click.echo("Testing database connection...")
    
    app = _cli_app()
    with app.app_context():
        if check_database_connection():
            click.echo("✓ Database connection successful!")
        else:
            click.echo("✗ Database connection failed!", err=True)
            sys.exit(1)


@cli.command()
def create_admin():
    """Create a new admin user interactively."""
    app = _cli_app()
    with app.app_context():
        from src.app.services import UserService
        from src.app.models import User
        
        click.echo("Creating new admin user...")
        
        username = click.prompt("Username")
        
        # Check if user already exists
        existing_user = db.session.query(User).filter_by(username=username).first()
        if existing_user:
            click.echo(f"✗ User '{username}' already exists!", err=True)
            sys.exit(1)
        
        password = click.prompt("Password", hide_input=True, confirmation_prompt=True)
        email = click.prompt("Email (optional)", default="")
        first_name = click.prompt("First name (optional)", default="")
        last_name = click.prompt("Last name (optional)", default="")
        
        try:
            user = UserService.create_user(
                username=username,
                password=password,
                email=email or None,
                first_name=first_name or None,
                last_name=last_name or None,
                is_admin=True
            )
            click.echo(f"✓ Admin user '{username}' created successfully!")
        except Exception as e:
            click.echo(f"✗ Error creating user: {str(e)}", err=True)
            sys.exit(1)


@cli.command()
def create_user():
    """Create a new non-admin user interactively."""
    app = _cli_app()
    with app.app_context():
        from src.app.services import UserService
        from src.app.models import User

        click.echo("Creating new non-admin user...")

        username = click.prompt("Username")

        # Check if user already exists
        existing_user = db.session.query(User).filter_by(username=username).first()
        if existing_user:
            click.echo(f"✗ User '{username}' already exists!", err=True)
            sys.exit(1)

        password = click.prompt("Password", hide_input=True, confirmation_prompt=True)
        email = click.prompt("Email (optional)", default="")
        first_name = click.prompt("First name (optional)", default="")
        last_name = click.prompt("Last name (optional)", default="")

        try:
            user = UserService.create_user(
                username=username,
                password=password,
                email=email or None,
                first_name=first_name or None,
                last_name=last_name or None,
                is_admin=False
            )
            click.echo(f"✓ User '{user.username}' created successfully!")
        except Exception as e:
            click.echo(f"✗ Error creating user: {str(e)}", err=True)
            sys.exit(1)


@cli.command()
def migrate():
    """Run database migrations (placeholder for future use)."""
    click.echo("Running database migrations...")
    
    # This is a placeholder for future migration functionality
    # In a real application, you might use Flask-Migrate or Alembic
    
    app = _cli_app()
    with app.app_context():
        click.echo("✓ No migrations to run (placeholder)")


if __name__ == '__main__':
    cli()