from datetime import timedelta
from pathlib import Path
from flask import Flask, url_for
import logging

from .routes import index, dashboard, login, logout, make_session, analyze, readme, favicon, health
from .config import get_config
from . import env_vars

# Import models to ensure they are registered with SQLAlchemy
from .models import Base, User, TTestAnalysis, DataSet
from .models.base import db
from .utils.database import create_tables, init_database

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SRC_DIR = Path(__file__).resolve().parents[1]
INSTANCE_DIR = SRC_DIR / 'instance'
INSTANCE_DIR.mkdir(parents=True, exist_ok=True)

app = Flask(
    __name__,
    template_folder='templates',
    static_folder='static',
    instance_path=str(INSTANCE_DIR),
)

# Load configuration based on environment
config_class = get_config(env_vars.ENV_TYPE)
app.config.from_object(config_class)

# Override with legacy configuration for backward compatibility
app.secret_key = env_vars.APP_SECRET
app.permanent_session_lifetime = timedelta(minutes=env_vars.SESSION_TIME)


@app.context_processor
def override_url_for() -> dict:
    def _url_for(endpoint, **values):
        # Normal behavior for non-static files
        if endpoint != "static":
            return url_for(endpoint, **values)
 
        # For static, switch depending on ENV
        filename = values.get("filename", "")
        if app.config["ENV_TYPE"] == "prod":
            gcs_bucket_url = app.config.get("GCS_BUCKET_URL")
            return f"{gcs_bucket_url}/{filename}"
        else:
            return url_for(endpoint, **values)
 
    return dict(url_for=_url_for)


def create_app(sqlalchemy_echo: bool = None):
    """Create and configure the Flask application."""

    if sqlalchemy_echo is not None:
        app.config["SQLALCHEMY_ECHO"] = sqlalchemy_echo
    
    # Initialize database
    init_database(app)
    
    # Create database tables if they don't exist
    with app.app_context():
        try:
            create_tables()
            logger.info("Database tables created/verified successfully")
        except Exception as e:
            logger.error(f"Error creating database tables: {str(e)}")
    
    # Register blueprints
    app.register_blueprint(make_session.bp)
    app.register_blueprint(analyze.bp)
    app.register_blueprint(index.bp)
    app.register_blueprint(dashboard.bp)
    app.register_blueprint(login.bp)
    app.register_blueprint(logout.bp)
    app.register_blueprint(readme.bp)
    app.register_blueprint(favicon.bp)
    app.register_blueprint(health.bp)
    
    # Register error handlers
    register_error_handlers(app)
    
    logger.info("Flask application created successfully")
    return app


def register_error_handlers(app):
    """Register error handlers for the application."""
    
    @app.errorhandler(404)
    def not_found_error(error):
        return {'error': 'Resource not found'}, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return {'error': 'Internal server error'}, 500
    
    @app.errorhandler(403)
    def forbidden_error(error):
        return {'error': 'Access forbidden'}, 403
    
    @app.errorhandler(401)
    def unauthorized_error(error):
        return {'error': 'Authentication required'}, 401