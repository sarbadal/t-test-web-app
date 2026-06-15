import os
from typing import Literal
from . import env_vars

EnvType = Literal["dev", "prod"]


def get_gcs_bucket_url(prefix: str = env_vars.GCS_BUCKET_PREFIX) -> str:
    bucket = env_vars.GCS_BUCKET_NAME
    gcs_blob_base_url = env_vars.GCS_BLOB_BASE_URL
    return f"https://{gcs_blob_base_url}/{bucket}/{prefix}/static"

class Config:
    # Environment configuration
    ENV_TYPE = env_vars.ENV_TYPE
    GCS_BUCKET_URL = get_gcs_bucket_url()

    # File types or folders that should be served from GCS
    OFFLOAD_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".svg", ".mp4", ".webm"}
    OFFLOAD_FOLDERS = {"images", "videos", "uploads"}
    
    # Database configuration
    SQLALCHEMY_DATABASE_URI = env_vars.DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = env_vars.SQLALCHEMY_TRACK_MODIFICATIONS
    SQLALCHEMY_RECORD_QUERIES = env_vars.SQLALCHEMY_RECORD_QUERIES
    SQLALCHEMY_ECHO = env_vars.DATABASE_ECHO
    
    # Database pool settings (for production databases)
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': env_vars.DATABASE_POOL_SIZE,
        'pool_timeout': env_vars.DATABASE_POOL_TIMEOUT,
        'pool_recycle': env_vars.DATABASE_POOL_RECYCLE,
        'pool_pre_ping': True,  # Verify connections before use
    }
    
    # Security configuration
    SECRET_KEY = env_vars.APP_SECRET
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    SQLALCHEMY_ECHO = True


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    SQLALCHEMY_ECHO = False


class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False


# Configuration mapping
config_map = {
    'dev': DevelopmentConfig,
    'prod': ProductionConfig,
    'test': TestingConfig,
}

def get_config(env_type: str = None) -> Config:
    """Get configuration class based on environment type."""
    env_type = env_type or env_vars.ENV_TYPE
    return config_map.get(env_type, DevelopmentConfig)


# https://storage.cloud.google.com/t-test-analysis/t-test/app/static/js/donut_chart.js
# gsutil iam ch allUsers:objectViewer gs://t-test-analysis

