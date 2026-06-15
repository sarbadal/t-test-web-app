from flask import Blueprint, jsonify
from sqlalchemy import inspect

from ..models.base import db

bp = Blueprint("health", __name__)


@bp.route("/api/health", methods=["GET"])
def health() -> tuple:
    """Health endpoint showing DB connectivity and required table readiness."""
    try:
        inspector = inspect(db.engine)
        tables = set(inspector.get_table_names())
        required_tables = {"users", "datasets", "ttest_analyses"}
        missing_tables = sorted(required_tables - tables)
        is_ready = len(missing_tables) == 0

        return jsonify({
            "status": "ok" if is_ready else "degraded",
            "database_connected": True,
            "required_tables_present": is_ready,
            "missing_tables": missing_tables,
        }), 200 if is_ready else 503
    except Exception as exc:
        return jsonify({
            "status": "error",
            "database_connected": False,
            "required_tables_present": False,
            "missing_tables": [],
            "error": str(exc),
        }), 503
