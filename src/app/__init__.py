"""T-Test Analysis Flask Application Package.

This package contains a Flask web application for performing statistical t-tests
with a database-backed architecture for storing users, datasets, and analysis results.
"""

from flask import Flask
from .models.base import db
from .utils.database import init_database


def create_app(config_name=None):
    """Application factory pattern for creating Flask app instances."""
    from .run import create_app as _create_app
    return _create_app()


__version__ = "2.0.0"
__author__ = "T-Test Analysis Team"
