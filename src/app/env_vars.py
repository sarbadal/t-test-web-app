import os
from pathlib import Path

ENV_TYPE = os.getenv("ENV_TYPE", "dev")  # dev or prod
API_BASE_URL = os.getenv("API_BASE_URL", "/api/data")
APP_PASSWORD = os.getenv("APP_PASSWORD", "0000")
APP_SECRET = os.getenv("APP_SECRET", "51HgZrX9Q2bYlX3sYvPqL9aTgZrX9Q2b")
SESSION_TIME = int(os.getenv("SESSION_TIME", 10))
DASHBOARD_TITLE = os.getenv("DASHBOARD_TITLE", "OGS A|B Testing Dashboard")
DASHBOARD_FOOTER = os.getenv("DASHBOARD_FOOTER", "© 2023 OGS. All rights reserved.")
GCS_BUCKET_NAME = os.getenv("GCS_BUCKET_NAME", "t-test-analysis")
GCS_BUCKET_PREFIX = os.getenv("GCS_BUCKET_PREFIX", "t-test-analysis/t-test/app")
GCS_BLOB_BASE_URL = os.getenv("GCS_BLOB_BASE_URL", "storage.googleapis.com")
STATIC_BASE_URL = os.getenv("STATIC_BASE_URL", "")

# Database configuration
_SRC_DIR = Path(__file__).resolve().parents[1]
_DEFAULT_DB_PATH = (_SRC_DIR / "instance" / "ttest_analysis.db").resolve()
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{_DEFAULT_DB_PATH}")
DATABASE_ECHO = os.getenv("DATABASE_ECHO", "False").lower() == "true"
DATABASE_POOL_SIZE = int(os.getenv("DATABASE_POOL_SIZE", "5"))
DATABASE_POOL_TIMEOUT = int(os.getenv("DATABASE_POOL_TIMEOUT", "30"))
DATABASE_POOL_RECYCLE = int(os.getenv("DATABASE_POOL_RECYCLE", "3600"))

# SQLAlchemy configuration
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_RECORD_QUERIES = os.getenv("SQLALCHEMY_RECORD_QUERIES", "False").lower() == "true"
